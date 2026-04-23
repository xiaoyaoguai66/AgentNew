import asyncio
import logging
import time
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.ai import AiChatRequest, AiChatResponse, AiSourceItem, AiWorkflowTraceItem
from services import (
    agent_observability_service,
    ai_service,
    answer_verifier_service,
    dual_route_filter_service,
    news_retrieval_service,
    query_analysis_service,
    response_formatter_service,
    retrieval_fusion_service,
    retrieval_planner_service,
    tavily_service,
    vector_index_pipeline_service,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkflowState:
    trace_id: str = ""
    run_id: str = ""
    query_analysis: object | None = None
    plan_decision: object | None = None
    local_sources: list[AiSourceItem] = field(default_factory=list)
    web_sources: list[AiSourceItem] = field(default_factory=list)
    merged_sources: list[AiSourceItem] = field(default_factory=list)
    confidence: float = 0.0
    strategy: str = ""
    verification_result: object | None = None
    follow_up_suggestions: list[str] = field(default_factory=list)
    workflow_trace: list[AiWorkflowTraceItem] = field(default_factory=list)


def _build_no_hit_reply() -> str:
    return (
        "当前没有检索到足够可靠的本地新闻或 Web 搜索证据，所以我先不直接生成结论，避免误导。"
        "你可以尝试换一个更明确的关键词、放宽时间范围，或者继续追问具体事件。"
    )


def _resolve_strategy(
    retrieval_plan: str,
    local_sources: list[AiSourceItem],
    web_sources: list[AiSourceItem],
) -> str:
    if retrieval_plan == "local-first":
        if local_sources and web_sources:
            return "local_first_with_web_fallback_answer"
        if local_sources:
            return "local_first_answer"
        if web_sources:
            return "local_first_web_fallback_answer"
        return "local_first_nohit"

    if retrieval_plan == "web-first":
        if web_sources and local_sources:
            return "web_first_with_local_support_answer"
        if web_sources:
            return "web_first_answer"
        if local_sources:
            return "web_first_local_fallback_answer"
        return "web_first_nohit"

    if local_sources and web_sources:
        return "hybrid_local_web_reranked_answer"
    if local_sources:
        return "hybrid_local_only_answer"
    if web_sources:
        return "hybrid_web_only_answer"
    return "hybrid_nohit"


def _append_trace(
    trace: list[AiWorkflowTraceItem],
    node: str,
    status: str,
    detail: str,
    started_at: float,
) -> None:
    trace.append(
        AiWorkflowTraceItem(
            stepIndex=len(trace) + 1,
            node=node,
            status=status,
            detail=detail,
            durationMs=max(int((time.perf_counter() - started_at) * 1000), 0),
        )
    )


def _build_workflow_summary(trace: list[AiWorkflowTraceItem]) -> str:
    if not trace:
        return ""
    return " -> ".join(step.node for step in trace)


@agent_observability_service.langsmith_traceable(
    name="Query Analysis",
    run_type="chain",
    tags=["query-analysis"],
)
def _run_query_analysis(data: AiChatRequest):
    return query_analysis_service.analyze_query(
        question=data.question,
        category=data.category,
        time_range=data.time_range,
        mode=data.mode,
        web_enabled=tavily_service.is_enabled(),
    )


@agent_observability_service.langsmith_traceable(
    name="Retrieval Planner",
    run_type="chain",
    tags=["retrieval-planner"],
)
def _run_retrieval_planner(data: AiChatRequest, query_analysis):
    return retrieval_planner_service.decide_retrieval_plan(
        question=data.question,
        category=data.category,
        time_range=data.time_range,
        web_enabled=tavily_service.is_enabled(),
        analysis=query_analysis,
    )


@agent_observability_service.langsmith_traceable(
    name="Local News Retrieval",
    run_type="retriever",
    tags=["local-retrieval"],
)
async def _retrieve_local(db: AsyncSession, data: AiChatRequest) -> list[AiSourceItem]:
    return await news_retrieval_service.retrieve_news_sources(
        db=db,
        question=data.question,
        category=data.category,
        time_range=data.time_range,
    )


@agent_observability_service.langsmith_traceable(
    name="Tavily Web Retrieval",
    run_type="retriever",
    tags=["web-retrieval"],
)
async def _retrieve_web(data: AiChatRequest) -> list[AiSourceItem]:
    return await tavily_service.search_news_sources(
        question=data.question,
        category=data.category,
        time_range=data.time_range,
    )


async def _safe_retrieve_web(data: AiChatRequest, run_context: dict) -> list[AiSourceItem]:
    try:
        return await _retrieve_web(
            data,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="web-retrieval",
                metadata={"category": data.category, "time_range": data.time_range},
            ),
        )
    except Exception as exc:  # pragma: no cover - external integration fallback
        logger.warning("web retrieval degraded to empty results: %s", exc)
        return []


