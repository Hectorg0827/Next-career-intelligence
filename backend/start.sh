#!/bin/bash

# Start Backend Script
# This script properly configures and starts the FastAPI backend

echo "🚀 Starting Career Intelligence Backend..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Export Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY may not be configured in .env"
fi

# Start uvicorn
echo "✅ Starting server on http://localhost:8000"
echo "📚 API docs at http://localhost:8000/docs"
echo ""

python3 -m uvicorn app.main:app --reload --port 8000
