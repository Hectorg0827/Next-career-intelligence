#!/bin/bash
# Start Redis locally with Docker for development/testing
# For production, use managed Redis (AWS ElastiCache, Google Cloud Memorystore, Redis Cloud)

echo "🚀 Starting Redis for AI Displacement Risk Engine..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Redis container already exists
if docker ps -a | grep -q "redis-risk-engine"; then
    echo "📦 Redis container already exists"
    
    # Check if it's running
    if docker ps | grep -q "redis-risk-engine"; then
        echo "✅ Redis is already running"
        docker ps | grep "redis-risk-engine"
    else
        echo "▶️ Starting existing Redis container..."
        docker start redis-risk-engine
        sleep 2
        echo "✅ Redis started successfully"
    fi
else
    echo "📦 Creating new Redis container..."
    docker run -d \
        --name redis-risk-engine \
        -p 6379:6379 \
        -v redis-risk-data:/data \
        redis:7-alpine \
        redis-server --appendonly yes
    
    sleep 3
    
    if docker ps | grep -q "redis-risk-engine"; then
        echo "✅ Redis container created and running"
    else
        echo "❌ Failed to start Redis"
        exit 1
    fi
fi

# Test Redis connection
echo ""
echo "🔍 Testing Redis connection..."
if docker exec redis-risk-engine redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis responding to PING"
else
    echo "❌ Redis not responding"
    exit 1
fi

# Display connection info
echo ""
echo "📊 Redis Connection Info:"
echo "   Host: localhost"
echo "   Port: 6379"
echo "   URL:  redis://localhost:6379/0"
echo ""
echo "🔧 Useful Commands:"
echo "   Stop Redis:  docker stop redis-risk-engine"
echo "   Start Redis: docker start redis-risk-engine"
echo "   Logs:        docker logs redis-risk-engine"
echo "   CLI:         docker exec -it redis-risk-engine redis-cli"
echo "   Remove:      docker rm -f redis-risk-engine"
echo ""
echo "✅ Redis is ready for AI Displacement Risk Engine!"
