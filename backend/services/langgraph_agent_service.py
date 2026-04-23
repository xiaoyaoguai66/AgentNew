import asyncio
import logging
import time
from functools import lru_cache
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
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


class GraphContext(TypedDict):
    db: AsyncSession
    run_context: dict


class AgentGraphState(TypedDict, total=False):
    data: AiChatRequest
    trace_id: str
    run_id: str
    query_analysis: Any
    plan_decision: Any
    local_sources: list[AiSourceItem]
    web_sources: list[AiSourceItem]
    merged_sources: list[AiSourceItem]
    confidence: float
    strategy: str
    verification_result: Any
    follow_up_suggestions: list[str]
    workflow_trace: list[AiWorkflowTraceItem]
    final_reply: str
    final_model: str
    final_verification_status: str
    final_verification_reason: str
    final_evidence_level: str
    final_guardrail_applied: bool


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
    state: AgentGraphState,
    *,
    node: str,
    status: Literal["completed", "guarded", "fallback"],
    detail: str,
    started_at: float,
) -> list[AiWorkflowTraceItem]:
    trace = list(state.get("workflow_trace", []))
    trace.append(
        AiWorkflowTraceItem(
            stepIndex=len(trace) + 1,
            node=node,
            status=status,
            detail=detail,
            durationMs=max(int((time.perf_counter() - started_at) * 1000), 0),
        )
    )
    return trace


def _build_workflow_summary(trace: list[AiWorkflowTraceItem]) -> str:
    if not trace:
        return ""
    return " -> ".join(step.node for step in trace)


