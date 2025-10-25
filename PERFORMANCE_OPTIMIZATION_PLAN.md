# Performance Optimization Plan for NEXT Career Intelligence

## Current Performance Issues

### Analysis Latency: ~130 seconds
**Root Causes:**
1. **Sequential AI Calls** - 3 separate Gemini API calls made one after another
   - Risk Analysis: ~20-30s
   - Skill Insights: ~30-40s  
   - Industry Benchmarks: ~40-50s
   - **Total: 90-120s + overhead**

2. **No Caching** - Every request hits Gemini API even for identical jobs
3. **Synchronous Processing** - Not utilizing async/await properly
4. **Large Prompts** - Verbose prompts increase processing time

### Chatbot Conversation Issues
1. No streaming responses - user waits for full response
2. No conversation context caching
3. Each message is independent (no memory optimization)

---

## Optimization Strategy

### 🚀 PHASE 1: Parallel Processing (Immediate - 60% faster)
**Impact: Reduce latency from 130s → 50-60s**

#### Implementation:
- Run all 3 AI calls in parallel using `asyncio.gather()`
- Current: Sequential (20s + 30s + 40s = 90s)
- Optimized: Parallel (max(20s, 30s, 40s) = 40s)

#### Code Changes:
```python
# Instead of:
risk_analysis = await nextai.analyze_displacement_risk(...)
skill_insights = await nextai.generate_skill_insights(...)
benchmarks = await nextai.generate_industry_benchmarks(...)

# Use:
risk_analysis, skill_insights, benchmarks = await asyncio.gather(
    nextai.analyze_displacement_risk(...),
    nextai.generate_skill_insights(...),
    nextai.generate_industry_benchmarks(...)
)
```

---

### ⚡ PHASE 2: Redis Caching (Immediate - 95% faster for cached results)
**Impact: Cached requests return in <2 seconds**

#### Strategy:
- Cache analysis results by job title + skills hash
- TTL: 24 hours (job market data changes slowly)
- Cache key: `analysis:{job_title}:{skills_hash}`

#### Benefits:
- Popular job titles (Software Engineer, Nurse, Teacher) served instantly
- Reduces API costs dramatically
- Better user experience

#### Implementation:
```python
import hashlib
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_cache_key(job_title: str, skills: List[str]) -> str:
    skills_str = ','.join(sorted(skills))
    hash_obj = hashlib.md5(f"{job_title}:{skills_str}".encode())
    return f"analysis:{hash_obj.hexdigest()}"

# Check cache first
cache_key = get_cache_key(request.job_title, request.skills)
cached_result = redis_client.get(cache_key)
if cached_result:
    return json.loads(cached_result)

# ... perform analysis ...

# Cache result
redis_client.setex(cache_key, 86400, json.dumps(analysis_result))
```

---

### 🎯 PHASE 3: Prompt Optimization (10-20% faster)
**Impact: Reduce each AI call by 3-5 seconds**

#### Current Issues:
- Verbose prompts with excessive instructions
- Requesting JSON structure in prompt (slower parsing)
- Too much context repetition

#### Optimizations:
1. **Shorter, focused prompts**
2. **Use Gemini's function calling** (faster, more reliable)
3. **Remove markdown instructions** (we clean it anyway)
4. **Use structured output mode** (Gemini 1.5+)

#### Example:
```python
# Before (verbose):
prompt = """You are NextAI, an advanced career intelligence system. 
Analyze this role for AI displacement risk with REAL, specific insights:

**Role Analysis:**
Job Title: {job_title}
Key Skills: {', '.join(skills)}
... [300 more words] ...
"""

# After (concise):
prompt = f"""Analyze AI automation risk for {job_title} with skills: {', '.join(skills[:5])}.
Score 0-100, identify 3 human advantages, 3 automation risks.
Focus: specific tasks, not generic statements."""
```

---

### 💬 PHASE 4: Streaming Chatbot Responses (Immediate)
**Impact: User sees response in <2s instead of waiting 15-20s**

#### Implementation:
```python
# Backend: Enable streaming
async def chat_stream(message: str):
    response = model.generate_content(message, stream=True)
    for chunk in response:
        yield chunk.text

# Frontend: Server-Sent Events (SSE)
const eventSource = new EventSource('/api/coach/stream');
eventSource.onmessage = (event) => {
  appendMessage(event.data); // Show chunks as they arrive
};
```

---

### 🧠 PHASE 5: Conversation Context Optimization
**Impact: 30-40% faster chatbot responses**

