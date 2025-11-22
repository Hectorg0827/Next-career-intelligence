import os
import sys
import psycopg2

DATABASE_URL = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"

def check_schema():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'skills';
        """)
        
        columns = cursor.fetchall()
        print("Columns in 'skills' table:")
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
