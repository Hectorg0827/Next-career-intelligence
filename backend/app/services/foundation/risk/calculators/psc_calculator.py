"""
Personal Skill Currency (PSC) Calculator
Measures the market value of a user's current skills.
"""

from typing import List, Tuple
import asyncpg
import math
from ..cache import get_cache


class SkillCurrencyCalculator:
    """
    Calculates PSC (Personal Skill Currency) from user skills and market data.
    
    Formula:
        PSC = Weighted Average of:
            - Demand Score (40%): Current market demand for skill
            - Trend Score (30%): Growth trajectory
            - Complementarity (20%): How well AI enhances this skill
            - Proficiency (10%): User's mastery level
    
    Adjusted by:
        - Recency: exp(-days_since_last_used / 365)
    """
    
    def __init__(self, db_connection):
        """
        Initialize calculator with database connection.
        
        Args:
            db_connection: asyncpg connection or pool
        """
        self.db = db_connection
        self.cache = get_cache()
    
    async def calculate(
        self,
        user_skills: List[dict],
        industry: str = "all"
    ) -> Tuple[float, float]:
        """
        Calculate PSC for a user's skill set.
        
        Args:
            user_skills: List of dicts with:
                {
                    "skill_name": str,
                    "proficiency": float (0-1),
                    "years_experience": float,
                    "last_used_days_ago": int
                }
            industry: Industry context for market data
        
        Returns:
            Tuple of (PSC score 0-100, SkillCoverage % 0-100)
            
        Example:
            >>> calculator = SkillCurrencyCalculator(db)
            >>> skills = [
            ...     {"skill_name": "Python", "proficiency": 0.85, 
            ...      "years_experience": 5, "last_used_days_ago": 30},
            ...     {"skill_name": "Machine Learning", "proficiency": 0.70,
            ...      "years_experience": 3, "last_used_days_ago": 15}
            ... ]
            >>> psc, coverage = await calculator.calculate(skills, "Technology")
            >>> print(f"PSC: {psc:.1f}, Coverage: {coverage:.1f}%")
            PSC: 68.5, Coverage: 100.0%
        """
        if not user_skills:
            return 0.0, 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        skills_with_data = 0
        
        for skill in user_skills:
            skill_name = skill.get("skill_name", "")
            proficiency = skill.get("proficiency", 0.5)
            years_exp = skill.get("years_experience", 0.0)
            days_ago = skill.get("last_used_days_ago", 0)
            
            # Get market data for this skill
            market_data = await self._get_skill_market_data(skill_name, industry)
            
            if not market_data:
                # No market data: use neutral score
                continue
            
            skills_with_data += 1
            
            # Calculate skill currency components
            demand = market_data.get("demand_score", 0.5)
            trend = (market_data.get("trend_score", 0.0) + 1.0) / 2.0  # Convert -1..1 to 0..1
            complementarity = market_data.get("complementarity", 0.5)
            
            # Weighted combination
            skill_value = (
                0.40 * demand +
                0.30 * trend +
                0.20 * complementarity +
                0.10 * proficiency
            )
            
            # Apply recency decay (skills rust over time)
            recency_factor = math.exp(-days_ago / 365.0)
            skill_value *= recency_factor
            
            # Weight by years of experience (more experience = more weight)
            experience_weight = min(years_exp / 10.0, 1.0)  # Cap at 10 years
            
            total_weighted_score += skill_value * experience_weight
            total_weight += experience_weight
        
        if total_weight == 0:
            return 0.0, 0.0
        
        # Calculate PSC (0-1 scale, convert to 0-100)
        psc = (total_weighted_score / total_weight) * 100.0
        psc = max(0.0, min(100.0, psc))
        
        # Coverage (% of skills we have market data for)
        coverage = (skills_with_data / len(user_skills)) * 100.0
        
        return psc, coverage
    
    async def _get_skill_market_data(self, skill_name: str, industry: str) -> dict:
        """
        Get market data for a specific skill.
        
        Returns dict with:
            - demand_score
            - trend_score
            - complementarity
        """
        # Check cache first (1 hour TTL)
        cached = await self.cache.get_skill_demand_data(skill_name, industry)
        if cached:
            return cached
        
        query = """
            SELECT 
                demand_score,
                trend_score
            FROM public.skill_demand_history
            WHERE skill_name = $1
              AND (industry = $2 OR industry = 'all')
              AND snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY snapshot_date DESC
            LIMIT 1
        """
        
        try:
            row = await self.db.fetchrow(query, skill_name, industry)
            if not row:
                return {}
            
            # Get complementarity from automation_evidence
            comp_query = """
                SELECT complementarity
                FROM public.automation_evidence
                WHERE entity_type = 'skill'
                  AND entity_id = $1
                ORDER BY updated_at DESC
                LIMIT 1
            """
            comp_row = await self.db.fetchrow(comp_query, skill_name)
            
            result = {
                "demand_score": float(row['demand_score']),
                "trend_score": float(row['trend_score'] or 0.0),
                "complementarity": float(comp_row['complementarity']) if comp_row else 0.5
            }
            
            # Cache the result (1 hour TTL)
            await self.cache.set_skill_demand_data(skill_name, industry, result)
            
            return result
        except Exception as e:
            print(f"Error getting market data for {skill_name}: {e}")
            return {}
    
    async def calculate_with_breakdown(
        self,
        user_skills: List[dict],
        industry: str = "all"
    ) -> dict:
        """
        Calculate PSC with per-skill breakdown.
        
        Returns:
            {
                "psc": float,
                "coverage": float,
                "skill_breakdown": [
                    {
                        "name": str,
                        "value": float,
                        "demand": float,
                        "trend": float,
                        "proficiency": float
                    },
                    ...
                ]
            }
        """
        psc, coverage = await self.calculate(user_skills, industry)
        
        # Get breakdown for each skill
        breakdown = []
        for skill in user_skills:
            market_data = await self._get_skill_market_data(
                skill.get("skill_name", ""),
                industry
            )
            
            if market_data:
                demand = market_data.get("demand_score", 0.5)
                trend = market_data.get("trend_score", 0.0)
                complementarity = market_data.get("complementarity", 0.5)
                proficiency = skill.get("proficiency", 0.5)
                
                skill_value = (
                    0.40 * demand +
                    0.30 * (trend + 1.0) / 2.0 +
                    0.20 * complementarity +
                    0.10 * proficiency
                ) * 100.0
                
                breakdown.append({
                    "name": skill.get("skill_name", ""),
                    "value": round(skill_value, 1),
                    "demand": round(demand * 100, 1),
                    "trend": round(trend * 100, 1),
                    "proficiency": round(proficiency * 100, 1)
                })
        
        # Sort by value descending
        breakdown.sort(key=lambda x: x['value'], reverse=True)
        
        return {
            "psc": round(psc, 1),
            "coverage": round(coverage, 1),
            "skill_breakdown": breakdown
        }
