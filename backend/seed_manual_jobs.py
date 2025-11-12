"""Manual job seeding with realistic sample data."""

import sys
import uuid
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import SessionLocal
from app.models.database import Job

# High-quality sample jobs
SAMPLE_JOBS = [
    {
        "title": "Senior Python Developer",
        "company": "Tech Innovators Inc",
        "description": """Looking for a Senior Python Developer with 5+ years of experience.
        You'll work with Python, Django, FastAPI, and AWS. Experience with PostgreSQL, Redis, and Docker required.
        This is a fully remote position perfect for senior-level engineers wanting to lead architecture decisions.
        Salary: $180,000 - $220,000""",
        "location": "San Francisco, CA",
        "remote_type": "remote",
        "salary_min": 180000,
        "salary_max": 220000,
        "experience_level": "senior",
        "job_type": "full_time",
        "required_skills": ["python", "django", "fastapi", "aws", "postgresql", "redis", "docker"],
    },
    {
        "title": "Full Stack JavaScript Developer",
        "company": "Digital Solutions Co",
        "description": """Join our team as a Full Stack JavaScript Developer!
        Requirements: React, Next.js, Node.js, Express, MongoDB, Git
        You'll work on exciting web applications using modern JavaScript frameworks.
        This is a hybrid position in our NYC office. Entry to mid-level welcome.
        Salary: $100,000 - $140,000""",
        "location": "New York, NY",
        "remote_type": "hybrid",
        "salary_min": 100000,
        "salary_max": 140000,
        "experience_level": "mid",
        "job_type": "full_time",
        "required_skills": ["javascript", "react", "nextjs", "nodejs", "express", "mongodb"],
    },
    {
        "title": "DevOps Engineer",
        "company": "Cloud Native Systems",
        "description": """Seeking an experienced DevOps Engineer to manage our Kubernetes infrastructure.
        Must have: Kubernetes, Docker, Terraform, AWS/GCP, CI/CD pipelines, Linux
        Build and maintain scalable cloud infrastructure. Fully remote opportunity.
        Salary: $150,000 - $190,000""",
        "location": "Remote",
        "remote_type": "remote",
        "salary_min": 150000,
        "salary_max": 190000,
        "experience_level": "mid",
        "job_type": "full_time",
        "required_skills": ["kubernetes", "docker", "terraform", "aws", "cicd", "linux"],
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Pioneers",
        "description": """Build the future with our ML team! We're looking for ML Engineers with experience in:
        Python, TensorFlow/PyTorch, Deep Learning, Computer Vision, NLP
        Work on cutting-edge AI models. Based in our Boston office with flexible remote options.
        Salary: $170,000 - $210,000""",
        "location": "Boston, MA",
        "remote_type": "hybrid",
        "salary_min": 170000,
        "salary_max": 210000,
        "experience_level": "senior",
        "job_type": "full_time",
        "required_skills": ["python", "tensorflow", "pytorch", "deep learning", "machine learning"],
    },
    {
        "title": "Frontend Developer (React)",
        "company": "Web Creations Ltd",
        "description": """We're hiring a Frontend Developer to build beautiful, responsive web applications.
        Skills needed: React, TypeScript, Tailwind CSS, Next.js, REST APIs
        Entry-level candidates welcome. Fully remote. Growth opportunities available.
        Salary: $80,000 - $120,000""",
        "location": "Remote",
        "remote_type": "remote",
        "salary_min": 80000,
        "salary_max": 120000,
        "experience_level": "entry",
        "job_type": "full_time",
        "required_skills": ["react", "typescript", "tailwind", "nextjs", "html", "css"],
    },
    {
        "title": "Backend Engineer (Go)",
        "company": "High Performance Systems",
        "description": """Build scalable backend systems with Go! Looking for experienced backend engineers.
        Required: Go, Microservices, gRPC, PostgreSQL, Redis, Docker
        This senior position offers competitive compensation and remote flexibility.
        Salary: $195,000 - $240,000""",
        "location": "Remote",
        "remote_type": "remote",
        "salary_min": 195000,
        "salary_max": 240000,
        "experience_level": "senior",
        "job_type": "full_time",
        "required_skills": ["go", "microservices", "grpc", "postgresql", "redis", "docker"],
    },
    {
        "title": "Data Engineer",
        "company": "Analytics Corp",
        "description": """Build data pipelines and analytics infrastructure!
        Skills: Python, SQL, Spark, Airflow, Hadoop, AWS
        Mid-level position in our Seattle office. Hybrid work available.
        Salary: $130,000 - $170,000""",
        "location": "Seattle, WA",
        "remote_type": "hybrid",
        "salary_min": 130000,
        "salary_max": 170000,
        "experience_level": "mid",
        "job_type": "full_time",
        "required_skills": ["python", "sql", "spark", "airflow", "hadoop", "aws"],
    },
    {
        "title": "Mobile Developer (React Native)",
        "company": "App Studio Pro",
        "description": """Create amazing mobile apps with React Native!
        Required: React Native, JavaScript, TypeScript, mobile development
        Entry to mid-level developers welcome. Fully remote.
        Salary: $90,000 - $140,000""",
        "location": "Remote",
        "remote_type": "remote",
        "salary_min": 90000,
        "salary_max": 140000,
        "experience_level": "mid",
        "job_type": "full_time",
        "required_skills": ["react native", "javascript", "typescript", "mobile", "ios", "android"],
    },
    {
        "title": "Systems Administrator",
        "company": "Enterprise IT Solutions",
        "description": """Manage enterprise infrastructure and systems. Entry-level position available.
        Skills: Linux, Windows Server, Networking, Cloud platforms
        Work from our Austin office. On-site position.
        Salary: $70,000 - $100,000""",
        "location": "Austin, TX",
        "remote_type": "on_site",
        "salary_min": 70000,
        "salary_max": 100000,
        "experience_level": "entry",
        "job_type": "full_time",
        "required_skills": ["linux", "windows", "networking", "aws", "azure"],
    },
    {
        "title": "Java Backend Developer",
        "company": "Enterprise Software Corp",
        "description": """Build enterprise applications with Java and Spring Boot.
        Required: Java 17+, Spring Boot, Microservices, SQL, REST APIs
        Mid to senior level position. Based in Chicago with remote options.
        Salary: $120,000 - $160,000""",
        "location": "Chicago, IL",
        "remote_type": "hybrid",
        "salary_min": 120000,
        "salary_max": 160000,
        "experience_level": "mid",
        "job_type": "full_time",
        "required_skills": ["java", "spring", "microservices", "sql", "rest", "docker"],
    },
    {
        "title": "Cloud Architect",
        "company": "Cloud Giants",
        "description": """Design and architect cloud solutions for enterprise clients.
        Skills: AWS, Azure, GCP, Kubernetes, Terraform, Security
        Senior position with excellent compensation. Fully remote.
        Salary: $200,000 - $260,000""",
        "location": "Remote",
        "remote_type": "remote",
        "salary_min": 200000,
        "salary_max": 260000,
        "experience_level": "senior",
        "job_type": "full_time",
        "required_skills": ["aws", "azure", "kubernetes", "terraform", "security", "architecture"],
    },
]


