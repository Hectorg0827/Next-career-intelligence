"""
Adaptability Score (AS) Calculator
Measures a user's learning velocity and adaptation to AI.
"""

from typing import List, Tuple
import asyncpg
import math


class AdaptabilityCalculator:
    """
    Calculates AS (Adaptability Score) from user learning actions.
    
    Formula:
        AS = Σ(BasePoints × QualityMultiplier × RecencyDecay)
    
    Where:
        - BasePoints: 8-15 points per action (course=10, project=12, cert=15)
        - QualityMultiplier: 1.0-2.0 (verified certificate=2.0x, portfolio project=1.5x)
        - RecencyDecay: exp(-days_ago / 120) [half-life of 120 days]
    """
    
    # Base point values for different action types
    BASE_POINTS = {
        "course": 10,
        "certification": 15,
        "project": 12,
        "publication": 8,
        "assessment": 5,
        "mentor_session": 8
    }
    
    def __init__(self, db_connection):
        """
        Initialize calculator with database connection.
        
        Args:
            db_connection: asyncpg connection or pool
        """
        self.db = db_connection
    
    async def calculate(self, user_id: str) -> Tuple[float, int]:
        """
        Calculate AS for a user based on their action log.
        
        Args:
            user_id: User ID to calculate adaptability for
        
        Returns:
            Tuple of (AS score 0-100, action_count)
            
        Example:
            >>> calculator = AdaptabilityCalculator(db)
            >>> adaptability, count = await calculator.calculate("user_123")
            >>> print(f"AS: {adaptability:.1f}, Actions: {count}")
            AS: 42.5, Actions: 8
        """
        # Query user actions from the last 365 days
        query = """
            SELECT 
                action_type,
                linked_skills,
                has_certificate,
                has_verified_project,
                completed_at,
                EXTRACT(DAY FROM NOW() - completed_at) as days_ago
            FROM public.user_action_log
            WHERE user_id = $1
              AND completed_at >= NOW() - INTERVAL '365 days'
            ORDER BY completed_at DESC
        """
        
        try:
            rows = await self.db.fetch(query, user_id)
        except Exception as e:
            print(f"Error querying user_action_log: {e}")
            return 0.0, 0
        
        if not rows:
            return 0.0, 0
        
        total_score = 0.0
        
        for row in rows:
            action_type = row['action_type']
            has_cert = row['has_certificate']
            has_project = row['has_verified_project']
            days_ago = float(row['days_ago'])
            
            # Get base points for action type
            base_points = self.BASE_POINTS.get(action_type, 5)
            
            # Calculate quality multiplier
            quality_multiplier = 1.0
            if has_cert:
                quality_multiplier = 2.0  # Verified certificate doubles value
            elif has_project:
                quality_multiplier = 1.5  # Portfolio project adds 50%
            
            # Apply recency decay (half-life of 120 days)
            # exp(-days/120): 120 days ago = 0.37x, 240 days = 0.14x
            recency_factor = math.exp(-days_ago / 120.0)
            
            # Calculate action score
            action_score = base_points * quality_multiplier * recency_factor
            total_score += action_score
        
        # Normalize to 0-100 scale
        # Assume 50 points in 90 days = high adaptability (100)
        # 0 points = 0 adaptability
        # This scales linearly
        max_expected_score = 50.0  # Calibration: 50 points = 100% adaptability
        adaptability = min(total_score / max_expected_score, 1.0) * 100.0
        
        return adaptability, len(rows)
    
    async def calculate_with_breakdown(self, user_id: str) -> dict:
        """
        Calculate AS with detailed action breakdown.
        
        Returns:
            {
                "adaptability": float,
                "action_count": int,
                "recent_actions": [
                    {
                        "type": str,
                        "skills": List[str],
                        "score": float,
                        "days_ago": int
                    },
                    ...
                ],
                "learning_velocity": str  # "high", "medium", "low"
            }
        """
        adaptability, action_count = await self.calculate(user_id)
        
        # Get detailed action breakdown
        query = """
            SELECT 
                action_type,
                linked_skills,
                has_certificate,
                has_verified_project,
                completed_at,
                EXTRACT(DAY FROM NOW() - completed_at) as days_ago
            FROM public.user_action_log
            WHERE user_id = $1
              AND completed_at >= NOW() - INTERVAL '365 days'
            ORDER BY completed_at DESC
            LIMIT 10
        """
        
        try:
            rows = await self.db.fetch(query, user_id)
            
            recent_actions = []
            for row in rows:
                action_type = row['action_type']
                days_ago = int(row['days_ago'])
                has_cert = row['has_certificate']
                has_project = row['has_verified_project']
                
                # Calculate action score
                base_points = self.BASE_POINTS.get(action_type, 5)
                quality_multiplier = 2.0 if has_cert else (1.5 if has_project else 1.0)
                recency_factor = math.exp(-days_ago / 120.0)
                action_score = base_points * quality_multiplier * recency_factor
                
                recent_actions.append({
                    "type": action_type,
                    "skills": row['linked_skills'] or [],
                    "score": round(action_score, 1),
                    "days_ago": days_ago,
                    "has_certificate": has_cert,
                    "has_project": has_project
                })
        except Exception:
            recent_actions = []
        
        # Determine learning velocity
        if adaptability >= 70:
            velocity = "high"
        elif adaptability >= 40:
            velocity = "medium"
        else:
            velocity = "low"
        
        # Calculate actions in last 90 days
        recent_count = sum(1 for a in recent_actions if a['days_ago'] <= 90)
        
        return {
            "adaptability": round(adaptability, 1),
            "action_count": action_count,
            "recent_actions_90d": recent_count,
            "recent_actions": recent_actions,
            "learning_velocity": velocity
        }
    
    async def log_action(
        self,
        user_id: str,
        action_type: str,
        linked_skills: List[str] = None,
        has_certificate: bool = False,
        has_verified_project: bool = False
    ) -> bool:
        """
        Log a new user learning action.
        
        Args:
            user_id: User ID
            action_type: Type of action (course, project, certification, etc.)
            linked_skills: List of skill names this action develops
            has_certificate: Whether user earned a verified certificate
            has_verified_project: Whether user created a portfolio project
        
        Returns:
            True if logged successfully
        """
        query = """
            INSERT INTO public.user_action_log (
                user_id,
                action_type,
                linked_skills,
                has_certificate,
                has_verified_project,
                completed_at
            ) VALUES ($1, $2, $3, $4, $5, NOW())
        """
        
        try:
            await self.db.execute(
                query,
                user_id,
                action_type,
                linked_skills or [],
                has_certificate,
                has_verified_project
            )
            return True
        except Exception as e:
            print(f"Error logging action: {e}")
            return False
