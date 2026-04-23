# M1.1 + M1.2 News Read Cache

## Goal

This phase introduces the first usable Redis cache architecture for the news public read path.

Scope in this phase:

- cache infrastructure modules
- cache keys and TTL rules
- cache-aside for:
  - categories
  - news list
  - news detail
  - related news

Not included yet:

- Redis-based view count aggregation
- hot ranking
- user-state cache
- Agent retrieval cache

## Architectural Change

Before this phase, cache logic was mixed into `crud/news_cache.py`.

Now the responsibility is split into:

- `backend/cache/`
  - cache primitives
  - key naming
  - TTL policies
  - news cache accessors
- `backend/services/news_service.py`
  - cache hit/miss decisions
  - DB fallback
  - response assembly
- `backend/crud/news.py`
  - MySQL data access only

This makes the direction clear:

`router -> service -> cache/crud`

## New Cache Modules

### `backend/cache/client.py`

Provides the basic Redis JSON read/write contract.

Important behavior:

- `MISSING` means Redis miss or Redis unavailable
- `None` means the key is intentionally cached as null
- callers can distinguish miss from null-cache

### `backend/cache/codec.py`

Defines:

- JSON encode/decode helpers
- `NULL_SENTINEL`

### `backend/cache/ttl.py`

Defines TTLs for this phase:

- categories: 2h
- news list: 10min
- news detail: 30min
- related news: 15min
- null cache: 60s

Also includes TTL jitter to reduce synchronized expiration.

### `backend/cache/keys.py`

Current key patterns:

```text
news:category:list:{skip}:{limit}
news:list:{category_id}:{page}:{page_size}
news:detail:{news_id}
news:related:{news_id}
```

### `backend/cache/news_cache.py`

News-specific cache accessors:

- `get_cached_categories`
- `set_cached_categories`
- `get_cached_news_list`
- `set_cached_news_list`
- `get_cached_news_detail`
- `set_cached_news_detail`
- `set_cached_news_detail_null`
- `get_cached_related_news`
- `set_cached_related_news`

## Cache Strategy Used

This phase uses `cache-aside`.

### Categories

1. read Redis
2. on miss, read MySQL
3. serialize with API schema
4. write Redis

### News List

1. read Redis by category/page/pageSize
2. on miss, query MySQL
3. serialize to API contract
4. write Redis

### News Detail

1. read cached detail
2. if null-cache, return 404
3. if miss, read MySQL and cache base detail
4. update DB views as before
5. fetch or build related-news cache
6. update cached detail views for current response

### Related News

1. read Redis
2. on miss, read MySQL
3. serialize and cache

## Detail Cache Tradeoff

In this phase, detail cache still updates MySQL views directly on each request.

This is intentional.

Why:

- current functionality remains stable
- we avoid changing behavior too early
- M1.4 will replace this with Redis delta aggregation

Current compromise:

- detail base data is cached
- views are incremented in DB
- cached detail `views` is updated for the current response path

This keeps the app usable while preparing for the next optimization phase.

## Degradation Behavior

If Redis is unavailable:

- cache reads return `MISSING`
- service falls back to MySQL
- cache writes fail silently without breaking the API

This is important because Redis should improve latency, not become a hard dependency.

## Files Changed

- Added:
  - `backend/cache/__init__.py`
  - `backend/cache/client.py`
  - `backend/cache/codec.py`
  - `backend/cache/keys.py`
  - `backend/cache/ttl.py`
- Reworked:
  - `backend/cache/news_cache.py`
  - `backend/services/news_service.py`
- Deprecated:
  - `backend/crud/news_cache.py`

## Validation Checklist

Recommended smoke tests:

1. start Redis and backend
2. request `/api/news/categories` twice
3. request `/api/news/list?categoryId=1&page=1&pageSize=10` twice
4. request `/api/news/detail?id=<valid_id>` twice
5. stop Redis and request the same endpoints again

Expected result:

- API still works with Redis running
- API still works with Redis stopped
- repeated requests should use Redis when available

## Next Step

Next M1 step will focus on write-side optimization:

- Redis view delta
- periodic MySQL flush
- groundwork for hot ranking

