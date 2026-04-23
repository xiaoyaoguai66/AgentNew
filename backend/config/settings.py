import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _parse_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


_load_env_file(PROJECT_ROOT / ".env")
_load_env_file(PROJECT_ROOT / "backend" / ".env")


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = _parse_bool(os.getenv("DEBUG"), default=False)
    cors_origins: list[str] = None
    mysql_url: str = os.getenv("MYSQL_URL", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    view_flush_interval_seconds: int = _parse_int(
        os.getenv("VIEW_FLUSH_INTERVAL_SECONDS"),
        60,
    )
    llm_base_url: str = os.getenv(
        "LLM_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    )
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "qwen3-max-preview")
    llm_request_timeout_seconds: int = _parse_int(os.getenv("LLM_REQUEST_TIMEOUT_SECONDS"), 60)
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    tavily_base_url: str = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com/search")
    tavily_search_depth: str = os.getenv("TAVILY_SEARCH_DEPTH", "basic")
    tavily_max_results: int = _parse_int(os.getenv("TAVILY_MAX_RESULTS"), 3)
    tavily_timeout_seconds: int = _parse_int(os.getenv("TAVILY_TIMEOUT_SECONDS"), 8)
    local_retrieval_engine: str = os.getenv("LOCAL_RETRIEVAL_ENGINE", "lexical")
    enable_vector_retrieval: bool = _parse_bool(os.getenv("ENABLE_VECTOR_RETRIEVAL"), default=False)
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "newscopilot_news_chunks")
    qdrant_timeout_seconds: int = _parse_int(os.getenv("QDRANT_TIMEOUT_SECONDS"), 5)
    qdrant_local_path: str = os.getenv("QDRANT_LOCAL_PATH", str(PROJECT_ROOT / "backend" / "data" / "qdrant"))
    embedding_base_url: str = os.getenv("EMBEDDING_BASE_URL", "")
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "")
    langsmith_tracing: bool = _parse_bool(os.getenv("LANGSMITH_TRACING"), default=False)
    langsmith_api_key: str = os.getenv("LANGSMITH_API_KEY", "")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "newscopilot-dev")
    langsmith_endpoint: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    agent_run_log_path: str = os.getenv(
        "AGENT_RUN_LOG_PATH",
        str(PROJECT_ROOT / "backend" / "data" / "agent_runs" / "agent_runs.jsonl"),
    )
    agent_workflow_engine: str = os.getenv("AGENT_WORKFLOW_ENGINE", "langgraph")
    ai_low_confidence_threshold: float = _parse_float(os.getenv("AI_LOW_CONFIDENCE_THRESHOLD"), 0.58)
    ai_refusal_confidence_threshold: float = _parse_float(os.getenv("AI_REFUSAL_CONFIDENCE_THRESHOLD"), 0.34)
    ai_session_memory_ttl_seconds: int = _parse_int(os.getenv("AI_SESSION_MEMORY_TTL_SECONDS"), 86400)
    ai_session_recent_message_limit: int = _parse_int(os.getenv("AI_SESSION_RECENT_MESSAGE_LIMIT"), 6)
    ai_session_summary_max_chars: int = _parse_int(os.getenv("AI_SESSION_SUMMARY_MAX_CHARS"), 900)
    news_chunk_size_chars: int = _parse_int(os.getenv("NEWS_CHUNK_SIZE_CHARS"), 480)
    news_chunk_overlap_chars: int = _parse_int(os.getenv("NEWS_CHUNK_OVERLAP_CHARS"), 80)
    vector_index_batch_size: int = _parse_int(os.getenv("VECTOR_INDEX_BATCH_SIZE"), 20)

    def __post_init__(self) -> None:
        if not self.mysql_url:
            raise RuntimeError("MYSQL_URL is required. Please set it in .env or the environment.")
        object.__setattr__(
            self,
            "cors_origins",
            _parse_csv(
                os.getenv("CORS_ORIGINS"),
                ["http://127.0.0.1:5173", "http://localhost:5173"],
            ),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

