"""
Neo4j Talent Graph Client

Connects to Neo4j graph database for career intelligence queries:
- Skill gap analysis
- Career pathway discovery
- Skill relationship mapping
- Job-to-role matching
"""

from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import List, Dict, Optional
import os
from loguru import logger


class Neo4jClient:
    """Async Neo4j client for Talent Graph queries"""

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "next-career-password-2024")
        self.driver: Optional[AsyncDriver] = None

    async def connect(self):
        """Initialize connection to Neo4j"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )

            # Verify connectivity
            await self.driver.verify_connectivity()
            logger.info(f"✅ Connected to Neo4j Talent Graph at {self.uri}")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

    async def health_check(self) -> bool:
        """Check if Neo4j is healthy"""
        try:
            if not self.driver:
                return False

            async with self.driver.session() as session:
                result = await session.run("RETURN 1")
                await result.single()
                return True

        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

    # ========================================
    # User Node Management
    # ========================================

    async def create_user_node(self, user_id: str, profile: Dict) -> Dict:
        """
        Create or update user node in graph

        Args:
            user_id: User UUID
            profile: User profile data (current_role, experience_years, skills, etc.)

        Returns:
            Dict with created node info
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MERGE (u:User {user_id: $user_id})
                    SET u.current_role = $current_role,
                        u.experience_years = $experience_years,
                        u.location = $location,
                        u.updated_at = datetime()
                    RETURN u
                    """,
                    user_id=user_id,
                    current_role=profile.get("current_role"),
                    experience_years=profile.get("experience_years", 0),
                    location=profile.get("location", "Remote")
                )

                record = await result.single()
                logger.info(f"Created/updated user node: {user_id}")

                return {
                    "user_id": user_id,
                    "created": True
                }

        except Exception as e:
            logger.error(f"Failed to create user node: {e}")
            raise

    async def link_user_skills(self, user_id: str, skills: List[str]) -> int:
        """
        Create HAS_SKILL relationships for user

        Args:
            user_id: User UUID
            skills: List of skill names

        Returns:
            Number of skills linked
        """
        try:
            async with self.driver.session() as session:
                linked_count = 0

                for skill in skills:
                    await session.run(
                        """
                        MATCH (u:User {user_id: $user_id})
                        MERGE (s:Skill {name: $skill_name})
                        MERGE (u)-[r:HAS_SKILL]->(s)
                        SET r.acquired_at = datetime(),
                            r.proficiency = 'intermediate'
                        """,
                        user_id=user_id,
                        skill_name=skill
                    )
                    linked_count += 1

                logger.info(f"Linked {linked_count} skills for user {user_id}")
                return linked_count

        except Exception as e:
            logger.error(f"Failed to link user skills: {e}")
            raise

    # ========================================
    # Skill Gap Analysis
    # ========================================

    async def get_skill_gaps(
        self,
        user_id: str,
        target_role: str,
        target_seniority: str = "mid"
    ) -> List[Dict]:
        """
        Find skills user needs to acquire for target role

        Args:
            user_id: User UUID
            target_role: Desired job title (e.g., "Software Engineer")
            target_seniority: Target seniority level (entry/mid/senior/staff)

        Returns:
            List of skill gaps with importance and required proficiency
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (u:User {user_id: $user_id})
                    MATCH (target:Role {title: $target_role, seniority: $target_seniority})
                    MATCH (target)-[req:REQUIRES_SKILL]->(s:Skill)
                    WHERE NOT (u)-[:HAS_SKILL]->(s)
                    RETURN s.name AS skill,
                           s.category AS category,
                           s.demand_score AS demand_score,
                           s.avg_salary_premium AS salary_premium,
                           s.learning_curve AS learning_curve,
                           req.importance AS importance,
                           req.proficiency AS required_level,
                           req.substitutable AS substitutable
                    ORDER BY req.importance DESC, s.demand_score DESC
                    """,
                    user_id=user_id,
                    target_role=target_role,
                    target_seniority=target_seniority
                )

                gaps = []
                async for record in result:
                    gaps.append({
                        "skill": record["skill"],
                        "category": record["category"],
                        "demand_score": record["demand_score"],
                        "salary_premium": record["salary_premium"],
                        "learning_curve": record["learning_curve"],
                        "importance": record["importance"],
                        "required_level": record["required_level"],
                        "substitutable": record["substitutable"]
                    })

                logger.info(f"Found {len(gaps)} skill gaps for user {user_id} → {target_role}")
                return gaps

        except Exception as e:
            logger.error(f"Failed to get skill gaps: {e}")
            return []

    # ========================================
    # Career Pathways
    # ========================================

    async def get_career_pathways(
        self,
        current_role: str,
        current_seniority: str,
        target_role: str,
        target_seniority: str,
        max_steps: int = 4
    ) -> List[Dict]:
        """
        Find possible career paths from current to target role

        Args:
            current_role: Current job title
            current_seniority: Current seniority level
            target_role: Target job title
            target_seniority: Target seniority level
            max_steps: Maximum number of intermediate steps

        Returns:
            List of pathways with roles, years, and success rates
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH path = shortestPath(
                        (start:Role {title: $current_role, seniority: $current_seniority})
                        -[:PATHWAY_TO*..4]->
                        (end:Role {title: $target_role, seniority: $target_seniority})
                    )
                    WITH path,
                         [node in nodes(path) | node.title + ' (' + node.seniority + ')'] AS pathway_roles,
                         [rel in relationships(path) | rel.typical_years] AS years,
                         reduce(rate = 1.0, rel in relationships(path) | rate * rel.success_rate) AS success_rate
                    RETURN pathway_roles,
                           years,
                           success_rate,
                           reduce(total = 0, y in years | total + y) AS total_years
                    ORDER BY success_rate DESC, total_years ASC
                    LIMIT 5
                    """,
                    current_role=current_role,
                    current_seniority=current_seniority,
                    target_role=target_role,
                    target_seniority=target_seniority
                )

                pathways = []
                async for record in result:
                    pathways.append({
                        "roles": record["pathway_roles"],
                        "years_per_step": record["years"],
                        "total_years": record["total_years"],
                        "success_rate": record["success_rate"],
                        "difficulty": self._calculate_difficulty(record["success_rate"])
                    })

                logger.info(f"Found {len(pathways)} pathways from {current_role} to {target_role}")
                return pathways

        except Exception as e:
            logger.error(f"Failed to get career pathways: {e}")
            return []

    def _calculate_difficulty(self, success_rate: float) -> str:
        """Calculate difficulty label from success rate"""
        if success_rate >= 0.7:
            return "achievable"
        elif success_rate >= 0.5:
            return "challenging"
        elif success_rate >= 0.3:
            return "difficult"
        else:
            return "very_difficult"

    # ========================================
    # Skill Relationships
    # ========================================

    async def get_related_skills(
        self,
        skill: str,
        radius: int = 2,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find skills commonly learned together with given skill

        Args:
            skill: Skill name
            radius: Graph traversal depth (1-3)
            limit: Max number of related skills

        Returns:
            List of related skills with pairing frequency and synergy
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (s:Skill {name: $skill})-[r:OFTEN_PAIRED_WITH*1..2]-(related:Skill)
                    WITH DISTINCT related,
                         avg(r.frequency) AS avg_frequency,
                         avg(r.synergy_score) AS avg_synergy
                    RETURN related.name AS skill,
                           related.category AS category,
                           related.demand_score AS demand,
                           related.growth_rate AS growth,
                           avg_frequency AS pairing_frequency,
                           avg_synergy AS synergy_score
                    ORDER BY avg_frequency DESC, demand DESC
                    LIMIT $limit
                    """,
                    skill=skill,
                    limit=limit
                )

                related = []
                async for record in result:
                    related.append({
                        "skill": record["skill"],
                        "category": record["category"],
                        "demand_score": record["demand"],
                        "growth_rate": record["growth"],
                        "pairing_frequency": record["pairing_frequency"],
                        "synergy_score": record["synergy_score"]
                    })

                logger.info(f"Found {len(related)} skills related to {skill}")
                return related

        except Exception as e:
            logger.error(f"Failed to get related skills: {e}")
            return []

    # ========================================
    # Job Matching
    # ========================================

    async def match_job_to_roles(self, required_skills: List[str]) -> List[Dict]:
        """
        Find roles that match a set of skills (for job postings)

        Args:
            required_skills: List of skill names from job description

        Returns:
            List of matching roles with match scores
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (r:Role)-[req:REQUIRES_SKILL]->(s:Skill)
                    WHERE s.name IN $required_skills
                    WITH r,
                         count(s) AS matched_skills,
                         collect(s.name) AS matched_skill_names,
                         avg(req.importance) AS avg_importance
                    RETURN r.title AS role,
                           r.seniority AS seniority,
                           r.avg_salary AS avg_salary,
                           matched_skills,
                           matched_skill_names,
                           avg_importance
                    ORDER BY matched_skills DESC, avg_importance DESC
                    LIMIT 5
                    """,
                    required_skills=required_skills
                )

                matches = []
                async for record in result:
                    matches.append({
                        "role": record["role"],
                        "seniority": record["seniority"],
                        "avg_salary": record["avg_salary"],
                        "matched_skills": record["matched_skills"],
                        "matched_skill_names": record["matched_skill_names"],
                        "match_score": record["avg_importance"]
                    })

                logger.info(f"Found {len(matches)} role matches for {len(required_skills)} skills")
                return matches

        except Exception as e:
            logger.error(f"Failed to match job to roles: {e}")
            return []

    # ========================================
    # Analytics & Insights
    # ========================================

    async def get_skill_market_data(self, skill: str) -> Optional[Dict]:
        """
        Get market intelligence for a skill

        Args:
            skill: Skill name

        Returns:
            Market data (demand, growth, salary premium, etc.)
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (s:Skill {name: $skill})
                    OPTIONAL MATCH (r:Role)-[req:REQUIRES_SKILL]->(s)
                    WITH s, count(r) AS roles_requiring
                    RETURN s.name AS skill,
                           s.category AS category,
                           s.demand_score AS demand_score,
                           s.growth_rate AS growth_rate,
                           s.avg_salary_premium AS salary_premium,
                           s.automation_risk AS automation_risk,
                           s.learning_curve AS learning_curve,
                           roles_requiring
                    """,
                    skill=skill
                )

                record = await result.single()

                if not record:
                    return None

                return {
                    "skill": record["skill"],
                    "category": record["category"],
                    "demand_score": record["demand_score"],
                    "growth_rate": record["growth_rate"],
                    "salary_premium": record["salary_premium"],
                    "automation_risk": record["automation_risk"],
                    "learning_curve": record["learning_curve"],
                    "roles_requiring": record["roles_requiring"]
                }

        except Exception as e:
            logger.error(f"Failed to get skill market data: {e}")
            return None

    async def get_graph_stats(self) -> Dict:
        """
        Get overall graph statistics

        Returns:
            Node and relationship counts
        """
        try:
            async with self.driver.session() as session:
                # Count nodes
                node_result = await session.run(
                    """
                    MATCH (n)
                    RETURN labels(n)[0] AS label, count(n) AS count
                    """
                )

                nodes = {}
                async for record in node_result:
                    nodes[record["label"]] = record["count"]

                # Count relationships
                rel_result = await session.run(
                    """
                    MATCH ()-[r]->()
                    RETURN type(r) AS type, count(r) AS count
                    """
                )

                relationships = {}
                async for record in rel_result:
                    relationships[record["type"]] = record["count"]

                return {
                    "nodes": nodes,
                    "relationships": relationships,
                    "total_nodes": sum(nodes.values()),
                    "total_relationships": sum(relationships.values())
                }

        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {}


# Global instance
neo4j_client = Neo4jClient()
