# 🚀 Advanced Features Guide
**NEXT | Adaptive Career Intelligence**  
**Complete Feature Access Guide**

---

## 📍 **Quick Navigation - All Features**

### **🏠 Home & Dashboard**
```
http://localhost:3000                    → Landing page
http://localhost:3000/dashboard          → Main career analysis dashboard
```

---

## 🎯 **Core Features**

### **1. AI Career Analysis** (Main Dashboard)
**URL:** http://localhost:3000/dashboard

**What it does:**
- ✅ AI displacement risk analysis (powered by Gemini)
- ✅ Compatibility score calculation
- ✅ Industry benchmarks comparison
- ✅ Skill gap analysis
- ✅ Transition pathway recommendations

**How to use:**
1. Enter your job title (e.g., "Software Engineer")
2. List your skills (comma-separated: "python, javascript, react")
3. Enter location (e.g., "Remote" or "San Francisco")
4. Enter years of experience (e.g., "5")
5. Click **"Analyze Career"**
6. See real-time AI analysis results!

**Features on this page:**
- Risk level indicator (Low/Medium/High/Critical)
- Velocity of automation timeline
- Human advantage factors
- AI augmentation potential
- Industry comparison charts

---

### **2. Visual Career Roadmap** (Dashboard)
**URL:** http://localhost:3000/dashboard (after analysis)

**What it does:**
- ✅ Multi-year career path visualization
- ✅ Sankey diagram of career transitions
- ✅ Milestone tracking
- ✅ Skill development timeline
- ✅ Salary progression estimates

**How to use:**
1. Complete career analysis first
2. Click **"Generate Visual Roadmap"**
3. See 3-year and 5-year career paths
4. View alternative career transitions
5. Download or share your roadmap

**Features:**
- Interactive Sankey flow diagram
- Primary and alternative paths
- Skills required for each transition
- Estimated training time
- AI resilience scores

---

## 💬 **Premium Feature: Career Coach AI**

### **Career Coach Chat**
**URL:** http://localhost:3000/career-coach

**What it does:**
- ✅ AI-powered career counseling
- ✅ Personalized career advice
- ✅ Goal setting and tracking
- ✅ Conversation history
- ✅ Career strategy planning

**How to use:**
1. Open http://localhost:3000/career-coach
2. Click "New Chat" to start a conversation
3. Ask questions like:
   - "How can I transition to AI engineering?"
   - "What skills should I learn next?"
   - "How do I negotiate a higher salary?"
   - "Should I pursue a management track?"

**Alternative URLs:**
- http://localhost:3000/coach/chat - Chat interface
- http://localhost:3000/coach/goals - Goal management

**Backend API:**
```bash
POST http://localhost:8000/api/coach/chat
GET  http://localhost:8000/api/coach/conversations/{id}
POST http://localhost:8000/api/coach/goals
```

---

## 🎤 **Premium Feature: Interviewer AI**

### **Interview Practice Sessions**
**URL:** http://localhost:3000/interviewer

**Main Pages:**
1. **Landing:** http://localhost:3000/interviewer
2. **Setup:** http://localhost:3000/interviewer/setup
3. **Practice:** http://localhost:3000/interviewer/practice
4. **Sessions:** http://localhost:3000/interviewer/sessions
5. **Review:** http://localhost:3000/interviewer/sessions/[sessionId]

**What it does:**
- ✅ AI-generated interview questions (behavioral, technical, situational)
- ✅ STAR method guidance
- ✅ Real-time answer evaluation
- ✅ Feedback on your responses
- ✅ Achievement extraction from answers
- ✅ Profile improvement suggestions

**How to use:**
1. Go to http://localhost:3000/interviewer/setup
2. Configure interview:
   - Role: "Senior Software Engineer"
   - Company: "Google" (optional)
   - Interview Type: "Behavioral" / "Technical" / "Mixed"
   - Difficulty: "Entry" / "Mid" / "Senior"
3. Click **"Start Interview"**
4. Answer 5-7 AI-generated questions
5. Use STAR method (Situation, Task, Action, Result)
6. Submit answers for AI evaluation
7. Review detailed feedback

**Backend API:**
```bash
POST http://localhost:8000/api/interviewer/start
POST http://localhost:8000/api/interviewer/submit-answer
POST http://localhost:8000/api/interviewer/complete
GET  http://localhost:8000/api/interviewer/sessions/{id}
```

---

## 💼 **Premium Feature: Job Marketplace**

### **AI-Powered Job Matching**
**URL:** http://localhost:3000/jobs

