# Quick Start Guide

## 🚀 Getting Started (5 minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional, recommended)

### Option 1: Docker (Recommended)

1. **Clone and setup:**
   ```bash
   cd /Users/hectorgarcia/Desktop/Next-career-intelligence
   ```

2. **Create environment files:**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your API keys
   
   # Frontend
   cp frontend/.env.example frontend/.env.local
   # Edit frontend/.env.local and add Firebase config
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Database UI: http://localhost:8080

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start PostgreSQL (if not using Docker)
# Make sure PostgreSQL is running on localhost:5432

# Run migrations (future step)
# alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will run on http://localhost:8000

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local with Firebase config

# Start development server
npm run dev
```

Frontend will run on http://localhost:3000

## 🔑 Required API Keys

### 1. OpenAI API Key
- Get it from: https://platform.openai.com/api-keys
- Add to `backend/.env`: `OPENAI_API_KEY=sk-...`

### 2. O*NET Web Services
- Register at: https://services.onetcenter.org/reference/
- Add to `backend/.env`: `ONET_API_KEY=your-key`

### 3. Firebase (Frontend Auth)
- Create project: https://console.firebase.google.com/
- Enable Google Auth & Email/Password Auth
- Add config to `frontend/.env.local`

### 4. Coursera API (Optional)
- For production: https://tech.coursera.org/
- For development: app works with mock data

## 🧪 Test the Setup

### Test Backend:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "operational",
    "database": "operational"
  }
}
```

### Test Analysis Endpoint:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Developer",
    "skills": ["Python", "JavaScript"],
    "location": "United States"
  }'
```

### Run Tests:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📊 Database Setup

If using Docker, PostgreSQL is auto-configured. Otherwise:

```bash
# Create database
createdb next_career_db

# Run migrations (when implemented)
cd backend
alembic upgrade head
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Check PostgreSQL is running: `pg_isready`
- Verify environment variables in `.env`

### Frontend build errors
- Clear cache: `rm -rf .next node_modules && npm install`
- Check Node version: `node --version` (need 18+)

### API calls failing
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`

### Docker issues
- Restart containers: `docker-compose restart`
- View logs: `docker-compose logs -f backend`
- Rebuild: `docker-compose build --no-cache`

## 📝 Next Steps

1. ✅ Get API keys and add to `.env` files
2. ✅ Test health endpoints
3. ✅ Run a sample analysis
4. ✅ Set up Firebase authentication
5. ✅ Deploy to production (see main README.md)

## 🆘 Need Help?

- Check full README.md for detailed documentation
- Review API docs: http://localhost:8000/docs
- Check logs: `docker-compose logs -f`
