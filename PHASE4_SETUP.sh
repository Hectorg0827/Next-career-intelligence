#!/bin/bash

# Phase 4 Performance & Reliability Setup Script
# This script configures the environment for Phase 4 improvements

set -e

echo "🚀 Phase 4 Setup - Performance & Reliability"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env${NC}"
fi

# Add Phase 4 environment variables if they don't exist
echo -e "${BLUE}📝 Configuring Phase 4 environment variables...${NC}"

# Function to add env variable if it doesn't exist
add_env_var() {
    local key=$1
    local value=$2
    local file=$3
    
    if ! grep -q "^${key}=" "$file"; then
        echo "${key}=${value}" >> "$file"
        echo -e "${GREEN}✓ Added ${key}${NC}"
    else
        echo -e "${YELLOW}  ${key} already exists${NC}"
    fi
}

# Redis Configuration
echo -e "\n${BLUE}Redis Configuration:${NC}"
add_env_var "REDIS_HOST" "localhost" "backend/.env"
add_env_var "REDIS_PORT" "6379" "backend/.env"
add_env_var "REDIS_PASSWORD" "" "backend/.env"
add_env_var "REDIS_DB" "0" "backend/.env"
add_env_var "REDIS_ENABLED" "true" "backend/.env"

# Cache Configuration
echo -e "\n${BLUE}Cache Configuration:${NC}"
add_env_var "CACHE_TTL" "3600" "backend/.env"
add_env_var "CACHE_ENABLED" "true" "backend/.env"

# Rate Limiting Configuration
echo -e "\n${BLUE}Rate Limiting Configuration:${NC}"
add_env_var "RATE_LIMIT_ENABLED" "true" "backend/.env"
add_env_var "RATE_LIMIT_PER_MINUTE" "60" "backend/.env"
add_env_var "RATE_LIMIT_PER_HOUR" "1000" "backend/.env"

# Monitoring Configuration
echo -e "\n${BLUE}Monitoring Configuration:${NC}"
add_env_var "SENTRY_DSN" "" "backend/.env"
add_env_var "SENTRY_ENVIRONMENT" "development" "backend/.env"
add_env_var "SENTRY_ENABLED" "false" "backend/.env"

# Performance Configuration
echo -e "\n${BLUE}Performance Configuration:${NC}"
add_env_var "ENABLE_COMPRESSION" "true" "backend/.env"
add_env_var "COMPRESSION_LEVEL" "6" "backend/.env"
add_env_var "MAX_WORKERS" "4" "backend/.env"

# AI Service Configuration
echo -e "\n${BLUE}AI Service Configuration:${NC}"
add_env_var "AI_REQUEST_TIMEOUT" "30" "backend/.env"
add_env_var "AI_MAX_RETRIES" "3" "backend/.env"
add_env_var "AI_CIRCUIT_BREAKER_THRESHOLD" "5" "backend/.env"
add_env_var "AI_CIRCUIT_BREAKER_TIMEOUT" "60" "backend/.env"

# Database Pooling Configuration
echo -e "\n${BLUE}Database Pooling Configuration:${NC}"
add_env_var "DB_POOL_SIZE" "20" "backend/.env"
add_env_var "DB_MAX_OVERFLOW" "10" "backend/.env"
add_env_var "DB_POOL_TIMEOUT" "30" "backend/.env"

echo -e "\n${GREEN}✓ Environment variables configured!${NC}"

# Check if Redis is running
echo -e "\n${BLUE}🔍 Checking Redis status...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis is not running. Start it with: redis-server${NC}"
        echo -e "${YELLOW}   Or install with: brew install redis (macOS)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis is not installed.${NC}"
    echo -e "${YELLOW}   Install with: brew install redis (macOS)${NC}"
fi

# Install Python dependencies
echo -e "\n${BLUE}📦 Installing Python dependencies...${NC}"
if [ -f backend/requirements.txt ]; then
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

echo -e "\n${GREEN}✓ Phase 4 setup complete!${NC}"
echo -e "\n${BLUE}Next Steps:${NC}"
echo -e "1. Make sure Redis is running: ${YELLOW}redis-server${NC}"
echo -e "2. Update SENTRY_DSN in backend/.env if you want error monitoring"
echo -e "3. Start the backend: ${YELLOW}cd backend && uvicorn app.main:app --reload${NC}"
echo -e "4. Check health: ${YELLOW}curl http://localhost:8000/health${NC}"
echo -e "5. View metrics: ${YELLOW}http://localhost:8000/metrics${NC}"
echo -e "\n${BLUE}📚 Documentation: See PHASE4_IMPLEMENTATION_GUIDE.md for details${NC}"
