"""
Task Automation Score (TAS) Calculator
Queries ai_task_taxonomy to calculate role-level automation risk.
"""

from typing import Tuple
import asyncpg
from ..cache import get_cache


class TaskAutomationCalculator:
    """
    Calculates TAS (Task Automation Score) from task-level automation evidence.
    
    Formula:
        TAS = Σ(TaskRisk_i × TaskImportance_i) / Σ(TaskImportance_i) × 100
    
    Where:
        - TaskRisk = technical_capability × economic_viability
        - TaskImportance = importance_score from O*NET
    """
    
    def __init__(self, db_connection):
        """
        Initialize calculator with database connection.
        
        Args:
            db_connection: asyncpg connection or pool
        """
        self.db = db_connection
        self.cache = get_cache()
    
    async def calculate(self, occupation_code: str) -> Tuple[float, float]:
        """
        Calculate TAS for a given occupation.
        
        Args:
            occupation_code: O*NET SOC code (e.g., "15-2051" for Software Developers)
        
        Returns:
            Tuple of (TAS score 0-100, TaskCoverage % 0-100)
            
        Example:
            >>> calculator = TaskAutomationCalculator(db)
            >>> tas, coverage = await calculator.calculate("15-2051")
            >>> print(f"TAS: {tas:.1f}, Coverage: {coverage:.1f}%")
            TAS: 68.2, Coverage: 85.0%
        """
        # Check cache first (1 hour TTL)
        cached = await self.cache.get_task_automation_scores(occupation_code)
        if cached:
            return cached['tas'], cached['coverage']
        
        # Query all tasks for this occupation
        query = """
            SELECT 
                task_risk,
                importance_score,
                confidence_level
            FROM public.ai_task_taxonomy
            WHERE occupation_code = $1
              AND importance_score IS NOT NULL
            ORDER BY importance_score DESC
        """
        
        try:
            rows = await self.db.fetch(query, occupation_code)
        except Exception as e:
            print(f"Error querying ai_task_taxonomy: {e}")
            # Return median with zero confidence on error
            return 50.0, 0.0
        
        if not rows or len(rows) == 0:
            # No data for this occupation: return median with low confidence
            # This signals to calling code that data is missing
            return 50.0, 0.0
        
        # Calculate weighted TAS
        numerator = 0.0
        denominator = 0.0
        
        for row in rows:
            task_risk = float(row['task_risk'])
            importance = float(row['importance_score'])
            
            numerator += task_risk * importance
            denominator += importance
        
        if denominator == 0:
            # Should not happen if importance_score IS NOT NULL, but defensive
            return 50.0, 0.0
        
        # Calculate TAS (0-1 scale from task_risk, converted to 0-100)
        tas = (numerator / denominator) * 100.0
        
        # Clamp to valid range
        tas = max(0.0, min(100.0, tas))
        
        # Calculate coverage (% of typical tasks we have data for)
        # O*NET has ~10-30 tasks per occupation, avg ~20
        # Coverage tells us how confident we are in the TAS
        expected_task_count = 20.0
        coverage = min(len(rows) / expected_task_count, 1.0) * 100.0
        
        # Cache the result (1 hour TTL)
        await self.cache.set_task_automation_scores(
            occupation_code,
            {'tas': tas, 'coverage': coverage}
        )
        
        return tas, coverage
    
    async def calculate_with_breakdown(self, occupation_code: str) -> dict:
        """
        Calculate TAS with detailed task-level breakdown.
        Useful for debugging or showing users which tasks contribute most.
        
        Returns:
            {
                "tas": float,
                "coverage": float,
                "task_count": int,
                "top_risk_tasks": [
                    {"name": str, "risk": float, "importance": float},
                    ...
                ]
            }
        """
        query = """
            SELECT 
                task_name,
                task_risk,
                importance_score,
                confidence_level
            FROM public.ai_task_taxonomy
            WHERE occupation_code = $1
              AND importance_score IS NOT NULL
            ORDER BY (task_risk * importance_score) DESC
            LIMIT 5
        """
        
        # Get TAS score
        tas, coverage = await self.calculate(occupation_code)
        
        # Get top risk tasks
        try:
            rows = await self.db.fetch(query, occupation_code)
            top_tasks = [
                {
                    "name": row['task_name'],
                    "risk": float(row['task_risk']),
                    "importance": float(row['importance_score'])
                }
                for row in rows
            ]
        except Exception:
            top_tasks = []
        
        return {
            "tas": round(tas, 1),
            "coverage": round(coverage, 1),
            "task_count": len(top_tasks),
            "top_risk_tasks": top_tasks
        }
