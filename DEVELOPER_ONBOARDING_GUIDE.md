# Career OS: Developer Onboarding Guide

**Welcome to the Career OS team!** 🚀  
This guide will help you get up to speed in your first week.

---

## 📅 Your First Week

### Day 1: Environment Setup (3-4 hours)

#### Morning (1 hour)

- [ ] **Welcome Call**
  - [ ] Meet the team (30 min)
  - [ ] Understand your role and responsibilities
  - [ ] Review current priorities
  - [ ] Get access to Slack, GitHub, etc.

- [ ] **Access Setup**
  - [ ] GitHub organization access
  - [ ] GCP project access
  - [ ] Slack workspace
  - [ ] Google Drive access
  - [ ] Notion workspace access
  - [ ] Linear or issue tracker access

#### Afternoon (2-3 hours)

- [ ] **Local Development Environment**
  - [ ] Clone repository:
    ```bash
    git clone https://github.com/Hectorg0827/Next-career-intelligence.git
    cd Next-career-intelligence
    ```

  - [ ] Backend setup (30 min):
    ```bash
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

  - [ ] Frontend setup (20 min):
    ```bash
    cd frontend
    npm install
    ```

  - [ ] Database setup (20 min):
    ```bash
    # Follow BACKEND_DATABASE_FIX.md for Supabase setup
    ```

  - [ ] Environment variables:
    ```bash
    # Create .env files in backend/ and frontend/
    # Ask team lead for values
    cp .env.example .env
    ```

  - [ ] Run services:
    ```bash
    # Terminal 1: Backend
    cd backend
    PYTHONPATH=$(pwd) python3 -m uvicorn app.main:app --reload
    
    # Terminal 2: Frontend
    cd frontend
    npm run dev
    ```

  - [ ] Verify both running:
    - Backend: http://localhost:8000 (should show "Career OS API")
    - Frontend: http://localhost:3000 (should show dashboard)

### Day 2: Understanding the Architecture (Full Day)

#### Reading Materials (3-4 hours)

Priority order (read in this order):

1. **CAREER_OS_SYSTEM_OVERVIEW.md** (30 min)
   - High-level system architecture
   - All three phases overview
   - Current status

2. **PHASE1_INTEGRATION_GUIDE.md** (45 min)
   - Foundation layer (events, journey tracking, profile manager)
   - Database schema
   - Service orchestration

3. **PHASE2_IMPLEMENTATION_COMPLETE.md** (60 min)
   - All 5 AI agents explained
   - All 14 endpoints documented
   - Integration points

4. **PHASE3_iOS_INTEGRATION.md** (30 min, skim)
   - Next phase architecture (don't need deep knowledge yet)
   - Useful for context on where we're heading

#### Code Walkthrough (2-3 hours)

1. **Backend Structure**
   ```
   backend/
   ├── app/
   │   ├── main.py              (entry point)
   │   ├── services/
   │   │   ├── foundation/      (Phase 1)
   │   │   │   ├── events/      (event store)
   │   │   │   ├── journey/     (analytics)
   │   │   │   ├── profile/     (profile manager)
   │   │   │   └── ai/          (AI agents)
   │   │   └── ...
   │   ├── models/              (database models)
   │   ├── api/                 (API routes)
   │   └── tasks/               (background jobs)
   ├── database/
   │   ├── phase1_foundation_schema.sql
   │   └── phase2_ai_agents_schema.sql
   └── requirements.txt
   ```

   **Key files to review**:
   - `backend/app/main.py` - FastAPI setup, CORS, middleware
   - `backend/app/services/foundation/events/event_store.py` - Event system
   - `backend/app/services/foundation/ai/` - All AI agent implementations
   - `backend/app/api/` - All route definitions

2. **Frontend Structure**
   ```
   frontend/
   ├── src/
   │   ├── app/
   │   │   ├── page.tsx          (home)
   │   │   ├── dashboard/        (main dashboard)
   │   │   ├── profile/          (profile pages)
   │   │   ├── jobs/             (job search)
   │   │   └── layout.tsx        (root layout)
   │   ├── components/
   │   │   ├── dashboard/        (dashboard components)
   │   │   ├── profile/          (profile components)
   │   │   ├── jobs/             (job components)
   │   │   └── common/           (shared components)
   │   ├── hooks/                (custom React hooks)
   │   ├── lib/                  (utilities)
   │   └── styles/               (CSS/styling)
   └── package.json
   ```

   **Key files to review**:
   - `frontend/src/app/page.tsx` - Home page
   - `frontend/src/app/dashboard/page.tsx` - Main dashboard
   - `frontend/src/components/dashboard/AIGuidancePanel.tsx` - AI guidance UI
   - `frontend/src/components/profile/AIProfileAssistant.tsx` - Profile optimization UI

3. **Database Schema**
   - Review: `backend/database/phase1_foundation_schema.sql`
   - Review: `backend/database/phase2_ai_agents_schema.sql`
   - Understand:
     - Event store (immutable log of all interactions)
     - Profile tables (user data)
     - AI tables (memory, recommendations, guidance, predictions)

#### Hands-On Activity (1-2 hours)

- [ ] **Make a simple API call**
  ```bash
  # Check health
  curl http://localhost:8000/health
  
  # Get recommendations (with auth header)
  curl -H "Authorization: Bearer YOUR_TOKEN" \
       http://localhost:8000/api/ai/recommendations
  ```

- [ ] **Run the test suite**
  ```bash
  # From backend directory
  python3 test-phase2-integration.py
  python3 test-phase2.py
  ```

- [ ] **Make a small frontend change**
  - Open `frontend/src/app/page.tsx`
  - Change a string and refresh browser
  - Verify hot reload works

### Day 3: Deep Dive into Your Component (Full Day)

This depends on your assigned area:

#### If you're assigned to Backend/AI

- [ ] **Read: AI Agent Implementation Guide**
  - Read: `backend/app/services/foundation/ai/README.md` (if exists)
  - Focus: Which AI agent are you working on?
  - Understand: Input/output, database tables, business logic

- [ ] **Review Specific Agent Code**
  ```python
  # Example: Recommendation Engine
  backend/app/services/foundation/ai/recommendation_engine.py
  
  # Understand:
  # - How jobs are scored
  # - How skills are matched
  # - How the ML algorithm works
  # - Edge cases handled
  ```

- [ ] **Trace an API Call**
  - Pick one endpoint: `/api/ai/recommendations`
  - Find the route handler in `backend/app/api/`
  - Follow the code to the service layer
  - Understand the complete flow

- [ ] **Database Deep Dive**
  - Look at the relevant tables
  - Understand the schema
  - Look at example queries in service code

#### If you're assigned to Frontend

- [ ] **Component Deep Dive**
  - Pick your main component (Dashboard, Profile, JobSearch, etc.)
  - Understand its state management
  - Review: React hooks used
  - Review: API calls made
  - Review: Styling approach

- [ ] **Review Component Examples**
  ```typescript
  // Example: AIGuidancePanel
  frontend/src/components/dashboard/AIGuidancePanel.tsx
  
  // Understand:
  // - Props interface
  // - State management
  // - Effects/hooks
  // - Event handlers
  // - Styling (Tailwind CSS)
  ```

- [ ] **Test the Feature**
  - Use the app with test data
  - Verify: All interactions work
  - Note: Any UI/UX issues
  - Test: Mobile view
  - Test: Error states

#### If you're assigned to DevOps/Infrastructure

- [ ] **Infrastructure Review**
  - Read: `PRODUCTION_DEPLOYMENT_CHECKLIST.md`
  - Review: `cloudbuild.yaml` - GCP deployment config
  - Review: `docker-compose.yml` - Local docker setup
  - Understand: Current deployment architecture

- [ ] **Database Setup**
  - Understand: Supabase setup
  - Review: Database schemas
  - Test: Connection from local environment
  - Practice: Running migrations

### Day 4: Code Review & Team Discussion (Full Day)

- [ ] **Join Code Review Session**
  - Ask to review an open PR
  - Provide thoughtful feedback
  - Ask questions about decisions

- [ ] **Pair Programming (2 hours)**
  - Pair with an existing team member
  - Work on a small bug or feature
  - Learn the coding style and conventions
  - Ask about best practices

- [ ] **Architecture Discussion (1 hour)**
  - Ask team lead about architectural decisions
  - Understand: Why was X chosen over Y?
  - Understand: Technical debt, if any
  - Understand: Future plans

- [ ] **Complete First Task**
  - Pick a small bug or feature (difficulty: easy)
  - Implement the fix
  - Write tests
  - Submit PR for review
  - Incorporate feedback

### Day 5: First Full Week Review (2-3 hours)

- [ ] **Reflection & Sync**
  - What did you learn this week?
  - What questions do you still have?
  - What's confusing?
  - Meeting with your manager/lead

- [ ] **Get Feedback**
  - PR feedback incorporated?
  - Ready for next task?
  - Any blockers?

- [ ] **Plan Next Week**
  - Pick next tasks
  - Identify knowledge gaps
  - Set learning goals

---

## 🛠️ Essential Tools & Technologies

### Backend Stack

**Language & Framework**
- Python 3.12
- FastAPI (modern async web framework)
- SQLAlchemy (ORM)

**Key Libraries**
```
dependencies installed from requirements.txt:
- uvicorn: ASGI server
- python-dotenv: Environment variables
- google-generativeai: Gemini API
- firebase-admin: Firebase integration
- sqlalchemy: Database ORM
- alembic: Database migrations
- pydantic: Data validation
- pytest: Testing
```

**Database**
- PostgreSQL 13+ (primary database)
- Supabase (managed PostgreSQL + auth)

**External APIs**
- Google Gemini API (AI/embeddings)
- Firebase (authentication, hosting)
- OpenAI (optional, for future features)

### Frontend Stack

**Framework & Language**
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS (styling)

**Key Libraries**
```
from package.json:
- react: UI library
- react-dom: React DOM
- next: Framework
- typescript: Type safety
- tailwindcss: Styling
- axios: HTTP client
- zustand or context: State management
- date-fns: Date utilities
- chart.js: Charts (if needed)
```

**APIs**
- Backend REST API
- Google Firebase (auth)

### DevOps & Deployment

**Cloud Platform**
- Google Cloud Platform (GCP)
- Cloud Run (serverless containers)
- Cloud SQL (managed PostgreSQL)
- Cloud Storage (file storage)

**Containerization**
- Docker (local development)
- Docker Compose (orchestration)

**Version Control**
- Git (version control)
- GitHub (repository hosting)

**CI/CD**
- Cloud Build (GCP CI/CD)
- Cloudbuild.yaml (pipeline config)

---

## 📚 Key Documentation Files

### Essential Reading (In Order)

1. **[START HERE] CAREER_OS_SYSTEM_OVERVIEW.md**
   - High-level overview of entire system
   - All phases explained
   - Current status and roadmap
   - Estimated reading time: 30 min

2. **PHASE1_INTEGRATION_GUIDE.md**
   - Foundation layer architecture
   - Event-driven system explanation
   - Database schema overview
   - Estimated reading time: 45 min

3. **PHASE2_IMPLEMENTATION_COMPLETE.md**
   - All 5 AI agents explained in detail
   - Each of the 14 endpoints documented
   - Integration points explained
   - Estimated reading time: 60 min

4. **PHASE3_iOS_INTEGRATION.md** (skim)
   - Next phase architecture
   - Mobile sync strategy
   - Useful for context
   - Estimated reading time: 30 min (skim)

### Component-Specific Documentation

**If working on backend/AI**:
- Read: `backend/app/services/foundation/ai/README.md`
- Read: Specific agent implementation files
- Review: Database schema for AI tables

**If working on frontend**:
- Read: Component README files (if exist)
- Review: Styling conventions (Tailwind CSS)
- Review: React hooks patterns used

**If working on DevOps**:
- Read: `PRODUCTION_DEPLOYMENT_CHECKLIST.md`
- Read: Infrastructure setup docs
- Review: CI/CD pipeline configuration

### Quick References

- **API Documentation**: PHASE2_IMPLEMENTATION_COMPLETE.md (AI endpoints section)
- **Database Schema**: `backend/database/phase1_foundation_schema.sql` and `phase2_ai_agents_schema.sql`
- **Code Examples**: Look in test files: `test-phase2.py`, `test-phase2-integration.py`

---

## 💻 Local Development Commands

### Backend

```bash
# Setup
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env file (ask team for values)
cp .env.example .env

