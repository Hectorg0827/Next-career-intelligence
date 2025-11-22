import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load env vars
load_dotenv('backend/.env')

def inspect_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        return

    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    
    for table in ['skills', 'user_skills', 'education']:
        if table in tables:
            print(f"\nTable: {table}")
            columns = inspector.get_columns(table)
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print(f"\nTable {table} does not exist.")

if __name__ == "__main__":
    inspect_db()
