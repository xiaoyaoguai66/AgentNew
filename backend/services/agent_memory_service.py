from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from cache import client as cache_client
from cache.client import MISSING
from cache.keys import ai_session_index_key, ai_session_state_key
from config.settings import get_settings
from schemas.ai import AiChatHistoryMessage, AiChatRequest, AiChatResponse


settings = get_settings()
RECENT_LIMIT = max(settings.ai_session_recent_message_limit, 2)
SUMMARY_MAX_CHARS = max(settings.ai_session_summary_max_chars, 200)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_text(content: str, max_chars: int = 180) -> str:
    normalized = " ".join((content or "").split())
    return normalized[:max_chars].strip()


def _generate_session_id() -> str:
    return uuid4().hex


def _empty_state(session_id: str) -> dict:
    return {
        "sessionId": session_id,
        "title": "新对话",
        "preview": "",
        "summary": "",
        "messageCount": 0,
        "updatedAt": _utc_now_iso(),
        "recentMessages": [],
    }


def _normalize_title(content: str) -> str:
    title = _normalize_text(content, 28)
    return title or "新对话"


def _normalize_preview(content: str) -> str:
    return _normalize_text(content, 64)


async def _load_session_index() -> list[dict]:
    cached = await cache_client.get_json(ai_session_index_key())
    if cached is None or cached is MISSING or not isinstance(cached, list):
        return []
    return cached


async def _save_session_index(items: list[dict]) -> None:
    normalized = sorted(
        items,
        key=lambda item: item.get("updatedAt", ""),
        reverse=True,
    )[:50]
    await cache_client.set_json(
        ai_session_index_key(),
        normalized,
        expire=settings.ai_session_memory_ttl_seconds,
    )


async def _upsert_session_index_item(item: dict) -> None:
    items = await _load_session_index()
    filtered = [
        existing
        for existing in items
        if existing.get("sessionId") != item.get("sessionId")
    ]
    filtered.append(item)
    await _save_session_index(filtered)


async def _remove_session_index_item(session_id: str) -> None:
    items = await _load_session_index()
    filtered = [
        existing
        for existing in items
        if existing.get("sessionId") != session_id
    ]
    await _save_session_index(filtered)


def _build_rollup_piece(messages: list[dict]) -> str:
    user_points = [
        _normalize_text(item.get("content", ""), 72)
        for item in messages
        if item.get("role") == "user"
    ][-3:]
    assistant_points = [
        _normalize_text(item.get("content", ""), 96)
        for item in messages
        if item.get("role") == "assistant"
    ][-2:]

    lines: list[str] = []
    if user_points:
        lines.append("已讨论问题：" + "；".join(point for point in user_points if point))
    if assistant_points:
        lines.append("已有回答结论：" + "；".join(point for point in assistant_points if point))
    return " | ".join(lines)


def _merge_summary(existing_summary: str, overflow_messages: list[dict]) -> str:
    parts = [part for part in [existing_summary.strip(), _build_rollup_piece(overflow_messages)] if part]
    merged = " | ".join(parts)
    if len(merged) <= SUMMARY_MAX_CHARS:
        return merged
    return merged[-SUMMARY_MAX_CHARS:]


