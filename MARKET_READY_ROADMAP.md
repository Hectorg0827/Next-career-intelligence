# 🚀 Market-Ready Product Roadmap
**NEXT | Adaptive Career Intelligence**  
**From Prototype to Production - Complete Action Plan**

---

## 📊 **Current State Assessment**

### ✅ What's Working
- All UI pages built and rendering
- Backend API operational with 25+ endpoints
- Gemini AI integration working
- Basic data flow established
- Component library complete

### ⚠️ What's Missing for Market Launch
The app currently has **feature shells** but lacks **production functionality**:

1. **No Real Authentication** - Users can't create accounts or log in
2. **No Data Persistence** - Nothing is saved to database
3. **No Payment Integration** - Can't actually subscribe
4. **No User State Management** - No session tracking
5. **Mock Data Everywhere** - Frontend uses hardcoded data
6. **No Error Handling** - App crashes on failures
7. **No Loading States** - Poor UX during API calls
8. **No Testing** - Zero unit/integration tests
9. **No Security** - No rate limiting, validation, or protection
10. **No Deployment** - Not configured for production

---

## 🎯 **CRITICAL PATH: MVP Market Launch (4-6 Weeks)**

### **Phase 1: Authentication & User Management (Week 1)**

#### 1.1 Firebase Authentication Setup ✅ HIGH PRIORITY
**Why Critical:** Users need accounts to save data and subscribe

**Tasks:**
- [ ] Create Firebase project (if not exists)
- [ ] Configure Firebase authentication
- [ ] Add email/password signup
- [ ] Add Google OAuth login
- [ ] Implement protected routes
- [ ] Create user onboarding flow

**Files to Modify:**
```
frontend/src/lib/firebase.ts - Already configured, needs real credentials
frontend/src/app/login/page.tsx - CREATE
frontend/src/app/signup/page.tsx - CREATE
frontend/src/app/onboarding/page.tsx - CREATE
frontend/src/middleware.ts - CREATE (route protection)
```

**Implementation:**
```typescript
// frontend/src/lib/auth-context.tsx - CREATE
import { createContext, useContext, useEffect, useState } from 'react';
import { onAuthChange, signInWithGoogle, signInWithEmail } from './firebase';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthChange((user) => {
      setUser(user);
      setLoading(false);
      
      // Store user ID in localStorage for API calls
      if (user) {
        localStorage.setItem('userId', user.uid);
        localStorage.setItem('authToken', user.getIdToken());
      } else {
        localStorage.removeItem('userId');
        localStorage.removeItem('authToken');
      }
    });

    return unsubscribe;
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
```

**Validation:**
- [ ] User can sign up with email/password
- [ ] User can log in with Google OAuth
- [ ] Protected routes redirect to login
- [ ] User ID is sent with all API requests
- [ ] Session persists across page refreshes

---

### **Phase 2: Database Integration & Data Persistence (Week 1-2)**

#### 2.1 Fix Supabase RLS Permissions ✅ CRITICAL
**Why Critical:** Without this, nothing can be saved to database

**Tasks:**
- [ ] Access Supabase dashboard
- [ ] Configure RLS policies for all tables
- [ ] Test insert/update/delete operations
- [ ] Verify backend can write to database

**Supabase RLS Policies to Add:**
```sql
-- Users table
CREATE POLICY "Users can view own data" ON users
  FOR SELECT USING (auth.uid() = firebase_uid);

CREATE POLICY "Users can update own data" ON users
  FOR UPDATE USING (auth.uid() = firebase_uid);

-- Career profiles table
CREATE POLICY "Users can manage own profiles" ON career_profiles
  FOR ALL USING (auth.uid() = (SELECT firebase_uid FROM users WHERE id = user_id));

-- Analyses table
CREATE POLICY "Users can view own analyses" ON analyses
  FOR SELECT USING (auth.uid() = (SELECT firebase_uid FROM users WHERE id = user_id));

-- Similar policies for all tables...
```

