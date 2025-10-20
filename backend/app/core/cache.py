"""
Redis Caching Layer
Provides caching for API responses, user data, and rate limiting
"""

import redis
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from loguru import logger
import os
from datetime import timedelta

# Initialize Redis connection
_redis_client = None

def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client singleton"""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    try:
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test connection
        _redis_client.ping()
        logger.info(f"✅ Redis connected: {redis_url}")
        return _redis_client
    except Exception as e:
        logger.warning(f"⚠️ Redis unavailable: {e} - caching disabled")
        return None


class Cache:
    """Cache management"""

    # Cache TTLs (in seconds)
    TTL_SHORT = 300  # 5 minutes
    TTL_MEDIUM = 3600  # 1 hour
    TTL_LONG = 86400  # 24 hours

    @staticmethod
    def _make_key(namespace: str, key: str) -> str:
        """Generate cache key with namespace"""
        return f"next:{namespace}:{key}"

    @staticmethod
    async def get(namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            namespace: Cache namespace (e.g., 'profile', 'analysis')
            key: Cache key

        Returns:
            Cached value or None
        """
        client = get_redis_client()
        if not client:
            return None

        try:
            cache_key = Cache._make_key(namespace, key)
            value = client.get(cache_key)

            if value:
                logger.debug(f"✅ Cache hit: {cache_key}")
                return json.loads(value)

            logger.debug(f"❌ Cache miss: {cache_key}")
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    @staticmethod
    async def set(namespace: str, key: str, value: Any, ttl: int = TTL_MEDIUM) -> bool:
        """
        Set value in cache

        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds

        Returns:
            Success boolean
        """
        client = get_redis_client()
        if not client:
            return False

        try:
            cache_key = Cache._make_key(namespace, key)
            serialized = json.dumps(value)
            client.setex(cache_key, ttl, serialized)
            logger.debug(f"✅ Cached: {cache_key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    @staticmethod
    async def delete(namespace: str, key: str) -> bool:
        """Delete value from cache"""
        client = get_redis_client()
        if not client:
            return False

        try:
            cache_key = Cache._make_key(namespace, key)
            client.delete(cache_key)
            logger.debug(f"🗑️ Deleted cache: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    @staticmethod
    async def invalidate_pattern(namespace: str, pattern: str) -> int:
        """
        Invalidate all keys matching pattern

        Args:
            namespace: Cache namespace
            pattern: Pattern to match (e.g., 'user_*')

        Returns:
            Number of keys deleted
        """
        client = get_redis_client()
        if not client:
            return 0

        try:
            search_pattern = Cache._make_key(namespace, pattern)
            keys = client.keys(search_pattern)

            if keys:
                count = client.delete(*keys)
                logger.info(f"🗑️ Invalidated {count} cache keys: {search_pattern}")
                return count

            return 0

        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return 0


class RateLimiter:
    """Rate limiting using Redis"""

    @staticmethod
    async def check_rate_limit(
        identifier: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if request should be rate limited

        Args:
            identifier: Unique identifier (e.g., user_id, IP)
            max_requests: Max requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed, info_dict)
        """
        client = get_redis_client()
        if not client:
            # If Redis unavailable, allow request
            return True, {"remaining": max_requests, "reset_in": window_seconds}

        try:
            key = f"ratelimit:{identifier}"

            # Use Redis pipeline for atomic operations
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = pipe.execute()

            current_count = results[0]
            remaining = max(0, max_requests - current_count)

            if current_count > max_requests:
                ttl = client.ttl(key)
                logger.warning(f"⚠️ Rate limit exceeded: {identifier} ({current_count}/{max_requests})")
                return False, {
                    "remaining": 0,
                    "reset_in": ttl,
                    "limit": max_requests
                }

            return True, {
                "remaining": remaining,
                "reset_in": window_seconds,
                "limit": max_requests
            }

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # On error, allow request
            return True, {"remaining": max_requests, "reset_in": window_seconds}

    @staticmethod
    async def reset_rate_limit(identifier: str) -> bool:
        """Reset rate limit for an identifier"""
        client = get_redis_client()
        if not client:
            return False

        try:
            key = f"ratelimit:{identifier}"
            client.delete(key)
            logger.info(f"✅ Reset rate limit: {identifier}")
            return True

        except Exception as e:
            logger.error(f"Rate limit reset error: {e}")
            return False


def cached(
    namespace: str,
    ttl: int = Cache.TTL_MEDIUM,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results

    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        key_builder: Optional function to build cache key from args

    Example:
        @cached("profile", ttl=3600)
        async def get_profile(user_id: str):
            # Expensive operation
            return profile_data
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: use function name + args
                args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
                cache_key = f"{func.__name__}:{hashlib.md5(args_str.encode()).hexdigest()}"

            # Try to get from cache
            cached_value = await Cache.get(namespace, cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await Cache.set(namespace, cache_key, result, ttl)

            return result

        return wrapper
    return decorator


# Global instances
cache = Cache()
rate_limiter = RateLimiter()


# Helper function for profile caching
async def get_cached_profile(user_id: str) -> Optional[dict]:
    """Get career profile from cache"""
    return await cache.get("profile", user_id)


async def cache_profile(user_id: str, profile_data: dict, ttl: int = Cache.TTL_MEDIUM):
    """Cache career profile"""
    return await cache.set("profile", user_id, profile_data, ttl)


async def invalidate_profile_cache(user_id: str):
    """Invalidate profile cache when updated"""
    await cache.delete("profile", user_id)
    # Also invalidate related caches
    await cache.invalidate_pattern("analysis", f"{user_id}_*")
    await cache.invalidate_pattern("suggestions", f"{user_id}_*")


async def get_cached_suggestions(user_id: str) -> Optional[list]:
    """Get pending suggestions from cache"""
    return await cache.get("suggestions", f"{user_id}_pending")


async def cache_suggestions(user_id: str, suggestions: list):
    """Cache pending suggestions"""
    return await cache.set("suggestions", f"{user_id}_pending", suggestions, Cache.TTL_SHORT)
