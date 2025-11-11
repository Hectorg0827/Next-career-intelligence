# Run Staging Benchmarks - Quick Guide

**Time**: 15 minutes
**Purpose**: Validate 50-90% performance improvements before production deployment

---

## Step 1: Set Environment Variables (2 min)

Open your terminal and set your staging credentials:

```bash
# Navigate to project
cd /Users/hectorgarcia/Desktop/Next-career-intelligence

# Set Supabase staging credentials
export SUPABASE_URL="YOUR_STAGING_SUPABASE_URL"
export SUPABASE_SERVICE_ROLE_KEY="YOUR_STAGING_SERVICE_ROLE_KEY"

# Example:
# export SUPABASE_URL="https://xxxxx.supabase.co"
# export SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Where to find credentials:**
1. Go to Supabase Dashboard: https://app.supabase.com
2. Select your **staging** project
3. Go to **Settings** → **API**
4. Copy:
   - **URL** → `SUPABASE_URL`
   - **service_role key** (anon key won't work) → `SUPABASE_SERVICE_ROLE_KEY`

---

## Step 2: Install Dependencies (1 min)

```bash
cd backend

# Activate virtual environment (if you have one)
# source venv/bin/activate

# Install required packages
pip3 install supabase
```

---

## Step 3: Run Benchmarks (10 min)

```bash
cd backend
python3 benchmark_performance.py
```

**Expected Output:**
```
============================================================
DATABASE PERFORMANCE BENCHMARK
Migration 009: Database Optimization
============================================================

Fetching sample data for benchmarks...
  Sample User ID: 123e4567-e89b-12d3-a456-426614174000
  Sample Company ID: 123e4567-e89b-12d3-a456-426614174001

============================================================
Benchmarking: Job Search (active + sorted)
============================================================
  Run 1/10: 87.32ms
  Run 2/10: 82.15ms
  ...
  Results:
    Average: 85.23ms
    Median:  84.50ms
    Min:     78.12ms
    Max:     91.45ms

[... similar output for other benchmarks ...]

============================================================
BENCHMARK SUMMARY
============================================================

Query Type                          Avg (ms)     Target (ms)  Status
----------------------------------------------------------------------
Job Search (active + sorted)          85.23          150        ✅ PASS
User Dashboard                        72.41          100        ✅ PASS
Company Job Listings                  45.67           80        ✅ PASS
Salary Range Filter                   68.92          100        ✅ PASS
Skill Matching                        95.34          120        ✅ PASS
Company Stats (Materialized View)    125.78          200        ✅ PASS

============================================================
✅ ALL BENCHMARKS PASSED - Ready for production!
============================================================

📊 Expected Performance Improvements (vs baseline):
  • Job Search: 80-85% faster (500-800ms → 50-150ms)
  • User Dashboard: 75-83% faster (300-500ms → 50-100ms)
  • Company Listings: 80-85% faster (200-400ms → 30-80ms)
  • Full-text Search: 85-90% faster (1000-2000ms → 100-300ms)
  • Analytics: 95-98% faster (2000-5000ms → 50-200ms)
```

---

## Step 4: Interpret Results (2 min)

### ✅ Success Criteria (All Must Pass):
- [x] All 6 benchmarks show ✅ PASS
- [x] Average < Target for all queries
- [x] No errors or timeouts

### ⚠️ If Benchmarks Fail:
1. **Check if Migration 009 was deployed:**
   ```bash
   psql $DATABASE_URL_STAGING -c "\di public.idx_jobs*"
   ```
   Should show ~15 indexes starting with "idx_jobs"

2. **Refresh materialized views:**
   ```bash
   psql $DATABASE_URL_STAGING -c "SELECT refresh_all_materialized_views();"
   ```

3. **Check for sample data:**
   ```bash
   psql $DATABASE_URL_STAGING -c "SELECT COUNT(*) FROM jobs WHERE is_active = true;"
   ```
   Should show > 0 jobs

4. **Re-run ANALYZE:**
   ```bash
   psql $DATABASE_URL_STAGING -c "ANALYZE public.jobs; ANALYZE public.companies;"
   ```

---

## Step 5: Save Results (Optional)

```bash
# Save benchmark output to file
python3 benchmark_performance.py > benchmark_results_$(date +%Y%m%d_%H%M%S).txt

# Review results
cat benchmark_results_*.txt
```

---

## Troubleshooting

### Error: "No module named 'supabase'"
```bash
pip3 install supabase
```

### Error: "Connection refused" or "Authentication failed"
- Double-check your `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- Make sure you're using the **service_role** key, not the anon key
- Verify staging project is running in Supabase Dashboard

### Error: "No sample data found"
You need to seed the database first:
```bash
# Seed staging database with test data
curl -X POST https://YOUR_STAGING_API/api/seed/jobs
```

Or manually create a test user and company in Supabase Dashboard.

---

## Next Steps After Benchmarks Pass ✅

Once all benchmarks pass, you're ready for production deployment!

Follow: **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Step 4 onwards**

### Quick Production Deployment Steps:

**Step 4: Deploy to Production** (45 min)
```bash
# 1. Set production database URL
export DATABASE_URL_PROD="YOUR_PRODUCTION_DB_URL"

# 2. Run migrations
psql $DATABASE_URL_PROD -f backend/migrations/009_optimize_database_performance.sql
psql $DATABASE_URL_PROD -f backend/migrations/010_force_password_reset.sql
psql $DATABASE_URL_PROD -f backend/migrations/011_migrate_to_jwt.sql

# 3. Update environment variables
gcloud run services update next-backend \
  --set-env-vars STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET \
  --set-env-vars SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))") \
  --set-env-vars ENVIRONMENT=production \
  --region us-central1

# 4. Deploy backend
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_ENV=production,_SERVICE_NAME=next-backend \
  --region=us-central1

# 5. Deploy frontend
cd frontend && vercel --prod
```

---

## Summary Checklist

Before running benchmarks:
- [ ] Migration 009 deployed to staging
- [ ] Staging credentials exported (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
- [ ] Dependencies installed (pip3 install supabase)
- [ ] Sample data exists in staging database

After benchmarks pass:
- [ ] All 6 benchmarks show ✅ PASS
- [ ] Performance improvements validated (50-90% faster)
- [ ] Ready to deploy to production

---

**Total Time**: 15 minutes
**Status**: Ready to run ✅
