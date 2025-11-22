"""
Background Jobs for AI Agents
==============================

Scheduled tasks for maintaining AI system health:
- Memory formation (daily)
- Recommendation updates (hourly)
- Churn prediction (weekly)
- Profile analysis refresh (daily)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.database_pool import get_supabase
from app.services.foundation.ai.memory import ai_memory
from app.services.foundation.ai.recommendations import recommendation_engine
from app.services.foundation.ai.predictions import predictive_analytics
from app.services.foundation.ai.profile_assistant import profile_assistant
from app.services.foundation.ai.guidance import proactive_guidance

logger = logging.getLogger(__name__)


class AIBackgroundJobs:
    """Manages all background jobs for AI agents"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    def start(self):
        """Start all scheduled jobs"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
            
        # Daily memory formation (runs at 2 AM)
        self.scheduler.add_job(
            self.form_daily_memories,
            CronTrigger(hour=2, minute=0),
            id='daily_memory_formation',
            name='Form Daily Memories',
            replace_existing=True
        )

        # Daily job ingestion (runs at 3 AM)
        self.scheduler.add_job(
            self.run_daily_job_ingestion,
            CronTrigger(hour=3, minute=0),
            id='daily_job_ingestion',
            name='Daily Job Ingestion',
            replace_existing=True
        )
        
        # Hourly recommendation updates
        self.scheduler.add_job(
            self.update_recommendations,
            CronTrigger(minute=0),  # Every hour
            id='hourly_recommendation_update',
            name='Update Recommendations',
            replace_existing=True
        )
        
        # Weekly churn prediction (runs Sunday at 3 AM)
        self.scheduler.add_job(
            self.predict_churn_risk,
            CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='weekly_churn_prediction',
            name='Predict Churn Risk',
            replace_existing=True
        )
        
        # Daily profile analysis (runs at 4 AM)
        self.scheduler.add_job(
            self.analyze_profiles,
            CronTrigger(hour=4, minute=0),
            id='daily_profile_analysis',
            name='Analyze Profiles',
            replace_existing=True
        )
        
        # Cleanup old data (runs at 5 AM)
        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(hour=5, minute=0),
            id='daily_data_cleanup',
            name='Cleanup Old Data',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("AI background jobs scheduler started")
        
    def stop(self):
        """Stop all scheduled jobs"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("AI background jobs scheduler stopped")
    
    async def form_daily_memories(self):
        """
        Daily job to form memories from user interactions
        Runs at 2 AM to process previous day's interactions
        """
        logger.info("Starting daily memory formation...")
        
        try:
            db = get_supabase()
            
            # Get all active users from recent interactions
            result = db.table('user_interactions').select('user_id').gte(
                'created_at', 'now() - interval \'1 day\''
            ).execute()
            
            user_ids = list(set([row['user_id'] for row in result.data]))
            
            logger.info(f"Processing memories for {len(user_ids)} users")
            
            # Process each user
            success_count = 0
            for user_id in user_ids:
                try:
                    # Get recent interactions
                    interactions = await self._get_user_interactions(user_id)
                    
                    if not interactions:
                        continue
                        
                    # Form memory
                    await ai_memory.form_memory(
                        user_id=user_id,
                        interaction_type="daily_summary",
                        interaction_data={
                            "interactions": interactions,
                            "period": "past_24_hours"
                        }
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to form memory for user {user_id}: {e}")
                    continue
            
            logger.info(f"Memory formation complete: {success_count}/{len(user_ids)} succeeded")
            
        except Exception as e:
            logger.error(f"Daily memory formation failed: {e}")
    
    async def update_recommendations(self):
        """
        Hourly job to refresh job recommendations
        Updates cached recommendations for active users
        """
        logger.info("Starting recommendation updates...")
        
        try:
            db = get_supabase()
            
            # Get users who need updated recommendations (recent activity or stale recs)
            # Simplified: just get users with recent interactions
            result = db.table('user_interactions').select('user_id').gte(
                'created_at', 'now() - interval \'1 hour\''
            ).limit(100).execute()
            
            user_ids = list(set([row['user_id'] for row in result.data]))
            
            logger.info(f"Updating recommendations for {len(user_ids)} users")
            
            success_count = 0
            for user_id in user_ids:
                try:
                    # Generate fresh recommendations
                    recommendations = await recommendation_engine.get_recommendations(
                        user_id=user_id,
                        limit=20,
                        refresh=True
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to update recommendations for user {user_id}: {e}")
                    continue
            
            logger.info(f"Recommendation updates complete: {success_count}/{len(user_ids)} succeeded")
            
        except Exception as e:
            logger.error(f"Recommendation update failed: {e}")
    
    async def predict_churn_risk(self):
        """
        Weekly job to predict user churn risk
        Identifies users at risk of disengagement
        """
        logger.info("Starting weekly churn prediction...")
        
        try:
            db = get_supabase()
            
            # Get active users (profiles older than 7 days)
            result = db.table('career_profiles').select('user_id').lt(
                'created_at', 'now() - interval \'7 days\''
            ).limit(200).execute()
            
            user_ids = [row['user_id'] for row in result.data]
            
            logger.info(f"Predicting churn risk for {len(user_ids)} users")
            
            high_risk_count = 0
            medium_risk_count = 0
            
            for user_id in user_ids:
                try:
                    # Predict churn risk
                    prediction = await predictive_analytics.predict_churn(user_id)
                    
                    if prediction.get("churn_risk") == "high":
                        high_risk_count += 1
                    elif prediction.get("churn_risk") == "medium":
                        medium_risk_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to predict churn for user {user_id}: {e}")
                    continue
            
            logger.info(
                f"Churn prediction complete: {high_risk_count} high risk, "
                f"{medium_risk_count} medium risk out of {len(user_ids)} users"
            )
            
        except Exception as e:
            logger.error(f"Churn prediction failed: {e}")
    
    async def analyze_profiles(self):
        """
        Daily job to analyze and score profiles
        Refreshes profile completeness and suggestions
        """
        logger.info("Starting daily profile analysis...")
        
        try:
            db = get_supabase()
            
            # Get profiles updated in the last day
            result = db.table('career_profiles').select('user_id').gte(
                'updated_at', 'now() - interval \'1 day\''
            ).limit(200).execute()
            
            user_ids = [row['user_id'] for row in result.data]
            
            logger.info(f"Analyzing profiles for {len(user_ids)} users")
            
            success_count = 0
            for user_id in user_ids:
                try:
                    # Analyze profile
                    analysis = await profile_assistant.analyze_profile(user_id)
                    
                    # Generate suggestions if completeness < 80%
                    if analysis.get("completeness_score", 0) < 0.8:
                        await profile_assistant.suggest_improvements(user_id)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to analyze profile for user {user_id}: {e}")
                    continue
            
            logger.info(f"Profile analysis complete: {success_count}/{len(user_ids)} succeeded")
            
        except Exception as e:
            logger.error(f"Profile analysis failed: {e}")
    
    async def cleanup_old_data(self):
        """
        Daily cleanup of old AI-generated data
        Removes stale recommendations, old predictions, etc.
        """
        logger.info("Starting daily data cleanup...")
        
        try:
            db = get_supabase()
            
            # Clean old recommendations (>30 days)
            result = db.table('ai_recommendations').delete().lt(
                'created_at', 'now() - interval \'30 days\''
            ).execute()
            recs_deleted = len(result.data) if result.data else 0
            
            # Clean old predictions (>90 days)
            result = db.table('churn_predictions').delete().lt(
                'created_at', 'now() - interval \'90 days\''
            ).execute()
            predictions_deleted = len(result.data) if result.data else 0
            
            # Clean dismissed guidance (>60 days)
            result = db.table('ai_guidance').delete().eq(
                'status', 'dismissed'
            ).lt(
                'updated_at', 'now() - interval \'60 days\''
            ).execute()
            guidance_deleted = len(result.data) if result.data else 0
            
            # Expire old jobs (>60 days)
            result = db.table('jobs').update({'status': 'expired'}).eq('status', 'active').lt(
                'posted_at', 'now() - interval \'60 days\''
            ).execute()
            jobs_expired = len(result.data) if result.data else 0

            logger.info(
                f"Cleanup complete: {recs_deleted} recommendations, "
                f"{predictions_deleted} predictions, {guidance_deleted} guidance messages deleted, "
                f"{jobs_expired} jobs expired"
            )
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    async def run_daily_job_ingestion(self):
        """Run daily job ingestion from all sources"""
        from app.services.job_aggregator import JobAggregatorService
        
        logger.info("⏰ Starting scheduled job ingestion...")
        aggregator = JobAggregatorService()
        try:
            await aggregator.run_scrape_and_store()
        except Exception as e:
            logger.error(f"Scheduled job ingestion failed: {e}")
        finally:
            await aggregator.close()
    
    async def _get_user_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent interactions for a user"""
        try:
            db = get_supabase()
            result = db.table('user_interactions').select(
                'interaction_type', 'interaction_data', 'created_at'
            ).eq(
                'user_id', user_id
            ).gte(
                'created_at', 'now() - interval \'1 day\''
            ).order('created_at', desc=True).execute()
            
            interactions = []
            for row in result.data:
                interactions.append({
                    "type": row.get('interaction_type'),
                    "data": row.get('interaction_data'),
                    "timestamp": row.get('created_at')
                })
            
            return interactions
        except Exception as e:
            logger.error(f"Failed to get interactions for user {user_id}: {e}")
            return []


# Global scheduler instance
ai_jobs = AIBackgroundJobs()


def start_ai_jobs():
    """Start AI background jobs (called at app startup)"""
    ai_jobs.start()


def stop_ai_jobs():
    """Stop AI background jobs (called at app shutdown)"""
    ai_jobs.stop()
