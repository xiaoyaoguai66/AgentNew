import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cache.client import MISSING
from cache.news_cache import (
    get_cached_categories,
    get_cached_news_detail,
    get_cached_news_list,
    get_cached_related_news,
    get_hot_news_ids,
    get_news_views_delta,
    get_news_views_delta_map,
    increment_news_view_stats,
    set_cached_categories,
    set_cached_news_detail,
    set_cached_news_detail_null,
    set_cached_news_list,
    set_cached_related_news,
)
from crud import news as news_repo
from schemas.base import CategoryItemResponse, NewsItemBase
from schemas.news import NewsDetailResponse, NewsListPageResponse


logger = logging.getLogger(__name__)


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    cached_categories = await get_cached_categories(skip, limit)
    if cached_categories is not MISSING:
        return cached_categories

    categories = await news_repo.get_categories(db, skip, limit)
    payload = [
        CategoryItemResponse.model_validate(item).model_dump(by_alias=True, mode="json")
        for item in categories
    ]
    await set_cached_categories(skip, limit, payload)
    return payload


async def get_news_list(
    db: AsyncSession,
    category_id: int,
    page: int = 1,
    page_size: int = 10,
) -> NewsListPageResponse:
    skip = (page - 1) * page_size
    total = await news_repo.get_news_count(db, category_id)

    cached_news_list = await get_cached_news_list(category_id, page, page_size)
    if cached_news_list is MISSING:
        news_list = await news_repo.get_news_list(db, category_id, skip, page_size)
        cached_news_list = [
            NewsItemBase.model_validate(item).model_dump(by_alias=True, mode="json")
            for item in news_list
        ]
        await set_cached_news_list(category_id, page, page_size, cached_news_list)

    items = [NewsItemBase.model_validate(item) for item in cached_news_list]
    has_more = (skip + page_size) < total
    return NewsListPageResponse(list=items, total=total, hasMore=has_more)


async def get_news_detail(db: AsyncSession, news_id: int) -> NewsDetailResponse:
    cached_news_detail = await get_cached_news_detail(news_id)
    if cached_news_detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

    if cached_news_detail is MISSING:
        news_detail = await news_repo.get_news_detail(db, news_id)
        if not news_detail:
            await set_cached_news_detail_null(news_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

        cached_news_detail = {
            **NewsItemBase.model_validate(news_detail).model_dump(by_alias=True, mode="json"),
            "content": news_detail.content,
            "relatedNews": [],
        }
        await set_cached_news_detail(news_id, cached_news_detail)

    base_views = int(cached_news_detail.get("views", 0))
    category_id = int(cached_news_detail["categoryId"])
    cache_recorded = await increment_news_view_stats(news_id, category_id)

    if cache_recorded:
        response_views = base_views + await get_news_views_delta(news_id)
    else:
        logger.warning(
            "redis view aggregation unavailable, fallback to mysql update",
            extra={"news_id": news_id},
        )
        increased = await news_repo.increase_news_view(db, news_id)
        if not increased:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

        response_views = base_views + 1
        cached_news_detail["views"] = response_views
        await set_cached_news_detail(news_id, cached_news_detail)

    cached_related_news = await get_cached_related_news(news_id)
    if cached_related_news is MISSING:
        related_news = await news_repo.get_related_news(db, category_id, news_id)
        cached_related_news = [
            NewsItemBase.model_validate(item).model_dump(by_alias=True, mode="json")
            for item in related_news
        ]
        await set_cached_related_news(news_id, cached_related_news)

    response_payload = dict(cached_news_detail)
    response_payload["views"] = response_views
    response_payload["relatedNews"] = cached_related_news if cached_related_news is not None else []
    return NewsDetailResponse.model_validate(response_payload)


async def get_hot_news(
    db: AsyncSession,
    category_id: int | None = None,
    limit: int = 10,
) -> list[NewsItemBase]:
    hot_news_ids = await get_hot_news_ids(category_id, limit)

    if hot_news_ids:
        hot_news = await news_repo.get_news_by_ids(db, hot_news_ids)
    else:
        hot_news = await news_repo.get_hot_news(db, category_id, limit)

    if not hot_news:
        return []

    delta_map = await get_news_views_delta_map([item.id for item in hot_news])
    hot_items: list[NewsItemBase] = []
    for item in hot_news:
        payload = NewsItemBase.model_validate(item).model_dump(by_alias=True, mode="json")
        payload["views"] = int(payload.get("views", 0)) + delta_map.get(item.id, 0)
        hot_items.append(NewsItemBase.model_validate(payload))

    return hot_items
