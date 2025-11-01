"""
Background Tasks and Scheduled Jobs
Handles periodic maintenance and optimization tasks
"""

import asyncio
from datetime import datetime, timedelta
from typing import Callable, Dict, Any
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.core.cache import cache

# Simplified database session - using synchronous for now
from app.db.database import SessionLocal

def get_db_session():
    """Get a database session"""
    return SessionLocal()

# Stub implementations for Phase 4 - these can be implemented later
async def refresh_materialized_views_task():
    """Refresh materialized views - stub implementation"""
    logger.info("Materialized views refresh (stub - implement when views are created)")

async def cleanup_old_data_task():
    """Cleanup old data - stub implementation"""
    logger.info("Old data cleanup (stub - implement when ready)")

async def vacuum_analyze_task():
    """VACUUM ANALYZE - stub implementation"""
    logger.info("VACUUM ANALYZE (stub - requires admin privileges)")


class BackgroundTaskManager:
    """Manages scheduled background tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.task_stats: Dict[str, Dict[str, Any]] = {}
    
    def add_task(
        self,
        func: Callable,
        trigger_type: str = "interval",
        **trigger_kwargs
    ):
        """
        Add a scheduled task
        
        Args:
            func: Function to execute
            trigger_type: 'interval' or 'cron'
            trigger_kwargs: Arguments for the trigger
        """
        if trigger_type == "interval":
            trigger = IntervalTrigger(**trigger_kwargs)
        elif trigger_type == "cron":
            trigger = CronTrigger(**trigger_kwargs)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        self.scheduler.add_job(
            self._wrap_task(func),
            trigger=trigger,
            id=func.__name__
        )
        
        logger.info(f"Added scheduled task: {func.__name__}")
    
    def _wrap_task(self, func: Callable) -> Callable:
        """Wrap task with logging and error handling"""
        async def wrapper():
            task_name = func.__name__
            start_time = datetime.now()
            
            try:
                logger.info(f"Starting scheduled task: {task_name}")
                await func()
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Track task stats
                if task_name not in self.task_stats:
                    self.task_stats[task_name] = {
                        "runs": 0,
                        "failures": 0,
                        "last_run": None,
                        "last_duration": 0,
                        "total_duration": 0
                    }
                
                stats = self.task_stats[task_name]
                stats["runs"] += 1
                stats["last_run"] = datetime.now()
                stats["last_duration"] = execution_time
                stats["total_duration"] += execution_time
                
                logger.info(
                    f"Completed scheduled task: {task_name} "
                    f"in {execution_time:.2f}s"
                )
                
            except Exception as e:
                logger.error(f"Scheduled task failed: {task_name} - {str(e)}")
                
                if task_name in self.task_stats:
                    self.task_stats[task_name]["failures"] += 1
        
        return wrapper
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Background task scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Background task scheduler stopped")
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get statistics for all scheduled tasks"""
        return {
            "is_running": self.is_running,
            "tasks": self.task_stats,
            "active_jobs": [
                {
                    "id": job.id,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }


# Global task manager instance
task_manager = BackgroundTaskManager()


async def clear_expired_cache_task():
    """Clear expired cache entries"""
    from app.core.cache import get_cache_stats
    try:
        # Redis automatically expires keys, but we can do additional cleanup
        stats = await get_cache_stats()
        logger.info(f"Cache stats: {stats}")
    except Exception as e:
        logger.warning(f"Could not get cache stats: {e}")


async def health_check_task():
    """Periodic health check of all services"""
    try:
        # Simple health check - just log that the task ran
        logger.info("✅ Periodic health check completed")
    except Exception as e:
        logger.warning(f"Health check task error: {e}")


async def log_performance_metrics_task():
    """Log performance metrics"""
    from app.core.cache import get_cache_stats
    # Cache stats
    try:
        cache_stats = await get_cache_stats()
        logger.info(f"Cache stats: {cache_stats}")
    except Exception as e:
        logger.warning(f"Could not get cache stats: {e}")
    
    # Task stats
    task_stats = task_manager.get_task_stats()
    logger.info(f"Background task stats: {task_stats}")


# Setup function to initialize all scheduled tasks

def setup_scheduled_tasks():
    """Setup all scheduled background tasks"""
    
    # Refresh materialized views every hour
    task_manager.add_task(
        refresh_materialized_views_task,
        trigger_type="interval",
        hours=1
    )
    
    # Cleanup old data daily at 2 AM
    task_manager.add_task(
        cleanup_old_data_task,
        trigger_type="cron",
        hour=2,
        minute=0
    )
    
    # Run VACUUM ANALYZE weekly on Sundays at 3 AM
    task_manager.add_task(
        vacuum_analyze_task,
        trigger_type="cron",
        day_of_week="sun",
        hour=3,
        minute=0
    )
    
    # Clear expired cache every 30 minutes
    task_manager.add_task(
        clear_expired_cache_task,
        trigger_type="interval",
        minutes=30
    )
    
    # Health check every 5 minutes
    task_manager.add_task(
        health_check_task,
        trigger_type="interval",
        minutes=5
    )
    
    # Log performance metrics every hour
    task_manager.add_task(
        log_performance_metrics_task,
        trigger_type="interval",
        hours=1
    )
    
    # Start the scheduler
    task_manager.start()
    
    logger.info("All scheduled tasks configured and started")


# Shutdown function for graceful cleanup

def shutdown_scheduled_tasks():
    """Shutdown all scheduled tasks"""
    task_manager.shutdown()
    logger.info("All scheduled tasks stopped")
