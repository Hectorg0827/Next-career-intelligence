import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/next_career_db")

def check_tables():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    target_tables = ["skills", "user_skills", "education"]
    
    for table in target_tables:
        if table in tables:
            print(f"\nTable '{table}' exists.")
            columns = inspector.get_columns(table)
            print(f"Columns in '{table}':")
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
        else:
            print(f"\nTable '{table}' does NOT exist.")

if __name__ == "__main__":
    check_tables()