def seed_manual_jobs():
    """Seed database with manual sample jobs."""
    db = SessionLocal()
    created = 0
    skipped = 0

    print("\n" + "=" * 70)
    print("🌱 Manual Job Seeding - Sample Data")
    print("=" * 70 + "\n")

    for job_data in SAMPLE_JOBS:
        try:
            # Create unique job ID
            job_id = f"manual_{uuid.uuid4().hex[:12]}"

            # Check if job already exists
            existing = (
                db.query(Job)
                .filter(
                    Job.title == job_data["title"],
                    Job.company == job_data["company"],
                    Job.source == "manual",
                )
                .first()
            )

            if existing:
                print(f"⏭️  Skipping: {job_data['title']}")
                skipped += 1
                continue

            # Create job record
            job = Job(
                id=job_id,
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                location=job_data["location"],
                remote_type=job_data["remote_type"],
                salary_min=job_data["salary_min"],
                salary_max=job_data["salary_max"],
                experience_level=job_data["experience_level"],
                job_type=job_data["job_type"],
                required_skills=job_data["required_skills"],
                source="manual",
                external_id=job_id,
                is_active="active",
            )

            db.add(job)
            created += 1
            print(f"✅ Added: {job_data['title']} at {job_data['company']}")

        except Exception as e:
            print(f"❌ Error adding job: {e}")
            skipped += 1

    try:
        db.commit()
        print(f"\n✅ Database seeding complete!")
        print(f"   📊 Created: {created} jobs")
        print(f"   ⏭️  Skipped: {skipped} (already in database)")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error committing to database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_manual_jobs()
    print("\n" + "=" * 70)
    print("✨ Seeding complete! Your database now has sample jobs.")
    print("=" * 70 + "\n")