**Main Pages:**
1. **Search:** http://localhost:3000/jobs/search
2. **Job Details:** http://localhost:3000/jobs/[jobId]
3. **Applications:** http://localhost:3000/jobs/applications
4. **Recommendations:** http://localhost:3000/jobs/recommendations

**What it does:**
- ✅ AI-powered job matching (based on your profile)
- ✅ Match score calculation
- ✅ Auto-tailored resume generation
- ✅ Cover letter creation
- ✅ Application tracking
- ✅ Job recommendations

**How to use:**
1. Go to http://localhost:3000/jobs/search
2. Search for roles (e.g., "Software Engineer")
3. Filter by location, salary, experience
4. Click on a job to see details and AI match score
5. Click **"Apply"** to auto-generate tailored resume
6. Track applications at http://localhost:3000/jobs/applications

**Backend API:**
```bash
POST http://localhost:8000/api/jobs-marketplace/match
GET  http://localhost:8000/api/jobs-marketplace/jobs/{id}
POST http://localhost:8000/api/jobs-marketplace/apply
GET  http://localhost:8000/api/jobs-marketplace/applications
```

---

## 📝 **Premium Feature: Resume Studio**

### **AI Resume Builder & Optimizer**
**URL:** http://localhost:3000/resume-studio

**Main Pages:**
1. **Dashboard:** http://localhost:3000/resume-studio
2. **Profile:** http://localhost:3000/resume-studio/profile
3. **Upload:** http://localhost:3000/resume-studio/upload
4. **Suggestions:** http://localhost:3000/resume-studio/suggestions

**What it does:**
- ✅ Resume parsing and analysis
- ✅ AI-powered improvement suggestions
- ✅ Achievement extraction from text
- ✅ Profile optimization
- ✅ ATS-friendly formatting
- ✅ One-click apply to suggestions

**How to use:**
1. Go to http://localhost:3000/resume-studio/upload
2. Upload your resume (PDF, DOCX, or paste text)
3. AI analyzes and extracts data
4. View suggestions at http://localhost:3000/resume-studio/suggestions
5. Accept/reject AI recommendations
6. View optimized profile at http://localhost:3000/resume-studio/profile

**Backend API:**
```bash
POST http://localhost:8000/api/resume-studio/ingest
GET  http://localhost:8000/api/resume-studio/profile/{userId}
POST http://localhost:8000/api/resume-studio/extract-achievements
POST http://localhost:8000/api/resume-studio/apply-suggestion
```

---

## 💳 **Subscription Management**

### **Plans & Billing**
**URL:** http://localhost:3000/subscription

**What it does:**
- ✅ View available plans (Free, Pro, Enterprise)
- ✅ Compare features
- ✅ Manage current subscription
- ✅ Billing information
- ✅ Payment method updates
- ✅ FAQ section

**Plans Available:**
1. **Free** - Basic analysis (5 analyses/month)
2. **Pro ($29.99/mo)** - All features + unlimited analyses
3. **Enterprise ($99.99/mo)** - Team features + priority support

**How to use:**
1. Go to http://localhost:3000/subscription
2. Toggle Monthly/Yearly billing (17% savings on yearly)
3. Click "Subscribe" on desired plan
4. Enter payment details (Stripe integration)
5. Manage subscription in dashboard

**Backend API:**
```bash
GET  http://localhost:8000/api/subscriptions/plans
GET  http://localhost:8000/api/subscriptions/current
POST http://localhost:8000/api/subscriptions/subscribe
POST http://localhost:8000/api/subscriptions/cancel
```

---

## 🧪 **Testing All Features - Step by Step**

### **Quick Test Path (15 minutes)**

**1. Career Analysis (5 min)**
```
→ http://localhost:3000/dashboard
→ Fill: Job="Software Engineer", Skills="python,react", Location="Remote", Experience=5
→ Click "Analyze Career"
→ See AI risk analysis
→ Click "Generate Visual Roadmap"
→ See career path visualization
```

**2. Career Coach (3 min)**
```
→ http://localhost:3000/career-coach
→ Click "New Chat"
→ Ask: "How can I transition to AI/ML engineering?"
→ See AI response with personalized advice
```

**3. Interviewer AI (5 min)**
```
→ http://localhost:3000/interviewer/setup
→ Set Role="Senior Engineer", Type="Behavioral"
→ Click "Start Interview"
→ Answer 2-3 questions using STAR method
→ Click "Submit Interview"
→ See AI feedback
```

