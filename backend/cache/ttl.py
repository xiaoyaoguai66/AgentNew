import random


CATEGORY_TTL_SECONDS = 2 * 60 * 60
NEWS_LIST_TTL_SECONDS = 10 * 60
NEWS_DETAIL_TTL_SECONDS = 30 * 60
RELATED_NEWS_TTL_SECONDS = 15 * 60
NULL_CACHE_TTL_SECONDS = 60


def with_jitter(base_ttl: int, jitter_seconds: int = 120) -> int:
    return base_ttl + random.randint(0, jitter_seconds)
