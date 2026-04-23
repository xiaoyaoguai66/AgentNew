import json
from pathlib import Path

from config.settings import PROJECT_ROOT
from schemas.ai import AiEvalCase, AiEvalCaseResult
from services import (
    agent_eval_artifact_service,
    query_analysis_service,
    retrieval_planner_service,
    tavily_service,
)


EVAL_DATASET_PATH = PROJECT_ROOT / "backend" / "data" / "evals" / "news_agent_eval_dataset.json"


def load_eval_dataset() -> list[AiEvalCase]:
    if not EVAL_DATASET_PATH.exists():
        return []

    payload = json.loads(EVAL_DATASET_PATH.read_text(encoding="utf-8"))
    raw_cases = payload.get("cases", [])
    return [AiEvalCase.model_validate(item) for item in raw_cases]


def _select_cases(cases: list[AiEvalCase], *, limit: int, case_ids: list[str]) -> list[AiEvalCase]:
    if case_ids:
        wanted = set(case_ids)
        cases = [item for item in cases if item.case_id in wanted]
    return cases[:limit]


def _accuracy(hit_count: int, total_count: int) -> float:
    if total_count <= 0:
        return 0.0
    return round(hit_count / total_count, 4)


def run_eval(*, limit: int = 20, case_ids: list[str] | None = None) -> dict:
    case_ids = case_ids or []
    cases = _select_cases(load_eval_dataset(), limit=limit, case_ids=case_ids)
    web_enabled = tavily_service.is_enabled()
    run_context = agent_eval_artifact_service.create_eval_run_context()

    planner_hits = 0
    intent_hits = 0
    freshness_hits = 0
    scope_hits = 0
    passed = 0
    results: list[AiEvalCaseResult] = []

    for case in cases:
        analysis = query_analysis_service.analyze_query(
            question=case.question,
            category=case.category,
            time_range=case.time_range,
            mode=case.mode,
            web_enabled=web_enabled,
        )
        plan_decision = retrieval_planner_service.decide_retrieval_plan(
            question=case.question,
            category=case.category,
            time_range=case.time_range,
            web_enabled=web_enabled,
            analysis=analysis,
        )

        mismatches: list[str] = []
        plan_ok = plan_decision.plan_type == case.expected_plan
        intent_ok = analysis.intent == case.expected_intent
        freshness_ok = analysis.freshness_need == case.expected_freshness
        scope_ok = analysis.scope_preference == case.expected_scope

        if plan_ok:
            planner_hits += 1
        else:
            mismatches.append("plan")
        if intent_ok:
            intent_hits += 1
        else:
            mismatches.append("intent")
        if freshness_ok:
            freshness_hits += 1
        else:
            mismatches.append("freshness")
        if scope_ok:
            scope_hits += 1
        else:
            mismatches.append("scope")

        case_passed = not mismatches
        if case_passed:
            passed += 1

        results.append(
            AiEvalCaseResult(
                caseId=case.case_id,
                title=case.title,
                passed=case_passed,
                actualPlan=plan_decision.plan_type,
                expectedPlan=case.expected_plan,
                actualIntent=analysis.intent,
                expectedIntent=case.expected_intent,
                actualFreshness=analysis.freshness_need,
                expectedFreshness=case.expected_freshness,
                actualScope=analysis.scope_preference,
                expectedScope=case.expected_scope,
                plannerReason=plan_decision.reason,
                analysisReason=analysis.reason,
                mismatches=mismatches,
            )
        )

    total = len(cases)
    payload = {
        "runId": run_context["runId"],
        "totalCount": total,
        "passedCount": passed,
        "webEnabled": web_enabled,
        "plannerAccuracy": _accuracy(planner_hits, total),
        "intentAccuracy": _accuracy(intent_hits, total),
        "freshnessAccuracy": _accuracy(freshness_hits, total),
        "scopeAccuracy": _accuracy(scope_hits, total),
        "results": results,
    }
    agent_eval_artifact_service.record_eval_run(
        {
            "runId": run_context["runId"],
            "recordedAt": run_context["recordedAt"],
            "totalCount": payload["totalCount"],
            "passedCount": payload["passedCount"],
            "plannerAccuracy": payload["plannerAccuracy"],
            "intentAccuracy": payload["intentAccuracy"],
            "freshnessAccuracy": payload["freshnessAccuracy"],
            "scopeAccuracy": payload["scopeAccuracy"],
        }
    )
    agent_eval_artifact_service.record_failure_cases(
        run_context=run_context,
        results=[item.model_dump(mode="json", by_alias=True) for item in results],
    )
    return payload
