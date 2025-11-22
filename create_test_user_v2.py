import os
import sys
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load env
load_dotenv('backend/.env')

from app.models.database import User

def create_test_user():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        return

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print(f"Test user already exists: {existing_user.id}")
            return

        # Create new user
        new_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            firebase_uid="test_firebase_uid_" + str(uuid.uuid4())[:8],
            first_name="Test",
            last_name="User",
            role="user",
            subscription_status="free",
            account_created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        print(f"Created test user: {new_user.id}")
        
    except Exception as e:
        print(f"Failed to create user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
