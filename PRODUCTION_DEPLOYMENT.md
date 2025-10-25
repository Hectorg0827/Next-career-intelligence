# 🚀 Production Deployment Guide

## Deploy Next-Career-Intelligence to Production

---

## 📋 Pre-Deployment Checklist

Before deploying, verify all items:

### Backend
- [ ] All Phase 4 endpoints tested and working
- [ ] Database migrations verified on Supabase
- [ ] Environment variables configured:
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_KEY
  - [ ] GOOGLE_API_KEY (Gemini)
  - [ ] FIREBASE_ADMIN_KEY
  - [ ] DEBUG=false

### Frontend
- [ ] All pages tested on mobile and desktop
- [ ] Environment variables configured:
  - [ ] NEXT_PUBLIC_API_URL
  - [ ] NEXT_PUBLIC_FIREBASE_CONFIG
  - [ ] NEXT_PUBLIC_STRIPE_KEY
  - [ ] NODE_ENV=production

### Database
- [ ] Supabase backups enabled
- [ ] All 4 Phase 4 tables created and indexed
- [ ] Replication configured (if needed)

### Testing
- [ ] All E2E tests pass (28/28)
- [ ] No console errors in production build
- [ ] Performance metrics acceptable
- [ ] Mobile responsive verified

---

## 🔧 Production Configuration

### Backend Configuration

**File: `backend/.env.production`**
```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key_here
SUPABASE_JWT_SECRET=your_jwt_secret

# API Configuration
API_URL=https://api.nextcareerintelligence.com
ALLOWED_ORIGINS=https://nextcareerintelligence.com,https://www.nextcareerintelligence.com

# AI Services
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_key_if_needed

# Firebase
FIREBASE_ADMIN_KEY=your_firebase_admin_key

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Logging
DEBUG=false
LOG_LEVEL=info

# Security
SECRET_KEY=generate_with_python_secrets
CORS_ORIGINS=["https://nextcareerintelligence.com"]
```

### Frontend Configuration

**File: `frontend/.env.production`**
```bash
NEXT_PUBLIC_API_URL=https://api.nextcareerintelligence.com
NEXT_PUBLIC_API_TIMEOUT=30000

# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key

# Analytics
NEXT_PUBLIC_GA_ID=G_your_google_analytics_id

# Environment
NODE_ENV=production
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## 🐳 Docker Deployment

### Build Docker Images

**Backend Image:**
```bash
cd backend
docker build -t nextcareer/backend:latest \
  --build-arg ENVIRONMENT=production \
  .
```

**Frontend Image:**
```bash
cd frontend
docker build -t nextcareer/frontend:latest \
  --build-arg ENVIRONMENT=production \
  .
```

### Push to Registry

```bash
# Login to Docker registry
docker login your-registry.com

# Tag images
docker tag nextcareer/backend:latest your-registry.com/nextcareer/backend:v1.0.0
docker tag nextcareer/frontend:latest your-registry.com/nextcareer/frontend:v1.0.0

# Push images
docker push your-registry.com/nextcareer/backend:v1.0.0
docker push your-registry.com/nextcareer/frontend:v1.0.0
```

### Production Docker Compose

**File: `docker-compose.production.yml`**
```yaml
version: '3.8'

services:
  backend:
    image: your-registry.com/nextcareer/backend:v1.0.0
    container_name: nextcareer-backend-prod
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - FIREBASE_ADMIN_KEY=${FIREBASE_ADMIN_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - DEBUG=false
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - nextcareer-network

  frontend:
    image: your-registry.com/nextcareer/frontend:v1.0.0
    container_name: nextcareer-frontend-prod
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_FIREBASE_API_KEY=${NEXT_PUBLIC_FIREBASE_API_KEY}
      - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY}
      - NODE_ENV=production
    restart: always
    depends_on:
      - backend
    networks:
      - nextcareer-network

networks:
  nextcareer-network:
    driver: bridge
```

---

## ☁️ Cloud Deployment Options

### Option 1: Deploy to AWS

**Backend (Elastic Beanstalk):**
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p docker nextcareer-backend --region us-east-1

# Create environment
eb create nextcareer-backend-prod

# Deploy
eb deploy
```

**Frontend (CloudFront + S3):**
```bash
# Build Next.js
cd frontend
npm run build
npm run export

# Upload to S3
aws s3 sync out/ s3://nextcareer-frontend-prod/

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Option 2: Deploy to Google Cloud

**Backend (Cloud Run):**
```bash
# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT/nextcareer-backend

# Deploy to Cloud Run
gcloud run deploy nextcareer-backend \
  --image gcr.io/YOUR_PROJECT/nextcareer-backend:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars SUPABASE_URL=$SUPABASE_URL
```

**Frontend (Firebase Hosting):**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Deploy
firebase deploy --only hosting
```

### Option 3: Deploy to DigitalOcean

**Create App Platform Deployment:**
```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create app spec
cat > app.yaml << EOF
name: nextcareer
services:
- name: backend
  source_dir: backend
  build_command: pip install -r requirements.txt
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8000
  http_port: 8000
  health_check:
    http_path: /api/v1/health
- name: frontend
  source_dir: frontend
  build_command: npm install && npm run build
  run_command: npm run start
  http_port: 3000
EOF

# Deploy
doctl apps create --spec app.yaml
```

---

## 🔐 Security Hardening

