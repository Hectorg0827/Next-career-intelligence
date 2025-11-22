import os
import sys
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add backend to path (current dir)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.database import Job

def seed_jobs():
    db = SessionLocal()
    
    print("Seeding jobs...")
    
    titles = [
        "Senior Python Developer", "Frontend Engineer (React)", "Data Scientist", 
        "DevOps Engineer", "Product Manager", "UX Designer", "Full Stack Developer",
        "Machine Learning Engineer", "Cloud Architect", "QA Automation Engineer"
    ]
    
    companies = ["Tech Corp", "Startup Inc", "Big Data Co", "Cloud Systems", "Design Studio"]
    locations = ["Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "London, UK"]
    skills_pool = ["Python", "React", "AWS", "Docker", "Kubernetes", "SQL", "NoSQL", "TypeScript", "Java", "Go", "Figma", "JIRA"]
    
    jobs_to_create = []
    
    for i in range(20):
        title = random.choice(titles)
        company_name = random.choice(companies)
        full_title = f"{title} at {company_name}"
        
        job_skills = random.sample(skills_pool, k=random.randint(3, 6))
        
        job = Job(
            id=uuid.uuid4(),
            title=full_title,
            description=f"We are looking for a {title} to join our team at {company_name}. \n\nRequirements:\n- Experience with {', '.join(job_skills)}.\n- Strong communication skills.",
            location=random.choice(locations),
            remote_policy=random.choice(["remote", "hybrid", "on_site"]),
            employment_type=random.choice(["full_time", "contract"]),
            salary_min=random.randint(80000, 120000),
            salary_max=random.randint(130000, 200000),
            salary_currency="USD",
            required_skills=job_skills,
            seniority=random.choice(["entry", "mid", "senior"]),
            source="mock_seeder",
            is_active=True,
            posted_date=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        jobs_to_create.append(job)
        
    try:
        db.add_all(jobs_to_create)
        db.commit()
        print(f"Successfully seeded {len(jobs_to_create)} jobs.")
    except Exception as e:
        print(f"Error seeding jobs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_jobs()