**Backend Updates:**
```python
# backend/app/api/analyze.py - Add user_id to database writes
async def analyze_career(request: AnalysisRequest, user_id: str):
    # ... existing analysis code ...
    
    # Save to database
    db = SupabaseDB()
    analysis_data = {
        "id": analysis_id,
        "user_id": user_id,  # From auth token
        "job_title": request.job_title,
        "ai_displacement_risk": risk_analysis,
        "skill_insights": skill_insights,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db.insert("analyses", analysis_data)
    
    return analysis_result
```

**Validation:**
- [ ] Backend health check shows `"database": "operational"`
- [ ] Analysis results saved to Supabase
- [ ] User can view analysis history
- [ ] Data persists across sessions

---

#### 2.2 Implement User History & Analytics
**Tasks:**
- [ ] Save all analyses to database
- [ ] Create analysis history page
- [ ] Add "View Past Analyses" button
- [ ] Show analysis trends over time

**Files to Create:**
```
frontend/src/app/history/page.tsx - Analysis history
frontend/src/components/AnalysisCard.tsx - Display past analysis
backend/app/api/users.py - Add GET /users/{user_id}/analyses
```

---

### **Phase 3: Payment Integration (Week 2)**

#### 3.1 Stripe Integration ✅ CRITICAL FOR REVENUE
**Why Critical:** Can't make money without payment processing

**Tasks:**
- [ ] Create Stripe account
- [ ] Configure Stripe products (Free/Pro/Enterprise)
- [ ] Add Stripe SDK to frontend
- [ ] Create checkout flow
- [ ] Implement webhook handlers
- [ ] Add subscription status checks

**Backend Implementation:**
```python
# backend/app/api/subscriptions.py - UPDATE
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/subscriptions/subscribe")
async def create_subscription(
    plan_id: str,
    user_id: str,
    payment_method_id: str
):
    """Create Stripe subscription"""
    try:
        # Create or retrieve Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            payment_method=payment_method_id,
            metadata={"user_id": user_id}
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": plan_id}],
            expand=["latest_invoice.payment_intent"]
        )
        
        # Save to database
        db.insert("subscriptions", {
            "user_id": user_id,
            "stripe_customer_id": customer.id,
            "stripe_subscription_id": subscription.id,
            "plan": plan_id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end
        })
        
        return {"subscription": subscription}
    except stripe.error.StripeError as e:
        raise HTTPException(400, detail=str(e))
```

**Frontend Implementation:**
```tsx
// frontend/src/components/CheckoutForm.tsx - CREATE
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY!);

export function CheckoutForm({ planId, amount }) {
  const stripe = useStripe();
  const elements = useElements();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!stripe || !elements) return;
    
    // Create payment method
    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement)!,
    });
    
    if (error) {
      console.error(error);
      return;
    }
    
    // Send to backend
    const response = await SubscriptionsAPI.subscribe({
      plan_id: planId,
      payment_method_id: paymentMethod.id
    });
    
    // Handle result
    if (response.subscription.status === 'active') {
      alert('Subscription successful!');
      router.push('/dashboard');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      <button type="submit" disabled={!stripe}>
        Subscribe for ${amount}/month
      </button>
    </form>
  );
}
```

**Validation:**
- [ ] User can select a plan
- [ ] Stripe checkout modal opens
- [ ] Payment is processed
- [ ] Subscription status updates in database
- [ ] User sees "Pro" badge after upgrade
- [ ] Webhooks handle cancellations/renewals

---

### **Phase 4: Real Feature Functionality (Week 2-3)**

#### 4.1 Career Coach - Connect to Backend
**Current Issue:** Uses mock conversations, doesn't call API

