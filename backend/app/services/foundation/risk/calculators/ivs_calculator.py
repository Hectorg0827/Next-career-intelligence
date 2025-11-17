"""
Industry Velocity Score (IVS) Calculator
Measures the speed of AI adoption in an industry based on job posting trends.
"""

from typing import Tuple
import asyncpg


class IndustryVelocityCalculator:
    """
    Calculates IVS (Industry Velocity Score) from market trends.
    
    Formula:
        IVS = 0.5 × AI_Job_Growth + 0.5 × Legacy_Job_Decline
    
    Where:
        - AI_Job_Growth = % growth in AI-related jobs (normalized 0-100)
        - Legacy_Job_Decline = % decline in non-AI jobs (normalized 0-100)
    """
    
    def __init__(self, db_connection):
        """
        Initialize calculator with database connection.
        
        Args:
            db_connection: asyncpg connection or pool
        """
        self.db = db_connection
    
    async def calculate(self, industry: str) -> Tuple[float, float]:
        """
        Calculate IVS for a given industry.
        
        Args:
            industry: Industry name (e.g., "Technology", "Finance", "Healthcare")
        
        Returns:
            Tuple of (IVS score 0-100, PostingDensity % 0-100)
            
        Example:
            >>> calculator = IndustryVelocityCalculator(db)
            >>> ivs, density = await calculator.calculate("Technology")
            >>> print(f"IVS: {ivs:.1f}, Density: {density:.1f}%")
            IVS: 72.5, Density: 90.0%
        """
        # Query skill demand history for this industry
        # Look at latest 365-day trends
        query = """
            WITH latest_data AS (
                SELECT 
                    skill_name,
                    ai_job_postings,
                    legacy_job_postings,
                    job_posting_growth_365d,
                    trend_score,
                    snapshot_date
                FROM public.skill_demand_history
                WHERE industry = $1
                  AND snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY snapshot_date DESC
            )
            SELECT 
                AVG(CASE 
                    WHEN ai_job_postings > 0 THEN 
                        LEAST(job_posting_growth_365d / 100.0, 1.0)
                    ELSE 0
                END) as avg_ai_growth,
                AVG(CASE 
                    WHEN legacy_job_postings > 0 AND ai_job_postings = 0 THEN 
                        GREATEST(-1.0 * job_posting_growth_365d / 100.0, 0.0)
                    ELSE 0
                END) as avg_legacy_decline,
                AVG(trend_score) as avg_trend,
                COUNT(DISTINCT skill_name) as skill_count
            FROM latest_data
        """
        
        try:
            row = await self.db.fetchrow(query, industry)
        except Exception as e:
            print(f"Error querying skill_demand_history: {e}")
            return 50.0, 0.0
        
        if not row or row['skill_count'] == 0:
            # No data for this industry: return median with low confidence
            return 50.0, 0.0
        
        # Extract values
        ai_growth = float(row['avg_ai_growth'] or 0.0)
        legacy_decline = float(row['avg_legacy_decline'] or 0.0)
        skill_count = int(row['skill_count'])
        
        # Calculate IVS (0-1 scale, convert to 0-100)
        # Higher AI growth + higher legacy decline = higher velocity
        ivs = (0.5 * ai_growth + 0.5 * legacy_decline) * 100.0
        
        # Clamp to valid range
        ivs = max(0.0, min(100.0, ivs))
        
        # Posting density (how much data coverage we have)
        # More skills tracked = higher confidence
        expected_skill_count = 50.0  # Target: 50+ skills per industry
        density = min(skill_count / expected_skill_count, 1.0) * 100.0
        
        return ivs, density
    
    async def calculate_with_breakdown(self, industry: str) -> dict:
        """
        Calculate IVS with detailed breakdown by skill category.
        
        Returns:
            {
                "ivs": float,
                "density": float,
                "ai_job_growth": float,
                "legacy_job_decline": float,
                "top_growing_skills": [
                    {"name": str, "growth": float, "ai_postings": int},
                    ...
                ]
            }
        """
        # Get IVS score
        ivs, density = await self.calculate(industry)
        
        # Get top growing AI skills
        query = """
            SELECT 
                skill_name,
                job_posting_growth_365d,
                ai_job_postings,
                trend_score
            FROM public.skill_demand_history
            WHERE industry = $1
              AND snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
              AND ai_job_postings > 0
            ORDER BY job_posting_growth_365d DESC
            LIMIT 5
        """
        
        try:
            rows = await self.db.fetch(query, industry)
            top_skills = [
                {
                    "name": row['skill_name'],
                    "growth": float(row['job_posting_growth_365d'] or 0.0),
                    "ai_postings": int(row['ai_job_postings'] or 0),
                    "trend": float(row['trend_score'] or 0.0)
                }
                for row in rows
            ]
        except Exception:
            top_skills = []
        
        # Calculate components
        ai_growth = sum(s['growth'] for s in top_skills) / len(top_skills) if top_skills else 0.0
        
        return {
            "ivs": round(ivs, 1),
            "density": round(density, 1),
            "ai_job_growth": round(ai_growth, 1),
            "legacy_job_decline": round(100.0 - ivs, 1),  # Inverse approximation
            "top_growing_skills": top_skills
        }
