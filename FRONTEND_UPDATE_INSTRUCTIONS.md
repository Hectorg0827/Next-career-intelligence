# FRONTEND UPDATE INSTRUCTIONS

## Environment Variables to Update on Vercel Dashboard

For the project **nextci.net** on Vercel, update the following environment variable in the Production environment:

```
NEXT_PUBLIC_API_URL=https://next-career-backend-795538981829.us-central1.run.app
```

### Steps:
1. Go to https://vercel.com/dashboard
2. Select the "nextci" project (or the project linked to nextci.net)
3. Click on "Settings"
4. Click on "Environment Variables" in the left sidebar
5. Find the `NEXT_PUBLIC_API_URL` variable
6. Update its value from `https://next-backend-jxs4smo7nq-uc.a.run.app` to `https://next-career-backend-795538981829.us-central1.run.app`
7. Save the changes
8. Trigger a redeploy:
   - Go to "Deployments" tab
   - Click on the latest deployment
   - Click "Redeploy"
   - Or just push a commit to the repository to trigger automatic deploy

### Alternative: Update via Git
The `vercel.json` file has already been updated with the correct backend URL for API rewrites.
Just push the changes:

```bash
git push origin main
```

This will trigger Vercel to redeploy automatically.

## Verification
After Vercel redeploys, verify that:
1. Frontend loads at https://nextci.net
2. The analyze feature works (try analyzing a job)
3. No CORS errors in the browser console
4. API calls go to https://next-career-backend-795538981829.us-central1.run.app

## Files Updated
- `frontend/vercel.json` - Updated API rewrite destination
- `frontend/.env.local` - Updated NEXT_PUBLIC_API_URL (local only, not committed)