**Fix:**
```tsx
// frontend/src/app/career-coach/page.tsx - UPDATE
const handleSendMessage = async () => {
  if (!newMessage.trim()) return;
  
  const userMessage = { role: 'user', content: newMessage };
  setMessages([...messages, userMessage]);
  setNewMessage('');
  setIsLoading(true);
  
  try {
    // REAL API CALL - not mock
    const userId = localStorage.getItem('userId');
    const response = await CoachAPI.chat({
      user_id: userId!,
      message: newMessage,
      conversation_id: currentConversation?.id
    });
    
    const aiMessage = { 
      role: 'assistant', 
      content: response.response 
    };
    setMessages([...messages, userMessage, aiMessage]);
    
    // Update conversation ID
    if (response.conversation_id) {
      setCurrentConversation({ 
        id: response.conversation_id, 
        title: messages[0]?.content.substring(0, 50) 
      });
    }
  } catch (error) {
    console.error('Chat error:', error);
    alert('Failed to send message. Please try again.');
  } finally {
    setIsLoading(false);
  }
};
```

**Tasks:**
- [ ] Remove all mock data from career-coach page
- [ ] Connect to `/api/coach/chat` endpoint
- [ ] Save conversations to database
- [ ] Load conversation history on mount
- [ ] Add typing indicators during AI response
- [ ] Handle errors gracefully

---

#### 4.2 Interviewer AI - Full Flow Implementation
**Current Issue:** Setup page doesn't actually start interviews

**Fix:**
```tsx
// frontend/src/app/interviewer/setup/page.tsx - UPDATE
const handleStartInterview = async () => {
  setLoading(true);
  try {
    const userId = localStorage.getItem('userId');
    
    // REAL API CALL
    const response = await InterviewerAPI.startInterview({
      user_id: userId!,
      role_title: role,
      company_name: company || undefined,
      interview_type: interviewType,
      job_description: jobDescription || undefined
    });
    
    // Store session ID and navigate
    localStorage.setItem('currentInterviewSession', response.session_id);
    router.push('/interviewer/practice');
  } catch (error) {
    console.error('Failed to start interview:', error);
    setError('Failed to start interview. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

**Practice Page:**
```tsx
// frontend/src/app/interviewer/practice/page.tsx - UPDATE
useEffect(() => {
  const sessionId = localStorage.getItem('currentInterviewSession');
  if (!sessionId) {
    router.push('/interviewer/setup');
    return;
  }
  
  // Load session from backend
  loadSession(sessionId);
}, []);

const loadSession = async (sessionId: string) => {
  try {
    const session = await InterviewerAPI.getSession(sessionId);
    setQuestions(session.questions);
    setCurrentQuestionIndex(session.current_question || 0);
    setAnswers(session.answers || {});
  } catch (error) {
    console.error('Failed to load session:', error);
  }
};

const handleSubmitAnswer = async () => {
  setSubmitting(true);
  try {
    const response = await InterviewerAPI.submitAnswer({
      session_id: sessionId,
      question_id: questions[currentQuestionIndex].id,
      answer: currentAnswer
    });
    
    // Show feedback
    setFeedback(response.feedback);
    
    // Save answer locally
    setAnswers({
      ...answers,
      [questions[currentQuestionIndex].id]: {
        answer: currentAnswer,
        feedback: response.feedback
      }
    });
    
    // Move to next question
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setCurrentAnswer('');
    } else {
      // Complete interview
      completeInterview();
    }
  } catch (error) {
    console.error('Failed to submit answer:', error);
  } finally {
    setSubmitting(false);
  }
};
```

**Tasks:**
- [ ] Connect setup to backend API
- [ ] Load real questions from Gemini
- [ ] Submit answers to backend
- [ ] Get real-time AI feedback
- [ ] Save session progress
- [ ] Generate final interview report

---

#### 4.3 Job Marketplace - Real Job Data
**Current Issue:** No real jobs, mock data only

**Options:**

**Option A: Job Scraping (Recommended)**
```python
# backend/app/services/job_scraper.py - CREATE
import requests
from bs4 import BeautifulSoup

class JobScraper:
    """Scrape jobs from public sources"""
    
    async def scrape_indeed(self, query: str, location: str):
        """Scrape Indeed for job listings"""
        # Implement scraping logic
        pass
    
    async def scrape_linkedin(self, query: str):
        """Scrape LinkedIn (requires auth)"""
        pass
```

**Option B: Third-party API Integration**
```python
# backend/app/services/job_api.py - CREATE
import requests

