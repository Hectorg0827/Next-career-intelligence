# Quick Deployment Commands

## Backend to Google Cloud Run

```bash
cd backend

# Make deploy script executable
chmod +x deploy-backend.sh

# Deploy
./deploy-backend.sh
```

After deployment, note the URL and update it in frontend environment variables.

---

## Frontend to Vercel

### Method 1: Via Dashboard (Easiest)
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Set Root Directory to: `frontend`
4. Add all environment variables from `.env.local`
5. Click Deploy

### Method 2: Via CLI
```bash
cd frontend

# Install Vercel CLI (if needed)
npm i -g vercel

# Login
vercel login

# Deploy to production
vercel --prod
```

---

## Update Frontend API URL

After backend deployment:

1. Copy your Cloud Run URL
2. In Vercel Dashboard → Settings → Environment Variables
3. Update `NEXT_PUBLIC_API_URL` to your Cloud Run URL
4. Redeploy frontend

---

## Verify Deployment

```bash
# Test backend
curl https://your-backend-url.run.app/api/health

# Visit frontend
# Open: https://your-app.vercel.app
```

---

## Common Issues

### Backend: "Service unavailable"
- Check Cloud Run logs: `gcloud run services logs read next-backend`
- Verify environment variables are set
- Check database connection

### Frontend: "API Error"
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- View Vercel deployment logs

### Database: "Connection failed"
- Verify Supabase credentials
- Check if IP is allowed (Supabase allows all by default)
- Test connection from Cloud Run

---

## Monitoring

### Cloud Run Logs
```bash
gcloud run services logs read next-backend --limit 50 --follow
```

### Vercel Logs
- Dashboard → Deployments → View Logs

### Supabase Logs
- Dashboard → Logs → Database