# Run server
PYTHONPATH=$(pwd) python3 -m uvicorn app.main:app --reload

# Run tests
python3 -m pytest

# Run specific test
python3 -m pytest tests/test_specific.py::test_name

# Lint
python3 -m flake8 app/
python3 -m black app/  # Format code

# Check for issues
python3 -m mypy app/  # Type checking
```

### Frontend

```bash
# Setup
cd frontend
npm install

# Create .env.local file (ask team for values)
cp .env.example .env.local

# Run dev server
npm run dev
# Visit http://localhost:3000

# Build for production
npm run build

# Run tests
npm test

# Lint
npm run lint

# Format code
npm run format
```

### Database

```bash
# Connect to Supabase (you'll need psql installed)
psql -h your-db.supabase.co -U postgres -d postgres

# Run migrations (if using Alembic)
cd backend
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Git Workflow

```bash
# Update local code
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, then commit
git add .
git commit -m "Clear description of changes"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# (Ask for review from team members)

# After merge, delete branch
git branch -d feature/your-feature-name
```

---

## 🎯 Code Style & Conventions

### Python (Backend)

**Naming Conventions**
```python
# Classes: PascalCase
class UserProfile:
    pass

# Functions/methods: snake_case
def calculate_recommendation_score():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

**Code Organization**
```python
# Order:
# 1. Imports (stdlib, then third-party, then local)
# 2. Constants
# 3. Classes/functions
# 4. Main guard (if module is runnable)

