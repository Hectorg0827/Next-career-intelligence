# Phase 2 Quick Test Guide

## 🚀 Quick Start

### 1. Start Backend (Terminal 1)
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend
uvicorn app.main:app --reload
```

**Expected Output:**
```
✅ Sentry error monitoring initialized
✅ Redis cache initialized
✅ Supabase connection pool initialized
✅ Neo4j Talent Graph connected
✅ Scheduled background tasks initialized
✅ AI background jobs scheduler started
✅ All services initialized - API ready to accept requests
```

### 2. Start Frontend (Terminal 2)
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/frontend
npm run dev
```

**Access:** http://localhost:3000

### 3. Run Integration Tests (Terminal 3)
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence
python3 test-phase2-integration.py
```

---

## 🧪 Manual Testing Checklist

### Dashboard
- [ ] Visit http://localhost:3000/dashboard
- [ ] See AI Guidance Panel with priority-coded messages
- [ ] See Profile Intelligence Widget in sidebar showing completeness %
- [ ] Dismiss a guidance message (should save to localStorage)
- [ ] Click "View All X Suggestions" on profile widget

### Profile Page
- [ ] Visit http://localhost:3000/resume-studio/profile
- [ ] See full AI Profile Assistant at top
- [ ] View completeness score (0-100%) with progress bar
- [ ] See strengths (green) and weaknesses (yellow) lists
- [ ] View AI suggestions with priority badges
- [ ] Click "Quick Fill Profile" (should show inference result)
- [ ] Click "Generate Summary" (should show AI-generated text)
- [ ] See inferred skills section (if available)

### Jobs Marketplace
- [ ] Visit http://localhost:3000/jobs
- [ ] Search for jobs
- [ ] See AI-recommended jobs at top
- [ ] View match scores and explanations

---

## 🔍 API Endpoint Testing

### Quick cURL Tests

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Get AI Guidance:**
```bash
curl "http://localhost:8000/api/ai/guidance/test_user_123?limit=5"
```

**Get Recommendations:**
```bash
curl "http://localhost:8000/api/ai/recommendations/test_user_123?limit=10"
```

**Analyze Profile:**
```bash
curl "http://localhost:8000/api/ai/profile/analysis?user_id=test_user_123"
```

**Get Profile Suggestions:**
```bash
curl "http://localhost:8000/api/ai/profile/suggestions?user_id=test_user_123"
```

**Form Memory:**
```bash
curl -X POST http://localhost:8000/api/ai/memory/form \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "interaction_type": "job_search",
    "interaction_data": {"query": "python developer", "location": "remote"}
  }'
```

**Generate Guidance:**
```bash
curl -X POST http://localhost:8000/api/ai/guidance/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'
```

**Predict Churn:**
```bash
curl "http://localhost:8000/api/ai/predict-churn/test_user_123"
```

**Infer Profile Data:**
```bash
curl -X POST http://localhost:8000/api/ai/profile/infer \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'
```

**Generate Summary:**
```bash
curl -X POST http://localhost:8000/api/ai/profile/generate-summary \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'
```

---

## 📊 Database Verification

### Check Tables Exist
```sql
-- Connect to Supabase SQL Editor

-- AI Memories
SELECT COUNT(*) FROM ai_memories;
SELECT * FROM ai_memories LIMIT 5;

-- Recommendations
SELECT COUNT(*) FROM ai_recommendations;
SELECT * FROM ai_recommendations LIMIT 5;

-- Guidance
SELECT COUNT(*) FROM ai_guidance;
SELECT * FROM ai_guidance LIMIT 5;

-- Churn Predictions
SELECT COUNT(*) FROM churn_predictions;
SELECT * FROM churn_predictions LIMIT 5;

-- Profile Analysis
SELECT COUNT(*) FROM profile_analysis;
SELECT * FROM profile_analysis LIMIT 5;

-- Profile Suggestions
SELECT COUNT(*) FROM profile_suggestions;
SELECT * FROM profile_suggestions LIMIT 5;
```

---

## 🕐 Background Jobs Verification

### Check Jobs Are Running

**View Scheduler Logs:**
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend
tail -f logs/app.log | grep "AI jobs"
```

**Expected Log Messages:**
```
INFO - AI background jobs scheduler started
INFO - Starting daily memory formation...
INFO - Memory formation complete: X/Y succeeded
INFO - Starting recommendation updates...
INFO - Recommendation updates complete: X/Y succeeded
```

### Manually Trigger Jobs (for testing)

Open Python REPL:
```python
from app.tasks.ai_jobs import ai_jobs
import asyncio

# Test memory formation
asyncio.run(ai_jobs.form_daily_memories())

# Test recommendation updates
asyncio.run(ai_jobs.update_recommendations())

# Test churn prediction
asyncio.run(ai_jobs.predict_churn_risk())

# Test profile analysis
asyncio.run(ai_jobs.analyze_profiles())

# Test cleanup
asyncio.run(ai_jobs.cleanup_old_data())
```

---

## ⚡ Performance Benchmarks

### Expected Response Times
- Health check: <50ms
- Get guidance: <500ms
- Get recommendations: <800ms
- Profile analysis: <1000ms
- Infer data: <2000ms
- Generate summary: <3000ms

### Load Test (optional)
```bash
# Install apache bench
brew install httpd

# Test endpoint
ab -n 100 -c 10 http://localhost:8000/health
ab -n 50 -c 5 "http://localhost:8000/api/ai/guidance/test_user_123"
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Python version (need 3.9+)
python3 --version

# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Check environment variables
cat .env  # Must have GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY
```

### Frontend Components Not Showing
```bash
# Check console for errors
# Open browser DevTools → Console

# Rebuild frontend
cd frontend
rm -rf .next
npm run dev
```

### API Returns 500 Errors
```bash
# Check backend logs
cd backend
tail -f logs/app.log

# Check Gemini API key
echo $GEMINI_API_KEY  # Should not be empty

# Check Supabase connection
curl https://your-project.supabase.co/rest/v1/
```

### Background Jobs Not Running
```bash
# Check if APScheduler is installed
pip show APScheduler

# Check logs for scheduler startup
grep "AI jobs" backend/logs/app.log

# Verify scheduler is running
# Should see "AI background jobs scheduler started" at startup
```

---

## ✅ Success Indicators

### Backend
- [x] Server starts without errors
- [x] All 15 endpoints respond
- [x] Database tables populated
- [x] Background jobs log messages
- [x] No 500 errors in logs

### Frontend
- [x] Dashboard loads
- [x] AI Guidance Panel visible
- [x] Profile Widget shows percentage
- [x] Profile page shows full assistant
- [x] No console errors

### Integration
- [x] All integration tests pass
- [x] Response times < 2s
- [x] Error handling works (try invalid user_id)
- [x] Fallbacks work (disable Gemini API temporarily)

---

## 📞 Quick Commands Reference

```bash
# Start everything
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev &
cd .. && python3 test-phase2-integration.py

# View logs
tail -f backend/logs/app.log

# Check health
curl http://localhost:8000/health

# Test endpoint
curl http://localhost:8000/api/ai/guidance/test_user_123

# Access frontend
open http://localhost:3000/dashboard
```

---

## 🎯 Expected Results

After completing this guide, you should see:
1. ✅ Backend running with AI jobs scheduler
2. ✅ Frontend displaying AI components
3. ✅ All integration tests passing
4. ✅ Database tables populated with data
5. ✅ Background jobs executing on schedule

**Total Test Time:** ~15 minutes  
**Next:** Deploy to production! 🚀

---

*Quick Reference Version 1.0*  
*Last Updated: 2025-01-13*
