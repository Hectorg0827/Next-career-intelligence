#!/bin/bash
##############################################################################
# NEXT Career Intelligence - Neo4j Backup Script
#
# Purpose: Create backup of Neo4j Talent Graph database
# Usage: ./neo4j-backup.sh
# Schedule: Hourly via cron
##############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/backups/neo4j}"
NEO4J_CONTAINER="${NEO4J_CONTAINER:-next-neo4j-1}"
NEO4J_DATABASE="${NEO4J_DATABASE:-neo4j}"
S3_BUCKET="${S3_BACKUP_BUCKET:-s3://next-career-backups}"
RETENTION_DAYS=7

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Ensure backup directory exists
log_info "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log_error "Docker is not running"
    exit 1
fi

# Check if Neo4j container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${NEO4J_CONTAINER}$"; then
    log_error "Neo4j container '${NEO4J_CONTAINER}' not found"
    log_info "Available containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

# Check if Neo4j container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${NEO4J_CONTAINER}$"; then
    log_warn "Neo4j container is not running. Starting container..."
    docker start "$NEO4J_CONTAINER"
    sleep 10  # Wait for Neo4j to start
fi

BACKUP_FILE="neo4j_${TIMESTAMP}.dump"
CONTAINER_BACKUP_PATH="/backups/${BACKUP_FILE}"
HOST_BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
COMPRESSED_FILE="${HOST_BACKUP_PATH}.gz"

log_info "Starting Neo4j backup: $NEO4J_DATABASE"
log_info "Container backup path: $CONTAINER_BACKUP_PATH"

# Create backup using neo4j-admin
log_info "Running neo4j-admin database dump..."
docker exec "$NEO4J_CONTAINER" neo4j-admin database dump "$NEO4J_DATABASE" \
  --to-path=/backups \
  --overwrite-destination=true \
  2>&1 | tee "${BACKUP_DIR}/neo4j_backup_${TIMESTAMP}.log"

if [ $? -eq 0 ]; then
    log_info "Neo4j dump completed successfully"
else
    log_error "Neo4j dump failed"
    exit 1
fi

# Copy backup from container to host
log_info "Copying backup from container to host..."
docker cp "${NEO4J_CONTAINER}:${CONTAINER_BACKUP_PATH}" "$HOST_BACKUP_PATH"

if [ $? -eq 0 ]; then
    log_info "Backup copied successfully"
else
    log_error "Failed to copy backup from container"
    exit 1
fi

# Get backup size
BACKUP_SIZE=$(du -h "$HOST_BACKUP_PATH" | cut -f1)
log_info "Backup size: $BACKUP_SIZE"

# Compress backup
log_info "Compressing backup..."
gzip "$HOST_BACKUP_PATH"

COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
log_info "Compressed size: $COMPRESSED_SIZE"

# Upload to S3 (if AWS CLI is available)
if command -v aws >/dev/null 2>&1; then
    log_info "Uploading to S3: ${S3_BUCKET}/neo4j/${TIMESTAMP}/"

    aws s3 cp "$COMPRESSED_FILE" \
        "${S3_BUCKET}/neo4j/${TIMESTAMP}/" \
        --storage-class STANDARD_IA \
        --metadata "backup_date=${TIMESTAMP},database=${NEO4J_DATABASE},size=${COMPRESSED_SIZE}"

    if [ $? -eq 0 ]; then
        log_info "S3 upload successful"

        # Clean up container backup (no longer needed)
        log_info "Cleaning up container backup..."
        docker exec "$NEO4J_CONTAINER" rm -f "$CONTAINER_BACKUP_PATH"
    else
        log_error "S3 upload failed"
        exit 1
    fi
else
    log_warn "Skipping S3 upload (AWS CLI not available)"
fi

# Clean up old backups (keep last N days)
log_info "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -type f -delete
find "$BACKUP_DIR" -name "*.log" -mtime +$RETENTION_DAYS -type f -delete

REMAINING_BACKUPS=$(ls -1 "$BACKUP_DIR"/*.gz 2>/dev/null | wc -l)
log_info "Remaining local backups: $REMAINING_BACKUPS"

# Verify backup integrity (optional - can be slow for large backups)
# log_info "Verifying backup integrity..."
# gunzip -t "$COMPRESSED_FILE"

log_info "Neo4j backup process completed successfully"

# Exit with success
exit 0
