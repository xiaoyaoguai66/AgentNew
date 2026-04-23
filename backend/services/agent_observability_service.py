import asyncio
import json
import os
import threading
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config.settings import PROJECT_ROOT, get_settings
from schemas.ai import AiChatRequest, AiChatResponse


settings = get_settings()
_write_lock = threading.Lock()

try:  # pragma: no cover - optional dependency
    from langsmith import Client, traceable
    from langsmith.run_helpers import tracing_context

    LANGSMITH_SDK_INSTALLED = True
except ImportError:  # pragma: no cover - optional dependency
    Client = None
    tracing_context = None
    LANGSMITH_SDK_INSTALLED = False

    def traceable(*args, **kwargs):
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*wrapper_args, **wrapper_kwargs):
                    wrapper_kwargs.pop("langsmith_extra", None)
                    return await func(*wrapper_args, **wrapper_kwargs)

                return async_wrapper

            def sync_wrapper(*wrapper_args, **wrapper_kwargs):
                wrapper_kwargs.pop("langsmith_extra", None)
                return func(*wrapper_args, **wrapper_kwargs)

            return sync_wrapper

        return decorator


def _configure_langsmith_environment() -> None:
    os.environ["LANGSMITH_TRACING_V2"] = "true" if settings.langsmith_tracing else "false"

    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    if settings.langsmith_project:
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    if settings.langsmith_endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint


_configure_langsmith_environment()


def _build_langsmith_client():
    if not LANGSMITH_SDK_INSTALLED or not settings.langsmith_api_key:
        return None

    return Client(
        api_key=settings.langsmith_api_key,
        api_url=settings.langsmith_endpoint,
    )


LANGSMITH_CLIENT = _build_langsmith_client()


def is_langsmith_configured() -> bool:
    return bool(
        LANGSMITH_SDK_INSTALLED
        and settings.langsmith_tracing
        and settings.langsmith_api_key
        and LANGSMITH_CLIENT is not None
    )


def _resolve_log_path() -> Path:
    raw_path = Path(settings.agent_run_log_path)
    if raw_path.is_absolute():
        return raw_path
    return PROJECT_ROOT / raw_path


def _ensure_log_dir() -> Path:
    log_path = _resolve_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return log_path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_run_context(data: AiChatRequest) -> dict:
    return {
        "traceId": uuid4().hex,
        "runId": uuid4().hex,
        "startedAt": _utc_now_iso(),
        "question": data.question,
        "mode": data.mode,
        "category": data.category,
        "timeRange": data.time_range,
        "sessionId": data.session_id or "",
    }


def langsmith_traceable(*, name: str, run_type: str, tags: list[str] | None = None):
    return traceable(
        name=name,
        run_type=run_type,
        tags=tags or ["agentnews"],
        client=LANGSMITH_CLIENT,
        project_name=settings.langsmith_project,
        enabled=is_langsmith_configured(),
    )


def build_langsmith_extra(
    *,
    run_context: dict,
    node: str,
    metadata: dict | None = None,
    tags: list[str] | None = None,
) -> dict:
    return {
        "metadata": {
            "trace_id": run_context.get("traceId", ""),
            "run_id": run_context.get("runId", ""),
            "node": node,
            **(metadata or {}),
        },
        "tags": ["agentnews", node, *(tags or [])],
    }


def langsmith_context(*, run_context: dict, metadata: dict | None = None):
    if not is_langsmith_configured() or tracing_context is None:
        return nullcontext()

    return tracing_context(
        project_name=settings.langsmith_project,
        client=LANGSMITH_CLIENT,
        enabled=True,
        tags=["agentnews", "workflow"],
        metadata={
            "trace_id": run_context.get("traceId", ""),
            "run_id": run_context.get("runId", ""),
            **(metadata or {}),
        },
    )


def _append_jsonl(record: dict) -> None:
    log_path = _ensure_log_dir()
    payload = json.dumps(record, ensure_ascii=False)
    with _write_lock:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")


def record_success(
    run_context: dict,
    response: AiChatResponse,
) -> None:
    _append_jsonl(
        {
            **run_context,
            "finishedAt": _utc_now_iso(),
            "status": "completed",
            "response": response.model_dump(mode="json", by_alias=True),
        }
    )


def record_failure(
    run_context: dict,
    workflow_trace: list[dict] | None,
    error_message: str,
) -> None:
    _append_jsonl(
        {
            **run_context,
            "finishedAt": _utc_now_iso(),
            "status": "failed",
            "workflowTrace": workflow_trace or [],
            "error": error_message,
        }
    )


def read_recent_runs(limit: int = 10) -> list[dict]:
    log_path = _resolve_log_path()
    if not log_path.exists():
        return []

    records: list[dict] = []
    for raw_line in log_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    records.reverse()
    return records[: max(limit, 1)]


def get_runtime_status() -> dict:
    log_path = _resolve_log_path()
    return {
        "observabilityEnabled": True,
        "observabilityMode": "local-trace-log",
        "runLoggingEnabled": True,
        "runLogPath": str(log_path),
        "langsmithReady": LANGSMITH_SDK_INSTALLED,
        "langsmithSdkInstalled": LANGSMITH_SDK_INSTALLED,
        "langsmithTracing": settings.langsmith_tracing,
        "langsmithConfigured": is_langsmith_configured(),
        "langsmithProject": settings.langsmith_project,
        "langsmithEndpoint": settings.langsmith_endpoint,
    }