class JobAPI:
    """Integrate with job APIs like Adzuna, Reed, etc."""
    
    def __init__(self):
        self.adzuna_app_id = settings.ADZUNA_APP_ID
        self.adzuna_api_key = settings.ADZUNA_API_KEY
    
    async def search_jobs(self, query: str, location: str):
        """Search jobs via Adzuna API"""
        url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_api_key,
            "what": query,
            "where": location,
            "results_per_page": 20
        }
        
        response = requests.get(url, params=params)
        jobs = response.json()["results"]
        
        # Transform to our schema
        return [self._transform_job(job) for job in jobs]
```

**Tasks:**
- [ ] Choose job data source (API vs scraping)
- [ ] Implement job fetching service
- [ ] Store jobs in database (cache)
- [ ] Update `/jobs/search` to show real jobs
- [ ] Implement AI matching algorithm
- [ ] Add job application tracking

---

#### 4.4 Resume Studio - Real Parsing
**Current Issue:** No actual resume parsing

**Implementation:**
```python
# backend/app/services/resume_parser.py - CREATE
from pypdf import PdfReader
from docx import Document
import google.generativeai as genai

class ResumeParser:
    """Parse resumes using Gemini AI"""
    
    async def parse_resume(self, file_content: bytes, file_type: str):
        """Extract structured data from resume"""
        
        # Extract text
        if file_type == "pdf":
            text = self._extract_from_pdf(file_content)
        elif file_type == "docx":
            text = self._extract_from_docx(file_content)
        else:
            text = file_content.decode('utf-8')
        
        # Use Gemini to extract structured data
        model = genai.GenerativeModel('gemini-1.5-pro')
        prompt = f"""
        Extract the following information from this resume:
        - Name
        - Email
        - Phone
        - Skills (list)
        - Work Experience (list of jobs with company, title, dates, responsibilities)
        - Education (list with degree, institution, year)
        - Certifications
        
        Resume text:
        {text}
        
        Return as JSON.
        """
        
        response = await model.generate_content_async(prompt)
        parsed_data = json.loads(response.text)
        
        return parsed_data
```

**Tasks:**
- [ ] Add file upload handling
- [ ] Implement PDF/DOCX parsing
- [ ] Use Gemini for structured extraction
- [ ] Generate improvement suggestions
- [ ] Save parsed profile to database
- [ ] Auto-tailor for job applications

---

### **Phase 5: Production Readiness (Week 3-4)**

#### 5.1 Error Handling & Loading States
**Current Issue:** App crashes on errors, no user feedback

**Global Error Boundary:**
```tsx
// frontend/src/components/ErrorBoundary.tsx - CREATE
import { Component, ReactNode } from 'react';

class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Send to error tracking service (Sentry)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-page">
          <h1>Something went wrong</h1>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Loading States:**
```tsx
// Add to all pages
{isLoading ? (
  <div className="flex items-center justify-center min-h-screen">
    <Loader2 className="w-8 h-8 animate-spin" />
    <p className="ml-4">Analyzing your career data...</p>
  </div>
) : (
  // Actual content
)}
```

**Tasks:**
- [ ] Add error boundaries to all pages
- [ ] Implement toast notifications (react-hot-toast)
- [ ] Add loading spinners to all async operations
- [ ] Show progress bars for long operations
- [ ] Graceful degradation on API failures

---

#### 5.2 Security Hardening
**Current Issues:** No rate limiting, no input validation, exposed keys

**Rate Limiting:**
```python
# backend/app/main.py - ADD
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to endpoints
@router.post("/analyze")
@limiter.limit("10/hour")  # Max 10 analyses per hour for free users
async def analyze_career(request: Request, data: AnalysisRequest):
    ...
```

**Input Validation:**
```python
# backend/app/models/schemas.py - UPDATE
from pydantic import BaseModel, Field, validator

class AnalysisRequest(BaseModel):
    job_title: str = Field(..., min_length=2, max_length=100)
    skills: List[str] = Field(..., min_items=1, max_items=50)
    
    @validator('job_title')
    def validate_job_title(cls, v):
        # Sanitize input
        if any(char in v for char in ['<', '>', '{', '}']):
            raise ValueError('Invalid characters in job title')
        return v.strip()
    
    @validator('skills')
    def validate_skills(cls, v):
        return [skill.strip()[:50] for skill in v if skill.strip()]
```

