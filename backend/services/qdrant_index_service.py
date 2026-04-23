import asyncio
from functools import lru_cache
from pathlib import Path
import uuid

from qdrant_client import QdrantClient, models

from config.settings import get_settings
from services.news_chunking_service import NewsChunkDocument


settings = get_settings()


def _resolve_local_path() -> Path:
    path = Path(settings.qdrant_local_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def _resolve_mode() -> str:
    return "server" if settings.qdrant_url else "local"


def is_configured() -> bool:
    return bool(settings.qdrant_collection and (settings.qdrant_url or settings.qdrant_local_path))


def get_runtime_status() -> dict:
    return {
        "qdrantConfigured": is_configured(),
        "qdrantCollection": settings.qdrant_collection,
        "qdrantUrl": settings.qdrant_url or "",
        "qdrantMode": _resolve_mode(),
        "qdrantLocalPath": str(_resolve_local_path()) if _resolve_mode() == "local" else "",
    }


@lru_cache(maxsize=1)
def _get_client() -> QdrantClient:
    if _resolve_mode() == "server":
        return QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
            timeout=settings.qdrant_timeout_seconds,
        )

    return QdrantClient(path=str(_resolve_local_path()))


def close_client() -> None:
    if _get_client.cache_info().currsize == 0:
        return
    client = _get_client()
    client.close()
    _get_client.cache_clear()


async def get_collection_info():
    if not is_configured():
        return None
    client = _get_client()
    exists = await asyncio.to_thread(client.collection_exists, settings.qdrant_collection)
    if not exists:
        return None
    return await asyncio.to_thread(client.get_collection, settings.qdrant_collection)


async def ensure_collection(vector_size: int):
    if not is_configured():
        raise RuntimeError("Qdrant is not configured")

    client = _get_client()
    exists = await asyncio.to_thread(client.collection_exists, settings.qdrant_collection)
    if exists:
        return await asyncio.to_thread(client.get_collection, settings.qdrant_collection)

    await asyncio.to_thread(
        client.create_collection,
        collection_name=settings.qdrant_collection,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
    )
    return await asyncio.to_thread(client.get_collection, settings.qdrant_collection)


def build_points(chunks: list[NewsChunkDocument], vectors: list[list[float]]) -> list[models.PointStruct]:
    points: list[models.PointStruct] = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        publish_time_iso = chunk.publish_time.isoformat() if chunk.publish_time else None
        publish_timestamp = int(chunk.publish_time.timestamp()) if chunk.publish_time else None
        points.append(
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id)),
                vector=vector,
                payload={
                    "news_id": chunk.news_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "title": chunk.title,
                    "snippet": chunk.snippet,
                    "chunk_text": chunk.chunk_text,
                    "category_id": chunk.category_id,
                    "publish_time": publish_time_iso,
                    "publish_timestamp": publish_timestamp,
                    "author": chunk.author,
                    "char_count": chunk.char_count,
                },
            )
        )
    return points


async def upsert_points(points: list[models.PointStruct]) -> dict:
    if not points:
        return {"status": "skipped", "count": 0}

    client = _get_client()
    result = await asyncio.to_thread(
        client.upsert,
        collection_name=settings.qdrant_collection,
        points=points,
        wait=True,
    )
    return {
        "status": getattr(result, "status", "completed"),
        "count": len(points),
    }


def build_query_filter(category_id: int | list[int] | None = None, published_after_timestamp: int | None = None):
    conditions: list[models.FieldCondition] = []

    if category_id is not None:
        if isinstance(category_id, list):
            match_condition = models.MatchAny(any=category_id)
        else:
            match_condition = models.MatchValue(value=category_id)
        conditions.append(
            models.FieldCondition(
                key="category_id",
                match=match_condition,
            )
        )

    if published_after_timestamp is not None:
        conditions.append(
            models.FieldCondition(
                key="publish_timestamp",
                range=models.Range(gte=published_after_timestamp),
            )
        )

    if not conditions:
        return None
    return models.Filter(must=conditions)


async def query_points(
    vector: list[float],
    limit: int,
    category_id: int | list[int] | None = None,
    published_after_timestamp: int | None = None,
):
    client = _get_client()
    query_filter = build_query_filter(
        category_id=category_id,
        published_after_timestamp=published_after_timestamp,
    )
    response = await asyncio.to_thread(
        client.query_points,
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=limit,
        with_payload=True,
        query_filter=query_filter,
    )
    return getattr(response, "points", []) or []
