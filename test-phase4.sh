#!/bin/bash

# Test Phase 4 Features
echo "🧪 Testing Phase 4 Implementation..."
echo ""

# Start backend in background
echo "Starting backend..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for startup
echo "Waiting for backend to start..."
sleep 5

# Test health endpoint
echo ""
echo "1. Testing basic health check..."
curl -s http://localhost:8000/api/health | jq '.' || echo "Failed"

# Test detailed health
echo ""
echo "2. Testing detailed health check..."
curl -s http://localhost:8000/api/health/detailed | jq '.' || echo "Failed"

# Test performance metrics
echo ""
echo "3. Testing performance metrics..."
curl -s http://localhost:8000/api/performance | jq '.' || echo "Failed"

# Test a regular endpoint with caching
echo ""
echo "4. Testing API endpoint (should be cached on 2nd call)..."
echo "First call:"
time curl -s http://localhost:8000/api/health > /dev/null
echo "Second call (should be faster - cached):"
time curl -s http://localhost:8000/api/health > /dev/null

echo ""
echo "✅ Phase 4 testing complete!"
echo ""
echo "Backend is running on PID: $BACKEND_PID"
echo "To stop: kill $BACKEND_PID"
echo "Logs: tail -f backend.log"
