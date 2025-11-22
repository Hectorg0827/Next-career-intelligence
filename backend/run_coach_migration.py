#!/usr/bin/env python3
"""
Database Migration Script for AI Coach & Skill Engine
Executes the SQL migration files using psycopg2
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
    """Execute the AI Coach & Skill Engine database migrations"""
    
    # Database connection string
    DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"
    
    # Migration files to run
    migrations = [
        "012_create_coach_memory.sql",
        "013_create_skill_graph.sql"
    ]
    
    print("🔄 Connecting to Supabase database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected successfully")
        
        for migration_file in migrations:
            sql_file = Path(__file__).parent / "migrations" / migration_file
            
            if not sql_file.exists():
                print(f"❌ Error: SQL file not found at {sql_file}")
                sys.exit(1)
                
            print(f"\n📄 Reading SQL file: {migration_file}")
            
            # Read SQL file
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            print(f"📊 Executing migration ({len(sql_content)} characters)...")
            
            # Execute SQL
            cursor.execute(sql_content)
            
            # Commit transaction
            conn.commit()
            print(f"✅ {migration_file} executed successfully")
        
        # Verify tables created
        print("\n🔍 Verifying tables created...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (
                table_name = 'coach_memory' OR 
                table_name = 'skills' OR
                table_name = 'user_skills' OR
                table_name = 'role_skill_templates'
            )
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print(f"\n✅ Tables found ({len(tables)} total):")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE - AI Coach & Skill Engine Database Ready!")
        print("="*60)
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("  AI Coach & Skill Engine")
    print("  Database Migration Script")
    print("="*60)
    print()
    
    run_migration()
