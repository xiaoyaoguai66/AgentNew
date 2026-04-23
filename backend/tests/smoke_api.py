from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main
from services import news_agent_service


def _assert_success(response, path: str) -> dict:
    assert response.status_code == 200, f"{path} returned {response.status_code}"
    payload = response.json()
    assert payload["code"] == 200, f"{path} business code is not 200"
    return payload


def _assert_plain_success(response, path: str) -> dict:
    assert response.status_code == 200, f"{path} returned {response.status_code}"
    return response.json()


def run_smoke_checks() -> None:
    original_chat = news_agent_service.chat

    async def fake_chat(db, data):
        return SimpleNamespace(
            reply="smoke-check-ok",
            model="fake-model",
            prompt_version="smoke",
            trace_id="trace-smoke",
            run_id="run-smoke",
            workflow_summary="smoke",
            strategy="smoke",
            retrieval_plan="hybrid",
            planner_reason="smoke",
            query_intent="summary",
            freshness_need="medium",
            scope_preference="hybrid",
            analysis_reason="smoke",
            confidence=0.9,
            verification_status="accepted",
            verification_reason="smoke",
            evidence_level="strong",
            guardrail_applied=False,
            follow_up_suggestions=["继续追问"],
            workflow_trace=[{"node": "query-analysis", "status": "done"}],
            sources=[{"title": "Smoke Source"}],
            retrieval_enabled=True,
            web_search_enabled=True,
            session_id="session-smoke",
            memory_enabled=True,
            memory_summary="smoke-memory",
            memory_message_count=2,
            memory_updated_at="2026-04-23T00:00:00Z",
        )

    news_agent_service.chat = fake_chat

    try:
        with TestClient(main.app) as client:
            root_payload = _assert_plain_success(client.get("/"), "/")
            assert root_payload["service"] == "NewsCopilot API"

            health_payload = _assert_plain_success(client.get("/health"), "/health")
            assert health_payload["status"] == "healthy"

            ai_status = _assert_success(client.get("/api/ai/status"), "/api/ai/status")
            assert "promptVersion" in ai_status["data"]

            session_start = _assert_success(
                client.post("/api/ai/session/start"),
                "/api/ai/session/start",
            )
            assert session_start["data"]["sessionId"]

            session_id = session_start["data"]["sessionId"]
            session_get = _assert_success(
                client.get(f"/api/ai/session/{session_id}"),
                "/api/ai/session/{id}",
            )
            assert session_get["data"]["sessionId"]

            sessions = _assert_success(
                client.get(f"/api/ai/sessions?active_session_id={session_id}"),
                "/api/ai/sessions",
            )
            assert isinstance(sessions["data"], list)

            workflow_graph = _assert_success(
                client.get("/api/ai/workflow/graph"),
                "/api/ai/workflow/graph",
            )
            assert workflow_graph["data"]["nodes"], "workflow graph nodes should not be empty"

            eval_dataset = _assert_success(
                client.get("/api/ai/eval/dataset"),
                "/api/ai/eval/dataset",
            )
            assert isinstance(eval_dataset["data"], list)

            eval_run = _assert_success(
                client.post("/api/ai/eval/run", json={"limit": 1}),
                "/api/ai/eval/run",
            )
            assert eval_run["data"]["totalCount"] >= 1

            response_eval_dataset = _assert_success(
                client.get("/api/ai/eval/response/dataset"),
                "/api/ai/eval/response/dataset",
            )
            assert isinstance(response_eval_dataset["data"], list)

            response_eval_run = _assert_success(
                client.post("/api/ai/eval/response/run", json={"limit": 1}),
                "/api/ai/eval/response/run",
            )
            assert response_eval_run["data"]["totalCount"] >= 1

            session_clear = _assert_success(
                client.delete(f"/api/ai/session/{session_id}"),
                "/api/ai/session/{id}",
            )
            assert session_clear["data"]["deleted"] is True
    finally:
        news_agent_service.chat = original_chat


if __name__ == "__main__":
    run_smoke_checks()
    print("NewsCopilot smoke checks passed.")

