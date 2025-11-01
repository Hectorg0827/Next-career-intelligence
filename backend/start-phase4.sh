#!/bin/bash

# Phase 4 Backend Startup Script
set -e

cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend

echo "🚀 Starting NEXT Career Intelligence API with Phase 4 improvements..."

# Export PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Find uvicorn
if [ -f "/Users/hectorgarcia/Library/Python/3.9/bin/uvicorn" ]; then
    UV_PATH="/Users/hectorgarcia/Library/Python/3.9/bin/uvicorn"
elif command -v uvicorn &> /dev/null; then
    UV_PATH="uvicorn"
else
    echo "❌ uvicorn not found!"
    exit 1
fi

echo "✓ Using uvicorn at: $UV_PATH"
echo "✓ Starting on http://localhost:8000"
echo ""

# Start server
$UV_PATH app.main:app --reload --host 0.0.0.0 --port 8000
