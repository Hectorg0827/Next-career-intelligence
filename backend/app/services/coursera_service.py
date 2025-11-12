"""
Coursera API integration for training recommendations
"""

import httpx
from loguru import logger
from typing import List, Dict, Any
from app.core.config import settings


class CourseraService:
    """Service for Coursera course recommendations"""

    def __init__(self):
        self.base_url = settings.COURSERA_BASE_URL
        self.api_key = settings.COURSERA_API_KEY

    async def get_recommendations(self, skill_gaps: List[str]) -> List[Dict[str, Any]]:
        """
        Get course recommendations for skill gaps

        Args:
            skill_gaps: List of skills to learn

        Returns:
            List of training resources
        """

        if not self.api_key:
            logger.warning("Coursera API key not configured, using mock recommendations")
            return self._get_mock_recommendations(skill_gaps)

        try:
            recommendations = []

            for skill in skill_gaps[:5]:  # Limit to 5 skills
                courses = await self._search_courses(skill)
                recommendations.extend(courses[:2])  # Top 2 courses per skill

            return recommendations

        except Exception as e:
            logger.error(f"Coursera API error: {e}")
            return self._get_mock_recommendations(skill_gaps)

    async def _search_courses(self, skill: str) -> List[Dict[str, Any]]:
        """Search for courses by skill keyword"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/courses.v1",
                    params={"q": "search", "query": skill},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )

                response.raise_for_status()
                data = response.json()

                courses = []
                for course in data.get("elements", [])[:2]:
                    courses.append(
                        {
                            "title": course.get("name"),
                            "provider": "Coursera",
                            "url": f"https://www.coursera.org/learn/{course.get('slug')}",
                            "duration": self._format_duration(course.get("workload")),
                            "skill_covered": skill,
                            "cost": "Free to audit, paid certificate",
                            "rating": course.get("averageRating"),
                        }
                    )

                return courses

        except Exception as e:
            logger.error(f"Course search error for {skill}: {e}")
            return []

    def _format_duration(self, workload: str) -> str:
        """Format course duration"""
        if not workload:
            return "Self-paced"
        return workload

    def _get_mock_recommendations(self, skill_gaps: List[str]) -> List[Dict[str, Any]]:
        """Mock course recommendations for development/testing"""

        mock_courses = {
            "AI literacy": {
                "title": "AI For Everyone",
                "provider": "Coursera (DeepLearning.AI)",
                "url": "https://www.coursera.org/learn/ai-for-everyone",
                "duration": "4 weeks, 2-3 hours/week",
                "cost": "Free to audit",
                "rating": 4.8,
            },
            "Data interpretation": {
                "title": "Data Analysis and Interpretation",
                "provider": "Coursera (Wesleyan)",
                "url": "https://www.coursera.org/specializations/data-analysis",
                "duration": "5 months, 4 hours/week",
                "cost": "$49/month",
                "rating": 4.6,
            },
            "Python programming": {
                "title": "Python for Everybody",
                "provider": "Coursera (University of Michigan)",
                "url": "https://www.coursera.org/specializations/python",
                "duration": "8 months, 3 hours/week",
                "cost": "Free to audit",
                "rating": 4.8,
            },
            "Machine learning": {
                "title": "Machine Learning Specialization",
                "provider": "Coursera (Stanford)",
                "url": "https://www.coursera.org/specializations/machine-learning-introduction",
                "duration": "3 months, 9 hours/week",
                "cost": "$49/month",
                "rating": 4.9,
            },
            "Data visualization": {
                "title": "Data Visualization with Tableau",
                "provider": "Coursera (UC Davis)",
                "url": "https://www.coursera.org/specializations/data-visualization",
                "duration": "6 months, 3 hours/week",
                "cost": "$49/month",
                "rating": 4.6,
            },
        }

        recommendations = []

        for skill in skill_gaps[:5]:
            # Try to match skill to mock courses
            matched = False
            for course_skill, course_data in mock_courses.items():
                if any(word in skill.lower() for word in course_skill.lower().split()):
                    recommendations.append(
                        {
                            "title": course_data["title"],
                            "provider": course_data["provider"],
                            "url": course_data["url"],
                            "duration": course_data["duration"],
                            "skill_covered": skill,
                            "cost": course_data["cost"],
                            "rating": course_data["rating"],
                        }
                    )
                    matched = True
                    break

            # If no match, provide a generic course
            if not matched:
                recommendations.append(
                    {
                        "title": f"Introduction to {skill}",
                        "provider": "Coursera",
                        "url": f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}",
                        "duration": "Self-paced",
                        "skill_covered": skill,
                        "cost": "Varies",
                        "rating": None,
                    }
                )

        return recommendations
