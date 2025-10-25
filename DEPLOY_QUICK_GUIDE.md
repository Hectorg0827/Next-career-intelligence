# Backend Deployment - Quick Reference

## 🚀 Deploy Backend NOW

```bash
./deploy-now.sh
```

## 📋 What You Have

✅ Gemini API Key: `9c6779342f509f9f39e21adf9e3ec54d4ac5df70`  
✅ Authenticated: `hector.garcia0827@gmail.com`  
✅ Scripts: Ready in project root  

## ⏱️ Timeline

- Deployment: 3-5 minutes
- First request: 2-3 seconds (cold start)
- Subsequent: < 1 second

## 💰 Cost

- Free tier: 2 million requests/month
- Estimated: $5-20/month
- Scales to $0 when idle

## 🧪 After Deployment

1. **Get URL** (shown after deployment)
2. **Test:** `curl YOUR_URL/api/v1/health`
3. **Update frontend/.env.local:**
   ```
   NEXT_PUBLIC_API_URL=YOUR_URL
   ```
4. **Restart frontend**

## 📊 Monitor

- Logs: `gcloud run services logs read next-backend --region us-central1`
- Console: https://console.cloud.google.com/run
- Metrics: Request count, latency, errors

## 🔄 Update Later

```bash
cd backend
gcloud run deploy next-backend --source . --region us-central1
```

---

**Ready? Run:** `./deploy-now.sh`
