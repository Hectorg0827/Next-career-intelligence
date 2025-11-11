# 🔐 Backup and Disaster Recovery Plan
## NEXT Career Intelligence Platform

**Version:** 1.0
**Last Updated:** November 10, 2025
**Review Cycle:** Quarterly

---

## 📋 Executive Summary

This document outlines the backup, disaster recovery, and business continuity procedures for NEXT Career Intelligence. It defines Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), and step-by-step recovery procedures.

**Critical Metrics:**
- **RTO (Recovery Time Objective):** 1 hour
- **RPO (Recovery Point Objective):** 15 minutes
- **Target Uptime:** 99.9% (8.76 hours downtime/year)

---

## 🗄️ Data Classification

### Critical Data (Tier 1)
**RPO: 15 minutes | RTO: 1 hour**

- User accounts and authentication data
- Resume content and tailored versions
- Job applications and tracking
- Payment and subscription records
- Career Health Score history

**Backup Strategy:** Real-time replication + hourly snapshots

### Important Data (Tier 2)
**RPO: 1 hour | RTO: 4 hours**

- AI conversation history (Career Coach)
- Interview session recordings and feedback
- RFT feedback data
- Neo4j Talent Graph data
- User preferences and settings

**Backup Strategy:** Hourly backups + daily snapshots

### Non-Critical Data (Tier 3)
**RPO: 24 hours | RTO: 24 hours**

- Analytics and usage logs
- System logs
- Cached data
- Temporary files

**Backup Strategy:** Daily backups + weekly archives

---

## 💾 Backup Configuration

### 1. Supabase (PostgreSQL) Backups

#### Automated Backups

```yaml
# Supabase Backup Configuration
backup_schedule:
  type: automated
  frequency: continuous
  point_in_time_recovery: enabled

daily_backups:
  frequency: every_24_hours
  time: 02:00 UTC
  retention: 30 days

hourly_snapshots:
  frequency: every_hour
  retention: 7 days

monthly_archives:
  frequency: first_of_month
  retention: 12 months
```

#### Enable Supabase Backups (Production)

**Step 1: Access Supabase Dashboard**
```bash
# Navigate to: https://app.supabase.com/project/[YOUR_PROJECT_ID]/settings/database
```

**Step 2: Enable Point-in-Time Recovery (PITR)**
```
Settings → Database → Backups
- Enable "Point in Time Recovery"
- Retention: 7 days (Pro plan)
```

**Step 3: Configure Automated Backups**
```
Settings → Database → Backups
- Daily backups: Enabled
- Backup time: 02:00 UTC
- Retention: 30 days
```

**Step 4: Verify Backup Status**
```sql
-- Run in SQL Editor to check backup status
SELECT
  backup_date,
  backup_size_bytes / 1024 / 1024 AS size_mb,
  backup_type,
  status
FROM _supabase_backup_status
ORDER BY backup_date DESC
LIMIT 10;
```

#### Manual Backup Script

```bash
#!/bin/bash
# manual-backup.sh - Create manual database backup

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/supabase"
DB_NAME="next_career_db"

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Create backup using pg_dump
PGPASSWORD=$SUPABASE_DB_PASSWORD pg_dump \
  -h $SUPABASE_HOST \
  -U postgres \
  -d $DB_NAME \
  -F c \
  -b \
  -v \
  -f "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# Compress backup
gzip "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# Upload to S3
aws s3 cp \
  "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump.gz" \
  "s3://next-career-backups/supabase/${TIMESTAMP}/"

# Delete local backup (keep last 3 days)
find $BACKUP_DIR -name "*.gz" -mtime +3 -delete

echo "Backup completed: ${DB_NAME}_${TIMESTAMP}.dump.gz"
```

**Make script executable:**
```bash
chmod +x manual-backup.sh
```

**Schedule daily backups via cron:**
```cron
# Run daily at 2 AM UTC
0 2 * * * /path/to/manual-backup.sh >> /var/log/backup.log 2>&1
```

---

### 2. Neo4j Talent Graph Backups

