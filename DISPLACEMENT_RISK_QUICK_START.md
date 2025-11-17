# 🎯 AI Displacement Risk Engine - Quick Start Guide

**Status**: Ready to Implement  
**Created**: November 16, 2025  
**Priority**: HIGH - Core Product Differentiator  
**Timeline**: 5-7 days to v1.0 launch

---

## What You Just Got

### 📄 Documentation Created (3 Files)

1. **DISPLACEMENT_RISK_ENGINE_IMPLEMENTATION.md** (30,000+ lines)
   - Complete v1.0 blueprint with architecture diagrams
   - All 6 calculation layers explained (StructuralRisk, PersonalShield, etc.)
   - Database schema design (6 tables)
   - Backend service implementation (800+ lines of Python)
   - API endpoints specification
   - Data ingestion pipelines
   - Testing & calibration process
   - Enterprise integration strategy

2. **phase3_displacement_risk_schema.sql** (500+ lines)
   - Production-ready database migration
   - 6 tables with indexes, constraints, comments
   - Helper functions (refresh views, update percentiles)
   - Sample data for testing
   - Validation queries

3. **This Quick Start Guide**
   - Get started in 5 minutes
   - Next immediate actions
   - Success criteria

---

## What This Engine Does

### The Core Formula

```
DisplacementRisk (0-100) = StructuralRisk × (1 - PersonalShield/100)

Where:
- StructuralRisk = 0.6×TAS + 0.4×IVS (external job risk)
- PersonalShield = 0.45×PSC + 0.30×AS + 0.15×Seniority + 0.10×Credentials (internal protection)

Plus context layers:
- TimeHorizon: "0-2 years", "2-5 years", "5+ years"
- Confidence: 0-100 (based on data coverage)
- Percentile: Compare to peers in same role
- Trajectory: "improving", "stable", "worsening"
```

### Example Output

```json
{
  "ai_displacement_risk": {
    "level": "Medium",
    "score": 42.5,
    "time_horizon": "2–5 years",
    "confidence": 78.3,
    "percentile_vs_role": 72.0,
    "trajectory": "improving",
    "justification": "Your risk score of 42.5 reflects...",
    "primary_vulnerabilities": [
      "High task automation potential (TAS: 68.2/100)",
      "Limited recent learning activity (AS: 45.0/100)"
    ],
    "protection_opportunities": [
      "Learn AI-complementary skills (e.g., prompt engineering)",
      "Complete a certified course to boost Adaptability Score",
      "Build a verified project demonstrating new skills"
    ]
  },
  "debug_components": {
    "StructuralRisk": 65.3,
    "PersonalShield": 58.7,
    "TAS": 68.2,
    "IVS": 60.5,
    "PSC": 62.1,
    "AS": 45.0,
    ...
  }
}
```

---

## Why This Is Your Wedge

### Competitive Advantage

| Feature | LinkedIn/Indeed | Career OS v1.0 |
|---------|-----------------|----------------|
| Risk score | ❌ Generic lists | ✅ Personalized 0-100 score |
| Time horizon | ❌ No timeline | ✅ "0-2 years", "2-5 years", "5+ years" |
| Confidence | ❌ No transparency | ✅ Shows data coverage % |
| Actionable | ❌ Vague advice | ✅ Specific protection opportunities |
| Data moat | ❌ No flywheel | ✅ User actions improve model |
| Peer comparison | ❌ No benchmarks | ✅ "Safer than 72% of peers" |
| Trajectory | ❌ Point-in-time | ✅ "improving/stable/worsening" |

### The Revenue Hook

**For B2C Users** ($0-29/month):
- See your displacement risk score
- Get 3 protection opportunities
- Track monthly trajectory

**For B2B Enterprise** ($150K+/year):
- API access for all employees (batch calculations)
- Custom dashboards showing team-level risk
- Real-time alerts when risk increases
- Skill gap analysis across workforce
- ROI reports: "Training 50 employees reduces team risk by 30%"

**The Flywheel**:
```
User sees risk score
    ↓
Takes action (course, project)
    ↓
Action logged in user_action_log
    ↓
Adaptability Score improves
    ↓
Next calculation shows lower risk
    ↓
User trusts system more
    ↓
Shares with employer
    ↓
Enterprise signs $150K contract
    ↓
More data → Better percentiles → Network effects
    ↓
MOAT ACHIEVED ✅
```

