#!/usr/bin/env python3
"""
Check database schema
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print("📊 Database Tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n" + "="*60)
    
    # Get columns for each important table
    for table_name in ['users', 'jobs', 'applications']:
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            print(f"\n📋 {table_name.upper()} columns:")
            for col, dtype in columns:
                print(f"  - {col} ({dtype})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