#### Automated Backup Script

```bash
#!/bin/bash
# neo4j-backup.sh - Backup Neo4j Talent Graph

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/neo4j"
NEO4J_CONTAINER="next-neo4j-1"

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Create backup using neo4j-admin
docker exec $NEO4J_CONTAINER neo4j-admin database dump neo4j \
  --to=/backups/neo4j_${TIMESTAMP}.dump

# Copy from container to host
docker cp $NEO4J_CONTAINER:/backups/neo4j_${TIMESTAMP}.dump $BACKUP_DIR/

# Compress backup
gzip "$BACKUP_DIR/neo4j_${TIMESTAMP}.dump"

# Upload to S3
aws s3 cp \
  "$BACKUP_DIR/neo4j_${TIMESTAMP}.dump.gz" \
  "s3://next-career-backups/neo4j/${TIMESTAMP}/"

# Delete local backup (keep last 7 days)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Neo4j backup completed: neo4j_${TIMESTAMP}.dump.gz"
```

**Make script executable:**
```bash
chmod +x neo4j-backup.sh
```

**Schedule hourly backups:**
```cron
# Run every hour
0 * * * * /path/to/neo4j-backup.sh >> /var/log/neo4j-backup.log 2>&1
```

#### Neo4j Backup Configuration

```yaml
# docker-compose.neo4j.yml - Add backup volume
services:
  neo4j:
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - ./backups/neo4j:/backups  # Add backup mount
```

---

### 3. Application Code & Configuration

#### Git Repository Backup

```bash
# Automatic push to GitHub (primary)
git push origin main

# Mirror to GitLab (backup)
git remote add gitlab git@gitlab.com:your-org/next-career.git
git push gitlab main --mirror

# Backup to S3 as tar.gz archive
git archive --format=tar.gz --prefix=next-career/ HEAD \
  > next-career-$(date +%Y%m%d).tar.gz
aws s3 cp next-career-*.tar.gz s3://next-career-backups/code/
```

#### Environment Variables Backup

```bash
# Backup .env files (NEVER commit to git)
tar -czf env-backup-$(date +%Y%m%d).tar.gz \
  backend/.env \
  frontend/.env.local

# Encrypt before uploading
gpg --symmetric --cipher-algo AES256 env-backup-*.tar.gz

# Upload encrypted backup
aws s3 cp env-backup-*.tar.gz.gpg s3://next-career-backups/config/

# Delete local copy
rm env-backup-*
```

---

### 4. Redis Cache Backup

```bash
#!/bin/bash
# redis-backup.sh - Backup Redis data

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/redis"

mkdir -p $BACKUP_DIR

# Trigger Redis BGSAVE
redis-cli BGSAVE

# Wait for save to complete
while [ $(redis-cli LASTSAVE) -eq $(redis-cli LASTSAVE) ]; do
  sleep 1
done

# Copy RDB file
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/dump_${TIMESTAMP}.rdb"

# Compress
gzip "$BACKUP_DIR/dump_${TIMESTAMP}.rdb"

# Upload to S3
aws s3 cp "$BACKUP_DIR/dump_${TIMESTAMP}.rdb.gz" \
  "s3://next-career-backups/redis/${TIMESTAMP}/"

# Keep last 24 hours only
find $BACKUP_DIR -name "*.gz" -mtime +1 -delete
```

---

## 🔄 Backup Testing Schedule

**Monthly Test (1st Monday):**
- Restore Supabase backup to test environment
- Verify data integrity
- Test application functionality
- Document any issues

**Quarterly Test (1st Monday of Q):**
- Full disaster recovery drill
- Restore all systems from backups
- Measure actual RTO
- Update runbook with learnings

**Bi-Annual Test (January & July):**
- Executive-level disaster recovery simulation
- Test communication procedures
- Verify contact information
- Update business continuity plan

---

## 🚨 Disaster Recovery Procedures

### Scenario 1: Database Corruption

**Symptoms:**
- Application errors related to database queries
- Data inconsistencies
- Failed transactions

**Recovery Steps:**

