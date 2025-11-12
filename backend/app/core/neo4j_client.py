"""
Neo4j Talent Graph Client (Temporarily Disabled)

This module is temporarily stubbed to allow deployment.
Neo4j features will be re-enabled in a future update.
"""

from typing import List, Dict, Optional
import os
from loguru import logger


class Neo4jClient:
    """Neo4j client for Talent Graph queries (temporarily disabled for deployment)"""

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "next-career-password-2024")
        self.driver = None
        logger.warning("⚠️ Neo4j Talent Graph temporarily disabled")

    async def connect(self):
        """Initialize connection to Neo4j"""
        logger.warning("Neo4j connection skipped - feature temporarily disabled")
        return

    async def close(self):
        """Close Neo4j connection"""
        return

    async def health_check(self) -> bool:
        """Check if Neo4j is healthy"""
        return False

    async def create_user_node(self, user_id: str, profile: Dict) -> Dict:
        """Create or update user node in graph (stub)"""
        return {"user_id": user_id, "created": False, "message": "Neo4j temporarily disabled"}

    async def link_user_skills(self, user_id: str, skills: List[str]) -> int:
        """Create HAS_SKILL relationships for user (stub)"""
        return 0

    async def get_skill_gaps(self, user_id: str, target_role: str, target_seniority: str = "mid") -> List[Dict]:
        """Get skill gaps (stub)"""
        return []

    async def get_career_pathways(
        self, current_role: str, current_seniority: str, target_role: str, target_seniority: str, max_steps: int = 4
    ) -> List[Dict]:
        """Get career pathways (stub)"""
        return []

    async def get_related_skills(self, skill: str, radius: int = 2, limit: int = 10) -> List[Dict]:
        """Get related skills (stub)"""
        return []

    async def get_skill_market_data(self, skill: str) -> Optional[Dict]:
        """Get skill market data (stub)"""
        return {"skill": skill, "demand_score": 0, "growth_rate": 0, "salary_premium": 0}

    async def match_job_to_roles(self, required_skills: List[str]) -> List[Dict]:
        """Match job to roles (stub)"""
        return []

    async def get_graph_stats(self) -> Dict:
        """Get graph statistics (stub)"""
        return {"nodes": {}, "relationships": {}, "total_nodes": 0, "total_relationships": 0}


# Global instance
neo4j_client = Neo4jClient()