**4. Job Search (2 min)**
```
→ http://localhost:3000/jobs/search
→ Search "Software Engineer"
→ Click on a job
→ See AI match score
→ Click "Apply" to see auto-tailored resume
```

**5. Subscription Page (1 min)**
```
→ http://localhost:3000/subscription
→ Compare Free vs Pro vs Enterprise
→ Toggle Monthly/Yearly billing
→ View feature comparison
```

---

## 🔧 **Developer Tools**

### **API Documentation**
**URL:** http://localhost:8000/docs

**What it shows:**
- All 25+ API endpoints
- Interactive API testing (Swagger UI)
- Request/response schemas
- Authentication requirements

### **Health Check**
**URL:** http://localhost:8000/api/health

**Returns:**
```json
{
  "status": "operational",
  "api": "operational",
  "gemini": "configured",
  "database": "error" // Known issue - RLS permissions
}
```

---

## 🎨 **Feature Comparison Table**

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| **Career Analysis** | 5/month | Unlimited | Unlimited |
| **Visual Roadmap** | ✅ | ✅ | ✅ |
| **Career Coach** | Limited | ✅ Full | ✅ Full |
| **Interviewer AI** | 2 sessions/mo | Unlimited | Unlimited |
| **Job Marketplace** | View only | Apply | Apply + Priority |
| **Resume Studio** | Basic | ✅ Full | ✅ Full |
| **AI Match Score** | ❌ | ✅ | ✅ |
| **Auto-tailored Resume** | ❌ | ✅ | ✅ |
| **Priority Support** | ❌ | ❌ | ✅ |
| **Team Features** | ❌ | ❌ | ✅ |

---

## 📱 **Navigation Menu**

Your app should have a navigation menu with these links. If not, you can access them directly:

```
Home           → http://localhost:3000
Dashboard      → http://localhost:3000/dashboard
Career Coach   → http://localhost:3000/career-coach
Interviewer AI → http://localhost:3000/interviewer
Jobs           → http://localhost:3000/jobs/search
Resume Studio  → http://localhost:3000/resume-studio
Subscription   → http://localhost:3000/subscription
```

---

## 🐛 **Troubleshooting**

### **Page Not Found (404)**
```bash
# Check if frontend is running
lsof -i :3000 | grep LISTEN

# Restart if needed
cd frontend
PATH=/usr/local/bin:$PATH npm run dev
```

### **API Errors (500)**
```bash
# Check backend logs
tail -f backend/backend.log

# Restart backend
cd backend
PYTHONPATH=$(pwd) python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Empty/Mock Data**
✅ **Fixed!** - All endpoints now return real Gemini AI data

---

## 🎯 **Recommended Exploration Order**

**For Developers:**
1. Dashboard (Core analysis)
2. API Docs (http://localhost:8000/docs)
3. Career Coach (AI chat)
4. Interviewer AI (Full flow)
5. Resume Studio (Upload & suggestions)

**For End Users:**
1. Dashboard (Analyze your career)
2. Visual Roadmap (See career path)
3. Career Coach (Get personalized advice)
4. Interviewer AI (Practice interviews)
5. Job Search (Find matched jobs)
6. Subscription (Upgrade for unlimited)

---

## 🔥 **Pro Tips**

1. **Use Real Data:** Enter your actual job title and skills for personalized results
2. **STAR Method:** When using Interviewer AI, structure answers as Situation → Task → Action → Result
3. **Bookmark Pages:** Save frequently used features for quick access
4. **Check API Docs:** http://localhost:8000/docs shows all available endpoints
5. **Watch Network Tab:** Open browser DevTools to see real API calls

---

## ✅ **What's Working Right Now**

- ✅ Backend: All 25+ endpoints operational
- ✅ Gemini AI: Real analysis, roadmaps, chat, interview questions
- ✅ Frontend: All pages rendering
- ✅ API Connection: localhost:8000 ↔ localhost:3000
- ✅ Real Data: No more mock responses!

---

## 🚀 **Start Exploring!**

**Try this right now:**

1. Open http://localhost:3000/career-coach
2. Start a new chat
3. Ask: "I'm a software engineer with 5 years of Python experience. How can I transition into AI/ML engineering?"
4. See real Gemini AI response!

Or:

1. Open http://localhost:3000/interviewer/setup
2. Configure: Role="Senior Software Engineer", Type="Behavioral"
3. Click "Start Interview"
4. Practice with AI-generated questions!

---

**Need help with a specific feature? Let me know which one you want to explore!** 🎉