1. **Stop Application** (2 minutes)
   ```bash
   # Stop Cloud Run services
   gcloud run services update next-backend --region us-central1 --no-traffic
   ```

2. **Assess Damage** (5 minutes)
   ```sql
   -- Check for corrupted tables
   SELECT schemaname, tablename
   FROM pg_tables
   WHERE schemaname = 'public';

   -- Verify data integrity
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM resumes;
   ```

3. **Restore from Backup** (20 minutes)
   ```bash
   # Download latest backup
   aws s3 cp s3://next-career-backups/supabase/latest/ ./backup.dump.gz

   # Decompress
   gunzip backup.dump.gz

   # Restore to temporary database
   pg_restore -h $SUPABASE_HOST -U postgres -d next_career_db_temp backup.dump

   # Verify restored data
   psql -h $SUPABASE_HOST -U postgres -d next_career_db_temp -c "SELECT COUNT(*) FROM users;"
   ```

4. **Switch to Restored Database** (5 minutes)
   ```bash
   # Rename databases
   psql -h $SUPABASE_HOST -U postgres <<EOF
   ALTER DATABASE next_career_db RENAME TO next_career_db_corrupted;
   ALTER DATABASE next_career_db_temp RENAME TO next_career_db;
   EOF
   ```

5. **Restart Application** (5 minutes)
   ```bash
   # Route traffic back
   gcloud run services update next-backend --region us-central1 --traffic latest=100
   ```

6. **Verify Recovery** (10 minutes)
   - Test user login
   - Test resume upload
   - Test job application
   - Monitor error logs

**Total RTO:** ~47 minutes (within 1-hour target)

---

### Scenario 2: Total Data Center Outage

**Symptoms:**
- All services unreachable
- Cloud provider region down
- Network connectivity lost

**Recovery Steps:**

1. **Activate Incident Response Team** (5 minutes)
   - Alert on-call engineer
   - Notify engineering team
   - Update status page

2. **Assess Scope** (10 minutes)
   - Check cloud provider status page
   - Verify regional outage
   - Estimate recovery time

3. **Fail Over to Backup Region** (30 minutes)
   ```bash
   # Deploy to backup region (us-east1)
   gcloud run deploy next-backend \
     --region us-east1 \
     --image gcr.io/next-career/backend:latest

   gcloud run deploy next-frontend \
     --region us-east1 \
     --image gcr.io/next-career/frontend:latest
   ```

4. **Restore Databases** (30 minutes)
   ```bash
   # Restore Supabase from latest backup
   # (Supabase handles multi-region automatically)

   # Restore Neo4j
   docker run -d --name neo4j-restore \
     -v /backups/neo4j:/backups \
     neo4j:5.15.0

   docker exec neo4j-restore neo4j-admin database load neo4j \
     --from=/backups/neo4j_latest.dump
   ```

5. **Update DNS** (15 minutes)
   ```bash
   # Update Cloudflare DNS to point to new region
   # Or use automated failover
   ```

6. **Verify Services** (10 minutes)
   - Test all critical user flows
   - Monitor error rates
   - Check database connections

**Total RTO:** ~100 minutes (exceeds target, requires multi-region setup)

**Prevention:**
- Implement active-active multi-region deployment
- Use global load balancer (Cloudflare)
- Enable automatic failover

---

### Scenario 3: Accidental Data Deletion

**Symptoms:**
- User reports missing data
- Admin accidentally deleted records
- Bulk delete operation error

**Recovery Steps:**

1. **Stop Further Damage** (2 minutes)
   ```bash
   # Revoke admin access immediately
   # Stop application if needed
   ```

2. **Identify Deleted Data** (10 minutes)
   ```sql
   -- Check audit logs
   SELECT * FROM audit_logs
   WHERE action = 'DELETE'
   AND created_at > NOW() - INTERVAL '1 hour';
   ```

3. **Restore from Point-in-Time** (15 minutes)
   ```bash
   # Supabase PITR - Restore to 5 minutes before deletion
   # Via Supabase Dashboard:
   # Settings → Database → Backups → Point in Time Recovery
   # Select timestamp before deletion
   ```