from typing import List, Optional
import json
from fastapi import FastAPI

BATCH_SIZE = 100

class UserRepository:
    pass

def get_users() -> List[User]:
    pass

if __name__ == "__main__":
    pass
```

**Type Hints**
```python
# Always include type hints
from typing import List, Optional, Dict

def get_recommendations(user_id: str, limit: int = 10) -> List[Dict]:
    """Get AI recommendations for a user.
    
    Args:
        user_id: The user's ID
        limit: Maximum recommendations to return
        
    Returns:
        List of recommendation dicts
    """
    pass
```

### TypeScript/React (Frontend)

**Naming Conventions**
```typescript
// Components: PascalCase
function UserProfile() {}

// Functions/variables: camelCase
const calculateScore = () => {}

// Constants: UPPER_SNAKE_CASE
const MAX_ITEMS = 100

// Interfaces/Types: PascalCase
interface User {
  id: string
  name: string
}
```

**Component Structure**
```typescript
// 1. Imports
import React, { useState } from 'react'

// 2. Type definitions
interface Props {
  userId: string
  onSelect?: (id: string) => void
}

// 3. Component
export function UserCard({ userId, onSelect }: Props) {
  const [isLoading, setIsLoading] = useState(false)
  
  // Hooks
  // Handlers
  // JSX
  return <div>...</div>
}

