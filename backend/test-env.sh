#!/bin/bash
# Test script to check if the environment is set up correctly

echo "Testing Cloud Run environment setup..."
echo "================================"

# Check if environment variables are available
echo "Checking environment variables..."
python3 << 'EOF'
import os
required_vars = [
    'SUPABASE_URL',
    'SUPABASE_SERVICE_KEY',
    'GEMINI_API_KEY',
    'SUPABASE_ANON_KEY'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var} is set (first 20 chars: {value[:20]}...)")
    else:
        print(f"✗ {var} is NOT set")
EOF

# Try importing the app
echo ""
echo "Testing app import..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
try:
    from app.main import app
    print("✓ Successfully imported FastAPI app")
    print(f"✓ App is: {app}")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    import traceback
    traceback.print_exc()
EOF