---

## Next Steps (Execute in Order)

### TODAY (Nov 16) - 2 hours

#### Step 1: Run Database Migration

```bash
cd backend

# Connect to your Supabase PostgreSQL
psql postgresql://your-connection-string

# Execute the migration
\i database/phase3_displacement_risk_schema.sql

# Verify tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE '%task%' OR table_name LIKE '%risk%';

# Expected output:
# - ai_task_taxonomy
# - automation_evidence
# - skill_demand_history
# - user_action_log
# - risk_calculation_snapshots
# - risk_percentiles_by_role
```

✅ **Success Criteria**: 6 tables created, sample data inserted

#### Step 2: Create Service Directory Structure

```bash
cd backend/app/services/foundation

# Create new risk service directory
mkdir -p risk/calculators

# Create empty files
touch risk/__init__.py
touch risk/models.py
touch risk/displacement_engine.py
touch risk/calculators/__init__.py
touch risk/calculators/tas_calculator.py
touch risk/calculators/ivs_calculator.py
touch risk/calculators/psc_calculator.py
touch risk/calculators/as_calculator.py

# Verify structure
tree risk/
```

Expected structure:
```
risk/
├── __init__.py
├── models.py
├── displacement_engine.py
└── calculators/
    ├── __init__.py
    ├── tas_calculator.py
    ├── ivs_calculator.py
    ├── psc_calculator.py
    └── as_calculator.py
```

✅ **Success Criteria**: Directory structure created, ready for implementation

---

### TOMORROW (Nov 17) - 4-6 hours

#### Step 3: Implement Data Models

Copy the `models.py` code from **DISPLACEMENT_RISK_ENGINE_IMPLEMENTATION.md** (search for "File: `backend/app/services/foundation/risk/models.py`")

Key models to implement:
- `UserProfile` (input)
- `JobData` (input)
- `RiskAnalysisRequest` (input)
- `DisplacementRiskScore` (output)
- `RiskAnalysisResponse` (output)

Test with:
```bash
python -m pytest backend/tests/test_risk_models.py -v
```

#### Step 4: Implement TAS Calculator

Copy the `tas_calculator.py` code from implementation doc.

This queries `ai_task_taxonomy` and calculates:
```
TAS = Σ(TaskRisk_i × TaskImportance_i) / Σ(TaskImportance_i) × 100
```

Test with sample occupation code:
```python
from app.services.foundation.risk.calculators import TaskAutomationCalculator

tas_calc = TaskAutomationCalculator(db)
tas_score, coverage = await tas_calc.calculate("15-2051")  # Software Developer

print(f"TAS: {tas_score}/100 (Coverage: {coverage}%)")
# Expected: TAS: 65-75/100 for software developers
```

#### Step 5: Implement IVS, PSC, AS Calculators

Similar process for each:
- Copy code from implementation doc
- Test with sample data
- Verify formulas match blueprint

---

### MONDAY (Nov 18) - 6 hours

#### Step 6: Implement Main Engine

Copy `displacement_engine.py` code (800+ lines).

This ties everything together:
1. Calls TAS/IVS calculators → StructuralRisk
2. Calls PSC/AS calculators + seniority/credentials → PersonalShield
3. Applies core formula → DisplacementRisk
4. Calculates context (TimeHorizon, Confidence)
5. Calculates comparison (Percentile, Trajectory)
6. Generates LLM justifications

Test with end-to-end example:
```python
from app.services.foundation.risk import DisplacementRiskEngine, RiskAnalysisRequest

engine = DisplacementRiskEngine(db)
result = await engine.analyze(user_profile, job_data)

assert result.ai_displacement_risk.score > 0
assert result.ai_displacement_risk.level in ["Low", "Medium", "High", "Critical"]
assert result.debug_components.TAS > 0
```

#### Step 7: Create API Endpoints

Copy `backend/app/api/v1/endpoints/risk.py` code.

Two endpoints:
- `POST /api/v1/risk/analyze` - Calculate risk
- `GET /api/v1/risk/history/:user_id` - Get history

Register in `api.py`:
```python
from .endpoints import risk
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
```