**Environment Security:**
```bash
# backend/.env - SECURE
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
ALLOWED_ORIGINS=https://yourdomain.com
STRIPE_WEBHOOK_SECRET=whsec_xxx  # From Stripe dashboard
```

**Tasks:**
- [ ] Add rate limiting (10/hour free, unlimited pro)
- [ ] Implement input sanitization
- [ ] Add CORS restrictions
- [ ] Enable HTTPS only
- [ ] Add Stripe webhook signature verification
- [ ] Implement API key rotation
- [ ] Add security headers
- [ ] Enable SQL injection protection

---

#### 5.3 Testing Infrastructure
**Current Issue:** Zero tests

**Unit Tests:**
```python
# backend/tests/test_analyzer.py - CREATE
import pytest
from app.services.gemini_analyzer import GeminiAnalyzer

@pytest.mark.asyncio
async def test_analyze_displacement_risk():
    analyzer = GeminiAnalyzer()
    result = await analyzer.analyze_displacement_risk(
        job_title="Software Engineer",
        skills=["python", "javascript"],
        years_experience=5
    )
    
    assert result["level"] in ["Low", "Medium", "High", "Critical"]
    assert 0 <= result["score"] <= 100
    assert "velocity" in result
```

**Integration Tests:**
```python
# backend/tests/test_api.py - CREATE
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_endpoint():
    response = client.post("/api/analyze", json={
        "job_title": "Software Engineer",
        "skills": ["python"],
        "location": "Remote",
        "years_experience": 5
    })
    
    assert response.status_code == 201
    assert "analysis_id" in response.json()
    assert "ai_displacement_risk" in response.json()
```

**Frontend Tests:**
```tsx
// frontend/__tests__/Dashboard.test.tsx - CREATE
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DashboardPage from '@/app/dashboard/page';

describe('Dashboard', () => {
  it('submits analysis form', async () => {
    render(<DashboardPage />);
    
    fireEvent.change(screen.getByLabelText('Job Title'), {
      target: { value: 'Software Engineer' }
    });
    
    fireEvent.click(screen.getByText('Analyze Career'));
    
    await waitFor(() => {
      expect(screen.getByText('AI Displacement Risk Analysis')).toBeInTheDocument();
    });
  });
});
```

**Tasks:**
- [ ] Write unit tests for all services (80% coverage)
- [ ] Write integration tests for all endpoints
- [ ] Write E2E tests for critical flows
- [ ] Set up CI/CD with GitHub Actions
- [ ] Add test coverage reporting

---

#### 5.4 Performance Optimization
**Current Issues:** Slow load times, large bundle size

**Frontend Optimization:**
```tsx
// Use dynamic imports for heavy components
const CareerSankeyDiagram = dynamic(
  () => import('@/components/VisualCareerMaps/CareerSankeyDiagram'),
  { loading: () => <Loader2 className="animate-spin" /> }
);

// Implement React Query for caching
import { useQuery } from '@tanstack/react-query';

function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['userAnalyses'],
    queryFn: () => apiClient.getUserHistory(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

**Backend Optimization:**
```python
# Add Redis caching
from redis import Redis
import json

redis_client = Redis(host='localhost', port=6379)

@router.post("/analyze")
async def analyze_career(request: AnalysisRequest):
    # Check cache first
    cache_key = f"analysis:{request.job_title}:{','.join(request.skills)}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Generate analysis
    result = await gemini.analyze_displacement_risk(...)
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result))
    
    return result
```

**Tasks:**
- [ ] Implement React Query for API caching
- [ ] Add Redis for backend caching
- [ ] Optimize images (WebP format)
- [ ] Code splitting with dynamic imports
- [ ] Enable gzip compression
- [ ] Add CDN for static assets
- [ ] Database query optimization

---

#### 5.5 Monitoring & Analytics
**Current Issue:** No visibility into app health or user behavior

**Error Tracking:**
```typescript
// frontend/src/lib/sentry.ts - CREATE
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
});
```

**Analytics:**
```typescript
// frontend/src/lib/analytics.ts - CREATE
import mixpanel from 'mixpanel-browser';

