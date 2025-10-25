# 🚀 Google Cloud Run Deployment Guide

## Quick Start (Recommended)

### Prerequisites
1. Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
2. Run: `gcloud auth login`
3. Have your Gemini API key ready: `9c6779342f509f9f39e21adf9e3ec54d4ac5df70`

### One-Command Deployment

```bash
chmod +x quick-deploy.sh
./quick-deploy.sh
```

This will:
- ✅ Build your Docker container automatically
- ✅ Deploy to Google Cloud Run
- ✅ Configure environment variables
- ✅ Set up autoscaling (0-10 instances)
- ✅ Return your public backend URL

---

## Manual Deployment Steps

### 1. Install Google Cloud CLI

**macOS:**
```bash
brew install google-cloud-sdk
```

**Or download from:** https://cloud.google.com/sdk/docs/install

### 2. Authenticate

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 4. Deploy Backend

```bash
cd backend

gcloud run deploy next-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars "GEMINI_API_KEY=9c6779342f509f9f39e21adf9e3ec54d4ac5df70,ENVIRONMENT=production,DEV_MODE=false"
```

### 5. Get Your Backend URL

```bash
gcloud run services describe next-backend \
  --region us-central1 \
  --format 'value(status.url)'
```

Example output: `https://next-backend-abc123-uc.a.run.app`

---

## Update Frontend Configuration

After deployment, update your frontend environment variables:

**File:** `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=https://next-backend-abc123-uc.a.run.app
```

Replace with your actual Cloud Run URL.

---

## Environment Variables Set on Cloud Run

| Variable | Value | Description |
|----------|-------|-------------|
| `GEMINI_API_KEY` | `9c6779342f509f9f39e21adf9e3ec54d4ac5df70` | Google Gemini AI API key |
| `ENVIRONMENT` | `production` | Runtime environment |
| `DEV_MODE` | `false` | Disables development features |
| `PORT` | `8000` | Container port (auto-set by Cloud Run) |

---

## Cloud Run Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| **Region** | `us-central1` | Iowa, USA (low latency) |
| **CPU** | 2 cores | Handles concurrent requests |
| **Memory** | 2 GB | Sufficient for AI processing |
| **Min Instances** | 0 | Scales to zero when idle (cost savings) |
| **Max Instances** | 10 | Auto-scales under load |
| **Timeout** | 300s (5 min) | Allows for long AI analysis |
| **Authentication** | Public | No auth required (handled by app) |

---

## Testing Your Deployment

### 1. Health Check
```bash
curl https://YOUR-URL/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

### 2. API Documentation
Visit: `https://YOUR-URL/docs`

### 3. Test Analysis Endpoint
```bash
curl -X POST "https://YOUR-URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"job_title": "Software Engineer"}'
```

---

## Monitoring & Logs

### View Logs
```bash
gcloud run services logs read next-backend --region us-central1
```

### View Metrics
Go to: [Cloud Run Console](https://console.cloud.google.com/run)

Metrics available:
- Request count
- Response latency
- Error rate
- Container CPU/Memory usage
- Instance count

---

## Cost Optimization

Cloud Run pricing (Pay-per-use):
- **First 2 million requests/month**: FREE
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GB-second
- **Requests**: $0.40 per million

**Estimated monthly cost for moderate traffic**: $5-20/month

**Scale to zero**: When idle, you pay nothing (min instances = 0)

---

## Updating Your Deployment

### Redeploy with Changes
```bash
cd backend
gcloud run deploy next-backend --source . --region us-central1
```

### Update Environment Variables Only
```bash
gcloud run services update next-backend \
  --region us-central1 \
  --set-env-vars "NEW_VAR=value"
```

### Rollback to Previous Version
```bash
gcloud run services update-traffic next-backend \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

---

## Custom Domain (Optional)

### 1. Map Custom Domain
```bash
gcloud run domain-mappings create \
  --service next-backend \
  --domain api.yourdomain.com \
  --region us-central1
```

### 2. Update DNS
Add the DNS records shown by gcloud to your domain provider.

### 3. Update Frontend
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')
```

### Service Errors
```bash
# View recent errors
gcloud run services logs read next-backend --limit=50 | grep ERROR
```

### Slow Startup
- Increase `--cpu` and `--memory`
- Use `--min-instances 1` to keep one instance warm

### Authentication Issues
```bash
# Make service public
gcloud run services add-iam-policy-binding next-backend \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

---

## Security Best Practices

### 1. Use Secret Manager (Recommended)
```bash
# Store Gemini API key in Secret Manager
echo -n "9c6779342f509f9f39e21adf9e3ec54d4ac5df70" | \
  gcloud secrets create gemini-api-key --data-file=-

# Update service to use secret
gcloud run services update next-backend \
  --region us-central1 \
  --update-secrets GEMINI_API_KEY=gemini-api-key:latest
```

### 2. Enable CORS
Already configured in `app/main.py`

### 3. Rate Limiting
Consider adding Cloud Armor for DDoS protection

---

## Next Steps

1. ✅ Deploy backend to Cloud Run
2. ✅ Test all endpoints
3. ✅ Update frontend API URL
4. ✅ Deploy frontend to Vercel/Netlify
5. ✅ Set up custom domains
6. ✅ Configure monitoring alerts
7. ✅ Set up CI/CD with GitHub Actions

---

## Support

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Status Dashboard**: https://status.cloud.google.com/

---

**Your Deployment Configuration:**
- Gemini API Key: `9c6779342f509f9f39e21adf9e3ec54d4ac5df70`
- Key Expiration: Dec 31, 9999
- Service: `next-backend`
- Region: `us-central1`
