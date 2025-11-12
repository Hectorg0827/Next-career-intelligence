#!/usr/bin/env python3
"""
Apply database optimizations to Supabase
"""
import os
import sys

# Read the SQL file
sql_file = "/Users/hectorgarcia/Desktop/Next-career-intelligence/backend/app/db/optimizations_v2.sql"
with open(sql_file, "r") as f:
    sql_content = f.read()

# Database connection
DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"

try:
    import psycopg2

    print("🔌 Connecting to Supabase database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("📝 Applying database optimizations...")

    # Execute the SQL
    cursor.execute(sql_content)
    conn.commit()

    print("✅ Database optimizations applied successfully!")

    # Get some stats
    cursor.execute(
        """
        SELECT schemaname, tablename, indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public' AND indexname LIKE 'idx_%'
        ORDER BY tablename, indexname
    """
    )

    indexes = cursor.fetchall()
    print(f"\n📊 Total custom indexes created: {len(indexes)}")

    cursor.close()
    conn.close()

except ImportError:
    print("❌ Error: psycopg2 not installed")
    print("Installing psycopg2-binary...")
    os.system("/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m pip install psycopg2-binary")
    print("\nPlease run this script again.")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error applying optimizations: {e}")
    sys.exit(1)
