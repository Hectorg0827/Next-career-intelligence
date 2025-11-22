import os
import sys
from sqlalchemy import create_engine, inspect
from app.core.config import settings

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def inspect_db():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    if inspector.has_table("job_applications"):
        print("Table 'job_applications' exists. Columns:")
        for column in inspector.get_columns("job_applications"):
            print(f"- {column['name']} ({column['type']}) - Nullable: {column['nullable']}")
    else:
        print("Table 'job_applications' does not exist.")

if __name__ == "__main__":
    inspect_db()