// 4. Export
export default UserCard
```

**File Organization**
```
src/
├── components/
│   ├── Dashboard/
│   │   ├── index.tsx        (main component)
│   │   ├── Dashboard.tsx    (if large)
│   │   ├── Dashboard.css    (styles)
│   │   └── Dashboard.test.tsx (tests)
│   └── ...
├── hooks/
│   ├── useAuth.ts
│   └── ...
├── lib/
│   ├── api.ts              (API calls)
│   └── utils.ts            (utilities)
└── types/
    └── index.ts            (shared types)
```

---

## 🧪 Testing Guidelines

### Backend Testing

```python
# test_recommendation_engine.py
import pytest
from app.services.foundation.ai.recommendation_engine import RecommendationEngine

class TestRecommendationEngine:
    """Test recommendation engine."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return RecommendationEngine()
    
    def test_score_calculation(self, engine):
        """Test that scoring works correctly."""
        score = engine.calculate_score(user_profile, job)
        assert 0 <= score <= 100
    
    def test_edge_cases(self, engine):
        """Test edge cases."""
        with pytest.raises(ValueError):
            engine.calculate_score(None, job)

# Run tests
pytest test_recommendation_engine.py -v
```

### Frontend Testing

```typescript
// UserCard.test.tsx
import { render, screen } from '@testing-library/react'
import UserCard from './UserCard'

describe('UserCard', () => {
  test('renders user name', () => {
    render(<UserCard userId="123" />)
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  test('calls onSelect when clicked', () => {
    const onSelect = jest.fn()
    render(<UserCard userId="123" onSelect={onSelect} />)
    screen.getByRole('button').click()
    expect(onSelect).toHaveBeenCalledWith('123')
  })
})

// Run tests
npm test
```

---

## 🐛 Debugging Tips

### Backend Debugging

```python
# 1. Use print statements (development only)
print(f"DEBUG: user_id={user_id}, score={score}")

# 2. Use logging (production)
import logging
logger = logging.getLogger(__name__)
logger.debug(f"user_id={user_id}, score={score}")

# 3. Use debugger (pdb)
import pdb; pdb.set_trace()
# Then use commands: l (list), n (next), s (step), c (continue)

# 4. Check logs
# From application stdout, or from logging system
```

### Frontend Debugging

```typescript
// 1. Browser DevTools
// - F12 to open
// - Elements tab for DOM
// - Console tab for errors
// - Network tab for API calls
// - Sources tab for breakpoints

// 2. Console logging
console.log("DEBUG:", { userId, score })
console.error("ERROR:", error)

// 3. React DevTools extension
// - Inspect component tree
// - View props and state
// - Profile performance

// 4. Debugger statement
debugger  // Execution will pause here (if DevTools open)

// 5. Network tab
// - Check API requests/responses
// - Look for failed requests
// - Verify headers
```

### Common Issues

**Backend won't start**
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Try running again
PYTHONPATH=$(pwd) python3 -m uvicorn app.main:app --reload
```

**Frontend won't start**
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Try again
npm run dev
```

**Database connection failed**
```bash
# Verify .env file has correct credentials
cat .env | grep DATABASE

# Test connection manually
psql -h your-host -U your-user -d your-db

# Check if database is running
# (for Supabase, check dashboard)
```

---

## 📞 Getting Help

### First Steps

1. **Check Documentation**
   - Is the answer in CAREER_OS_SYSTEM_OVERVIEW.md?
   - Is the answer in PHASE1_INTEGRATION_GUIDE.md?
   - Is the answer in code comments?

2. **Search in Code**
   - Search GitHub for similar code
   - Use Cmd+F to search files

3. **Google It**
   - "FastAPI + [your problem]"
   - "React hooks + [your problem]"
   - "PostgreSQL + [your problem]"

### Ask for Help

**Slack Channels**
- #engineering (general questions)
- #backend (backend-specific)
- #frontend (frontend-specific)
- #devops (infrastructure)

**In-Person**
- Pair with team member
- Ask during standup
- Schedule 1:1 with manager

**Code Review**
- Ask reviewer for clarification
- Comment on PR with questions

---

## 🎓 Learning Resources

### Backend/Python

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Python Best Practices**: https://pep8.org/
- **Async Python**: https://docs.python.org/3/library/asyncio.html

### Frontend/React

- **React Docs**: https://react.dev
- **Next.js Docs**: https://nextjs.org/docs
- **TypeScript Docs**: https://www.typescriptlang.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs

### Database

- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Supabase Guide**: https://supabase.com/docs
- **SQL Best Practices**: https://use-the-index-luke.com/

### DevOps

- **GCP Docs**: https://cloud.google.com/docs
- **Docker Docs**: https://docs.docker.com/
- **Kubernetes** (if using): https://kubernetes.io/docs/

---

## ✅ First Week Checklist

- [ ] Local environment set up (backend + frontend running)
- [ ] Read CAREER_OS_SYSTEM_OVERVIEW.md
- [ ] Read PHASE1_INTEGRATION_GUIDE.md
- [ ] Read PHASE2_IMPLEMENTATION_COMPLETE.md
- [ ] Skim PHASE3_iOS_INTEGRATION.md
- [ ] Reviewed relevant code in your area
- [ ] Made a small code change and tested it
- [ ] Ran the test suite successfully
- [ ] Attended code review session
- [ ] Paired with a team member
- [ ] Completed first task (small bug/feature)
- [ ] Submitted PR for review
- [ ] Got feedback and incorporated changes
- [ ] Had 1:1 with manager/lead
- [ ] Know who to ask for help

---

## 🎯 Success Metrics

By the end of your first week, you should:

✅ **Knowledge**
- Understand overall system architecture
- Know the three phases and current status
- Understand your specific component
- Know where to find information

✅ **Skills**
- Can run backend and frontend locally
- Can write and run tests
- Can make and push code changes
- Can review code (with guidance)

✅ **Culture**
- Understand team values and practices
- Know how to ask for help
- Feel comfortable in team meetings
- Know the team members and their roles

✅ **Productivity**
- Completed first task
- PR submitted and reviewed
- Got constructive feedback
- Ready for second task

---

## 🚀 Next Steps (Week 2)

After your first week:

1. **Pick Your First Feature**
   - With your manager, choose next task
   - Should be medium difficulty
   - Should use knowledge from Week 1

2. **Deep Dive Your Component**
   - Really understand the code
   - Read all related documentation
   - Make notes of questions

3. **Build & Test**
   - Implement feature/fix
   - Write comprehensive tests
   - Test manually in app

4. **Code Review & Feedback**
   - Get feedback from teammates
   - Incorporate suggestions
   - Learn from their comments

5. **Celebrate!**
   - Your first real contribution
   - You're now productive! 🎉

---

## 📝 Quick Reference

### Essential Commands

```bash
# Backend
cd backend && source .venv/bin/activate
PYTHONPATH=$(pwd) python3 -m uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Tests
python3 -m pytest
npm test

# Git
git pull origin main
git checkout -b feature/name
git add . && git commit -m "message"
git push origin feature/name
```

### Key Endpoints

```
Backend (localhost:8000):
  GET  /health                    - System health
  POST /api/ai/memory/form        - Form memory
  GET  /api/ai/recommendations    - Get recommendations
  GET  /api/ai/guidance           - Get guidance messages
  POST /api/ai/profile/analyze    - Analyze profile

Frontend (localhost:3000):
  /                               - Home
  /dashboard                      - Main dashboard
  /profile                        - User profile
  /jobs                           - Job search
```

### File Locations

```
Configuration:    .env, .env.local
Backend entry:    backend/app/main.py
Frontend entry:   frontend/src/app/page.tsx
Database schema:  backend/database/*.sql
Tests:            **/test_*.py, **/*.test.tsx
Docs:             *.md files in root
```

---

**Welcome aboard!** We're excited to have you on the team. Don't hesitate to ask questions—everyone was new once! 🚀

**Document v1.0** | Last Updated: November 14, 2025
