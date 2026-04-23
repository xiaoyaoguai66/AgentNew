from typing import Any

from config.cache_conf import redis_client

from cache import keys, ttl
from cache.client import get_json, set_json, set_null


async def get_cached_categories(skip: int, limit: int):
    return await get_json(keys.news_categories_key(skip, limit))


async def set_cached_categories(skip: int, limit: int, data: list[dict[str, Any]]):
    return await set_json(
        keys.news_categories_key(skip, limit),
        data,
        ttl.with_jitter(ttl.CATEGORY_TTL_SECONDS),
    )


async def get_cached_news_list(category_id: int, page: int, page_size: int):
    return await get_json(keys.news_list_key(category_id, page, page_size))


async def set_cached_news_list(
    category_id: int,
    page: int,
    page_size: int,
    news_list: list[dict[str, Any]],
):
    return await set_json(
        keys.news_list_key(category_id, page, page_size),
        news_list,
        ttl.with_jitter(ttl.NEWS_LIST_TTL_SECONDS),
    )


async def get_cached_news_detail(news_id: int):
    return await get_json(keys.news_detail_key(news_id))


async def set_cached_news_detail(news_id: int, news_detail: dict[str, Any]):
    return await set_json(
        keys.news_detail_key(news_id),
        news_detail,
        ttl.with_jitter(ttl.NEWS_DETAIL_TTL_SECONDS),
    )


async def set_cached_news_detail_null(news_id: int):
    return await set_null(keys.news_detail_key(news_id), ttl.NULL_CACHE_TTL_SECONDS)


async def get_cached_related_news(news_id: int):
    return await get_json(keys.news_related_key(news_id))


async def set_cached_related_news(news_id: int, related_news: list[dict[str, Any]]):
    return await set_json(
        keys.news_related_key(news_id),
        related_news,
        ttl.with_jitter(ttl.RELATED_NEWS_TTL_SECONDS),
    )


async def increment_news_view_stats(news_id: int, category_id: int) -> bool:
    try:
        pipeline = redis_client.pipeline()
        pipeline.incr(keys.news_views_delta_key(news_id))
        pipeline.zincrby(keys.news_hot_global_key(), 1, news_id)
        pipeline.zincrby(keys.news_hot_category_key(category_id), 1, news_id)
        await pipeline.execute()
        return True
    except Exception:
        return False


async def get_news_views_delta(news_id: int) -> int:
    try:
        value = await redis_client.get(keys.news_views_delta_key(news_id))
    except Exception:
        return 0

    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


async def get_news_views_delta_map(news_ids: list[int]) -> dict[int, int]:
    if not news_ids:
        return {}

    try:
        values = await redis_client.mget([keys.news_views_delta_key(news_id) for news_id in news_ids])
    except Exception:
        return {}

    delta_map: dict[int, int] = {}
    for news_id, raw_value in zip(news_ids, values, strict=False):
        try:
            delta_map[news_id] = int(raw_value or 0)
        except (TypeError, ValueError):
            delta_map[news_id] = 0
    return delta_map


async def pop_news_view_deltas() -> dict[int, int]:
    view_deltas: dict[int, int] = {}

    try:
        async for key in redis_client.scan_iter(match=keys.news_views_delta_pattern()):
            try:
                raw_value = await redis_client.getdel(key)
            except Exception:
                raw_value = await redis_client.get(key)
                if raw_value not in (None, "", "0", 0):
                    await redis_client.delete(key)

            if raw_value in (None, "", "0", 0):
                continue

            try:
                news_id = int(key.rsplit(":", 1)[-1])
                delta = int(raw_value)
            except (TypeError, ValueError):
                continue

            if delta > 0:
                view_deltas[news_id] = delta
    except Exception:
        return {}

    return view_deltas


async def restore_news_view_deltas(view_deltas: dict[int, int]) -> bool:
    if not view_deltas:
        return True

    try:
        pipeline = redis_client.pipeline()
        for news_id, delta in view_deltas.items():
            pipeline.incrby(keys.news_views_delta_key(news_id), delta)
        await pipeline.execute()
        return True
    except Exception:
        return False


async def sync_cached_news_detail_views(view_deltas: dict[int, int]) -> bool:
    if not view_deltas:
        return True

    try:
        for news_id, delta in view_deltas.items():
            cached_news_detail = await get_cached_news_detail(news_id)
            if not isinstance(cached_news_detail, dict):
                continue

            current_views = int(cached_news_detail.get("views", 0))
            cached_news_detail["views"] = current_views + delta
            await set_cached_news_detail(news_id, cached_news_detail)
        return True
    except Exception:
        return False


async def get_hot_news_ids(category_id: int | None, limit: int = 10) -> list[int]:
    hot_key = (
        keys.news_hot_category_key(category_id)
        if category_id is not None
        else keys.news_hot_global_key()
    )

    try:
        raw_ids = await redis_client.zrevrange(hot_key, 0, max(limit - 1, 0))
    except Exception:
        return []

    hot_ids: list[int] = []
    for raw_id in raw_ids:
        try:
            hot_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue
    return hot_ids
