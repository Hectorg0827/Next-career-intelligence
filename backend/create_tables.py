import os
import sys
from app.db.database import engine, Base
from app.models.database import JobApplication

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_tables():
    print("Creating tables...")
    # This will create tables that don't exist
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

if __name__ == "__main__":
    create_tables()
