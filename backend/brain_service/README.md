# NextCI Brain Service

The intelligent algorithm service for NextCI's career intelligence platform.

## Architecture

This service implements a **hybrid AI architecture** that combines:

1. **Rule-Based Filtering** - Fast elimination of irrelevant jobs
2. **Semantic Matching** - Understanding skill relationships using embeddings
3. **ML Models** - Custom models trained on career outcome data
4. **Graph Algorithms** - Career path discovery (Neo4j)
5. **LLMs** - Explanations and conversations (GPT-4/Claude)

## Components

```
brain_service/
├── app/
│   ├── services/          # Core algorithm services
│   │   ├── skill_matcher.py       # Semantic skill matching
│   │   ├── experience_matcher.py  # Experience level matching
│   │   ├── career_health.py       # Career health scoring
│   │   ├── ml_models.py           # Custom ML models
│   │   └── graph_service.py       # Neo4j career graph
│   ├── models/            # Data models
│   ├── api/              # API endpoints
│   └── core/             # Configuration, utilities
├── tests/                # Comprehensive tests
└── data/                 # Model artifacts, caches
```

## Key Features

### 1. Semantic Skill Matching
- Uses Sentence Transformers (all-MiniLM-L6-v2)
- Understands skill relationships (React ≈ JavaScript)
- ~20ms per evaluation
- Cost: $0 (runs on your server)

### 2. Experience Level Matching
- Extracts years requirements from job descriptions
- Classifies seniority levels
- Prevents mismatches (Senior Director → Junior roles)
- Deterministic and explainable

### 3. Career Health Scoring
- 5-component score (0-100)
- Daily background calculation
- Historical trend tracking
- Proactive alerts on score drops

### 4. ML Model Training
- XGBoost models trained on user interactions
- Continuous learning pipeline
- A/B testing framework
- Weekly retraining

## Cost Structure

For 10,000 users:
- Semantic matching: $0 (self-hosted)
- ML inference: $100/month (compute)
- Neo4j: $200/month
- LLM calls: $200/month (limited usage)
- **Total: ~$500/month**

Compare to LLM-only approach: $300,000/month

## Performance Targets

- Job matching: <100ms per evaluation
- Career health calculation: <5 seconds
- Batch scoring: 1000 jobs/second
- Uptime: 99.9%+

## Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- sentence-transformers==2.2.2
- scikit-learn==1.3.0
- xgboost==2.0.0
- numpy==1.24.3
- neo4j==5.14.0

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific component
pytest tests/test_skill_matcher.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Integration with Main API

The brain service is called by the main API via internal functions:

```python
from brain_service.app.services.skill_matcher import SemanticSkillMatcher

matcher = SemanticSkillMatcher()
result = matcher.calculate_skill_match(user_skills, job_skills)
```

## Development

1. Install dependencies: `pip install -r requirements.txt`
2. Download models: Models auto-download on first use
3. Run tests: `pytest tests/ -v`
4. Start service: Service runs as part of main FastAPI app

## License

Proprietary - NextCI Career Intelligence
