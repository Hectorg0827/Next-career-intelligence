# NEXT | Adaptive Career Intelligence 🧠

> An AI-powered career resilience platform that analyzes job displacement risk, career compatibility, and transition pathways using real-time data from O*NET, LinkedIn, Coursera, and OpenAI GPT-5.

[![Build Status](https://github.com/yourusername/next-career-intelligence/workflows/CI/badge.svg)](https://github.com/yourusername/next-career-intelligence/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Features

- ✅ **Real-time AI Risk Scoring** - Analyzes job displacement risk using GPT-5 and labor market data
- ✅ **Career Compatibility Analysis** - Identifies transition pathways to future-proof roles
- ✅ **Live API Integrations** - No mock data: O*NET, LinkedIn, Coursera, OpenAI
- ✅ **Skill Gap Detection** - Pinpoints missing skills and recommends training
- ✅ **Firebase Authentication** - Google & Email sign-in with saved user history
- ✅ **Interactive Dashboards** - Chart.js visualizations for risk and compatibility metrics
- ✅ **Auto-Debugging** - Built-in error detection and self-healing suggestions

---

## � NEW: Competitive Advantage Roadmap

**We've analyzed Eightfold.ai and SkyHive** to integrate their best features into NEXT Careers. See our comprehensive implementation guides:

### 📚 Implementation Documents

1. **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Start here: Overview and next steps
2. **[IMPLEMENTATION_WEEK_1.md](./IMPLEMENTATION_WEEK_1.md)** - Day-by-day coding guide with examples
3. **[COMPETITIVE_ADVANTAGE_ROADMAP.md](./COMPETITIVE_ADVANTAGE_ROADMAP.md)** - Full feature analysis
4. **[STRATEGIC_POSITIONING.md](./STRATEGIC_POSITIONING.md)** - Business strategy and positioning
5. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - At-a-glance feature comparison
6. **[VISUAL_ROADMAP.md](./VISUAL_ROADMAP.md)** - Timelines and visual planning

### 🔥 Key Features We're Adding

| Feature | From | Status | Impact |
|---------|------|--------|--------|
| **Skill Inference Engine** | Eightfold | 📅 Week 1 | 🔥 CRITICAL |
| **Multi-Year Career Pathways** | Both | 📅 Week 1 | 🔥 CRITICAL |
| **Labour Market Intelligence** | SkyHive | 📅 Week 2-3 | 🔥 HIGH |
| **Visual Career Maps** | Both | 📅 Week 3 | HIGH |
| **Explainable AI** | Eightfold | 📅 Week 1 | HIGH |
| **Benchmarking Dashboard** | SkyHive | 📅 Week 2 | HIGH |

**Our Competitive Edge:**
> "Enterprise-grade AI career intelligence (worth $50k/year) accessible to everyone at $10/month—with better privacy, design, and empathy."

---

## �🏗️ Architecture

### Tech Stack

**Frontend**
- Next.js 14+ (App Router)
- TypeScript
- TailwindCSS
- Firebase Authentication
- Chart.js / Recharts

**Backend**
- FastAPI (Python 3.11+)
- PostgreSQL (user profiles, analysis history)
- Neo4j (skills/roles graph - optional Phase 2)
- LangChain (API orchestration)
- OpenAI GPT-5 API

**Infrastructure**
- Docker & Docker Compose
- GitHub Actions CI/CD
- Vercel (frontend deployment)
- Google Cloud Run (backend deployment)

---

## 📋 Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.11+
- **Docker** & Docker Compose
- **PostgreSQL** 15+ (local or cloud)
- **Git**

### Required API Keys

You'll need accounts and API keys for:

1. **OpenAI** - [Get API Key](https://platform.openai.com/api-keys)
2. **Firebase** - [Create Project](https://console.firebase.google.com/)
3. **O*NET Web Services** - [Register](https://services.onetcenter.org/reference/)
4. **Coursera API** - [Partner Access](https://tech.coursera.org/) (or EdX)
5. **LinkedIn API** (optional) - [Developer Portal](https://developer.linkedin.com/)

---

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/next-career-intelligence.git
cd next-career-intelligence
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required Environment Variables (Backend):**

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/next_career_db

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# O*NET
ONET_API_KEY=your-onet-key-here

# Coursera (optional)
COURSERA_API_KEY=your-coursera-key-here

# Neo4j (optional - Phase 2)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
# or
yarn install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with Firebase config
nano .env.local
```

**Required Environment Variables (Frontend):**

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-app.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### 4. Database Setup

Start PostgreSQL using Docker:

```bash
# From project root
docker-compose up -d postgres

# Run migrations
cd backend
alembic upgrade head
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit: **http://localhost:3000**

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

### Linting & Formatting

**Backend:**
```bash
cd backend
black .
pylint app/
flake8 app/
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run format
```

---

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Adminer (DB UI): http://localhost:8080

---

## 🚢 Production Deployment

### Backend (Google Cloud Run)

```bash
cd backend

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/next-backend

# Deploy to Cloud Run
gcloud run deploy next-backend \
  --image gcr.io/YOUR_PROJECT_ID/next-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=your-prod-db-url,OPENAI_API_KEY=your-key"
```

### Frontend (Vercel)

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Or connect your GitHub repo to Vercel for automatic deployments.

---

## 📊 Database Schema

### PostgreSQL Tables

**users**
- `id` (UUID, PK)
- `email` (string, unique)
- `firebase_uid` (string, unique)
- `name` (string)
- `created_at` (timestamp)

**analyses**
- `id` (UUID, PK)
- `user_id` (UUID, FK)
- `job_title` (string)
- `skills` (jsonb)
- `location` (string)
- `risk_score` (float)
- `compatibility_score` (float)
- `analysis_result` (jsonb)
- `created_at` (timestamp)

---

## 🔌 API Endpoints

### Backend API

**POST /api/analyze**
```json
{
  "job_title": "Graphic Designer",
  "skills": ["Adobe Creative Suite", "UI/UX Design"],
  "location": "United States"
}
```

**Response:**
```json
{
  "ai_displacement_risk": {
    "level": "Medium",
    "score": 65,
    "velocity": "25% automation by 2027",
    "augmentation_potential": "High"
  },
  "compatibility_score": 82,
  "human_advantage_factors": [
    "Empathy and negotiation",
    "Creative problem solving"
  ],
  "transition_pathways": [
    {
      "role": "AI Collaboration Specialist",
      "ease": 85,
      "required_skills": ["AI literacy", "Data interpretation"],
      "training_resources": [...]
    }
  ],
  "skill_gaps": [...],
  "recommended_training": [...]
}
```

**GET /api/user/history** - Get user's previous analyses  
**GET /api/jobs/suggest?q={query}** - Job title autocomplete  
**GET /api/health** - Health check

---

## 🧰 Development Workflow

### Adding a New Feature

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make changes in `frontend/` or `backend/`
3. Run tests: `npm test` / `pytest`
4. Commit: `git commit -m "feat: your feature"`
5. Push and create PR: `git push origin feature/your-feature`
6. GitHub Actions will run CI tests automatically

### Debugging Tips

- **Backend logs:** `docker-compose logs -f backend`
- **Database inspect:** Visit http://localhost:8080 (Adminer)
- **API testing:** Use `backend/test_api.http` with REST Client extension
- **Frontend debug:** Check browser console and Network tab

---

## 📁 Project Structure

```
next-career-intelligence/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   │   ├── page.tsx     # Landing page
│   │   │   ├── dashboard/   # User dashboard
│   │   │   ├── results/     # Analysis results
│   │   │   └── api/         # API proxy routes
│   │   ├── components/      # React components
│   │   │   ├── ui/          # UI primitives
│   │   │   ├── forms/       # Input forms
│   │   │   ├── charts/      # Data visualizations
│   │   │   └── auth/        # Auth components
│   │   └── lib/             # Utilities & configs
│   │       ├── firebase.ts  # Firebase setup
│   │       └── api.ts       # API client
│   ├── public/              # Static assets
│   └── package.json
│
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # App entry point
│   │   ├── api/            # API routes
│   │   │   ├── analyze.py  # /analyze endpoint
│   │   │   ├── jobs.py     # Job-related endpoints
│   │   │   └── users.py    # User endpoints
│   │   ├── services/       # Business logic
│   │   │   ├── ai_analyzer.py      # GPT-5 integration
│   │   │   ├── onet_service.py     # O*NET API
│   │   │   ├── coursera_service.py # Coursera API
│   │   │   └── linkedin_service.py # LinkedIn API
│   │   ├── models/         # Pydantic & SQLAlchemy models
│   │   ├── db/             # Database config
│   │   └── utils/          # Helpers
│   ├── alembic/            # DB migrations
│   ├── tests/              # Pytest tests
│   └── requirements.txt
│
├── .github/
│   └── workflows/
│       ├── ci.yml          # Continuous Integration
│       └── deploy.yml      # Deployment workflow
│
├── docker-compose.yml      # Local development setup
└── README.md              # This file
```

---

## 🧪 Testing Scenarios

Test with these 5+ job titles to validate real API data:

1. **Teacher** → Expected: Medium risk, high human advantage
2. **Graphic Designer** → Expected: Medium-High risk, AI augmentation
3. **Software Engineer** → Expected: Low risk, AI collaboration
4. **Data Entry Clerk** → Expected: High risk, transition needed
5. **Nurse Practitioner** → Expected: Low risk, human-centric
6. **Marketing Manager** → Expected: Medium risk, strategic focus

---

## 🎯 Roadmap

### Phase 1 (Current MVP)
- ✅ User authentication (Firebase)
- ✅ AI risk analysis (GPT-5 + O*NET)
- ✅ Career transition pathways
- ✅ Training recommendations (Coursera)
- ✅ User history & persistence

### Phase 2 (Q1 2026)
- [ ] Neo4j skills graph
- [ ] Mentor matching (Firebase Firestore)
- [ ] Skill evolution timeline (D3.js)
- [ ] Voice assistant integration
- [ ] Mobile app (React Native)

### Phase 3 (Q2 2026)
- [ ] Company partnerships
- [ ] Advanced analytics dashboard
- [ ] Job application tracking
- [ ] Interview preparation AI

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ by the NEXT team

- **AI Architecture:** OpenAI GPT-5, LangChain
- **Data Sources:** O*NET, LinkedIn, Coursera
- **Infrastructure:** Google Cloud, Vercel

---

## 📞 Support

- **Documentation:** [Full Docs](https://docs.example.com)
- **Issues:** [GitHub Issues](https://github.com/yourusername/next-career-intelligence/issues)
- **Email:** support@nextcareer.ai

---

## 🙏 Acknowledgments

- [O*NET Web Services](https://services.onetcenter.org/)
- [OpenAI](https://openai.com/)
- [Coursera](https://www.coursera.org/)
- [Next.js](https://nextjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**Last Updated:** October 18, 2025  
**Version:** 1.0.0-MVP
