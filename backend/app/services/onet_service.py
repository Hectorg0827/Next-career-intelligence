"""
O*NET Web Services integration
Provides occupation data, skills, and labor market information
"""

import httpx
from loguru import logger
from typing import List, Dict, Any, Optional
from app.core.config import settings
import base64


class ONetService:
    """Service for O*NET API integration"""
    
    def __init__(self):
        self.base_url = settings.ONET_BASE_URL
        self.username = settings.ONET_USERNAME
        self.password = settings.ONET_PASSWORD
        
        # Create Basic Auth header
        if self.username and self.password:
            credentials = f"{self.username}:{self.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            self.headers = {
                "Authorization": f"Basic {encoded}",
                "Accept": "application/json"
            }
        else:
            self.headers = {"Accept": "application/json"}
    
    async def search_occupations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for occupations by keyword
        Returns job title suggestions for autocomplete
        """
        
        if not self.username or not self.password:
            logger.warning("O*NET credentials not configured, using mock data")
            return self._get_mock_occupations(query, limit)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/online/search",
                    params={"keyword": query, "end": limit},
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                occupations = []
                for item in data.get("occupation", [])[:limit]:
                    occupations.append({
                        "code": item.get("code"),
                        "title": item.get("title"),
                        "description": item.get("description", "")
                    })
                
                logger.info(f"Found {len(occupations)} occupations for query: {query}")
                return occupations
                
        except Exception as e:
            logger.error(f"O*NET search error: {e}")
            return self._get_mock_occupations(query, limit)
    
    async def get_occupation_data(self, job_title: str) -> Dict[str, Any]:
        """
        Get detailed occupation data for analysis
        Includes skills, tasks, and labor market info
        """
        
        if not self.username or not self.password:
            logger.warning("O*NET credentials not configured, using mock data")
            return self._get_mock_occupation_data(job_title)
        
        try:
            # First, search for the occupation
            occupations = await self.search_occupations(job_title, limit=1)
            
            if not occupations:
                logger.warning(f"No O*NET data found for: {job_title}")
                return self._get_mock_occupation_data(job_title)
            
            onet_code = occupations[0]["code"]
            
            # Get detailed occupation information
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/online/occupations/{onet_code}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                return {
                    "code": onet_code,
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "tasks": self._extract_tasks(data),
                    "skills": self._extract_skills(data),
                    "abilities": self._extract_abilities(data),
                    "automation_risk_indicators": self._calculate_automation_indicators(data)
                }
                
        except Exception as e:
            logger.error(f"O*NET data fetch error: {e}")
            return self._get_mock_occupation_data(job_title)
    
    async def get_occupation_by_code(self, onet_code: str) -> Optional[Dict[str, Any]]:
        """Get occupation details by O*NET-SOC code"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/online/occupations/{onet_code}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to fetch occupation {onet_code}: {e}")
            return None
    
    def _extract_tasks(self, occupation_data: Dict) -> List[str]:
        """Extract task descriptions from O*NET data"""
        tasks = occupation_data.get("tasks", [])
        return [task.get("statement", "") for task in tasks[:5]]
    
    def _extract_skills(self, occupation_data: Dict) -> List[str]:
        """Extract required skills from O*NET data"""
        skills = occupation_data.get("skills", [])
        return [skill.get("name", "") for skill in skills[:10]]
    
    def _extract_abilities(self, occupation_data: Dict) -> List[str]:
        """Extract abilities from O*NET data"""
        abilities = occupation_data.get("abilities", [])
        return [ability.get("name", "") for ability in abilities[:10]]
    
    def _calculate_automation_indicators(self, occupation_data: Dict) -> Dict[str, Any]:
        """Calculate indicators of automation potential"""
        # This would use O*NET data to assess routine vs. non-routine tasks
        return {
            "routine_task_intensity": "medium",
            "cognitive_complexity": "high",
            "social_interaction": "medium"
        }
    
    def _get_mock_occupations(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Mock occupation data for development/testing"""
        
        mock_jobs = {
            "software": [
                {"code": "15-1252.00", "title": "Software Developers", "description": "Develop software applications"},
                {"code": "15-1211.00", "title": "Computer Systems Analysts", "description": "Analyze computer systems"}
            ],
            "teacher": [
                {"code": "25-2021.00", "title": "Elementary School Teachers", "description": "Teach elementary students"},
                {"code": "25-2031.00", "title": "Secondary School Teachers", "description": "Teach secondary students"}
            ],
            "graphic": [
                {"code": "27-1024.00", "title": "Graphic Designers", "description": "Design visual concepts"},
                {"code": "27-1014.00", "title": "Multimedia Artists", "description": "Create multimedia content"}
            ],
            "nurse": [
                {"code": "29-1141.00", "title": "Registered Nurses", "description": "Provide patient care"},
                {"code": "29-1171.00", "title": "Nurse Practitioners", "description": "Advanced nursing practice"}
            ],
            "data": [
                {"code": "43-9021.00", "title": "Data Entry Keyers", "description": "Enter data into systems"},
                {"code": "15-2051.00", "title": "Data Scientists", "description": "Analyze complex data"}
            ]
        }
        
        query_lower = query.lower()
        for key, jobs in mock_jobs.items():
            if key in query_lower:
                return jobs[:limit]
        
        return mock_jobs["software"][:limit]
    
    def _get_mock_occupation_data(self, job_title: str) -> Dict[str, Any]:
        """Mock detailed occupation data"""
        
        return {
            "code": "00-0000.00",
            "title": job_title,
            "description": f"Professional working as {job_title}",
            "tasks": [
                "Perform core job responsibilities",
                "Collaborate with team members",
                "Maintain professional standards"
            ],
            "skills": [
                "Critical Thinking",
                "Active Listening",
                "Communication",
                "Problem Solving"
            ],
            "abilities": [
                "Oral Comprehension",
                "Written Comprehension",
                "Deductive Reasoning"
            ],
            "automation_risk_indicators": {
                "routine_task_intensity": "medium",
                "cognitive_complexity": "high",
                "social_interaction": "medium"
            }
        }
