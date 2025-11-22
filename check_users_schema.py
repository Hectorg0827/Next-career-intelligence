import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load env vars
load_dotenv('backend/.env')

def inspect_users_table():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        return

    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    print("Users table columns:")
    columns = inspector.get_columns('users')
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"  - {col['name']}: {col['type']} {nullable}")

if __name__ == "__main__":
    inspect_users_table()
