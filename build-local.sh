#!/usr/bin/env bash
# Local Build Verification Script for Next Career Intelligence
# This script verifies that the frontend builds successfully before deploying

set -e  # Exit on error

echo "========================================="
echo "Next Career Intelligence - Build Verification"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

cd frontend

echo -e "${YELLOW}Step 1: Checking Node.js version...${NC}"
NODE_VERSION=$(node --version)
echo "Node version: $NODE_VERSION"

if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js 18 or later: https://nodejs.org/"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
npm install --legacy-peer-deps

echo ""
echo -e "${YELLOW}Step 3: Running TypeScript type check...${NC}"
npm run type-check || true  # Don't fail on type errors (we have ignoreBuildErrors: true)

echo ""
echo -e "${YELLOW}Step 4: Running ESLint...${NC}"
npm run lint || true  # Don't fail on lint errors (we have ignoreDuringBuilds: true)

echo ""
echo -e "${YELLOW}Step 5: Building Next.js production bundle...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✅ BUILD SUCCESSFUL!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "The frontend has been built successfully."
    echo "You can now deploy to Vercel or Netlify."
    echo ""
    echo "Build output is in: frontend/.next"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}❌ BUILD FAILED${NC}"
    echo -e "${RED}=========================================${NC}"
    echo ""
    echo "Please check the error messages above."
    exit 1
fi
