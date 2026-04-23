from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from crud import news as news_repo
from services import embedding_service, news_chunking_service, qdrant_index_service


settings = get_settings()


def get_runtime_status() -> dict:
    qdrant_status = qdrant_index_service.get_runtime_status()
    embedding_status = embedding_service.get_runtime_status()
    chunking_status = news_chunking_service.get_runtime_status()
    return {
        **chunking_status,
        **embedding_status,
        **qdrant_status,
        "indexSyncReady": bool(
            chunking_status["chunkingReady"]
            and embedding_status["embeddingConfigured"]
            and qdrant_status["qdrantConfigured"]
        ),
        "vectorIndexBatchSize": settings.vector_index_batch_size,
    }


async def preview_news_chunks(db: AsyncSession, news_id: int) -> dict:
    news_item = await news_repo.get_news_detail(db, news_id)
    if news_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在，无法预览切块。")

    chunks = news_chunking_service.build_news_chunks(news_item)
    return {
        "newsId": news_item.id,
        "title": news_item.title,
        "chunkCount": len(chunks),
        "chunks": [
            {
                "chunkId": item.chunk_id,
                "chunkIndex": item.chunk_index,
                "snippet": item.snippet,
                "text": item.chunk_text,
                "charCount": item.char_count,
            }
            for item in chunks
        ],
    }


def _ensure_sync_allowed() -> None:
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="向量索引同步接口仅在 DEBUG 环境开放。",
        )


async def sync_news_index(
    db: AsyncSession,
    news_ids: list[int] | None = None,
    limit: int = 20,
    dry_run: bool = False,
) -> dict:
    _ensure_sync_allowed()

    runtime_status = get_runtime_status()
    news_items = await news_repo.get_news_for_indexing(db, news_ids=news_ids, limit=limit)
    chunks = []
    for item in news_items:
        chunks.extend(news_chunking_service.build_news_chunks(item))

    response = {
        "dryRun": dry_run,
        "indexedNewsCount": len(news_items),
        "chunkCount": len(chunks),
        "collection": settings.qdrant_collection,
        "vectorSize": None,
        "status": "ready-for-sync" if runtime_status["indexSyncReady"] else "pipeline-not-ready",
    }

    if dry_run or not chunks:
        return response

    if not runtime_status["embeddingConfigured"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Embedding 服务尚未配置，无法执行向量索引同步。",
        )
    if not runtime_status["qdrantConfigured"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Qdrant 尚未配置，无法执行向量索引同步。",
        )

    batch_size = max(settings.vector_index_batch_size, 1)
    total_upserted = 0
    vector_size = 0

    for start in range(0, len(chunks), batch_size):
        batch_chunks = chunks[start : start + batch_size]
        vectors = await embedding_service.embed_texts([item.embedding_text for item in batch_chunks])
        if not vectors:
            continue

        vector_size = len(vectors[0])
        await qdrant_index_service.ensure_collection(vector_size)
        points = qdrant_index_service.build_points(batch_chunks, vectors)
        await qdrant_index_service.upsert_points(points)
        total_upserted += len(points)

    response["status"] = "synced"
    response["upsertedPoints"] = total_upserted
    response["vectorSize"] = vector_size or None
    return response
