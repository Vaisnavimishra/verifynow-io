"""
Redis-backed caching and rate limiting.

Cache: avoids re-running an expensive web-search-grounded verification when the
same normalized content (same text / same URL) was checked recently.

Rate limiting: a simple fixed-window counter per client key (IP), so a single
client cannot hammer the (costly, external-API-backed) verification endpoint.
"""
import json
import time

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def _cache_key(normalized_hash: str) -> str:
    return f"verify:cache:{normalized_hash}"


async def get_cached_result(normalized_hash: str) -> dict | None:
    client = get_redis()
    raw = await client.get(_cache_key(normalized_hash))
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def set_cached_result(normalized_hash: str, result: dict) -> None:
    client = get_redis()
    await client.set(
        _cache_key(normalized_hash),
        json.dumps(result, default=str),
        ex=settings.CACHE_TTL_SECONDS,
    )


async def check_rate_limit(client_key: str) -> tuple[bool, int]:
    """
    Fixed-window rate limiter.

    Returns (allowed, remaining_in_window).
    """
    client = get_redis()
    window = int(time.time() // 60)  # 1-minute windows
    key = f"verify:ratelimit:{client_key}:{window}"

    count = await client.incr(key)
    if count == 1:
        await client.expire(key, 60)

    limit = settings.RATE_LIMIT_PER_MINUTE
    return count <= limit, max(limit - count, 0)
