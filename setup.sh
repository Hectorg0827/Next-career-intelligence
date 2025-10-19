#!/bin/bash

# NEXT Career Intelligence - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up NEXT | Adaptive Career Intelligence..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js 18 or higher"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo -e "${GREEN}✅ Docker $DOCKER_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Docker not found (optional)${NC}"
fi

echo ""

# Setup Backend
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your API keys${NC}"
else
    echo -e "${GREEN}✅ backend/.env already exists${NC}"
fi

cd ..

echo ""

# Setup Frontend
echo "⚛️  Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env.local file
if [ ! -f ".env.local" ]; then
    echo "Creating frontend .env.local file..."
    cp .env.example .env.local
    echo -e "${YELLOW}⚠️  Please edit frontend/.env.local and add your Firebase config${NC}"
else
    echo -e "${GREEN}✅ frontend/.env.local already exists${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env and add your API keys:"
echo "   - OPENAI_API_KEY (https://platform.openai.com/api-keys)"
echo "   - ONET_API_KEY (https://services.onetcenter.org/reference/)"
echo ""
echo "2. Edit frontend/.env.local and add Firebase config"
echo "   (https://console.firebase.google.com/)"
echo ""
echo "3. Start the development servers:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   cd frontend && npm run dev"
echo ""
echo "Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "📚 See QUICKSTART.md for more details"