async def _execute_retrieval_plan(
    db: AsyncSession,
    data: AiChatRequest,
    retrieval_plan: str,
    run_context: dict,
) -> tuple[list[AiSourceItem], list[AiSourceItem]]:
    local_sources: list[AiSourceItem] = []
    web_sources: list[AiSourceItem] = []

    if retrieval_plan == "local-first":
        local_sources = await _retrieve_local(
            db,
            data,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="local-retrieval",
                metadata={"retrieval_plan": retrieval_plan},
            ),
        )
        if tavily_service.is_enabled() and not retrieval_planner_service.is_local_result_strong(local_sources):
            web_sources = await _safe_retrieve_web(data, run_context)
        return local_sources, web_sources

    if retrieval_plan == "web-first":
        web_sources = await _safe_retrieve_web(data, run_context)
        if not retrieval_planner_service.is_web_result_strong(web_sources):
            local_sources = await _retrieve_local(
                db,
                data,
                langsmith_extra=agent_observability_service.build_langsmith_extra(
                    run_context=run_context,
                    node="local-retrieval",
                    metadata={"retrieval_plan": retrieval_plan},
                ),
            )
        return local_sources, web_sources

    local_result, web_result = await asyncio.gather(
        _retrieve_local(
            db,
            data,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="local-retrieval",
                metadata={"retrieval_plan": retrieval_plan},
            ),
        ),
        _safe_retrieve_web(data, run_context),
    )
    return local_result, web_result


@agent_observability_service.langsmith_traceable(
    name="Route Filter",
    run_type="chain",
    tags=["route-filter"],
)
def _run_route_filter(
    *,
    question: str,
    retrieval_plan: str,
    time_range: str,
    local_sources: list[AiSourceItem],
    web_sources: list[AiSourceItem],
) -> tuple[list[AiSourceItem], list[AiSourceItem]]:
    return dual_route_filter_service.filter_dual_route_sources(
        question=question,
        retrieval_plan=retrieval_plan,
        time_range=time_range,
        local_sources=local_sources,
        web_sources=web_sources,
    )


@agent_observability_service.langsmith_traceable(
    name="Final Rerank",
    run_type="chain",
    tags=["final-rerank"],
)
def _run_final_rerank(
    *,
    question: str,
    category: str,
    time_range: str,
    local_sources: list[AiSourceItem],
    web_sources: list[AiSourceItem],
    retrieval_plan: str,
) -> tuple[list[AiSourceItem], float]:
    merged_sources = retrieval_fusion_service.fuse_sources(
        question=question,
        category=category,
        time_range=time_range,
        local_sources=local_sources,
        web_sources=web_sources,
        retrieval_plan=retrieval_plan,
    )
    confidence = retrieval_fusion_service.estimate_confidence(
        local_sources,
        web_sources,
        merged_sources,
    )
    return merged_sources, confidence


@agent_observability_service.langsmith_traceable(
    name="LLM Generation",
    run_type="llm",
    tags=["generator"],
)
async def _run_generator(data: AiChatRequest, sources: list[AiSourceItem], query_analysis) -> str:
    return await ai_service.chat(data, sources, query_analysis=query_analysis)


@agent_observability_service.langsmith_traceable(
    name="Answer Verifier",
    run_type="chain",
    tags=["verifier"],
)
def _run_verifier(
    *,
    question: str,
    reply: str,
    sources: list[AiSourceItem],
    confidence: float,
    retrieval_plan: str,
):
    return answer_verifier_service.verify_answer(
        question=question,
        reply=reply,
        sources=sources,
        confidence=confidence,
        retrieval_plan=retrieval_plan,
    )


@agent_observability_service.langsmith_traceable(
    name="Response Formatter",
    run_type="chain",
    tags=["response-formatter"],
)
def _run_response_formatter(
    *,
    question: str,
    category: str,
    retrieval_plan: str,
    evidence_level: str,
    sources: list[AiSourceItem],
    reply: str,
) -> tuple[str, list[str]]:
    formatted_reply = response_formatter_service.format_reply(reply)
    followups = response_formatter_service.build_follow_up_suggestions(
        question=question,
        category=category,
        retrieval_plan=retrieval_plan,
        evidence_level=evidence_level,
        sources=sources,
    )
    return formatted_reply, followups