#### Strategy:
1. **Cache conversation context** - Don't resend entire history every time
2. **Use Gemini's context caching** (built-in feature)
3. **Compress conversation history** - Summarize old messages

#### Implementation:
```python
# Cache conversation context for 5 minutes
conversation_cache_key = f"conversation:{user_id}:{conversation_id}"
cached_context = redis_client.get(conversation_cache_key)

if cached_context:
    # Use cached context (faster)
    context = json.loads(cached_context)
else:
    # Build context from database
    context = build_conversation_context(conversation_id)
    redis_client.setex(conversation_cache_key, 300, json.dumps(context))
```

---

### 📊 PHASE 6: Use Gemini Flash Model for Speed
**Impact: 40-50% faster responses with similar quality**

#### Current: `gemini-2.5-flash` ✅ (Already optimized!)
- You're already using the fast model
- For even faster: `gemini-1.5-flash-8b` (lightweight)
- For better quality: `gemini-1.5-pro` (slower but more accurate)

#### Recommendations:
- **Analysis**: Keep `gemini-2.5-flash` (good balance)
- **Chatbot**: Use `gemini-1.5-flash-8b` (conversational, fast)
- **Critical analysis**: Use `gemini-1.5-pro` (accuracy-critical)

---

### 🔄 PHASE 7: Background Processing + Webhooks
**Impact: Instant UI response, analysis delivered when ready**

#### Strategy:
1. User submits job title
2. Backend returns immediately with `analysis_id`
3. Analysis runs in background (Celery/RQ task)
4. Frontend polls or uses WebSocket for updates
5. User gets result in 40-60s but can navigate away

#### Implementation:
```python
# Backend: Queue the task
from celery import Celery
celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def analyze_career_background(analysis_id, job_title, skills):
    result = perform_analysis(job_title, skills)
    redis_client.set(f"result:{analysis_id}", json.dumps(result))
    # Optional: Send webhook/notification to frontend

# API endpoint
@router.post("/analyze")
async def analyze_career(request: AnalysisRequest):
    analysis_id = str(uuid.uuid4())
    analyze_career_background.delay(analysis_id, request.job_title, request.skills)
    return {"analysis_id": analysis_id, "status": "processing"}

# Frontend: Poll for results
async function pollResults(analysisId) {
    const result = await fetch(`/api/analyze/${analysisId}`);
    if (result.status === 'complete') {
        showResults(result.data);
    } else {
        setTimeout(() => pollResults(analysisId), 2000);
    }
}
```

---

## Implementation Priority

### 🔥 IMMEDIATE (This week):
1. ✅ **Parallel AI Calls** - 60% faster, zero infrastructure
2. ✅ **Streaming Chatbot** - Better UX, same backend
3. ✅ **Prompt Optimization** - Cleaner code, faster

### 📅 SHORT-TERM (Next 2 weeks):
4. **Redis Caching** - Need Redis installation
5. **Conversation Context Cache** - Requires Redis
6. **Model Selection Per Use Case** - Configuration change

### 📈 LONG-TERM (Next month):
7. **Background Processing** - Requires Celery/RQ setup
8. **WebSocket Real-time Updates** - Better than polling
9. **Edge Caching (CDN)** - For static analysis results

---

## Expected Results

### Current State:
- Analysis: **130 seconds**
- Chatbot: **15-20 seconds per message**
- Cache Hit Rate: **0%**

### After Optimizations:
- Analysis (first time): **40-50 seconds** (60% faster)
- Analysis (cached): **<2 seconds** (98% faster)
- Chatbot: **2-3 seconds start, streaming** (90% perceived improvement)
- Cache Hit Rate: **60-70%** for common jobs

### User Experience Impact:
- **130s → 40s**: Acceptable wait time
- **Streaming**: Feels instant vs. 15s blank screen
- **Caching**: Most users get instant results
- **Background**: Users can navigate away during analysis

---

## Cost Savings

### API Call Reduction:
- Current: 3 calls per analysis
- With caching (70% hit rate): 0.9 calls per analysis
- **Savings: 70% on API costs**

### Infrastructure:
- Redis: ~$10/month (minimal)
- Celery workers: Use existing servers
- **ROI: Immediate with better UX**

---

## Next Steps

1. **Implement parallel calls** (30 min)
2. **Add prompt optimization** (1 hour)
3. **Setup Redis locally** (30 min)
4. **Implement caching layer** (2 hours)
5. **Add streaming to chatbot** (3 hours)
6. **Test and measure improvements**

**Total Implementation Time: 1-2 days for 60-90% improvement**
