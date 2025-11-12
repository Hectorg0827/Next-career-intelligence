"""
Database Query Optimizer Service
Provides query optimization, caching, and performance monitoring
"""

from typing import Any, Dict, List, Optional, Callable
from functools import wraps
import hashlib
import json
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core.cache import cache_manager


class QueryOptimizer:
    """Optimizes database queries with caching and performance monitoring"""

    def __init__(self):
        self.query_stats: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def generate_cache_key(query: str, params: Dict[str, Any]) -> str:
        """Generate a cache key from query and parameters"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        return f"query:{query_hash}:{params_hash}"

    async def execute_cached_query(
        self,
        db: AsyncSession,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        cache_ttl: int = 300,  # 5 minutes default
        cache_enabled: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Execute a query with caching

        Args:
            db: Database session
            query: SQL query string
            params: Query parameters
            cache_ttl: Cache time-to-live in seconds
            cache_enabled: Whether to use caching

        Returns:
            Query results as list of dictionaries
        """
        params = params or {}

        # Generate cache key
        cache_key = self.generate_cache_key(query, params)

        # Try to get from cache
        if cache_enabled and settings.REDIS_ENABLED:
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached_result

        # Execute query
        start_time = datetime.now()
        try:
            result = await db.execute(text(query), params)
            rows = result.fetchall()

            # Convert to list of dicts
            results = [dict(row._mapping) for row in rows]

            # Track query performance
            execution_time = (datetime.now() - start_time).total_seconds()
            self._track_query_performance(query, execution_time)

            # Cache results
            if cache_enabled and settings.REDIS_ENABLED:
                await cache_manager.set(cache_key, results, ttl=cache_ttl)
                logger.debug(f"Cached query results: {cache_key}")

            return results

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    def _track_query_performance(self, query: str, execution_time: float):
        """Track query execution time for monitoring"""
        query_key = query[:100]  # Use first 100 chars as key

        if query_key not in self.query_stats:
            self.query_stats[query_key] = {
                "count": 0,
                "total_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
                "avg_time": 0,
            }

        stats = self.query_stats[query_key]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["min_time"] = min(stats["min_time"], execution_time)
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["avg_time"] = stats["total_time"] / stats["count"]

        # Log slow queries
        if execution_time > 1.0:  # More than 1 second
            logger.warning(f"Slow query detected: {query[:100]}... " f"Execution time: {execution_time:.2f}s")

    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return {
            "total_queries": sum(s["count"] for s in self.query_stats.values()),
            "slow_queries": [
                {"query": q, "avg_time": s["avg_time"], "max_time": s["max_time"], "count": s["count"]}
                for q, s in self.query_stats.items()
                if s["avg_time"] > 0.5  # Queries averaging more than 500ms
            ],
            "all_stats": self.query_stats,
        }

    async def invalidate_cache_pattern(self, pattern: str):
        """Invalidate all cache keys matching a pattern"""
        if settings.REDIS_ENABLED:
            await cache_manager.delete_pattern(f"query:{pattern}*")
            logger.info(f"Invalidated cache for pattern: {pattern}")


# Global query optimizer instance
query_optimizer = QueryOptimizer()


def cached_query(cache_ttl: int = 300):
    """
    Decorator to cache database query results

    Usage:
        @cached_query(cache_ttl=600)
        async def get_active_jobs(db: AsyncSession):
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            func_name = func.__name__
            args_str = str(args) + str(kwargs)
            cache_key = f"func:{func_name}:{hashlib.md5(args_str.encode()).hexdigest()}"

            # Try to get from cache
            if settings.REDIS_ENABLED:
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for function: {func_name}")
                    return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            if settings.REDIS_ENABLED:
                await cache_manager.set(cache_key, result, ttl=cache_ttl)
                logger.debug(f"Cached function result: {func_name}")

            return result

        return wrapper

    return decorator


# Database optimization utilities


async def refresh_materialized_views(db: AsyncSession):
    """Refresh all materialized views"""
    try:
        await db.execute(text("SELECT refresh_job_match_scores()"))
        await db.commit()
        logger.info("Refreshed materialized views")
    except Exception as e:
        logger.error(f"Failed to refresh materialized views: {str(e)}")
        await db.rollback()


async def cleanup_old_data(db: AsyncSession):
    """Run cleanup functions for old data"""
    try:
        await db.execute(text("SELECT cleanup_old_notifications()"))
        await db.execute(text("SELECT cleanup_expired_jobs()"))
        await db.commit()
        logger.info("Cleaned up old data")
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {str(e)}")
        await db.rollback()


async def vacuum_analyze(db: AsyncSession, table: Optional[str] = None):
    """Run VACUUM ANALYZE on specified table or all tables"""
    try:
        if table:
            await db.execute(text(f"VACUUM ANALYZE {table}"))
        else:
            await db.execute(text("VACUUM ANALYZE"))
        logger.info(f"Ran VACUUM ANALYZE{' on ' + table if table else ''}")
    except Exception as e:
        logger.error(f"Failed to run VACUUM ANALYZE: {str(e)}")


async def get_slow_queries(db: AsyncSession, min_time_ms: int = 100) -> List[Dict[str, Any]]:
    """Get slow queries from pg_stat_statements"""
    query = """
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        max_time
    FROM pg_stat_statements
    WHERE mean_time > :min_time
    ORDER BY total_time DESC
    LIMIT 50
    """

    result = await db.execute(text(query), {"min_time": min_time_ms})
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]


async def get_table_sizes(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get sizes of all tables"""
    query = """
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
        pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY size_bytes DESC
    """

    result = await db.execute(text(query))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]


async def get_index_usage(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get index usage statistics"""
    query = """
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch,
        pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
    FROM pg_stat_user_indexes
    ORDER BY idx_scan ASC
    LIMIT 50
    """

    result = await db.execute(text(query))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]


# Example optimized queries


@cached_query(cache_ttl=600)
async def get_user_recommended_jobs(
    db: AsyncSession, user_id: str, limit: int = 10, offset: int = 0
) -> List[Dict[str, Any]]:
    """Get recommended jobs for a user (cached)"""
    query = "SELECT * FROM get_user_recommended_jobs(:user_id, :limit, :offset)"

    return await query_optimizer.execute_cached_query(
        db=db, query=query, params={"user_id": user_id, "limit": limit, "offset": offset}, cache_ttl=600
    )


@cached_query(cache_ttl=300)
async def get_skill_gaps(db: AsyncSession, user_id: str, job_id: str) -> List[Dict[str, Any]]:
    """Get skill gaps for a user and job (cached)"""
    query = "SELECT * FROM get_skill_gaps(:user_id, :job_id)"

    return await query_optimizer.execute_cached_query(
        db=db, query=query, params={"user_id": user_id, "job_id": job_id}, cache_ttl=300
    )


@cached_query(cache_ttl=900)
async def get_active_jobs(
    db: AsyncSession, location: Optional[str] = None, limit: int = 20, offset: int = 0
) -> List[Dict[str, Any]]:
    """Get active jobs with optional location filter (cached)"""
    query = """
    SELECT id, title, location, salary_min, salary_max, posted_at
    FROM jobs
    WHERE status = 'active'
    """

    params = {"limit": limit, "offset": offset}

    if location:
        query += " AND location ILIKE :location"
        params["location"] = f"%{location}%"

    query += " ORDER BY posted_at DESC LIMIT :limit OFFSET :offset"

    return await query_optimizer.execute_cached_query(db=db, query=query, params=params, cache_ttl=900)
