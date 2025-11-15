#!/bin/bash
# Phase 1 Foundation - Quick Start Script

echo "🚀 Career OS - Phase 1 Foundation Setup"
echo "========================================"
echo ""

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed"
    echo "   Install it with:"
    echo "   - macOS: brew install redis"
    echo "   - Linux: apt-get install redis"
    exit 1
fi

echo "✅ Redis is installed"

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo "🔄 Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis started successfully"
    else
        echo "❌ Failed to start Redis"
        exit 1
    fi
else
    echo "✅ Redis is already running"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
cd backend
pip install -q redis[hiredis]==5.2.1

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check database schema
echo ""
echo "🗄️  Database Setup"
echo "   To apply the schema, run:"
echo "   psql \$DATABASE_URL -f backend/database/phase1_foundation_schema.sql"
echo ""

# Create .env if doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database
DATABASE_URL=your_supabase_url_here

# Redis
REDIS_URL=redis://localhost:6379

# Existing variables...
EOF
    echo "✅ Created .env file (update DATABASE_URL)"
else
    echo "✅ .env file exists"
fi

echo ""
echo "✅ Phase 1 Foundation Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. Update DATABASE_URL in .env"
echo "2. Apply database schema (see command above)"
echo "3. Integrate services (see PHASE1_INTEGRATION_GUIDE.md)"
echo "4. Start orchestrator service"
echo ""
echo "📖 Full guide: PHASE1_INTEGRATION_GUIDE.md"