def _node_query_analysis(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    analysis = query_analysis_service.analyze_query(
        question=data.question,
        category=data.category,
        time_range=data.time_range,
        mode=data.mode,
        web_enabled=tavily_service.is_enabled(),
    )
    return {
        "query_analysis": analysis,
        "workflow_trace": _append_trace(
            state,
            node="query-analysis",
            status="completed",
            detail=f"intent={analysis.intent}, freshness={analysis.freshness_need}, scope={analysis.scope_preference}",
            started_at=started_at,
        ),
    }


def _node_retrieval_planner(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    plan_decision = retrieval_planner_service.decide_retrieval_plan(
        question=data.question,
        category=data.category,
        time_range=data.time_range,
        web_enabled=tavily_service.is_enabled(),
        analysis=state["query_analysis"],
    )
    return {
        "plan_decision": plan_decision,
        "workflow_trace": _append_trace(
            state,
            node="retrieval-planner",
            status="completed",
            detail=f"plan={plan_decision.plan_type}",
            started_at=started_at,
        ),
    }


async def _safe_retrieve_web(data: AiChatRequest) -> list[AiSourceItem]:
    try:
        return await tavily_service.search_news_sources(
            question=data.question,
            category=data.category,
            time_range=data.time_range,
        )
    except Exception as exc:  # pragma: no cover - external integration fallback
        logger.warning("web retrieval degraded to empty results: %s", exc)
        return []


async def _node_retrieval(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    db = runtime.context["db"]
    retrieval_plan = state["plan_decision"].plan_type
    local_sources: list[AiSourceItem] = []
    web_sources: list[AiSourceItem] = []

    if retrieval_plan == "local-first":
        local_sources = await news_retrieval_service.retrieve_news_sources(
            db=db,
            question=data.question,
            category=data.category,
            time_range=data.time_range,
        )
        if tavily_service.is_enabled() and not retrieval_planner_service.is_local_result_strong(local_sources):
            web_sources = await _safe_retrieve_web(data)
    elif retrieval_plan == "web-first":
        web_sources = await _safe_retrieve_web(data)
        if not retrieval_planner_service.is_web_result_strong(web_sources):
            local_sources = await news_retrieval_service.retrieve_news_sources(
                db=db,
                question=data.question,
                category=data.category,
                time_range=data.time_range,
            )
    else:
        local_sources, web_sources = await asyncio.gather(
            news_retrieval_service.retrieve_news_sources(
                db=db,
                question=data.question,
                category=data.category,
                time_range=data.time_range,
            ),
            _safe_retrieve_web(data),
        )

    return {
        "local_sources": local_sources,
        "web_sources": web_sources,
        "workflow_trace": _append_trace(
            state,
            node="retrieval",
            status="completed",
            detail=f"local={len(local_sources)}, web={len(web_sources)}",
            started_at=started_at,
        ),
    }


def _node_route_filter(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    local_sources, web_sources = dual_route_filter_service.filter_dual_route_sources(
        question=data.question,
        retrieval_plan=state["plan_decision"].plan_type,
        time_range=data.time_range,
        local_sources=state.get("local_sources", []),
        web_sources=state.get("web_sources", []),
    )
    return {
        "local_sources": local_sources,
        "web_sources": web_sources,
        "workflow_trace": _append_trace(
            state,
            node="route-filter",
            status="completed",
            detail=f"local={len(local_sources)}, web={len(web_sources)}",
            started_at=started_at,
        ),
    }


def _node_final_rerank(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    merged_sources = retrieval_fusion_service.fuse_sources(
        question=data.question,
        category=data.category,
        time_range=data.time_range,
        local_sources=state.get("local_sources", []),
        web_sources=state.get("web_sources", []),
        retrieval_plan=state["plan_decision"].plan_type,
    )
    confidence = retrieval_fusion_service.estimate_confidence(
        state.get("local_sources", []),
        state.get("web_sources", []),
        merged_sources,
    )
    strategy = _resolve_strategy(
        state["plan_decision"].plan_type,
        state.get("local_sources", []),
        state.get("web_sources", []),
    )
    return {
        "merged_sources": merged_sources,
        "confidence": confidence,
        "strategy": strategy,
        "workflow_trace": _append_trace(
            state,
            node="final-rerank",
            status="completed",
            detail=f"merged={len(merged_sources)}, confidence={confidence}",
            started_at=started_at,
        ),
    }


def _route_after_rerank(state: AgentGraphState) -> str:
    if state.get("merged_sources"):
        return "generator"
    return "no-evidence-response"


def _node_no_evidence_response(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    trace = _append_trace(
        state,
        node="no-evidence-response",
        status="fallback",
        detail="no evidence -> refusal",
        started_at=started_at,
    )
    followups = response_formatter_service.build_follow_up_suggestions(
        question=data.question,
        category=data.category,
        retrieval_plan=state["plan_decision"].plan_type,
        evidence_level="none",
        sources=[],
    )
    return {
        "workflow_trace": trace,
        "final_reply": _build_no_hit_reply(),
        "final_model": "retrieval-fallback",
        "final_verification_status": "refused",
        "final_verification_reason": "当前没有检索到足够证据，已触发无证据拒答。",
        "final_evidence_level": "none",
        "final_guardrail_applied": True,
        "follow_up_suggestions": followups,
    }


async def _node_generator(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    raw_reply = await ai_service.chat(
        data,
        state.get("merged_sources", []),
        query_analysis=state.get("query_analysis"),
    )
    return {
        "final_reply": raw_reply,
        "workflow_trace": _append_trace(
            state,
            node="generator",
            status="completed",
            detail=f"reply_chars={len(raw_reply)}",
            started_at=started_at,
        ),
    }


def _node_verifier(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    verification_result = answer_verifier_service.verify_answer(
        question=data.question,
        reply=state.get("final_reply", ""),
        sources=state.get("merged_sources", []),
        confidence=state.get("confidence", 0.0),
        retrieval_plan=state["plan_decision"].plan_type,
    )
    trace_status: Literal["completed", "guarded", "fallback"] = (
        "completed" if verification_result.status == "accepted" else "guarded"
    )
    return {
        "verification_result": verification_result,
        "workflow_trace": _append_trace(
            state,
            node="verifier",
            status=trace_status,
            detail=f"status={verification_result.status}, evidence={verification_result.evidence_level}",
            started_at=started_at,
        ),
    }


def _node_response_formatter(state: AgentGraphState, runtime: Runtime[GraphContext]) -> dict:
    started_at = time.perf_counter()
    data = state["data"]
    verification_result = state["verification_result"]
    formatted_reply = response_formatter_service.format_reply(verification_result.reply)
    followups = response_formatter_service.build_follow_up_suggestions(
        question=data.question,
        category=data.category,
        retrieval_plan=state["plan_decision"].plan_type,
        evidence_level=verification_result.evidence_level,
        sources=state.get("merged_sources", []),
    )
    return {
        "final_reply": formatted_reply,
        "final_model": ai_service.settings.llm_model,
        "final_verification_status": verification_result.status,
        "final_verification_reason": verification_result.reason,
        "final_evidence_level": verification_result.evidence_level,
        "final_guardrail_applied": verification_result.guardrail_applied,
        "follow_up_suggestions": followups,
        "workflow_trace": _append_trace(
            state,
            node="response-formatter",
            status="completed",
            detail=f"followups={len(followups)}",
            started_at=started_at,
        ),
    }


@lru_cache(maxsize=1)
def _get_compiled_graph():
    graph = StateGraph(AgentGraphState, context_schema=GraphContext)
    graph.add_node("query-analysis", _node_query_analysis)
    graph.add_node("retrieval-planner", _node_retrieval_planner)
    graph.add_node("retrieval", _node_retrieval)
    graph.add_node("route-filter", _node_route_filter)
    graph.add_node("final-rerank", _node_final_rerank)
    graph.add_node("no-evidence-response", _node_no_evidence_response)
    graph.add_node("generator", _node_generator)
    graph.add_node("verifier", _node_verifier)
    graph.add_node("response-formatter", _node_response_formatter)

    graph.add_edge(START, "query-analysis")
    graph.add_edge("query-analysis", "retrieval-planner")
    graph.add_edge("retrieval-planner", "retrieval")
    graph.add_edge("retrieval", "route-filter")
    graph.add_edge("route-filter", "final-rerank")
    graph.add_conditional_edges(
        "final-rerank",
        _route_after_rerank,
        {
            "generator": "generator",
            "no-evidence-response": "no-evidence-response",
        },
    )
    graph.add_edge("generator", "verifier")
    graph.add_edge("verifier", "response-formatter")
    graph.add_edge("response-formatter", END)
    graph.add_edge("no-evidence-response", END)
    return graph.compile()


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
        "workflowEngine": "langgraph",
        "workflowStyle": "langgraph-stategraph",
        "graphVisualizationReady": True,
        "workflowNodes": [
            "query-analysis",
            "retrieval-planner",
            "retrieval",
            "route-filter",
            "final-rerank",
            "generator",
            "verifier",
            "response-formatter",
            "no-evidence-response",
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


async def chat(db: AsyncSession, data: AiChatRequest) -> AiChatResponse:
    run_context = agent_observability_service.create_run_context(data)
    graph = _get_compiled_graph()
    initial_state: AgentGraphState = {
        "data": data,
        "trace_id": run_context["traceId"],
        "run_id": run_context["runId"],
        "local_sources": [],
        "web_sources": [],
        "merged_sources": [],
        "confidence": 0.0,
        "strategy": "",
        "follow_up_suggestions": [],
        "workflow_trace": [],
    }

    try:
        with agent_observability_service.langsmith_context(
            run_context=run_context,
            metadata={
                "category": data.category,
                "mode": data.mode,
                "time_range": data.time_range,
                "workflow_engine": "langgraph",
            },
        ):
            result = await graph.ainvoke(
                initial_state,
                config={
                    "run_name": "AgentNews Workflow",
                    "tags": ["agentnews", "langgraph", "stategraph"],
                },
                context={
                    "db": db,
                    "run_context": run_context,
                },
            )

        response = AiChatResponse(
            reply=result.get("final_reply", _build_no_hit_reply()),
            model=result.get("final_model", ai_service.settings.llm_model),
            promptVersion=ai_service.PROMPT_VERSION,
            traceId=run_context["traceId"],
            runId=run_context["runId"],
            workflowSummary=_build_workflow_summary(result.get("workflow_trace", [])),
            strategy=result.get("strategy", "hybrid_nohit"),
            retrievalPlan=result["plan_decision"].plan_type,
            plannerReason=result["plan_decision"].reason,
            queryIntent=result["query_analysis"].intent,
            freshnessNeed=result["query_analysis"].freshness_need,
            scopePreference=result["query_analysis"].scope_preference,
            analysisReason=result["query_analysis"].reason,
            confidence=result.get("confidence", 0.0),
            verificationStatus=result.get("final_verification_status", "accepted"),
            verificationReason=result.get("final_verification_reason", ""),
            evidenceLevel=result.get("final_evidence_level", "none"),
            guardrailApplied=result.get("final_guardrail_applied", False),
            followUpSuggestions=result.get("follow_up_suggestions", []),
            workflowTrace=result.get("workflow_trace", []),
            sources=result.get("merged_sources", []),
            retrievalEnabled=True,
            webSearchEnabled=tavily_service.is_enabled(),
        )
        agent_observability_service.record_success(run_context, response)
        return response
    except Exception as exc:
        workflow_trace = initial_state.get("workflow_trace", [])
        agent_observability_service.record_failure(
            run_context=run_context,
            workflow_trace=[item.model_dump(mode="json", by_alias=True) for item in workflow_trace],
            error_message=str(exc),
        )
        raise
