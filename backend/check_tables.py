#!/usr/bin/env python3
import psycopg2

DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute(
    """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'onboarding'
    ORDER BY ordinal_position
"""
)

print("📋 ONBOARDING columns:")
for col, dtype in cursor.fetchall():
    print(f"  - {col} ({dtype})")

cursor.execute(
    """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'user_job_applications'
    ORDER BY ordinal_position
"""
)

print("\n📋 USER_JOB_APPLICATIONS columns:")
for col, dtype in cursor.fetchall():
    print(f"  - {col} ({dtype})")

cursor.close()
conn.close()
