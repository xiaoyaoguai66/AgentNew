from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main
from schemas.ai import AiChatRequest, AiChatResponse
from services import langgraph_agent_service


def _assert_success(response, path: str) -> dict:
    assert response.status_code == 200, f"{path} returned {response.status_code}"
    payload = response.json()
    assert payload["code"] == 200, f"{path} business code is not 200"
    return payload


def run_integration_checks() -> None:
    original_chat = langgraph_agent_service.chat

    async def fake_chat(db, data: AiChatRequest):
        latest_question = data.question.strip()
        return AiChatResponse.model_validate(
            {
                "reply": f"集成测试回答：{latest_question}",
                "model": "fake-integration-model",
                "promptVersion": "integration",
                "traceId": "trace-integration",
                "runId": "run-integration",
                "workflowSummary": "query-analysis -> retrieval-planner -> retrieval -> verifier -> response-formatter",
                "strategy": "hybrid_local_web_reranked_answer",
                "retrievalPlan": "hybrid",
                "plannerReason": "integration-test",
                "queryIntent": "summary",
                "freshnessNeed": "medium",
                "scopePreference": "hybrid",
                "analysisReason": "integration-test",
                "confidence": 0.88,
                "verificationStatus": "accepted",
                "verificationReason": "integration-test",
                "evidenceLevel": "strong",
                "guardrailApplied": False,
                "followUpSuggestions": ["继续追问"],
                "workflowTrace": [
                    {
                        "stepIndex": 1,
                        "node": "query-analysis",
                        "status": "completed",
                        "detail": "integration",
                        "durationMs": 1,
                    }
                ],
                "sources": [
                    {
                        "sourceType": "local",
                        "newsId": 1,
                        "title": "Integration Source",
                        "snippet": "integration-snippet",
                        "retrievalTags": ["lexical", "vector"],
                        "score": 0.95,
                    }
                ],
                "retrievalEnabled": True,
                "webSearchEnabled": True,
            }
        )

    langgraph_agent_service.chat = fake_chat

    try:
        with TestClient(main.app) as client:
            session_a = _assert_success(client.post("/api/ai/session/start"), "/api/ai/session/start")
            session_a_id = session_a["data"]["sessionId"]

            chat_a = _assert_success(
                client.post(
                    "/api/ai/chat",
                    json={
                        "question": "帮我总结一下大模型行业动态",
                        "history": [],
                        "mode": "brief",
                        "timeRange": "7d",
                        "category": "technology",
                        "sessionId": session_a_id,
                    },
                ),
                "/api/ai/chat",
            )
            assert chat_a["data"]["sessionId"] == session_a_id
            assert chat_a["data"]["memoryEnabled"] is True
            assert chat_a["data"]["memoryMessageCount"] == 2

            session_a_detail = _assert_success(
                client.get(f"/api/ai/session/{session_a_id}"),
                "/api/ai/session/{id}",
            )
            assert session_a_detail["data"]["title"], "session title should not be empty"
            assert session_a_detail["data"]["messageCount"] == 2
            assert len(session_a_detail["data"]["recentMessages"]) == 2

            sessions_after_first_chat = _assert_success(
                client.get(f"/api/ai/sessions?active_session_id={session_a_id}&limit=10"),
                "/api/ai/sessions",
            )
            assert any(item["sessionId"] == session_a_id for item in sessions_after_first_chat["data"])
            active_item = next(item for item in sessions_after_first_chat["data"] if item["sessionId"] == session_a_id)
            assert active_item["active"] is True
            assert active_item["title"], "active session title should exist"

            session_b = _assert_success(client.post("/api/ai/session/start"), "/api/ai/session/start")
            session_b_id = session_b["data"]["sessionId"]
            assert session_b_id != session_a_id

            chat_b = _assert_success(
                client.post(
                    "/api/ai/chat",
                    json={
                        "question": "今天最新的卫星发射计划有什么进展",
                        "history": [],
                        "mode": "timeline",
                        "timeRange": "24h",
                        "category": "international",
                        "sessionId": session_b_id,
                    },
                ),
                "/api/ai/chat",
            )
            assert chat_b["data"]["sessionId"] == session_b_id

            sessions_after_second_chat = _assert_success(
                client.get(f"/api/ai/sessions?active_session_id={session_b_id}&limit=10"),
                "/api/ai/sessions",
            )
            listed_ids = [item["sessionId"] for item in sessions_after_second_chat["data"]]
            assert session_a_id in listed_ids and session_b_id in listed_ids

            delete_a = _assert_success(
                client.delete(f"/api/ai/session/{session_a_id}"),
                "/api/ai/session/{id}",
            )
            assert delete_a["data"]["deleted"] is True

            sessions_after_delete = _assert_success(
                client.get(f"/api/ai/sessions?active_session_id={session_b_id}&limit=10"),
                "/api/ai/sessions",
            )
            listed_ids_after_delete = [item["sessionId"] for item in sessions_after_delete["data"]]
            assert session_a_id not in listed_ids_after_delete
            assert session_b_id in listed_ids_after_delete
    finally:
        langgraph_agent_service.chat = original_chat


if __name__ == "__main__":
    run_integration_checks()
    print("NewsCopilot integration checks passed.")

