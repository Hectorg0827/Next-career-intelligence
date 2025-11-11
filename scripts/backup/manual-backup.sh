#!/bin/bash
##############################################################################
# NEXT Career Intelligence - Manual Database Backup Script
#
# Purpose: Create manual backup of Supabase PostgreSQL database
# Usage: ./manual-backup.sh
# Schedule: Daily at 2 AM UTC via cron
##############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/backups/supabase}"
DB_NAME="${SUPABASE_DB_NAME:-postgres}"
SUPABASE_HOST="${SUPABASE_HOST:-db.your-project.supabase.co}"
SUPABASE_PASSWORD="${SUPABASE_DB_PASSWORD}"
S3_BUCKET="${S3_BACKUP_BUCKET:-s3://next-career-backups}"
RETENTION_DAYS=3

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

# Check if required tools are installed
command -v pg_dump >/dev/null 2>&1 || {
    log_error "pg_dump is not installed. Install postgresql-client."
    exit 1
}

command -v aws >/dev/null 2>&1 || {
    log_warn "AWS CLI not found. S3 upload will be skipped."
}

# Create backup filename
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

log_info "Starting backup: $DB_NAME"
log_info "Backup file: $BACKUP_FILE"

# Create backup using pg_dump
PGPASSWORD="$SUPABASE_PASSWORD" pg_dump \
  -h "$SUPABASE_HOST" \
  -U postgres \
  -d "$DB_NAME" \
  -F c \
  -b \
  -v \
  -f "$BACKUP_FILE" 2>&1 | tee "${BACKUP_DIR}/backup_${TIMESTAMP}.log"

# Check if backup was successful
if [ $? -eq 0 ]; then
    log_info "Backup completed successfully"
else
    log_error "Backup failed"
    exit 1
fi

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log_info "Backup size: $BACKUP_SIZE"

# Compress backup
log_info "Compressing backup..."
gzip "$BACKUP_FILE"

COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
log_info "Compressed size: $COMPRESSED_SIZE"

# Upload to S3 (if AWS CLI is available)
if command -v aws >/dev/null 2>&1; then
    log_info "Uploading to S3: ${S3_BUCKET}/supabase/${TIMESTAMP}/"

    aws s3 cp "$COMPRESSED_FILE" \
        "${S3_BUCKET}/supabase/${TIMESTAMP}/" \
        --storage-class STANDARD_IA \
        --metadata "backup_date=${TIMESTAMP},db_name=${DB_NAME},size=${COMPRESSED_SIZE}"

    if [ $? -eq 0 ]; then
        log_info "S3 upload successful"
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

# Send notification (optional - requires notification service)
# curl -X POST "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
#   -d "{\"text\":\"✅ Backup completed: ${DB_NAME}_${TIMESTAMP}.dump.gz (${COMPRESSED_SIZE})\"}"

log_info "Backup process completed successfully"

# Exit with success
exit 0
