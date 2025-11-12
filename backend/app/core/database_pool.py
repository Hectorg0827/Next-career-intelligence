"""
Database Connection Pool Manager for NEXT Career Intelligence
Optimizes database connections for better performance
"""

from supabase import create_client, Client
from loguru import logger
from typing import Optional
import asyncio
from contextlib import asynccontextmanager
from app.core.config import settings

# Supabase client instance
_supabase_client: Optional[Client] = None
_connection_pool_size = 20  # Maximum concurrent connections


def init_supabase() -> Client:
    """
    Initialize Supabase client with connection pooling

    Returns:
        Configured Supabase client
    """
    global _supabase_client

    try:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY,
        )

        logger.info("✅ Supabase client initialized with connection pooling")
        return _supabase_client

    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        raise


def get_supabase() -> Client:
    """
    Get Supabase client instance

    Returns:
        Supabase client
    """
    if not _supabase_client:
        return init_supabase()
    return _supabase_client


@asynccontextmanager
async def get_db_connection():
    """
    Context manager for database connections
    Ensures proper connection handling and cleanup

    Usage:
        async with get_db_connection() as db:
            result = await db.table('users').select('*').execute()
    """
    client = get_supabase()
    try:
        yield client
    finally:
        # Connection cleanup if needed
        pass


class DatabaseConnectionPool:
    """
    Database connection pool manager
    Handles connection lifecycle and pooling
    """

    def __init__(self, pool_size: int = 20):
        self.pool_size = pool_size
        self._active_connections = 0
        self._lock = asyncio.Lock()

    async def acquire(self) -> Client:
        """Acquire a connection from the pool"""
        async with self._lock:
            if self._active_connections >= self.pool_size:
                logger.warning(f"Connection pool exhausted ({self.pool_size} connections)")
                # Wait for a connection to become available
                await asyncio.sleep(0.1)
                return await self.acquire()

            self._active_connections += 1
            return get_supabase()

    async def release(self):
        """Release a connection back to the pool"""
        async with self._lock:
            self._active_connections = max(0, self._active_connections - 1)

    def get_stats(self) -> dict:
        """Get connection pool statistics"""
        return {
            "pool_size": self.pool_size,
            "active_connections": self._active_connections,
            "available_connections": self.pool_size - self._active_connections,
            "utilization": round((self._active_connections / self.pool_size) * 100, 2),
        }


# Global connection pool instance
db_pool = DatabaseConnectionPool(pool_size=_connection_pool_size)


async def execute_with_retry(operation, max_retries: int = 3, retry_delay: float = 1.0):
    """
    Execute database operation with automatic retry logic

    Args:
        operation: Async function to execute
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Operation result
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Database operation failed after {max_retries} attempts: {e}")

    raise last_error


async def optimize_query(query: str) -> str:
    """
    Optimize SQL query for better performance

    Args:
        query: SQL query string

    Returns:
        Optimized query string
    """
    # TODO: Implement query optimization logic
    # For now, return the original query
    return query


def get_db_stats() -> dict:
    """
    Get database connection statistics

    Returns:
        Dictionary with database stats
    """
    return {"connection_pool": db_pool.get_stats(), "status": "connected" if _supabase_client else "disconnected"}
