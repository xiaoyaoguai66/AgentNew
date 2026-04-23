import asyncio
import json
import logging
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


def _resolve_embedding_base_url() -> str:
    if settings.embedding_base_url:
        return settings.embedding_base_url
    if "dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" in settings.llm_base_url:
        return "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    return ""


def _resolve_embedding_api_key() -> str:
    return settings.embedding_api_key or settings.llm_api_key


def _resolve_embedding_model() -> str:
    return settings.embedding_model or "text-embedding-v4"


def _resolve_embedding_config_mode() -> str:
    has_explicit_override = bool(settings.embedding_base_url or settings.embedding_api_key or settings.embedding_model)
    if has_explicit_override:
        return "explicit" if is_configured() else "partial"
    return "llm-fallback" if is_configured() else "missing"


def is_configured() -> bool:
    return bool(_resolve_embedding_base_url() and _resolve_embedding_api_key() and _resolve_embedding_model())


def get_runtime_status() -> dict:
    return {
        "embeddingConfigured": is_configured(),
        "embeddingModel": _resolve_embedding_model(),
        "embeddingProviderReady": bool(_resolve_embedding_base_url()),
        "embeddingConfigMode": _resolve_embedding_config_mode(),
    }


def _extract_embeddings(payload: dict) -> list[list[float]]:
    data = payload.get("data")
    if isinstance(data, list):
        vectors: list[list[float]] = []
        for item in data:
            embedding = item.get("embedding") if isinstance(item, dict) else None
            if isinstance(embedding, list):
                vectors.append([float(value) for value in embedding])
        return vectors

    if isinstance(payload.get("embeddings"), list):
        return [[float(value) for value in vector] for vector in payload["embeddings"]]

    return []


def _request_embeddings(texts: list[str]) -> list[list[float]]:
    if not is_configured():
        raise RuntimeError("Embedding service is not configured")

    body = json.dumps(
        {
            "model": _resolve_embedding_model(),
            "input": texts,
        }
    ).encode("utf-8")

    request = Request(
        _resolve_embedding_base_url(),
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_resolve_embedding_api_key()}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.llm_request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Embedding request failed: {detail or exc.reason}") from exc
    except (URLError, TimeoutError, SocketTimeout, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Embedding service unavailable: {exc}") from exc

    vectors = _extract_embeddings(payload)
    if len(vectors) != len(texts):
        raise RuntimeError("Embedding response size does not match input size")
    return vectors


async def embed_texts(texts: list[str]) -> list[list[float]]:
    sanitized = [" ".join((text or "").split())[:4000] for text in texts if (text or "").strip()]
    if not sanitized:
        return []
    return await asyncio.to_thread(_request_embeddings, sanitized)