mixpanel.init(process.env.NEXT_PUBLIC_MIXPANEL_TOKEN!);

export const analytics = {
  track: (event: string, properties?: any) => {
    mixpanel.track(event, properties);
  },
  identify: (userId: string) => {
    mixpanel.identify(userId);
  },
};

// Usage in components
analytics.track('Career Analyzed', {
  job_title: formData.jobTitle,
  risk_level: analysisResult.ai_displacement_risk.level
});
```

**Health Monitoring:**
```python
# backend/app/api/health.py - UPDATE
@router.get("/health")
async def health_check():
    return {
        "status": "operational",
        "uptime": time.time() - start_time,
        "requests_processed": request_counter,
        "active_users": get_active_user_count(),
        "cache_hit_rate": redis_client.info()["keyspace_hits"],
        "services": {
            "api": "operational",
            "database": check_database_connection(),
            "gemini": "configured",
            "stripe": check_stripe_connection()
        }
    }
```

**Tasks:**
- [ ] Set up Sentry for error tracking
- [ ] Add Mixpanel/PostHog for analytics
- [ ] Track key user events (signup, analysis, subscription)
- [ ] Set up uptime monitoring (Pingdom/UptimeRobot)
- [ ] Create admin dashboard for metrics
- [ ] Set up alerting (PagerDuty/email)

---

### **Phase 6: Deployment & DevOps (Week 4)**

#### 6.1 Production Deployment

**Backend (Google Cloud Run):**
```yaml
# backend/cloudbuild.yaml - CREATE
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/career-intelligence-backend', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/career-intelligence-backend']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'career-intelligence-api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/career-intelligence-backend'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'ENVIRONMENT=production,GEMINI_API_KEY=${_GEMINI_API_KEY}'
```

**Frontend (Vercel):**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://your-backend-url.run.app
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_xxx
```

**Tasks:**
- [ ] Set up production domains
- [ ] Configure SSL certificates
- [ ] Deploy backend to Google Cloud Run
- [ ] Deploy frontend to Vercel
- [ ] Set up environment variables
- [ ] Configure CDN
- [ ] Enable auto-scaling

---

#### 6.2 CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml - CREATE
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
          
  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Cloud Run
        run: gcloud run deploy ...
        
  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel deploy --prod
