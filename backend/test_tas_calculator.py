"""
Test TAS Calculator with real database connection
"""

import asyncio
import asyncpg
import sys
sys.path.append('/Users/hectorgarcia/Desktop/Next-career-intelligence/backend')

from app.services.foundation.risk.calculators.tas_calculator import TaskAutomationCalculator


async def test_tas_calculator():
    """Test TAS calculator with Supabase database."""
    
    print("="*60)
    print("🧪 Testing TAS Calculator")
    print("="*60)
    print()
    
    # Database connection
    DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"
    
    print("🔄 Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected successfully\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Initialize calculator
    calculator = TaskAutomationCalculator(conn)
    print("✅ TAS Calculator initialized\n")
    
    # Test 1: Software Developer (should have sample data)
    print("Test 1: Software Developer (15-2051)")
    print("-" * 40)
    try:
        tas, coverage = await calculator.calculate("15-2051")
        print(f"✅ TAS Score: {tas:.1f}/100")
        print(f"✅ Coverage: {coverage:.1f}%")
        
        # Validate expected range for software developer
        if 60.0 <= tas <= 80.0:
            print("✅ Score in expected range (60-80)")
        else:
            print(f"⚠️  Score outside expected range: {tas:.1f}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Detailed breakdown
    print("Test 2: Detailed Task Breakdown")
    print("-" * 40)
    try:
        breakdown = await calculator.calculate_with_breakdown("15-2051")
        print(f"✅ TAS Score: {breakdown['tas']}/100")
        print(f"✅ Coverage: {breakdown['coverage']}%")
        print(f"✅ Task Count: {breakdown['task_count']}")
        
        if breakdown['top_risk_tasks']:
            print("\n📊 Top Risk Tasks:")
            for i, task in enumerate(breakdown['top_risk_tasks'], 1):
                print(f"   {i}. {task['name'][:50]}...")
                print(f"      Risk: {task['risk']:.2f}, Importance: {task['importance']:.2f}")
        else:
            print("⚠️  No tasks found (expected 1 sample task)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Non-existent occupation (should return defaults)
    print("Test 3: Non-existent Occupation Code")
    print("-" * 40)
    try:
        tas, coverage = await calculator.calculate("99-9999")
        print(f"✅ TAS Score: {tas:.1f}/100 (default)")
        print(f"✅ Coverage: {coverage:.1f}% (no data)")
        
        if tas == 50.0 and coverage == 0.0:
            print("✅ Correct default values returned")
        else:
            print(f"⚠️  Unexpected values: TAS={tas}, Coverage={coverage}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 4: Check actual database content
    print("Test 4: Database Content Verification")
    print("-" * 40)
    try:
        query = """
            SELECT 
                occupation_code,
                task_name,
                task_risk,
                importance_score
            FROM public.ai_task_taxonomy
            LIMIT 5
        """
        rows = await conn.fetch(query)
        print(f"✅ Found {len(rows)} sample tasks in database")
        
        if rows:
            print("\n📋 Sample Tasks:")
            for row in rows:
                print(f"   - {row['occupation_code']}: {row['task_name'][:40]}...")
                print(f"     Risk: {float(row['task_risk']):.2f}, Importance: {float(row['importance_score']):.2f}")
        else:
            print("⚠️  No sample data found (run migration script?)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Close connection
    await conn.close()
    
    print()
    print("="*60)
    print("✅ TAS CALCULATOR TESTS COMPLETE")
    print("="*60)
    print()
    print("📋 Next steps:")
    print("   1. Implement IVS Calculator (Industry Velocity Score)")
    print("   2. Implement PSC Calculator (Personal Skill Currency)")
    print("   3. Implement AS Calculator (Adaptability Score)")
    print()


if __name__ == "__main__":
    asyncio.run(test_tas_calculator())
