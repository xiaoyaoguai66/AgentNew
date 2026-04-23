import logging

from cache.news_cache import (
    pop_news_view_deltas,
    restore_news_view_deltas,
    sync_cached_news_detail_views,
)
from config.db_conf import AsyncSessionLocal
from crud import news as news_repo


logger = logging.getLogger(__name__)


async def flush_news_view_deltas_once() -> int:
    view_deltas = await pop_news_view_deltas()
    if not view_deltas:
        return 0

    async with AsyncSessionLocal() as session:
        try:
            updated_count = await news_repo.batch_increase_news_views(session, view_deltas)
            await session.commit()
        except Exception:
            await session.rollback()
            await restore_news_view_deltas(view_deltas)
            logger.exception(
                "failed to flush redis news view deltas",
                extra={"view_delta_count": len(view_deltas)},
            )
            return 0

    await sync_cached_news_detail_views(view_deltas)
    logger.info(
        "flushed redis news view deltas",
        extra={"news_count": len(view_deltas), "updated_count": updated_count},
    )
    return updated_count
