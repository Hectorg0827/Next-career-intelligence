#!/usr/bin/env bash
# Helper script to install deps, run build, lint, and type-check for the frontend
# Produces frontend/build.log with stdout/stderr for analysis
# Usage: ./scripts/run_frontend_checks.sh

set -euo pipefail
cd "$(dirname "$0")/.."
FRONTEND_DIR=frontend
LOG_FILE="$PWD/frontend/build.log"

echo "Running frontend checks and capturing logs to: $LOG_FILE"
# Remove old log
rm -f "$LOG_FILE"

pushd "$FRONTEND_DIR" >/dev/null

# Ensure node exists
if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: node is not installed or not in PATH. Install Node 18+ (recommend using nvm)." | tee -a "$LOG_FILE"
  exit 2
fi

# Use npm ci when package-lock.json present, fallback to npm install
if [ -f package-lock.json ]; then
  echo "Running: npm ci --legacy-peer-deps" | tee -a "$LOG_FILE"
  npm ci --legacy-peer-deps 2>&1 | tee -a "$LOG_FILE"
else
  echo "Running: npm install --legacy-peer-deps" | tee -a "$LOG_FILE"
  npm install --legacy-peer-deps 2>&1 | tee -a "$LOG_FILE"
fi

# Build
echo "Running: npm run build" | tee -a "$LOG_FILE"
npm run build 2>&1 | tee -a "$LOG_FILE" || BUILD_EXIT_CODE=$?

# Lint (if configured)
if npm run | grep -q "lint"; then
  echo "Running: npm run lint --silent" | tee -a "$LOG_FILE"
  npm run lint --silent 2>&1 | tee -a "$LOG_FILE" || true
fi

# Type-check
if [ -f tsconfig.json ]; then
  echo "Running: npx tsc --noEmit" | tee -a "$LOG_FILE"
  npx tsc --noEmit 2>&1 | tee -a "$LOG_FILE" || true
fi

popd >/dev/null

# Print summary
if [ -n "${BUILD_EXIT_CODE-}" ]; then
  echo "BUILD EXITED WITH CODE: ${BUILD_EXIT_CODE}" | tee -a "$LOG_FILE"
else
  echo "BUILD EXITED WITH CODE: 0" | tee -a "$LOG_FILE"
fi

echo "Done. Tail of build log:" 
# show last 200 lines
tail -n 200 "$LOG_FILE"

exit 0