Test with curl:
```bash
curl -X POST http://localhost:8000/api/v1/risk/analyze \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

### TUESDAY-WEDNESDAY (Nov 19-20) - 8 hours

#### Step 8: Data Ingestion Pipelines

**O*NET Tasks**:
1. Download O*NET database: https://www.onetcenter.org/database.html
2. Implement `backend/app/tasks/data_ingestion/onet_tasks.py`
3. Run ingestion: `python -m app.tasks.data_ingestion.onet_tasks`
4. Target: 1000+ tasks across top 50 occupations

**Job Postings**:
1. Sign up for Adzuna API (free tier): https://developer.adzuna.com
2. Implement `backend/app/tasks/data_ingestion/job_postings.py`
3. Run daily scraper: `python -m app.tasks.data_ingestion.job_postings`
4. Target: 200+ tracked skills with 365-day history

#### Step 9: Testing & Calibration

Create 100+ test profiles:
- 30 low-risk (senior executives, strategic roles)
- 40 medium-risk (skilled professionals with adaptability)
- 30 high-risk (routine tasks, no recent learning)

Run all through engine, validate:
- ✅ Low-risk profiles score <40
- ✅ Medium-risk profiles score 40-65
- ✅ High-risk profiles score >65
- ✅ Time horizons match intuition
- ✅ Confidence reflects data coverage

Tune weights if needed:
```python
# In displacement_engine.py

# Current v1.0 weights:
structural_risk = (0.6 * tas) + (0.4 * ivs)
personal_shield = (0.45 * psc) + (0.30 * adaptability) + (0.15 * seniority) + (0.10 * credentials)

# If TAS seems too dominant, adjust:
structural_risk = (0.5 * tas) + (0.5 * ivs)  # Give IVS more weight

