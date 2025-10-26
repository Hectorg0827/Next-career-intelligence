"""
Peer Benchmarking Agent - Comparative Career Analytics
Compares user's progress against industry peers and standards
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai
from datetime import datetime

from app.core.config import settings
from app.models.user_profile import UserProfile


class PeerBenchmarkingAgent:
    """
    Peer Benchmarking Agent - The comparator
    
    Responsibilities:
    - Compare user progress vs peers at same career stage
    - Benchmark skills, salary, title progression
    - Identify where user is ahead/behind typical trajectory
    - Provide percentile rankings across key metrics
    - Answer: "How am I doing compared to my peers?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_benchmark_report(
        self,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Generate comprehensive peer benchmarking report
        
        Returns multi-dimensional comparison across career metrics
        """
        try:
            # Get peer cohort definition
            cohort = self._define_peer_cohort(user_profile)
            
            # Benchmark across dimensions
            salary_benchmark = await self._benchmark_salary(user_profile, cohort)
            skills_benchmark = await self._benchmark_skills(user_profile, cohort)
            progression_benchmark = await self._benchmark_progression(user_profile, cohort)
            
            # Calculate overall percentile
            overall_percentile = self._calculate_overall_percentile([
                salary_benchmark.get("percentile", 50),
                skills_benchmark.get("percentile", 50),
                progression_benchmark.get("percentile", 50)
            ])
            
            return {
                "peer_cohort": cohort,
                "overall_percentile": overall_percentile,
                "overall_rating": self._percentile_to_rating(overall_percentile),
                "salary_comparison": salary_benchmark,
                "skills_comparison": skills_benchmark,
                "progression_comparison": progression_benchmark,
                "strengths": self._identify_strengths(
                    salary_benchmark, skills_benchmark, progression_benchmark
                ),
                "improvement_areas": self._identify_gaps(
                    salary_benchmark, skills_benchmark, progression_benchmark
                ),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Benchmark report generation failed: {e}")
            return self._get_fallback_benchmark()
    
    async def _benchmark_salary(
        self,
        user_profile: UserProfile,
        cohort: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Benchmark salary against peers"""
        try:
            # Get typical salary range for cohort
            role = user_profile.job_title or "Professional"
            level = user_profile.seniority_level or "mid"
            location = user_profile.location or "United States"
            
            prompt = f"""
            Provide salary benchmark data for:
            Role: {role}
            Level: {level}
            Location: {location}
            Years Experience: {cohort.get('years_experience', '3-5')}
            
            Return typical salary distribution as JSON:
            {{
                "p10": 80000,
                "p25": 95000,
                "p50": 110000,
                "p75": 130000,
                "p90": 150000
            }}
            """
            
            response = self.model.generate_content(prompt)
            distribution = self._parse_salary_distribution(response.text, role)
            
            # Calculate user's percentile (simulated - would use actual salary in real app)
            user_salary = user_profile.salary_expectation or distribution["p50"]
            percentile = self._calculate_salary_percentile(user_salary, distribution)
            
            return {
                "user_salary": user_salary,
                "peer_median": distribution["p50"],
                "distribution": distribution,
                "percentile": percentile,
                "vs_median": user_salary - distribution["p50"],
                "vs_median_percent": round(((user_salary - distribution["p50"]) / distribution["p50"]) * 100, 1) if distribution["p50"] > 0 else 0,
                "assessment": self._assess_salary_standing(percentile)
            }
            
        except Exception as e:
            logger.error(f"Salary benchmarking failed: {e}")
            return {
                "percentile": 50,
                "assessment": "Average - insufficient data"
            }
    
    async def _benchmark_skills(
        self,
        user_profile: UserProfile,
        cohort: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Benchmark skills breadth and depth against peers"""
        try:
            user_skills = user_profile.skills or []
            skill_count = len(user_skills)
            
            # Expected skill counts by level
            expected_counts = {
                "entry": {"min": 3, "median": 5, "p75": 8},
                "junior": {"min": 5, "median": 8, "p75": 12},
                "mid": {"min": 8, "median": 12, "p75": 18},
                "senior": {"min": 12, "median": 18, "p75": 25},
                "lead": {"min": 15, "median": 22, "p75": 30}
            }
            
            level = user_profile.seniority_level or "mid"
            expected = expected_counts.get(level, expected_counts["mid"])
            
            # Calculate percentile based on skill count
            if skill_count >= expected["p75"]:
                percentile = 75
            elif skill_count >= expected["median"]:
                percentile = 60
            elif skill_count >= expected["min"]:
                percentile = 40
            else:
                percentile = 25
            
            # Analyze skill quality
            prompt = f"""
            Analyze skill set quality for {level} level {user_profile.job_title or 'professional'}:
            Skills: {', '.join(user_skills[:20])}
            
            Rate:
            1. Skill Relevance (how current/in-demand these skills are)
            2. Skill Depth (breadth vs specialization balance)
            3. Missing Critical Skills (gaps vs peer expectations)
            
            Return JSON with: relevance_score (0-100), depth_assessment, critical_gaps[]
            """
            
            response = self.model.generate_content(prompt)
            quality_analysis = self._parse_skills_quality(response.text)
            
            return {
                "skill_count": skill_count,
                "peer_median_count": expected["median"],
                "percentile": percentile,
                "relevance_score": quality_analysis.get("relevance_score", 70),
                "depth_assessment": quality_analysis.get("depth_assessment", "Balanced"),
                "critical_gaps": quality_analysis.get("critical_gaps", []),
                "assessment": self._assess_skills_standing(percentile, quality_analysis)
            }
            
        except Exception as e:
            logger.error(f"Skills benchmarking failed: {e}")
            return {
                "percentile": 50,
                "assessment": "Average skill set"
            }
    
    async def _benchmark_progression(
        self,
        user_profile: UserProfile,
        cohort: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Benchmark career progression speed against peers"""
        try:
            level = user_profile.seniority_level or "mid"
            years_exp = cohort.get("years_experience", "3-5")
            
            # Expected progression timeline
            progression_norms = {
                "entry": {"typical_years": "0-2", "next_level": "junior"},
                "junior": {"typical_years": "2-4", "next_level": "mid"},
                "mid": {"typical_years": "4-7", "next_level": "senior"},
                "senior": {"typical_years": "7-12", "next_level": "lead/staff"},
                "lead": {"typical_years": "12+", "next_level": "principal/director"}
            }
            
            norm = progression_norms.get(level, progression_norms["mid"])
            
            # Assess if on track (simplified - would use actual experience data)
            on_track = True
            percentile = 55  # Default to slightly above average
            
            return {
                "current_level": level,
                "typical_years_at_level": norm["typical_years"],
                "next_expected_level": norm["next_level"],
                "percentile": percentile,
                "on_track": on_track,
                "assessment": "On track with typical progression" if on_track else "Behind typical pace"
            }
            
        except Exception as e:
            logger.error(f"Progression benchmarking failed: {e}")
            return {
                "percentile": 50,
                "on_track": True,
                "assessment": "Average progression"
            }
    
    def _define_peer_cohort(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Define peer cohort for comparison"""
        return {
            "role": user_profile.job_title or "Professional",
            "seniority": user_profile.seniority_level or "mid",
            "industry": user_profile.industry or "Technology",
            "location": user_profile.location or "United States",
            "years_experience": "3-5"  # Would calculate from actual data
        }
    
    def _calculate_overall_percentile(self, dimension_percentiles: List[int]) -> int:
        """Calculate weighted average percentile across dimensions"""
        if not dimension_percentiles:
            return 50
        return int(sum(dimension_percentiles) / len(dimension_percentiles))
    
    def _percentile_to_rating(self, percentile: int) -> str:
        """Convert percentile to human-readable rating"""
        if percentile >= 90:
            return "exceptional"
        elif percentile >= 75:
            return "above_average"
        elif percentile >= 40:
            return "average"
        elif percentile >= 25:
            return "below_average"
        else:
            return "needs_improvement"
    
    def _calculate_salary_percentile(
        self,
        salary: int,
        distribution: Dict[str, int]
    ) -> int:
        """Calculate salary percentile"""
        if salary >= distribution.get("p90", float('inf')):
            return 90
        elif salary >= distribution.get("p75", float('inf')):
            return 75
        elif salary >= distribution.get("p50", float('inf')):
            return 60
        elif salary >= distribution.get("p25", float('inf')):
            return 40
        else:
            return 25
    
    def _assess_salary_standing(self, percentile: int) -> str:
        """Assess salary standing vs peers"""
        if percentile >= 75:
            return "Above market - well compensated vs peers"
        elif percentile >= 50:
            return "Market rate - competitive compensation"
        elif percentile >= 25:
            return "Below market - room for improvement"
        else:
            return "Significantly below market - consider negotiation"
    
    def _assess_skills_standing(
        self,
        percentile: int,
        quality: Dict[str, Any]
    ) -> str:
        """Assess skills standing"""
        if percentile >= 75 and quality.get("relevance_score", 0) >= 80:
            return "Strong skill set - ahead of peers"
        elif percentile >= 50:
            return "Competitive skill set - on par with peers"
        else:
            return "Skill development recommended - behind peers"
    
    def _identify_strengths(
        self,
        salary_bench: Dict[str, Any],
        skills_bench: Dict[str, Any],
        progression_bench: Dict[str, Any]
    ) -> List[str]:
        """Identify areas where user exceeds peers"""
        strengths = []
        
        if salary_bench.get("percentile", 0) >= 75:
            strengths.append("Compensation above peer average")
        
        if skills_bench.get("percentile", 0) >= 75:
            strengths.append("Strong skill set breadth")
        
        if skills_bench.get("relevance_score", 0) >= 80:
            strengths.append("Highly relevant, in-demand skills")
        
        if progression_bench.get("on_track", False):
            strengths.append("Career progression on track")
        
        return strengths if strengths else ["Building solid foundation"]
    
    def _identify_gaps(
        self,
        salary_bench: Dict[str, Any],
        skills_bench: Dict[str, Any],
        progression_bench: Dict[str, Any]
    ) -> List[str]:
        """Identify improvement areas"""
        gaps = []
        
        if salary_bench.get("percentile", 100) < 50:
            gaps.append("Salary below peer median - consider negotiation")
        
        if skills_bench.get("percentile", 100) < 40:
            gaps.append("Skill set development needed")
        
        critical_gaps = skills_bench.get("critical_gaps", [])
        if critical_gaps:
            gaps.append(f"Missing critical skills: {', '.join(critical_gaps[:3])}")
        
        if not progression_bench.get("on_track", True):
            gaps.append("Career progression slower than typical")
        
        return gaps if gaps else ["No major gaps identified"]
    
    def _parse_salary_distribution(self, response_text: str, role: str) -> Dict[str, int]:
        """Parse salary distribution from AI response"""
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback based on role
        base = 100000
        if "senior" in role.lower():
            base = 130000
        elif "lead" in role.lower() or "staff" in role.lower():
            base = 160000
        
        return {
            "p10": int(base * 0.7),
            "p25": int(base * 0.85),
            "p50": base,
            "p75": int(base * 1.2),
            "p90": int(base * 1.4)
        }
    
    def _parse_skills_quality(self, response_text: str) -> Dict[str, Any]:
        """Parse skills quality analysis"""
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "relevance_score": 70,
            "depth_assessment": "Balanced skill set",
            "critical_gaps": []
        }
    
    def _get_fallback_benchmark(self) -> Dict[str, Any]:
        """Fallback benchmark when analysis fails"""
        return {
            "overall_percentile": 50,
            "overall_rating": "average",
            "peer_cohort": {"role": "Professional"},
            "strengths": ["Complete your profile for detailed benchmarking"],
            "improvement_areas": ["Add skills and experience data"],
            "generated_at": datetime.utcnow().isoformat()
        }
