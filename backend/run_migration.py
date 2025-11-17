#!/usr/bin/env python3
"""
Database Migration Script for Phase 3: AI Displacement Risk Engine
Executes the SQL migration file using psycopg2
"""

import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("Error: psycopg2 not installed. Installing now...")
    os.system("pip3 install psycopg2-binary")
    import psycopg2
    from psycopg2 import sql

def run_migration():
    """Execute the Phase 3 database migration"""
    
    # Database connection string
    DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"
    
    # SQL file path
    sql_file = Path(__file__).parent / "database" / "phase3_displacement_risk_schema.sql"
    
    if not sql_file.exists():
        print(f"❌ Error: SQL file not found at {sql_file}")
        sys.exit(1)
    
    print("🔄 Connecting to Supabase database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected successfully")
        print(f"📄 Reading SQL file: {sql_file}")
        
        # Read SQL file
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        print(f"📊 Executing migration ({len(sql_content)} characters)...")
        
        # Execute SQL
        cursor.execute(sql_content)
        
        # Commit transaction
        conn.commit()
        
        print("✅ Migration executed successfully")
        
        # Verify tables created
        print("\n🔍 Verifying tables created...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (
                table_name LIKE '%task%' OR 
                table_name LIKE '%risk%' OR
                table_name LIKE '%skill_demand%' OR
                table_name LIKE '%automation%' OR
                table_name LIKE '%user_action%'
            )
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print(f"\n✅ Tables created ({len(tables)} total):")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check for the 6 expected tables
        expected_tables = [
            'ai_task_taxonomy',
            'automation_evidence',
            'skill_demand_history',
            'user_action_log',
            'risk_calculation_snapshots',
            'risk_percentiles_by_role'
        ]
        
        table_names = [t[0] for t in tables]
        missing_tables = [t for t in expected_tables if t not in table_names]
        
        if missing_tables:
            print(f"\n⚠️  Warning: Missing tables: {missing_tables}")
        else:
            print("\n✅ All 6 expected tables created successfully!")
        
        # Check row counts (should have sample data)
        print("\n📊 Row counts:")
        for table in expected_tables:
            if table in table_names:
                cursor.execute(f"SELECT COUNT(*) FROM public.{table}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count} rows")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE - Phase 3 Database Ready!")
        print("="*60)
        print("\n📋 Next steps:")
        print("   1. Create service directory structure (15 minutes)")
        print("   2. Implement data models (1 hour)")
        print("   3. Start building calculators")
        print("\n🚀 You're ready for Day 2!")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("  Phase 3: AI Displacement Risk Engine")
    print("  Database Migration Script")
    print("="*60)
    print()
    
    run_migration()
