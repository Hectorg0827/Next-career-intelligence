# Phase 2 Quick Reference - One-Liner Start Guide

## 🚀 Start Everything (Copy & Paste)

### Terminal 1 - Backend
```bash
cd ~/Desktop/Next-career-intelligence/backend && PYTHONPATH=$(pwd) python3 -m uvicorn app.main:app --port 8000
```

### Terminal 2 - Frontend
```bash
cd ~/Desktop/Next-career-intelligence/frontend && npm run dev
```

## ✅ Verify Everything Works

### Check Backend
```bash
curl http://localhost:8000/api/health | python3 -m json.tool
```

### Check Frontend
```bash
open http://localhost:3000
```

### Check All AI Routes
```bash
cd ~/Desktop/Next-career-intelligence && python3 PHASE2_ROUTE_VALIDATION.py
```

### Check Integration Tests
```bash
cd ~/Desktop/Next-career-intelligence && python3 test-phase2-integration.py
```

## 📚 Documentation

- **Full Report:** `PHASE2_COMPLETION_REPORT.md`
- **Route Validation:** `PHASE2_ROUTE_VALIDATION.py`
- **Integration Tests:** `test-phase2-integration.py`
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔗 Quick Links

| Service | URL |
|---------|-----|
| Backend Health | http://localhost:8000/api/health |
| Frontend | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI Spec | http://localhost:8000/openapi.json |

## 📊 Key Endpoints

```bash
# Memory Layer
curl http://localhost:8000/api/ai/memory/context

# Recommendations
curl http://localhost:8000/api/ai/recommendations

# Guidance
curl http://localhost:8000/api/ai/guidance

# Predictions
curl http://localhost:8000/api/ai/predictions/churn
curl http://localhost:8000/api/ai/predictions/success
curl http://localhost:8000/api/ai/predictions/engagement

# Profile Assistant
curl http://localhost:8000/api/ai/profile/analysis
curl http://localhost:8000/api/ai/profile/suggestions

# Intelligence Hub
curl http://localhost:8000/api/ai/intelligence
```

## ⚡ Status Summary

✅ All 5 AI Agents Working
✅ All 14 Endpoints Accessible
✅ Both Servers Running
✅ Background Jobs Scheduled
✅ Frontend Components Integrated
✅ 0 Critical Errors

---

**Everything is ready for Phase 3!** 🎉