```

**Tasks:**
- [ ] Set up GitHub Actions
- [ ] Add automated testing on PR
- [ ] Add automated deployment on merge
- [ ] Set up staging environment
- [ ] Add rollback mechanism

---

## 📋 **Market Launch Checklist**

### **MUST HAVE (MVP)**
- [ ] ✅ User authentication (email + Google OAuth)
- [ ] ✅ Data persistence (Supabase working)
- [ ] ✅ Payment integration (Stripe checkout)
- [ ] ✅ Career analysis with real Gemini AI
- [ ] ✅ Career roadmap generation
- [ ] ✅ Basic error handling
- [ ] ✅ Loading states on all pages
- [ ] ✅ Responsive design (mobile-friendly)
- [ ] ✅ Production deployment
- [ ] ✅ SSL/HTTPS enabled

### **SHOULD HAVE (Post-MVP)**
- [ ] Career Coach with conversation history
- [ ] Interviewer AI full flow
- [ ] Job marketplace with real jobs
- [ ] Resume parsing and optimization
- [ ] Usage analytics
- [ ] Error tracking
- [ ] Rate limiting
- [ ] Email notifications

### **NICE TO HAVE (Future)**
- [ ] Mobile apps (React Native)
- [ ] Team collaboration features
- [ ] API for third-party integrations
- [ ] Slack/Discord integration
- [ ] Chrome extension
- [ ] LinkedIn integration

---

## 💰 **Cost Estimates**

### **Infrastructure (Monthly)**
- Google Cloud Run (backend): $20-50
- Vercel (frontend): Free - $20
- Supabase: Free - $25
- Gemini API: ~$50-200 (depends on usage)
- Stripe: 2.9% + $0.30 per transaction
- Domain + SSL: $15/year

**Total: ~$100-300/month** (scales with users)

### **Third-party Services (Optional)**
- Sentry (error tracking): Free - $26/month
- Mixpanel (analytics): Free - $89/month
- SendGrid (emails): Free - $19.95/month
- Redis Cloud: Free - $7/month

---

## 📈 **Revenue Projections**

### **Pricing Strategy**
- Free: $0/month (5 analyses, limited features)
- Pro: $29.99/month (unlimited, all features)
- Enterprise: $99.99/month (team, priority support)

### **Break-even Analysis**
- Monthly costs: ~$200
- Need: 7 Pro users OR 2 Enterprise users
- **Break-even: ~10-20 paid users**

### **Growth Projections (Conservative)**
- Month 1: 10 paid users = $300 revenue
- Month 3: 50 paid users = $1,500 revenue
- Month 6: 200 paid users = $6,000 revenue
- Month 12: 500 paid users = $15,000 revenue

---

## 🎯 **Recommended Development Order**

### **Week 1: Core Infrastructure**
1. Firebase authentication (3 days)
2. Supabase RLS policies (1 day)
3. User onboarding flow (2 days)
4. Protected routes (1 day)

### **Week 2: Payments & Data**
1. Stripe integration (3 days)
2. Subscription management (2 days)
3. Data persistence for analyses (2 days)

### **Week 3: Feature Polish**
1. Career Coach real API (2 days)
2. Interviewer AI full flow (3 days)
3. Error handling & loading states (2 days)

### **Week 4: Production**
1. Security hardening (2 days)
2. Performance optimization (2 days)
3. Monitoring setup (1 day)
4. Deployment (2 days)

---

## 🚀 **Launch Checklist**

### **Pre-Launch (Week 4)**
- [ ] All authentication flows tested
- [ ] Payment processing working
- [ ] Database connections stable
- [ ] Error handling implemented
- [ ] SSL certificates active
- [ ] Terms of Service & Privacy Policy pages
- [ ] Help/FAQ page
- [ ] Contact form

### **Launch Day**
- [ ] Deploy to production
- [ ] Test all critical flows
- [ ] Monitor error logs
- [ ] Announce on social media
- [ ] Send email to beta users

### **Post-Launch (Week 1)**
- [ ] Monitor user signups
- [ ] Track conversion rates
- [ ] Collect user feedback
- [ ] Fix critical bugs
- [ ] Iterate on UX issues

---

## 💡 **Key Success Metrics**

**Technical Metrics:**
- Uptime: > 99.5%
- API response time: < 2s
- Page load time: < 3s
- Error rate: < 1%

**Business Metrics:**
- User signups: 100+ in month 1
- Free → Pro conversion: > 5%
- Churn rate: < 5%/month
- NPS score: > 40

---

## 🎓 **Learning Resources**

**Authentication:**
- Firebase Auth docs: https://firebase.google.com/docs/auth
- Protected routes in Next.js: https://nextjs.org/docs/authentication

**Payments:**
- Stripe integration: https://stripe.com/docs/payments
- Subscription webhooks: https://stripe.com/docs/billing/subscriptions/webhooks

**Testing:**
- Pytest: https://docs.pytest.org
- React Testing Library: https://testing-library.com/react

**Deployment:**
- Google Cloud Run: https://cloud.google.com/run/docs
- Vercel: https://vercel.com/docs

---

## 📞 **Next Steps**

**Immediate (Today):**
1. Review this roadmap
2. Prioritize features for MVP
3. Set up Firebase project
4. Configure Supabase RLS

**This Week:**
1. Implement authentication
2. Fix database persistence
3. Add Stripe integration

**This Month:**
1. Complete MVP features
2. Deploy to production
3. Launch to beta users

---

**Want me to start implementing any specific feature? Which one is the highest priority for you?** 🚀
