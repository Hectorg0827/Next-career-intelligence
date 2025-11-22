import sys
import os
import asyncio
from sqlalchemy.orm import Session

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.ai_matching_service import AIMatchingService

async def test_matching_service_imports():
    print("Testing AI Matching Service imports...")
    try:
        service = AIMatchingService()
        print("Service initialized successfully.")
    except NameError as e:
        print(f"NameError: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_matching_service_imports())