def _normalize_recent_messages(messages: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for item in messages[-RECENT_LIMIT:]:
        role = item.get("role")
        content = _normalize_text(item.get("content", ""), 1200)
        if role not in {"user", "assistant"} or not content:
            continue
        normalized.append({"role": role, "content": content})
    return normalized


def _serialize_history(history: list[AiChatHistoryMessage]) -> list[dict]:
    return [
        {
            "role": item.role,
            "content": _normalize_text(item.content, 1200),
        }
        for item in history
        if item.content
    ]


async def _load_state(session_id: str) -> dict | None:
    cached = await cache_client.get_json(ai_session_state_key(session_id))
    if cached is None or cached is MISSING:
        return None
    return cached


async def _save_state(state: dict) -> None:
    await cache_client.set_json(
        ai_session_state_key(state["sessionId"]),
        state,
        expire=settings.ai_session_memory_ttl_seconds,
    )


def get_runtime_status() -> dict:
    return {
        "memoryEnabled": True,
        "memoryBackend": "redis-session-memory",
        "memorySummaryStrategy": "heuristic-rollup",
        "memoryTtlSeconds": settings.ai_session_memory_ttl_seconds,
        "memoryRecentMessageLimit": RECENT_LIMIT,
    }


async def create_session(session_id: str | None = None) -> dict:
    resolved_session_id = session_id or _generate_session_id()
    state = await _load_state(resolved_session_id)
    if state is None:
        state = _empty_state(resolved_session_id)
        await _save_state(state)
        await _upsert_session_index_item(
            {
                "sessionId": resolved_session_id,
                "title": state["title"],
                "preview": state["preview"],
                "messageCount": state["messageCount"],
                "updatedAt": state["updatedAt"],
            }
        )
    return state


async def get_session(session_id: str) -> dict | None:
    if not session_id:
        return None
    return await _load_state(session_id)


async def clear_session(session_id: str) -> bool:
    if not session_id:
        return False
    deleted = await cache_client.delete(ai_session_state_key(session_id))
    await _remove_session_index_item(session_id)
    return deleted


async def list_sessions(limit: int = 20) -> list[dict]:
    items = await _load_session_index()
    return items[: max(limit, 1)]


async def prepare_request(data: AiChatRequest) -> tuple[AiChatRequest, dict]:
    state = await create_session(data.session_id)
    persisted_history = [
        AiChatHistoryMessage.model_validate(item)
        for item in state.get("recentMessages", [])
    ]
    history = persisted_history or data.history
    prepared = data.model_copy(
        update={
            "session_id": state["sessionId"],
            "history": history,
            "memory_summary": state.get("summary", ""),
        }
    )
    return prepared, state


async def persist_response(
    prepared_data: AiChatRequest,
    response: AiChatResponse,
) -> AiChatResponse:
    normalized_response = (
        response
        if isinstance(response, AiChatResponse)
        else AiChatResponse.model_validate(
            response.__dict__ if hasattr(response, "__dict__") else response
        )
    )
    state = await create_session(prepared_data.session_id)
    recent_messages = list(state.get("recentMessages", []))
    recent_messages.extend(
        [
            {"role": "user", "content": _normalize_text(prepared_data.question, 1200)},
            {"role": "assistant", "content": _normalize_text(normalized_response.reply, 1200)},
        ]
    )
    overflow_messages = recent_messages[:-RECENT_LIMIT]
    summary = state.get("summary", "")
    if overflow_messages:
        summary = _merge_summary(summary, overflow_messages)

    normalized_recent = _normalize_recent_messages(recent_messages)
    updated_state = {
        "sessionId": state["sessionId"],
        "title": state.get("title") or "新对话",
        "preview": _normalize_preview(normalized_response.reply),
        "summary": summary,
        "messageCount": int(state.get("messageCount", len(state.get("recentMessages", [])))) + 2,
        "updatedAt": _utc_now_iso(),
        "recentMessages": normalized_recent,
    }
    if updated_state["title"] == "新对话":
        updated_state["title"] = _normalize_title(prepared_data.question)
    await _save_state(updated_state)
    await _upsert_session_index_item(
        {
            "sessionId": updated_state["sessionId"],
            "title": updated_state["title"],
            "preview": updated_state["preview"] or summary or _normalize_preview(prepared_data.question),
            "messageCount": updated_state["messageCount"],
            "updatedAt": updated_state["updatedAt"],
        }
    )

    return normalized_response.model_copy(
        update={
            "session_id": updated_state["sessionId"],
            "memory_enabled": True,
            "memory_summary": updated_state["summary"],
            "memory_message_count": updated_state["messageCount"],
            "memory_updated_at": updated_state["updatedAt"],
        }
    )


def format_session_response(state: dict) -> dict:
    return {
        "sessionId": state["sessionId"],
        "title": state.get("title", "新对话"),
        "preview": state.get("preview", ""),
        "summary": state.get("summary", ""),
        "messageCount": int(state.get("messageCount", 0)),
        "updatedAt": state.get("updatedAt", ""),
        "recentMessages": _serialize_history(
            [AiChatHistoryMessage.model_validate(item) for item in state.get("recentMessages", [])]
        ),
        "memoryEnabled": True,
        "backend": "redis-session-memory",
    }
