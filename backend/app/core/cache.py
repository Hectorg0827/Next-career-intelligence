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
    """Get Redis client singleton with production-ready configuration"""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Production configuration
    max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    socket_connect_timeout = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
    cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    if not cache_enabled:
        logger.info("⚠️ Redis caching disabled by CACHE_ENABLED=false")
        return None

    try:
        # Create connection pool for better performance
        pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            socket_connect_timeout=socket_connect_timeout,
            socket_timeout=socket_timeout,
            decode_responses=True,
            # Enable SSL/TLS for production (Upstash uses rediss://)
            ssl_cert_reqs=None if redis_url.startswith("rediss://") else None,
            retry_on_timeout=True,
            health_check_interval=30,  # Check connection health every 30s
        )

        _redis_client = redis.Redis(connection_pool=pool)

        # Test connection
        _redis_client.ping()

        # Log sanitized connection info (hide password)
        safe_url = redis_url.split("@")[-1] if "@" in redis_url else redis_url
        logger.info(f"✅ Redis connected: {safe_url} (pool_size={max_connections})")

        return _redis_client
    except Exception as e:
        logger.warning(f"⚠️ Redis unavailable: {e} - caching disabled")
        return None


class Cache:
    """Cache management"""

    # Cache TTLs (in seconds) - configurable via environment variables
    TTL_SHORT = int(os.getenv("CACHE_SHORT_TTL", "300"))  # 5 minutes
    TTL_MEDIUM = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour
    TTL_LONG = int(os.getenv("CACHE_LONG_TTL", "86400"))  # 24 hours

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
    async def check_rate_limit(identifier: str, max_requests: int = 60, window_seconds: int = 60) -> tuple[bool, dict]:
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
                return False, {"remaining": 0, "reset_in": ttl, "limit": max_requests}

            return True, {"remaining": remaining, "reset_in": window_seconds, "limit": max_requests}

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


def cached(namespace: str, ttl: int = Cache.TTL_MEDIUM, key_builder: Optional[Callable] = None):
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


# Lifecycle management functions
async def init_redis():
    """Initialize Redis connection on startup"""
    client = get_redis_client()
    if client:
        logger.info("✅ Redis cache initialized")
    else:
        logger.warning("⚠️ Redis unavailable - running without cache")


async def cleanup_redis():
    """Cleanup Redis connection on shutdown"""
    global _redis_client
    if _redis_client:
        try:
            _redis_client.close()
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis: {e}")
        finally:
            _redis_client = None


async def get_cache_stats() -> dict:
    """Get cache statistics"""
    client = get_redis_client()
    if not client:
        return {"status": "unavailable", "connected": False}

    try:
        info = client.info()
        return {
            "status": "connected",
            "connected": True,
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
    except Exception as e:
        logger.error(f"❌ Error getting cache stats: {e}")
        return {"status": "error", "connected": False, "error": str(e)}