4. **Verify Restored Data** (5 minutes)
   ```sql
   -- Verify records restored
   SELECT COUNT(*) FROM users WHERE deleted_at IS NULL;
   ```

5. **Resume Operations** (5 minutes)
   - Notify affected users
   - Re-enable application
   - Monitor for issues

**Total RTO:** ~37 minutes (within 1-hour target)

---

## 📊 Backup Monitoring & Alerts

### Automated Monitoring

```yaml
# monitoring-config.yaml
backup_alerts:
  - name: supabase_backup_failed
    condition: last_backup_age > 25 hours
    severity: critical
    notify: pagerduty

  - name: neo4j_backup_failed
    condition: last_backup_age > 2 hours
    severity: high
    notify: slack

  - name: backup_size_anomaly
    condition: backup_size < (avg_size * 0.5)
    severity: medium
    notify: email

  - name: backup_restore_test_overdue
    condition: last_test_date > 32 days
    severity: medium
    notify: email
```

### Monitoring Dashboard

**Key Metrics:**
- Last successful backup timestamp
- Backup size trend
- Restore test success rate
- Storage utilization
- Backup duration

**Access:** https://monitoring.nextcareer.ai/backups

---

## 👥 Roles & Responsibilities

### Backup Administrator
**Primary:** DevOps Lead
**Backup:** CTO

**Responsibilities:**
- Configure and maintain backup systems
- Monitor backup health
- Perform quarterly restore tests
- Update backup procedures

### Incident Commander
**Primary:** CTO
**Backup:** Engineering Manager

**Responsibilities:**
- Declare disaster
- Coordinate recovery efforts
- Communicate with stakeholders
- Make go/no-go decisions

### Recovery Team
**Members:** All engineers

**Responsibilities:**
- Execute recovery procedures
- Verify data integrity
- Test application functionality
- Document recovery process

---

## 📞 Emergency Contacts

```
Incident Commander: [REDACTED]
Backup Admin: [REDACTED]
Supabase Support: support@supabase.com (Pro plan: priority)
Google Cloud Support: 1-877-355-5787 (P1: 15-min response)
Cloudflare Support: https://dash.cloudflare.com/
```

---

## 🔐 Security Considerations

### Backup Encryption

**At Rest:**
- Supabase: AES-256 encryption (default)
- S3: Server-side encryption (SSE-S3)
- Neo4j dumps: GPG encryption before upload

**In Transit:**
- TLS 1.3 for all data transfers
- VPN for backup operations
- Signed URLs for S3 access

### Access Control

```yaml
# IAM Policy for Backup Access
backup_access:
  users:
    - backup-service-account
  permissions:
    - s3:PutObject
    - s3:GetObject
    - s3:ListBucket
  resources:
    - s3://next-career-backups/*
  conditions:
    - ip_address: company_vpn_only
    - mfa_required: true
```

---

## 📈 Continuous Improvement

### Monthly Review
- Backup success rate
- Storage costs
- Recovery time trends
- Incident learnings

### Quarterly Goals
- Q1 2026: Implement multi-region active-active
- Q2 2026: Reduce RTO to 30 minutes
- Q3 2026: Automate restore testing
- Q4 2026: Achieve 99.99% uptime

---

## 📝 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-10 | 1.0 | Initial backup and recovery plan | Claude |

---

## ✅ Pre-Launch Checklist

- [ ] Supabase automated backups enabled
- [ ] Supabase PITR enabled (7-day retention)
- [ ] Neo4j backup script scheduled (hourly)
- [ ] S3 backup bucket created with versioning
- [ ] Backup monitoring alerts configured
- [ ] Manual backup scripts tested
- [ ] Restore procedure tested in staging
- [ ] Full disaster recovery drill completed
- [ ] Emergency contacts verified
- [ ] Runbook reviewed by team
- [ ] Backup documentation committed to repo

---

**This document should be reviewed quarterly and updated after any infrastructure changes or disaster recovery events.**
