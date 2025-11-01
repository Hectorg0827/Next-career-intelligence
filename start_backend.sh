#!/bin/bash

# Start Backend Server Script
# This script starts the backend server with correct PYTHONPATH

cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend

# Set PYTHONPATH to backend directory
export PYTHONPATH=/Users/hectorgarcia/Desktop/Next-career-intelligence/backend:$PYTHONPATH

echo "🚀 Starting NEXT Career Intelligence Backend..."
echo "   Port: 8000"
echo "   Environment: Production"
echo ""

# Start uvicorn
/Users/hectorgarcia/Library/Python/3.9/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

