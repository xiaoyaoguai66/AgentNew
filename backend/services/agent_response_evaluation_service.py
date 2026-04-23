import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import PROJECT_ROOT
from schemas.ai import AiChatRequest, AiResponseEvalCase, AiResponseEvalCaseResult
from services import agent_eval_artifact_service, news_agent_service


RESPONSE_EVAL_DATASET_PATH = PROJECT_ROOT / "backend" / "data" / "evals" / "news_agent_response_eval_dataset.json"


def load_response_eval_dataset() -> list[AiResponseEvalCase]:
    if not RESPONSE_EVAL_DATASET_PATH.exists():
        return []

    payload = json.loads(RESPONSE_EVAL_DATASET_PATH.read_text(encoding="utf-8"))
    return [AiResponseEvalCase.model_validate(item) for item in payload.get("cases", [])]


def _select_cases(cases: list[AiResponseEvalCase], *, limit: int, case_ids: list[str]) -> list[AiResponseEvalCase]:
    if case_ids:
        wanted = set(case_ids)
        cases = [item for item in cases if item.case_id in wanted]
    return cases[:limit]


def _accuracy(hit_count: int, total_count: int) -> float:
    if total_count <= 0:
        return 0.0
    return round(hit_count / total_count, 4)


def _build_request(case: AiResponseEvalCase) -> AiChatRequest:
    return AiChatRequest(
        question=case.question,
        mode=case.mode,
        timeRange=case.time_range,
        category=case.category,
    )


def _evaluate_case(case: AiResponseEvalCase, response) -> tuple[AiResponseEvalCaseResult, bool, bool]:
    mismatches: list[str] = []

    status_ok = response.verification_status in case.allowed_statuses
    if not status_ok:
        mismatches.append("status")

    source_count = len(response.sources)
    if source_count < case.min_sources or source_count > case.max_sources:
        mismatches.append("sources")

    follow_up_count = len(response.follow_up_suggestions)
    if case.require_follow_ups and follow_up_count <= 0:
        mismatches.append("followups")

    workflow_trace_count = len(response.workflow_trace)
    if case.require_workflow_trace and workflow_trace_count <= 0:
        mismatches.append("workflowTrace")

    if case.require_non_empty_reply and not (response.reply or "").strip():
        mismatches.append("reply")

    result = AiResponseEvalCaseResult(
        caseId=case.case_id,
        title=case.title,
        passed=not mismatches,
        actualStatus=response.verification_status,
        allowedStatuses=case.allowed_statuses,
        sourceCount=source_count,
        followUpCount=follow_up_count,
        workflowTraceCount=workflow_trace_count,
        mismatches=mismatches,
        note=case.note,
    )
    return result, status_ok, not any(item in mismatches for item in ("sources", "followups", "workflowTrace", "reply"))


async def run_response_eval(
    db: AsyncSession,
    *,
    limit: int = 10,
    case_ids: list[str] | None = None,
) -> dict:
    case_ids = case_ids or []
    cases = _select_cases(load_response_eval_dataset(), limit=limit, case_ids=case_ids)
    run_context = agent_eval_artifact_service.create_eval_run_context()

    status_hits = 0
    contract_hits = 0
    passed = 0
    results: list[AiResponseEvalCaseResult] = []

    for case in cases:
        response = await news_agent_service.chat(db, _build_request(case))
        result, status_ok, contract_ok = _evaluate_case(case, response)
        if status_ok:
            status_hits += 1
        if contract_ok:
            contract_hits += 1
        if result.passed:
            passed += 1
        results.append(result)

    total = len(cases)
    payload = {
        "runId": run_context["runId"],
        "totalCount": total,
        "passedCount": passed,
        "statusAccuracy": _accuracy(status_hits, total),
        "contractAccuracy": _accuracy(contract_hits, total),
        "results": results,
    }
    agent_eval_artifact_service.record_response_eval_run(
        {
            "runId": run_context["runId"],
            "recordedAt": run_context["recordedAt"],
            "totalCount": payload["totalCount"],
            "passedCount": payload["passedCount"],
            "statusAccuracy": payload["statusAccuracy"],
            "contractAccuracy": payload["contractAccuracy"],
        }
    )
    agent_eval_artifact_service.record_response_failure_cases(
        run_context=run_context,
        results=[item.model_dump(mode="json", by_alias=True) for item in results],
    )
    return payload