# If PSC seems too weak, adjust:
personal_shield = (0.50 * psc) + (0.25 * adaptability) + (0.15 * seniority) + (0.10 * credentials)
```

---

### THURSDAY (Nov 21) - Deploy to Staging

1. Merge to staging branch
2. Run full integration tests
3. Performance testing (<500ms per calculation)
4. Load testing (100 concurrent users)

Success criteria:
- ✅ All tests passing
- ✅ Response times <500ms
- ✅ No database errors
- ✅ Debug logs show correct component scores

---

### FRIDAY (Nov 22) - Production Launch 🚀

1. Deploy to production
2. Enable for 10% of users (A/B test)
3. Monitor metrics:
   - API error rate (<1%)
   - Response times (<500ms p95)
   - User engagement (click protection opportunities)
   - Feedback sentiment (>80% positive)
4. If stable, ramp to 100% over 24 hours

---

## Success Metrics

### Technical Metrics

- ✅ **Response Time**: <500ms p95 for risk calculation
- ✅ **Accuracy**: 90%+ of test users say score "feels accurate"
- ✅ **Coverage**: 1000+ tasks, 200+ skills in database
- ✅ **Uptime**: 99.9% API availability

### Business Metrics

- ✅ **Engagement**: 60%+ of users click protection opportunities
- ✅ **Retention**: Users return weekly to check trajectory
- ✅ **Conversion**: 40%+ of enterprise demos convert (they see this feature and say "we need this")
- ✅ **NPS**: >70 Net Promoter Score for risk feature

### Revenue Impact

**Month 1** (Dec 2025):
- 5 enterprise pilots at $150K/year = $750K ARR
- 1,000 B2C users at $29/month = $29K MRR

**Month 6** (May 2026):
- 15 enterprise customers = $2.25M ARR
- 10,000 B2C users = $290K MRR
- **Total**: $2.54M ARR

**Year 1** (Nov 2026):
- 25 enterprise customers = $3.75M ARR
- 50,000 B2C users = $1.45M ARR
- **Total**: $5.2M ARR

---

## Common Questions

### Q: Do I need all 6 tables to start?

**A**: Yes. The calculations depend on:
- `ai_task_taxonomy` → TAS calculation
- `skill_demand_history` → IVS and PSC calculation
- `user_action_log` → AS calculation
- `risk_calculation_snapshots` → Trajectory calculation
- `risk_percentiles_by_role` → Percentile comparison

But you can start with **sample data** (already in schema) and build real pipelines incrementally.

### Q: Can I use placeholder data for v1.0?

**A**: Yes, for MVP launch:
- Use O*NET data for tasks (free download)
- Use heuristic scores for automation (keyword matching)
- Use synthetic job posting data (100 skills × 12 months)
- Real data ingestion can happen in v1.1

### Q: How long does each calculation take?

**A**: Target <500ms:
- TAS calculation: ~50ms (query 20 tasks)
- IVS calculation: ~50ms (query 365 days of skill data)
- PSC calculation: ~100ms (query all user skills)
- AS calculation: ~50ms (query user_action_log)
- Context/comparison: ~50ms
- LLM generation: ~200ms

Total: ~500ms end-to-end

### Q: What if I don't have O*NET data yet?

**A**: Use the sample data in the schema, which includes:
- 1 sample task for Software Developers
- 1 sample skill (Python)
- 1 sample automation evidence

This is enough to test the engine. Full ingestion can happen later.

### Q: How do I integrate with the frontend?

**A**: Once API endpoints are live:

```javascript
// React component
const RiskDashboard = () => {
  const [risk, setRisk] = useState(null);
  
  useEffect(() => {
    fetch('/api/v1/risk/analyze', {
      method: 'POST',
      body: JSON.stringify({
        user_profile: currentUser,
        job_data: currentJob
      })
    })
    .then(res => res.json())
    .then(data => setRisk(data));
  }, []);
  
  return (
    <div>
      <h1>Your AI Displacement Risk</h1>
      <RiskScore score={risk.ai_displacement_risk.score} />
      <TimeHorizon horizon={risk.ai_displacement_risk.time_horizon} />
      <ProtectionOpportunities items={risk.ai_displacement_risk.protection_opportunities} />
    </div>
  );
};
```

---

## Files You Need to Reference

### Primary Documentation

1. **DISPLACEMENT_RISK_ENGINE_IMPLEMENTATION.md**
   - Read first: Architecture overview (pages 1-10)
   - Reference during implementation: Function signatures (pages 11-40)
   - Use for troubleshooting: Testing section (pages 41-45)

2. **phase3_displacement_risk_schema.sql**
   - Execute first to create tables
   - Reference table comments for field meanings
   - Use sample data for initial testing

### Code Implementation Order

1. `models.py` (30 min)
2. `tas_calculator.py` (1 hour)
3. `ivs_calculator.py` (1 hour)
4. `psc_calculator.py` (1.5 hours)
5. `as_calculator.py` (1 hour)
6. `displacement_engine.py` (3 hours)
7. `risk.py` (API endpoints, 1 hour)

**Total implementation time**: ~9 hours over 2-3 days

---

## Get Help

If you get stuck:

1. **Database issues**: Check table comments in schema for field explanations
2. **Formula questions**: Reference the v1.0 blueprint formulas in implementation doc
3. **Performance issues**: Add indexes on frequently queried fields
4. **Accuracy issues**: Tune weights in displacement_engine.py

---

## Final Checklist

Before launching to production:

- [ ] All 6 tables created and populated with sample data
- [ ] All 5 calculators implemented and tested
- [ ] Main engine (displacement_engine.py) passing all tests
- [ ] API endpoints responding with correct JSON structure
- [ ] O*NET data ingested (at least top 50 occupations)
- [ ] Skill demand data ingested (at least 100 skills)
- [ ] 100+ test profiles validated
- [ ] Weights calibrated based on test results
- [ ] Frontend integration tested
- [ ] Performance benchmarks met (<500ms)
- [ ] Documentation complete (API docs, error handling)

---

## What This Unlocks

Once v1.0 is live, you can:

✅ **Sell to enterprises**: "We calculate personalized AI risk for your entire workforce"  
✅ **Differentiate from competitors**: No one else has a principled, transparent model  
✅ **Build the moat**: User actions improve the model, creating network effects  
✅ **Revenue**: $150K+ contracts from enterprises who need workforce planning  
✅ **Expansion**: Add new features (skill recommendations, training ROI, team analytics)  

**This is your wedge. Now build it.** 🚀

---

**Ready to start?** Execute Step 1 (database migration) now.

**Questions?** Reference the full implementation doc.

**Stuck?** Check the troubleshooting section in the main doc.

Let's ship this! 💪