def get_runtime_status() -> dict:
    retrieval_status = news_retrieval_service.get_runtime_status()
    index_status = vector_index_pipeline_service.get_runtime_status()
    filter_status = dual_route_filter_service.get_runtime_status()
    rerank_status = retrieval_fusion_service.get_runtime_status()
    verifier_status = answer_verifier_service.get_runtime_status()
    analysis_status = query_analysis_service.get_runtime_status()
    formatter_status = response_formatter_service.get_runtime_status()
    observability_status = agent_observability_service.get_runtime_status()
    return {
        "promptVersion": ai_service.PROMPT_VERSION,
        "retrievalEnabled": True,
        "webSearchEnabled": tavily_service.is_enabled(),
        "plannerEnabled": True,
        "workflowEnabled": True,
        "workflowStyle": "stateful-node-pipeline",
        "workflowNodes": [
            "query-analysis",
            "retrieval-planner",
            "retrieval",
            "route-filter",
            "final-rerank",
            "generator",
            "verifier",
            "response-formatter",
        ],
        "supportedRetrievalPlans": list(retrieval_planner_service.SUPPORTED_RETRIEVAL_PLANS),
        **retrieval_status,
        **index_status,
        **filter_status,
        **rerank_status,
        **verifier_status,
        **analysis_status,
        **formatter_status,
        **observability_status,
    }


