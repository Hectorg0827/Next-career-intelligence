"""
Proactive Coach - Autonomous Career Guidance System

Continuously monitors users and provides proactive, contextual
guidance without waiting to be asked.
"""

from typing import Dict, List, Optional
import logging
import asyncio

from .guidance_detector import GuidanceDetector, GuidanceType
from .intervention_engine import InterventionEngine, InterventionMessage

logger = logging.getLogger(__name__)


class ProactiveCoach:
    """
    Autonomous career coach that proactively helps users.
    
    Monitors behavior, detects needs, and delivers timely guidance.
    """
    
    def __init__(self):
        self.detector = GuidanceDetector()
        self.intervention_engine = InterventionEngine()
        self.is_monitoring = False
        logger.info("Proactive coach initialized")
    
    # ==================== Individual User Guidance ====================
    
    async def check_user(self, user_id: str) -> List[InterventionMessage]:
        """
        Check a single user for guidance needs.
        
        Returns list of intervention messages that should be shown.
        """
        
        try:
            # Detect all guidance needs
            signals = await self.detector.detect_guidance_needs(user_id)
            
            if not signals:
                logger.debug(f"No guidance needs detected for {user_id}")
                return []
            
            # Generate interventions for detected needs
            interventions = []
            for signal in signals:
                intervention = await self.intervention_engine.generate_intervention(
                    user_id,
                    signal
                )
                if intervention:
                    interventions.append(intervention)
            
            logger.info(f"Generated {len(interventions)} interventions for {user_id}")
            return interventions
            
        except Exception as e:
            logger.error(f"Error checking user {user_id}: {e}")
            return []
    
    async def get_priority_guidance(
        self,
        user_id: str,
        limit: int = 1
    ) -> List[InterventionMessage]:
        """
        Get the most important guidance for a user.
        
        Returns top priority interventions only.
        """
        
        interventions = await self.check_user(user_id)
        
        # Sort by priority (high > medium > low)
        priority_order = {"high": 3, "medium": 2, "low": 1}
        interventions.sort(
            key=lambda x: priority_order.get(x.get("priority", "low"), 0),
            reverse=True
        )
        
        return interventions[:limit]
    
    async def check_specific_need(
        self,
        user_id: str,
        need_type: GuidanceType
    ) -> Optional[InterventionMessage]:
        """
        Check for a specific type of guidance need.
        
        Useful for targeted checks (e.g., check profile completion on profile page).
        """
        
        try:
            # Detect only this type
            signals = await self.detector.detect_guidance_needs(
                user_id,
                check_types=[need_type]
            )
            
            if not signals:
                return None
            
            # Generate intervention for first signal
            return await self.intervention_engine.generate_intervention(
                user_id,
                signals[0]
            )
            
        except Exception as e:
            logger.error(f"Error checking {need_type} for {user_id}: {e}")
            return None
    
    # ==================== Batch Processing ====================
    
    async def check_multiple_users(
        self,
        user_ids: List[str],
        batch_size: int = 10
    ) -> Dict[str, List[InterventionMessage]]:
        """
        Check multiple users in batches.
        
        Returns dict mapping user_id to interventions.
        """
        
        results = {}
        
        # Process in batches to avoid overwhelming system
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [self.check_user(uid) for uid in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results
            for user_id, interventions in zip(batch, batch_results):
                if isinstance(interventions, Exception):
                    logger.error(f"Error processing {user_id}: {interventions}")
                    results[user_id] = []
                else:
                    results[user_id] = interventions
            
            # Brief pause between batches
            if i + batch_size < len(user_ids):
                await asyncio.sleep(0.5)
        
        logger.info(f"Checked {len(user_ids)} users in batches")
        return results
    
    # ==================== Dashboard Integration ====================
    
    async def get_dashboard_guidance(self, user_id: str) -> Dict:
        """
        Get guidance for dashboard display.
        
        Returns single most important intervention plus status.
        """
        
        priority_interventions = await self.get_priority_guidance(user_id, limit=1)
        
        return {
            "has_guidance": len(priority_interventions) > 0,
            "intervention": priority_interventions[0] if priority_interventions else None,
            "checked_at": asyncio.get_event_loop().time()
        }
    
    async def get_contextual_tips(
        self,
        user_id: str,
        context: str
    ) -> Optional[str]:
        """
        Get contextual tips based on user location in app.
        
        Args:
            user_id: User ID
            context: Where user is (job_search, profile, coach, etc.)
            
        Returns:
            Contextual tip text or None
        """
        
        context_to_guidance = {
            "job_search": GuidanceType.APPLICATION_COACHING,
            "profile": GuidanceType.PROFILE_COMPLETION,
            "learning": GuidanceType.SKILL_DEVELOPMENT,
            "dashboard": GuidanceType.JOB_SEARCH_STRATEGY
        }
        
        guidance_type = context_to_guidance.get(context)
        if not guidance_type:
            return None
        
        intervention = await self.check_specific_need(user_id, guidance_type)
        
        return intervention["message"] if intervention else None
    
    # ==================== Continuous Monitoring (Future) ====================
    
    async def start_monitoring(
        self,
        check_interval_seconds: int = 3600
    ):
        """
        Start continuous monitoring (for background service).
        
        This would run as a background task checking users periodically.
        """
        
        self.is_monitoring = True
        logger.info("Started proactive coach monitoring")
        
        # This is a placeholder - in production, this would:
        # 1. Get list of active users from database
        # 2. Check each user periodically
        # 3. Queue interventions for delivery
        # 4. Handle delivery via notifications/emails/in-app
        
        while self.is_monitoring:
            try:
                # Placeholder - would check users here
                await asyncio.sleep(check_interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        logger.info("Stopped proactive coach monitoring")
    
    # ==================== Analytics ====================
    
    def get_intervention_stats(self) -> Dict:
        """Get statistics about interventions"""
        
        recent = self.intervention_engine.recent_interventions
        
        return {
            "total_users_receiving_guidance": len(set(
                key.split(":")[0] for key in recent.keys()
            )),
            "intervention_types_sent": len(recent),
            "recent_intervention_count": sum(len(v) for v in recent.values())
        }
