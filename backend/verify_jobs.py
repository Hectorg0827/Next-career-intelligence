import os
import sys
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.database import Job

def verify_jobs():
    db = SessionLocal()
    try:
        count = db.query(Job).count()
        print(f"Total jobs in database: {count}")
        
        jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
        print("\nLatest 5 jobs:")
        for job in jobs:
            print(f"- {job.title} ({job.location}) - {job.salary_min}-{job.salary_max} {job.salary_currency}")
            print(f"  Skills: {job.required_skills}")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_jobs()