@agent_observability_service.langsmith_traceable(
    name="AgentNews Workflow",
    run_type="chain",
    tags=["workflow"],
)
async def _run_agent_workflow(
    db: AsyncSession,
    data: AiChatRequest,
    run_context: dict,
) -> AiChatResponse:
    state = WorkflowState(
        trace_id=run_context["traceId"],
        run_id=run_context["runId"],
    )
    web_search_enabled = tavily_service.is_enabled()

    try:
        started_at = time.perf_counter()
        state.query_analysis = _run_query_analysis(
            data,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="query-analysis",
            ),
        )
        _append_trace(
            state.workflow_trace,
            "query-analysis",
            "completed",
            f"intent={state.query_analysis.intent}, freshness={state.query_analysis.freshness_need}, scope={state.query_analysis.scope_preference}",
            started_at,
        )

        started_at = time.perf_counter()
        state.plan_decision = _run_retrieval_planner(
            data,
            state.query_analysis,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="retrieval-planner",
            ),
        )
        _append_trace(
            state.workflow_trace,
            "retrieval-planner",
            "completed",
            f"plan={state.plan_decision.plan_type}",
            started_at,
        )

        started_at = time.perf_counter()
        state.local_sources, state.web_sources = await _execute_retrieval_plan(
            db,
            data,
            state.plan_decision.plan_type,
            run_context,
        )
        _append_trace(
            state.workflow_trace,
            "retrieval",
            "completed",
            f"local={len(state.local_sources)}, web={len(state.web_sources)}",
            started_at,
        )

        started_at = time.perf_counter()
        state.local_sources, state.web_sources = _run_route_filter(
            question=data.question,
            retrieval_plan=state.plan_decision.plan_type,
            time_range=data.time_range,
            local_sources=state.local_sources,
            web_sources=state.web_sources,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="route-filter",
            ),
        )
        _append_trace(
            state.workflow_trace,
            "route-filter",
            "completed",
            f"local={len(state.local_sources)}, web={len(state.web_sources)}",
            started_at,
        )

        started_at = time.perf_counter()
        state.merged_sources, state.confidence = _run_final_rerank(
            question=data.question,
            category=data.category,
            time_range=data.time_range,
            local_sources=state.local_sources,
            web_sources=state.web_sources,
            retrieval_plan=state.plan_decision.plan_type,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="final-rerank",
            ),
        )
        state.strategy = _resolve_strategy(
            state.plan_decision.plan_type,
            state.local_sources,
            state.web_sources,
        )
        _append_trace(
            state.workflow_trace,
            "final-rerank",
            "completed",
            f"merged={len(state.merged_sources)}, confidence={state.confidence}",
            started_at,
        )

        if not state.merged_sources:
            started_at = time.perf_counter()
            _append_trace(
                state.workflow_trace,
                "verifier",
                "fallback",
                "no evidence -> refusal",
                started_at,
            )
            started_at = time.perf_counter()
            _, state.follow_up_suggestions = _run_response_formatter(
                question=data.question,
                category=data.category,
                retrieval_plan=state.plan_decision.plan_type,
                evidence_level="none",
                sources=[],
                reply="",
                langsmith_extra=agent_observability_service.build_langsmith_extra(
                    run_context=run_context,
                    node="response-formatter",
                    metadata={"mode": "no-evidence"},
                ),
            )
            _append_trace(
                state.workflow_trace,
                "response-formatter",
                "completed",
                f"followups={len(state.follow_up_suggestions)}",
                started_at,
            )
            response = AiChatResponse(
                reply=_build_no_hit_reply(),
                model="retrieval-fallback",
                promptVersion=ai_service.PROMPT_VERSION,
                traceId=state.trace_id,
                runId=state.run_id,
                workflowSummary=_build_workflow_summary(state.workflow_trace),
                strategy=state.strategy,
                retrievalPlan=state.plan_decision.plan_type,
                plannerReason=state.plan_decision.reason,
                queryIntent=state.query_analysis.intent,
                freshnessNeed=state.query_analysis.freshness_need,
                scopePreference=state.query_analysis.scope_preference,
                analysisReason=state.query_analysis.reason,
                confidence=state.confidence,
                verificationStatus="refused",
                verificationReason="当前没有检索到足够证据，已触发无证据拒答。",
                evidenceLevel="none",
                guardrailApplied=True,
                followUpSuggestions=state.follow_up_suggestions,
                workflowTrace=state.workflow_trace,
                sources=[],
                retrievalEnabled=True,
                webSearchEnabled=web_search_enabled,
            )
            agent_observability_service.record_success(run_context, response)
            return response

        started_at = time.perf_counter()
        raw_reply = await _run_generator(
            data,
            state.merged_sources,
            state.query_analysis,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="generator",
                metadata={"source_count": len(state.merged_sources)},
            ),
        )
        _append_trace(
            state.workflow_trace,
            "generator",
            "completed",
            f"reply_chars={len(raw_reply)}",
            started_at,
        )

        started_at = time.perf_counter()
        state.verification_result = _run_verifier(
            question=data.question,
            reply=raw_reply,
            sources=state.merged_sources,
            confidence=state.confidence,
            retrieval_plan=state.plan_decision.plan_type,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="verifier",
            ),
        )
        verifier_status = "completed" if state.verification_result.status == "accepted" else "guarded"
        _append_trace(
            state.workflow_trace,
            "verifier",
            verifier_status,
            f"status={state.verification_result.status}, evidence={state.verification_result.evidence_level}",
            started_at,
        )

        started_at = time.perf_counter()
        formatted_reply, state.follow_up_suggestions = _run_response_formatter(
            question=data.question,
            category=data.category,
            retrieval_plan=state.plan_decision.plan_type,
            evidence_level=state.verification_result.evidence_level,
            sources=state.merged_sources,
            reply=state.verification_result.reply,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="response-formatter",
            ),
        )
        _append_trace(
            state.workflow_trace,
            "response-formatter",
            "completed",
            f"followups={len(state.follow_up_suggestions)}",
            started_at,
        )

        response = AiChatResponse(
            reply=formatted_reply,
            model=ai_service.settings.llm_model,
            promptVersion=ai_service.PROMPT_VERSION,
            traceId=state.trace_id,
            runId=state.run_id,
            workflowSummary=_build_workflow_summary(state.workflow_trace),
            strategy=state.strategy,
            retrievalPlan=state.plan_decision.plan_type,
            plannerReason=state.plan_decision.reason,
            queryIntent=state.query_analysis.intent,
            freshnessNeed=state.query_analysis.freshness_need,
            scopePreference=state.query_analysis.scope_preference,
            analysisReason=state.query_analysis.reason,
            confidence=state.confidence,
            verificationStatus=state.verification_result.status,
            verificationReason=state.verification_result.reason,
            evidenceLevel=state.verification_result.evidence_level,
            guardrailApplied=state.verification_result.guardrail_applied,
            followUpSuggestions=state.follow_up_suggestions,
            workflowTrace=state.workflow_trace,
            sources=state.merged_sources,
            retrievalEnabled=True,
            webSearchEnabled=web_search_enabled,
        )
        agent_observability_service.record_success(run_context, response)
        return response
    except Exception as exc:
        agent_observability_service.record_failure(
            run_context=run_context,
            workflow_trace=[item.model_dump(mode="json", by_alias=True) for item in state.workflow_trace],
            error_message=str(exc),
        )
        raise


async def chat(db: AsyncSession, data: AiChatRequest) -> AiChatResponse:
    run_context = agent_observability_service.create_run_context(data)
    with agent_observability_service.langsmith_context(
        run_context=run_context,
        metadata={
            "category": data.category,
            "mode": data.mode,
            "time_range": data.time_range,
        },
    ):
        return await _run_agent_workflow(
            db,
            data,
            run_context,
            langsmith_extra=agent_observability_service.build_langsmith_extra(
                run_context=run_context,
                node="workflow",
                metadata={"question_length": len(data.question)},
            ),
        )
