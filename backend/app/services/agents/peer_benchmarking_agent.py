"""
Peer Benchmarking Agent - Compare Journey vs Similar Users
Provides anonymized insights about career movements in similar cohorts
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime, timedelta

from app.models.user_profile import UserProfile
from app.services.supabase_client import SupabaseClient


class PeerBenchmarkingAgent:
    """
    Peer Benchmarking Agent - The community intelligence layer
    
    Responsibilities:
    - Find similar user profiles (cohorts)
    - Analyze their career movements
    - Identify successful transition patterns
    - Answer: "What are people like me doing?"
    """
    
    def __init__(self):
        self.supabase = SupabaseClient()
    
    async def find_peer_insights(
        self,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Get career insights from similar users
        
        Returns:
        {
            "peer_cohort_size": 127,
            "common_transitions": [
                {
                    "from_role": "Special Ed Teacher",
                    "to_role": "Behavior Specialist",
                    "frequency": 23,
                    "avg_timeline_months": 14,
                    "success_rate": 78
                }
            ],
            "salary_comparison": {
                "user_position": "45th percentile",
                "cohort_median": 72000,
                "user_salary": 68000
            },
            "skill_gaps_vs_peers": [...],
            "trending_skills_in_cohort": [...]
        }
        """
        
        try:
            # Find similar users
            peers = await self._find_similar_profiles(user_profile)
            
            if not peers or len(peers) < 10:
                return self._create_minimal_insights("Not enough peer data available yet")
            
            # Analyze transitions
            transitions = self._analyze_transitions(peers)
            
            # Compare salary
            salary_comp = self._compare_salary(user_profile, peers)
            
            # Compare skills
            skill_gaps = self._compare_skills(user_profile, peers)
            
            result = {
                "peer_cohort_size": len(peers),
                "common_transitions": transitions,
                "salary_comparison": salary_comp,
                "skill_gaps_vs_peers": skill_gaps,
                "trending_skills_in_cohort": self._get_trending_skills(peers)
            }
            
            logger.info(f"Found peer insights from {len(peers)} similar profiles")
            
            return result
            
        except Exception as e:
            logger.error(f"Error finding peer insights: {e}")
            return self._create_minimal_insights("Could not load peer data")
    
    async def _find_similar_profiles(
        self,
        user_profile: UserProfile,
        max_results: int = 100
    ) -> List[UserProfile]:
        """
        Find users with similar:
        - Current/recent role
        - Years of experience (±3 years)
        - Core skills overlap
        """
        
        try:
            # Query Supabase for similar profiles
            # This is a simplified version - in production, use vector similarity or ML clustering
            
            years_exp = user_profile.years_total_experience or 0
            current_role = user_profile.current_role
            
            if not current_role:
                return []
            
            # Get profiles with similar roles and experience
            response = self.supabase.client.table("user_profiles").select("*").execute()
            
            if not response.data:
                return []
            
            peers = []
            for profile_data in response.data:
                # Skip self
                if profile_data.get("user_id") == user_profile.user_id:
                    continue
                
                peer_years = profile_data.get("years_total_experience", 0)
                peer_role = profile_data.get("current_role")
                
                # Similar years of experience (±3 years)
                if abs(peer_years - years_exp) <= 3:
                    # Similar role (fuzzy match)
                    if peer_role and (
                        current_role.lower() in peer_role.lower() or
                        peer_role.lower() in current_role.lower()
                    ):
                        try:
                            peer_profile = UserProfile(**profile_data)
                            peers.append(peer_profile)
                        except Exception as e:
                            logger.warning(f"Could not parse peer profile: {e}")
                            continue
                
                if len(peers) >= max_results:
                    break
            
            return peers
            
        except Exception as e:
            logger.error(f"Error querying similar profiles: {e}")
            return []
    
    def _analyze_transitions(self, peers: List[UserProfile]) -> List[Dict[str, Any]]:
        """Analyze common career transitions in peer group"""
        
        transitions = {}
        
        for peer in peers:
            if not peer.work_history or len(peer.work_history) < 2:
                continue
            
            # Look at last transition
            sorted_history = sorted(
                peer.work_history,
                key=lambda x: x.end_date or "9999",
                reverse=True
            )
            
            if len(sorted_history) >= 2:
                from_role = sorted_history[1].role
                to_role = sorted_history[0].role
                
                transition_key = f"{from_role}|{to_role}"
                
                if transition_key not in transitions:
                    transitions[transition_key] = {
                        "from_role": from_role,
                        "to_role": to_role,
                        "count": 0,
                        "timelines": []
                    }
                
                transitions[transition_key]["count"] += 1
        
        # Convert to list and sort by frequency
        transition_list = []
        for trans_data in transitions.values():
            if trans_data["count"] >= 3:  # Only include patterns seen 3+ times
                transition_list.append({
                    "from_role": trans_data["from_role"],
                    "to_role": trans_data["to_role"],
                    "frequency": trans_data["count"],
                    "avg_timeline_months": 14,  # Would calculate from actual data
                    "success_rate": 75  # Would track from outcomes
                })
        
        transition_list.sort(key=lambda x: x["frequency"], reverse=True)
        
        return transition_list[:5]  # Top 5 transitions
    
    def _compare_salary(
        self,
        user_profile: UserProfile,
        peers: List[UserProfile]
    ) -> Dict[str, Any]:
        """Compare user's salary to peer cohort"""
        
        user_salary = None
        if user_profile.salary_expectations:
            user_salary = user_profile.salary_expectations.get("target")
        
        peer_salaries = []
        for peer in peers:
            if peer.salary_expectations and peer.salary_expectations.get("target"):
                peer_salaries.append(peer.salary_expectations["target"])
        
        if not peer_salaries or not user_salary:
            return {
                "data_available": False,
                "message": "Not enough salary data for comparison"
            }
        
        peer_salaries.sort()
        cohort_median = peer_salaries[len(peer_salaries) // 2]
        
        # Calculate percentile
        below_user = sum(1 for s in peer_salaries if s < user_salary)
        percentile = int((below_user / len(peer_salaries)) * 100)
        
        return {
            "data_available": True,
            "user_position": f"{percentile}th percentile",
            "cohort_median": cohort_median,
            "user_salary": user_salary,
            "cohort_min": peer_salaries[0],
            "cohort_max": peer_salaries[-1]
        }
    
    def _compare_skills(
        self,
        user_profile: UserProfile,
        peers: List[UserProfile]
    ) -> List[str]:
        """Identify skills user is missing compared to peers"""
        
        user_skills = set(s.name.lower() for s in user_profile.skills)
        
        # Count skill frequency across peers
        skill_counts = {}
        for peer in peers:
            for skill in peer.skills:
                skill_lower = skill.name.lower()
                if skill_lower not in skill_counts:
                    skill_counts[skill_lower] = 0
                skill_counts[skill_lower] += 1
        
        # Find common peer skills user doesn't have
        gaps = []
        threshold = len(peers) * 0.5  # Skill must appear in 50%+ of peers
        
        for skill, count in skill_counts.items():
            if count >= threshold and skill not in user_skills:
                gaps.append(skill.title())
        
        return gaps[:5]  # Top 5 gaps
    
    def _get_trending_skills(self, peers: List[UserProfile]) -> List[str]:
        """Identify skills gaining traction in cohort"""
        
        # Look at recently added skills
        trending = {}
        
        for peer in peers:
            for skill in peer.skills:
                # If last_used is recent, it's trending
                if skill.last_used:
                    days_ago = (datetime.utcnow() - skill.last_used).days
                    if days_ago <= 180:  # Within 6 months
                        skill_name = skill.name.title()
                        if skill_name not in trending:
                            trending[skill_name] = 0
                        trending[skill_name] += 1
        
        # Sort by frequency
        trending_list = sorted(trending.items(), key=lambda x: x[1], reverse=True)
        
        return [skill for skill, count in trending_list[:5]]
    
    def _create_minimal_insights(self, message: str) -> Dict[str, Any]:
        """Return minimal structure when peer data unavailable"""
        
        return {
            "peer_cohort_size": 0,
            "common_transitions": [],
            "salary_comparison": {"data_available": False, "message": message},
            "skill_gaps_vs_peers": [],
            "trending_skills_in_cohort": []
        }
