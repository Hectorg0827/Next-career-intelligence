"""
Job Seeder - Populate job marketplace with realistic data
Uses Gemini AI to generate diverse, realistic job postings
"""

from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta
import random
from loguru import logger

from app.services.gemini_analyzer import GeminiAnalyzer
from app.db.supabase import get_supabase_client


class JobSeeder:
    """Generate and seed realistic job postings"""
    
    def __init__(self):
        self.gemini = GeminiAnalyzer()
        self.client = get_supabase_client()
        
        # Common tech companies for realistic examples
        self.tech_companies = [
            {"name": "TechCorp", "industry": "Software", "size": "1000+"},
            {"name": "DataViz Inc", "industry": "Analytics", "size": "201-500"},
            {"name": "CloudFirst", "industry": "Cloud Services", "size": "501-1000"},
            {"name": "AI Innovations", "industry": "Artificial Intelligence", "size": "51-200"},
            {"name": "SecureNet", "industry": "Cybersecurity", "size": "201-500"},
            {"name": "GreenTech Solutions", "industry": "Clean Energy", "size": "51-200"},
            {"name": "HealthData Systems", "industry": "Healthcare IT", "size": "501-1000"},
            {"name": "FinanceFlow", "industry": "Fintech", "size": "201-500"},
        ]
        
        # Job titles by category
        self.job_categories = {
            "software": [
                "Software Engineer",
                "Senior Software Engineer",
                "Full Stack Developer",
                "Backend Engineer",
                "Frontend Developer",
                "DevOps Engineer",
                "Site Reliability Engineer"
            ],
            "data": [
                "Data Analyst",
                "Senior Data Analyst",
                "Data Scientist",
                "Machine Learning Engineer",
                "Business Intelligence Analyst",
                "Data Engineer"
            ],
            "product": [
                "Product Manager",
                "Senior Product Manager",
                "Product Owner",
                "Technical Product Manager"
            ],
            "design": [
                "UX Designer",
                "UI/UX Designer",
                "Product Designer",
                "Senior UX Researcher"
            ],
            "marketing": [
                "Marketing Manager",
                "Growth Marketing Manager",
                "Content Marketing Manager",
                "Digital Marketing Specialist"
            ]
        }
        
        # US Cities with tech presence
        self.locations = [
            {"city": "San Francisco", "state": "CA", "country": "USA"},
            {"city": "New York", "state": "NY", "country": "USA"},
            {"city": "Austin", "state": "TX", "country": "USA"},
            {"city": "Seattle", "state": "WA", "country": "USA"},
            {"city": "Boston", "state": "MA", "country": "USA"},
            {"city": "Denver", "state": "CO", "country": "USA"},
            {"city": "Chicago", "state": "IL", "country": "USA"},
            {"city": "Remote", "state": "", "country": "USA"},
        ]
    
    async def generate_job_description(self, title: str, company: str, seniority: str) -> Dict[str, Any]:
        """Use Gemini to generate realistic job description"""
        
        try:
            prompt = f"""Generate a realistic job posting for:
Title: {title}
Company: {company}
Seniority: {seniority}

Return ONLY valid JSON:
{{
    "description": "<2-3 paragraphs about the role and company>",
    "responsibilities": ["<responsibility 1>", "<responsibility 2>", "<3-5 total>"],
    "requirements": ["<requirement 1>", "<requirement 2>", "<5-8 total>"],
    "skills": ["<skill 1>", "<skill 2>", "<8-12 total specific skills>"],
    "benefits": ["<benefit 1>", "<benefit 2>", "<4-6 total>"],
    "experience_years_min": <number>,
    "experience_years_max": <number>,
    "salary_min": <number>,
    "salary_max": <number>
}}

Make it realistic and specific to the role."""

            response = self.gemini.client.models.generate_content(
                model=self.gemini.model_name,
                contents=prompt,
                config=self.gemini.generation_config
            )
            
            result = self.gemini._parse_json_response(response, f"job description for {title}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate job description: {e}")
            # Return fallback
            return self._get_fallback_description(title, seniority)
    
    def _get_fallback_description(self, title: str, seniority: str) -> Dict[str, Any]:
        """Fallback job description if AI generation fails"""
        
        base_salaries = {
            "entry": (60000, 90000),
            "mid": (90000, 130000),
            "senior": (130000, 180000),
            "lead": (160000, 220000)
        }
        
        salary_range = base_salaries.get(seniority, (70000, 120000))
        
        return {
            "description": f"We are seeking a talented {title} to join our growing team. This role offers exciting challenges and growth opportunities.",
            "responsibilities": [
                f"Lead {title.lower()} initiatives",
                "Collaborate with cross-functional teams",
                "Contribute to technical architecture",
                "Mentor junior team members"
            ],
            "requirements": [
                f"3+ years of experience in {title.lower()} role",
                "Strong problem-solving skills",
                "Excellent communication abilities",
                "Bachelor's degree or equivalent experience"
            ],
            "skills": ["Python", "SQL", "Git", "Agile", "Communication", "Problem Solving"],
            "benefits": [
                "Competitive salary and equity",
                "Health, dental, vision insurance",
                "401(k) matching",
                "Flexible PTO",
                "Remote work options"
            ],
            "experience_years_min": 2 if seniority == "entry" else 5,
            "experience_years_max": 5 if seniority == "entry" else 10,
            "salary_min": salary_range[0],
            "salary_max": salary_range[1]
        }
    
    async def seed_jobs(self, count: int = 50) -> List[str]:
        """Generate and insert job postings into database"""
        
        if not self.client:
            logger.error("Supabase client not available")
            return []
        
        logger.info(f"🌱 Seeding {count} job postings...")
        
        job_ids = []
        
        # Use fallback mode (no Gemini to avoid quota) and no employers table dependency
        for i in range(count):
            try:
                # Random selections
                category = random.choice(list(self.job_categories.keys()))
                title = random.choice(self.job_categories[category])
                company = random.choice(self.tech_companies)
                location = random.choice(self.locations)
                
                # Determine seniority from title
                if any(word in title.lower() for word in ["senior", "lead", "principal", "staff"]):
                    seniority = "senior"
                elif any(word in title.lower() for word in ["junior", "associate", "entry"]):
                    seniority = "entry"
                else:
                    seniority = "mid"
                
                # Use fallback job data (no AI)
                job_data = self._get_fallback_description(title, seniority)
                
                # Determine location type
                is_remote = location["city"] == "Remote" or random.random() < 0.3
                location_type = "remote" if is_remote else ("hybrid" if random.random() < 0.4 else "onsite")
                
                # Calculate salary range
                salary_min = job_data["salary_min"]
                salary_max = job_data["salary_max"]
                
                # Build job record with ONLY fields that exist in schema (excluding experience_years fields due to PostgREST cache)
                job_record = {
                    "title": title,
                    "seniority": seniority,
                    "description": job_data["description"],
                    "requirements": "\n".join(f"• {req}" for req in job_data["requirements"]),
                    "responsibilities": "\n".join(f"• {resp}" for resp in job_data["responsibilities"]),
                    "benefits": "\n".join(f"• {ben}" for ben in job_data["benefits"]),
                    "skills_extracted": job_data["skills"],
                    "location_type": location_type,
                    "location_city": location["city"] if not is_remote else None,
                    "location_state": location["state"] if not is_remote else None,
                    "location_country": location["country"],
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_currency": "USD",
                    "employment_type": "full_time",
                    "apply_url": f"https://careers.example.com/jobs/{i}",
                    "source": "seeded"
                }
                
                # Insert job
                response = self.client.table('jobs').insert(job_record).execute()
                
                if response.data:
                    job_id = response.data[0]['id']
                    job_ids.append(job_id)
                    logger.info(f"✅ Seeded job {i+1}/{count}: {title} at {company['name']}")
                    
            except Exception as e:
                logger.error(f"Failed to seed job {i+1}: {e}")
                continue
        
        logger.info(f"🎉 Successfully seeded {len(job_ids)} jobs!")
        return job_ids
    
    async def _seed_employers(self) -> List[str]:
        """Ensure employers exist in database"""
        
        employer_ids = []
        
        for company in self.tech_companies:
            try:
                # Check if exists
                response = self.client.table('employers')\
                    .select('id')\
                    .eq('name', company['name'])\
                    .execute()
                
                if response.data:
                    employer_ids.append(response.data[0]['id'])
                else:
                    # Create employer
                    employer_record = {
                        "name": company['name'],
                        "slug": company['name'].lower().replace(' ', '-'),
                        "industry": company['industry'],
                        "size_range": company['size'],
                        "verified": True,
                        "website": f"https://{company['name'].lower().replace(' ', '')}.com"
                    }
                    
                    response = self.client.table('employers').insert(employer_record).execute()
                    
                    if response.data:
                        employer_ids.append(response.data[0]['id'])
                        
            except Exception as e:
                logger.error(f"Failed to seed employer {company['name']}: {e}")
                # Add a placeholder ID
                employer_ids.append(None)
        
        return employer_ids
    
    async def clear_seeded_jobs(self):
        """Remove all seeded jobs (for testing)"""
        
        if not self.client:
            return
        
        try:
            response = self.client.table('jobs')\
                .delete()\
                .eq('source', 'seeded')\
                .execute()
            
            logger.info(f"🗑️ Cleared seeded jobs")
            
        except Exception as e:
            logger.error(f"Failed to clear seeded jobs: {e}")


# Singleton instance
job_seeder = JobSeeder()
