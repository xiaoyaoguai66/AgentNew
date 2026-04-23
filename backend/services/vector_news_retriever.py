import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from crud import news as news_repo
from schemas.ai import AiSourceItem
from services import embedding_service, lexical_news_retriever, qdrant_index_service


logger = logging.getLogger(__name__)
settings = get_settings()


def is_configured() -> bool:
    return qdrant_index_service.is_configured()


def is_enabled() -> bool:
    return bool(settings.enable_vector_retrieval and is_configured() and embedding_service.is_configured())


def get_runtime_status() -> dict:
    qdrant_status = qdrant_index_service.get_runtime_status()
    return {
        "vectorRetrievalEnabled": bool(settings.enable_vector_retrieval),
        "vectorStoreConfigured": is_configured(),
        "vectorBackend": "qdrant-local" if qdrant_status.get("qdrantMode") == "local" else "qdrant-server",
        "vectorRetrievalActive": is_enabled(),
    }


def _resolve_published_after(time_range: str) -> datetime | None:
    now = datetime.now()
    if time_range == "24h":
        return now - timedelta(hours=24)
    if time_range == "7d":
        return now - timedelta(days=7)
    return None


async def _resolve_category_ids(db: AsyncSession, category_key: str) -> list[int] | None:
    if category_key == "general":
        return None

    categories = await news_repo.get_categories(db, 0, 200)
    aliases = lexical_news_retriever.CATEGORY_ALIASES.get(category_key, [])
    matched_ids = [
        category.id
        for category in categories
        if any(alias in (category.name or "").lower() for alias in aliases)
    ]
    return matched_ids or None


async def retrieve_news_sources(
    db: AsyncSession,
    question: str,
    category: str,
    time_range: str,
    limit: int = 4,
) -> list[AiSourceItem]:
    if not settings.enable_vector_retrieval:
        return []

    if not is_configured():
        logger.info("vector retrieval skipped because Qdrant is not configured")
        return []

    if not embedding_service.is_configured():
        logger.info("vector retrieval skipped because embedding service is not configured")
        return []

    collection_info = await qdrant_index_service.get_collection_info()
    if collection_info is None:
        logger.info("vector retrieval skipped because collection %s does not exist", settings.qdrant_collection)
        return []

    vectors = await embedding_service.embed_texts([question])
    if not vectors:
        return []

    category_ids = await _resolve_category_ids(db, category)
    published_after = _resolve_published_after(time_range)
    published_after_timestamp = int(published_after.timestamp()) if published_after else None

    points = await qdrant_index_service.query_points(
        vector=vectors[0],
        limit=max(limit * 3, 8),
        category_id=category_ids,
        published_after_timestamp=published_after_timestamp,
    )

    aggregated: dict[int | str, dict[str, Any]] = {}
    for point in points:
        payload = getattr(point, "payload", {}) or {}
        score = float(getattr(point, "score", 0.0) or 0.0)
        snippet = (payload.get("snippet") or payload.get("chunk_text") or "")[:220]
        publish_time = payload.get("publish_time")
        if isinstance(publish_time, str):
            normalized = publish_time.replace("Z", "+00:00")
            try:
                publish_time = datetime.fromisoformat(normalized)
            except ValueError:
                publish_time = None

        news_id = payload.get("news_id")
        aggregate_key = news_id if news_id is not None else payload.get("chunk_id") or payload.get("title") or id(point)
        current = aggregated.get(aggregate_key)

        candidate = AiSourceItem(
            sourceType="local",
            newsId=news_id,
            title=payload.get("title") or "未命名新闻",
            snippet=snippet,
            categoryId=payload.get("category_id"),
            publishTime=publish_time,
            retrievalTags=["vector"],
            score=round(score, 3),
        )
        if current is None:
            aggregated[aggregate_key] = {
                "source": candidate,
                "score": score,
                "chunk_hits": 1,
            }
            continue

        current["chunk_hits"] += 1
        if score > current["score"]:
            current["score"] = score
            current["source"] = candidate

    sources: list[AiSourceItem] = []
    for item in aggregated.values():
        chunk_hits = item["chunk_hits"]
        best_score = min(item["score"] + min(max(chunk_hits - 1, 0), 2) * 0.03, 0.99)
        sources.append(item["source"].model_copy(update={"score": round(best_score, 3)}))

    sources.sort(
        key=lambda item: (
            -item.score,
            item.publish_time.isoformat() if item.publish_time else "",
            -(item.news_id or 0),
        )
    )
    return sources[:limit]
