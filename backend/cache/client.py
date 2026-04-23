from typing import Any

from config.cache_conf import redis_client

from cache.codec import NULL_SENTINEL, decode_json, encode_json


MISSING = object()


async def get_json(key: str) -> Any:
    try:
        raw_value = await redis_client.get(key)
    except Exception:
        return MISSING

    if raw_value is None:
        return MISSING
    if raw_value == NULL_SENTINEL:
        return None
    return decode_json(raw_value)


async def set_json(key: str, value: Any, expire: int) -> bool:
    try:
        await redis_client.setex(key, expire, encode_json(value))
        return True
    except Exception:
        return False


async def set_null(key: str, expire: int) -> bool:
    try:
        await redis_client.setex(key, expire, NULL_SENTINEL)
        return True
    except Exception:
        return False


async def delete(key: str) -> bool:
    try:
        await redis_client.delete(key)
        return True
    except Exception:
        return False
