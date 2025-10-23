#!/bin/bash

# Navigate to backend directory
cd "$(dirname "$0")"

# Start Uvicorn server
python3 -m uvicorn app.main:app --reload --reload-exclude='venv/*' --port 8000