### SSL/TLS Certificate
```bash
# Using Let's Encrypt with certbot
certbot certonly --standalone \
  -d api.nextcareerintelligence.com \
  -d nextcareerintelligence.com
```

### Environment Variables Security
```bash
# Encrypt sensitive environment variables
gpg --symmetric backend/.env.production
gpg --symmetric frontend/.env.production

# Decrypt for deployment
gpg --decrypt backend/.env.production.gpg > backend/.env.production
```

### Nginx Reverse Proxy Configuration

**File: `nginx.conf`**
```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 443 ssl http2;
    server_name api.nextcareerintelligence.com;
    
    ssl_certificate /etc/letsencrypt/live/api.nextcareerintelligence.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.nextcareerintelligence.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=100 nodelay;
    }
}

server {
    listen 443 ssl http2;
    server_name nextcareerintelligence.com;
    
    ssl_certificate /etc/letsencrypt/live/nextcareerintelligence.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nextcareerintelligence.com/privkey.pem;
    
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}
```

---

## 📊 Monitoring & Logging

### Application Monitoring

**Install Sentry (Error Tracking):**
```bash
# Backend
pip install sentry-sdk
```

**Backend integration:**
```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/your-project-id",
    environment="production",
    traces_sample_rate=0.1
)
```

### Log Aggregation

**CloudWatch Logs (AWS):**
```bash
# Install CloudWatch agent
aws logs create-log-group --log-group-name /nextcareer/backend
aws logs create-log-stream --log-group-name /nextcareer/backend --log-stream-name prod

# View logs
aws logs tail /nextcareer/backend --follow
```

### Performance Monitoring

**New Relic:**
```bash
# Install agent
pip install newrelic

# Start app with monitoring
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn app.main:app
```

---

## ✅ Post-Deployment Verification

### 1. Health Checks

```bash
# Backend health
curl https://api.nextcareerintelligence.com/api/v1/health

# Expected response:
# {"status": "ok", "timestamp": "2025-10-23T..."}
```

```bash
# Frontend accessibility
curl https://nextcareerintelligence.com

# Should return HTML
```

### 2. Database Connectivity

```bash
# Test from backend
curl https://api.nextcareerintelligence.com/api/v1/marketplace/jobs?limit=1

# Should return job data
```

### 3. Authentication

```bash
# Test Firebase auth
curl -X POST https://api.nextcareerintelligence.com/api/v1/auth/test \
  -H "Authorization: Bearer YOUR_TEST_TOKEN"
```

### 4. API Response Time

```bash
# Check endpoint performance
time curl https://api.nextcareerintelligence.com/api/v1/marketplace/jobs

# Should respond in < 500ms
```

### 5. Frontend Rendering

```bash
# Open browser and test:
# 1. Home page loads
# 2. Login works
# 3. Job browse page loads
# 4. Can search jobs
# 5. Can apply to job
# 6. Application tracking works
```

---

## 📈 Rollback Plan

### If Deployment Fails

**Backend Rollback:**
```bash
# Revert to previous version
docker pull your-registry.com/nextcareer/backend:v1.0.0-previous
docker stop nextcareer-backend-prod
docker run -d --name nextcareer-backend-prod \
  your-registry.com/nextcareer/backend:v1.0.0-previous
```

**Frontend Rollback:**
```bash
# AWS S3 rollback
aws s3 sync s3://nextcareer-frontend-previous s3://nextcareer-frontend-prod/

# Invalidate cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Database Rollback

```bash
# Restore from Supabase backup
# 1. Log into Supabase dashboard
# 2. Go to Backups section
# 3. Select previous backup
# 4. Click "Restore"
```

---

## 📞 Support & Monitoring

### Alert Configuration

**Slack Notifications:**
```bash
# Setup Slack webhook for alerts
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK \
  -H 'Content-Type: application/json' \
  -d '{"text":"Deployment to production complete"}'
```

### On-Call Monitoring

- **Backend downtime alert**: < 1 minute
- **Database disconnect alert**: < 5 minutes
- **High error rate alert**: > 5% errors
- **Slow response alert**: > 1 second average

---

## ✨ Launch Checklist

### Pre-Launch (24 hours before)
- [ ] Final security audit completed
- [ ] Database backups verified
- [ ] SSL certificates renewed
- [ ] DNS records configured
- [ ] Email notifications setup

### Launch Day
- [ ] Deploy to staging environment first
- [ ] Run full test suite in staging
- [ ] Verify all integrations (Firebase, Stripe, Supabase)
- [ ] Deploy to production
- [ ] Monitor error rates
- [ ] Verify user signups work
- [ ] Test payment flow
- [ ] Monitor API response times

### Post-Launch (First 24 hours)
- [ ] Monitor for errors every hour
- [ ] Check user signups and engagement
- [ ] Verify email confirmations arrive
- [ ] Test with real payment (small amount)
- [ ] Monitor database performance
- [ ] Check backup integrity

---

## 🎉 You're Live!

Your Next-Career-Intelligence platform is now in production! 

### Next Steps:
1. **Monitor**: Watch metrics in first week
2. **Feedback**: Gather user feedback and bug reports
3. **Optimize**: Based on usage patterns
4. **Scale**: Increase capacity if needed

---

**Generated:** October 23, 2025  
**Version:** 1.0.0  
**Status:** Production Ready  
**Launch Date:** [Your Date Here]
