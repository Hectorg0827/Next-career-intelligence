#!/usr/bin/env python3
"""Seed role_skill_templates table"""

import psycopg2

DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"

def seed_role_templates():
    with open('backend/migrations/014_seed_role_templates.sql', 'r') as f:
        sql = f.read()
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        conn.commit()
        print("✅ Role templates seeded successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_role_templates()
