# NEXT Career Intelligence Brain: Implementation Plan

## Executive Summary

Build a 5-layer hybrid AI system for career intelligence:
1. **Layer 1**: Rule-based filtering (<10ms, $0 cost)
2. **Layer 2**: Semantic skill matching (<20ms, embeddings)
3. **Layer 3**: Experience matching (<50ms, regex + ML)
4. **Layer 4**: Career health scoring (background, daily)
5. **Layer 5**: ML training loop (weekly retrain)

**Timeline**: 8 weeks
**Budget**: $400/month operational cost
**Performance**: <100ms job matching, 85%+ accuracy

---

## Week 1-2: Core Matching Engine

### Deliverables
- [ ] Layer 1: Rule-based filtering engine
- [ ] Layer 2: Semantic skill matcher
- [ ] Layer 3: Experience matcher
- [ ] Job orchestrator service
- [ ] FastAPI endpoints
- [ ] Unit tests (95%+ coverage)

### Layer 1: Rule-Based Filtering

**File**: `app/layers/layer1_filtering.py`

**Implementation Steps**:
1. Create `JobFilterEngine` class
2. Implement location filtering with Haversine formula
3. Implement salary range filtering
4. Implement hard requirements (certs, clearances)
5. Implement experience range filtering
6. Add caching for frequently-used filters
7. Write unit tests

**Key Functions**:
```python
class JobFilterEngine:
    def filter_jobs_for_user(user, jobs) -> List[Job]
    def _filter_by_location(user, jobs) -> List[Job]
    def _filter_by_salary(user, jobs) -> List[Job]
    def _filter_by_hard_requirements(user, jobs) -> List[Job]
    def _calculate_distance(loc1, loc2) -> float
```

**Performance Target**: <10ms for 10K jobs
**Test Coverage**: 95%+

---

### Layer 2: Semantic Skill Matching

**File**: `app/layers/layer2_semantic.py`

**Implementation Steps**:
1. Download and cache `all-MiniLM-L6-v2` model (80MB)
2. Create embedding cache system (pickle)
3. Implement `SemanticSkillMatcher` class
4. Calculate cosine similarity matrix
5. Generate match explanations
6. Add batch processing for efficiency
7. Write unit tests with diverse skill sets

**Key Functions**:
```python
class SemanticSkillMatcher:
    def __init__(cache_path)
    def get_embedding(skill) -> np.ndarray
    def calculate_skill_match(user_skills, job_skills) -> Dict
    def batch_match_jobs(user_skills, jobs) -> List[Tuple]
    def _generate_explanation(score, matched, missing) -> str
```

**Performance Target**: <20ms per job
**Accuracy Target**: 85%+ vs. human judgment
**Test Coverage**: 90%+

**Cache Strategy**:
- Store all embeddings in `data/skill_embeddings.pkl`
- Load once at startup (lazy loading)
- Save every 100 new embeddings

---

### Layer 3: Experience Matching

**File**: `app/layers/layer3_experience.py`

**Implementation Steps**:
1. Create `ExperienceMatcher` class
2. Implement regex patterns for years extraction
3. Build seniority level classification
4. Calculate appropriateness scores
5. Detect overqualification
6. Generate trajectory analysis
7. Write comprehensive test suite

**Key Functions**:
```python
class ExperienceMatcher:
    def extract_years_requirement(job_desc, job_title) -> Tuple[int, int]
    def extract_seniority_from_title(title) -> SeniorityLevel
    def calculate_experience_match(user, job) -> ExperienceMatch
    def _generate_explanation() -> str
```

**Performance Target**: <50ms per evaluation
**Accuracy Target**: 90%+ appropriate matches
**Test Coverage**: 95%+

---

### Job Orchestrator

**File**: `app/services/job_matcher.py`

Coordinates all layers in sequence:

```python
class JobMatchOrchestrator:
    def match_jobs_for_user(user_id, filters, limit=20):
        # 1. Fetch user profile
        user = get_user(user_id)

        # 2. Fetch candidate jobs (top 10K from DB)
        jobs = fetch_jobs(limit=10000)

        # 3. Layer 1: Filter (eliminates 90%)
        filtered = filter_engine.filter_jobs_for_user(user, jobs)
        # Now ~1K jobs

        # 4. Layer 2: Semantic skills (score all)
        skill_matches = semantic_matcher.batch_match_jobs(
            user.skills, filtered
        )

        # 5. Layer 3: Experience (score all)
        experience_matches = [
            experience_matcher.calculate_experience_match(
                user, job
            ) for job in filtered
        ]

        # 6. Combine scores
        final_matches = combine_scores(
            filtered, skill_matches, experience_matches
        )

        # 7. Sort and return top N
        final_matches.sort(key=lambda x: x.score, reverse=True)
        return final_matches[:limit]
```

---

## Week 3-4: Career Health Scoring

### Deliverables
- [ ] Layer 4: Career health algorithm
- [ ] TimescaleDB schema for history
- [ ] Background job scheduler
- [ ] Alert system for score drops
- [ ] Health dashboard API
- [ ] Celery tasks

### Layer 4: Career Health Service

**File**: `app/layers/layer4_health.py`

**5 Components (0-100 each)**:
1. **Skill Relevance (30%)**: Market demand of user's skills
2. **Experience Trajectory (20%)**: Career progression analysis
3. **Market Positioning (20%)**: Comparison to peers
4. **Learning Velocity (15%)**: Upskilling rate
5. **Automation Resilience (15%)**: AI-proof score

**Implementation Steps**:
1. Create `CareerHealthService` class
2. Implement each component calculation
3. Add weighted scoring algorithm
4. Build trend analysis (7d, 30d)
5. Generate actionable insights
6. Create alert triggers
7. Write comprehensive tests

**Key Functions**:
```python
class CareerHealthService:
    def calculate_career_health(user_id) -> CareerHealthResult
    def _calculate_skill_relevance(user_skills) -> float
    def _calculate_experience_trajectory(work_history) -> float
    def _calculate_market_positioning(user) -> float
    def _calculate_learning_velocity(learning_activity) -> float
    def _calculate_automation_resilience(user) -> float
    def _generate_insights(components, trend) -> List[str]
    def _generate_action_items(components, user) -> List[Dict]
```

**Performance Target**: <5s per calculation
**Update Frequency**: Daily (background job)

---

### Database Schema

**Table**: `career_health_history`
```sql
CREATE TABLE career_health_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    skill_relevance DECIMAL(5,2),
    experience_trajectory DECIMAL(5,2),
    market_positioning DECIMAL(5,2),
    learning_velocity DECIMAL(5,2),
    automation_resilience DECIMAL(5,2),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- TimescaleDB hypertable for efficient time-series queries
SELECT create_hypertable('career_health_history', 'timestamp');

-- Index for fast user lookups
CREATE INDEX idx_health_user_time ON career_health_history (user_id, timestamp DESC);
```

---

### Background Jobs

**File**: `app/tasks/health_tasks.py`

```python
@celery.task
def calculate_health_for_all_users():
    """Run daily at 2 AM"""
    users = get_active_users()

    for user in users:
        result = health_service.calculate_career_health(user.id)

        # Check for alerts
        if result.trend_7d < -5:
            send_alert(user, result)
```

**Schedule**:
- Daily: 2:00 AM (off-peak)
- Stagger execution: 100 users/minute
- Total time for 10K users: ~100 minutes

---

## Week 5-6: ML Training Pipeline

### Deliverables
- [ ] Layer 5: ML training pipeline
- [ ] Training data collection system
- [ ] XGBoost model implementation
- [ ] MLflow integration
- [ ] A/B testing framework
- [ ] Model deployment automation

### Layer 5: ML Training Loop

**File**: `app/layers/layer5_ml.py`

**Training Data**:
- **Positive examples**: User applied/bookmarked job
- **Negative examples**: User viewed but didn't engage
- **Features**: 25+ features from all layers
- **Labels**: Binary (interested: 1/0) or score (1-5 stars)

**Implementation Steps**:
1. Create `CareerMatchMLModel` class
2. Implement data collection from `job_views` table
3. Build feature engineering pipeline
4. Train XGBoost model with cross-validation
5. Integrate with MLflow for versioning
6. Build A/B testing framework
7. Create deployment automation

**Key Functions**:
```python
class CareerMatchMLModel:
    def collect_training_data(days=30) -> pd.DataFrame
    def prepare_features(df) -> Tuple[X, y]
    def train(retrain=False) -> Dict
    def evaluate(X_test, y_test) -> Dict
    def deploy_model(model_uri, traffic_pct=10) -> bool
    def monitor_performance() -> Dict
```

**Performance Targets**:
- Training time: <10 minutes (10K examples)
- Accuracy: 80%+ (binary classification)
- Precision@10: 70%+
- NDCG@20: 0.75+

---

### Feature Engineering

**25 Features**:
```python
FEATURES = [
    # From Layer 2
    'hard_skills_score',
    'soft_skills_score',
    'skill_overlap_count',
    'missing_critical_skills_count',

    # From Layer 3
    'experience_score',
    'seniority_match',
    'trajectory_score',

    # User features
    'user_years_experience',
    'user_skill_count',
    'user_career_health',
    'user_days_since_last_update',
    'user_application_rate',  # % of viewed jobs applied to

    # Job features
    'job_salary',
    'job_seniority_level',
    'job_is_remote',
    'job_days_since_posted',
    'job_application_count',

    # Match features
    'location_distance_km',
    'salary_vs_current_pct',
    'industry_match',

    # Context features
    'hour_of_day',
    'day_of_week',
    'search_intent',  # 0=browse, 1=specific
    'device_type',  # 0=mobile, 1=desktop
    'referral_source'  # 0=search, 1=email, 2=browse
]
```

---

### MLflow Integration

```python
import mlflow
import mlflow.xgboost

with mlflow.start_run():
    # Log parameters
    mlflow.log_params({
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100
    })

    # Train model
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)

    # Log metrics
    mlflow.log_metrics({
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'auc_roc': auc
    })

    # Log model
    mlflow.xgboost.log_model(model, 'model')

    # Register model if improved
    if accuracy > current_best_accuracy:
        mlflow.register_model(
            f'runs:/{run.info.run_id}/model',
            'CareerMatchModel'
        )
```

---

### A/B Testing Framework

**File**: `app/services/ab_testing.py`

```python
class ABTestingService:
    def get_model_for_user(user_id):
        """
        Route user to model version
        90% get production model
        10% get challenger model
        """
        hash_value = hash(user_id) % 100

        if hash_value < 90:
            return load_model('production')
        else:
            return load_model('challenger')

    def track_prediction(user_id, job_id, model_version, score):
        """Log prediction for evaluation"""
        db.insert('model_predictions', {
            'user_id': user_id,
            'job_id': job_id,
            'model_version': model_version,
            'predicted_score': score,
            'timestamp': now()
        })

    def evaluate_experiment():
        """
        After 1 week, compare:
        - Click-through rate
        - Application rate
        - User satisfaction
        """
        production_metrics = get_metrics('production')
        challenger_metrics = get_metrics('challenger')

        # Statistical significance test
        p_value = stats.ttest_ind(
            production_metrics,
            challenger_metrics
        ).pvalue

        if p_value < 0.05 and challenger_metrics.mean() > production_metrics.mean():
            return 'promote_challenger'
        else:
            return 'keep_production'
```

---

## Week 7-8: Production Readiness

### Deliverables
- [ ] Performance optimization
- [ ] Caching strategy
- [ ] Load testing (10K concurrent)
- [ ] Monitoring & alerting
- [ ] Documentation
- [ ] Deployment automation

### Performance Optimization

**Caching Strategy**:
```python
# Redis cache for hot data
@cache(ttl=3600)  # 1 hour
def get_user_profile(user_id):
    return db.query(User).get(user_id)

@cache(ttl=300)  # 5 minutes
def get_job_details(job_id):
    return db.query(Job).get(job_id)

# Embedding cache (never expires, file-based)
embedding_cache = load_pickle('data/skill_embeddings.pkl')
```

**Database Query Optimization**:
```sql
-- Index for job filtering
CREATE INDEX idx_jobs_location_salary ON jobs (location, salary_max);
CREATE INDEX idx_jobs_posted_date ON jobs (posted_date DESC);

-- Index for user lookups
CREATE INDEX idx_users_skills ON user_skills (user_id, skill_id);

-- Materialized view for aggregations
CREATE MATERIALIZED VIEW job_match_statistics AS
SELECT
    job_id,
    COUNT(*) as view_count,
    COUNT(application_id) as application_count,
    AVG(match_score) as avg_match_score
FROM job_views
GROUP BY job_id;

REFRESH MATERIALIZED VIEW CONCURRENTLY job_match_statistics;
```

---

### Load Testing

**File**: `tests/performance/load_test.py`

```python
from locust import HttpUser, task, between

class JobMatchUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def match_jobs(self):
        self.client.post('/api/v1/match/jobs', json={
            'user_id': f'user_{random.randint(1, 10000)}',
            'limit': 20
        })

    @task(1)
    def get_health(self):
        user_id = f'user_{random.randint(1, 10000)}'
        self.client.get(f'/api/v1/health/{user_id}')

# Run: locust -f tests/performance/load_test.py --users 1000 --spawn-rate 100
```

**Performance Targets**:
- 1000 concurrent users
- p95 latency: <200ms
- p99 latency: <500ms
- Error rate: <0.1%

---

### Monitoring

**Metrics to Track**:
```python
from prometheus_client import Counter, Histogram

# Request metrics
request_latency = Histogram(
    'job_match_latency_seconds',
    'Job matching latency'
)

request_count = Counter(
    'job_match_requests_total',
    'Total job match requests'
)

# Accuracy metrics
model_accuracy = Gauge(
    'ml_model_accuracy',
    'Current model accuracy'
)

# Cache metrics
cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)
```

**Alerts**:
```yaml
# Prometheus alerts
groups:
  - name: brain_service
    rules:
      - alert: HighLatency
        expr: job_match_latency_seconds{quantile="0.95"} > 0.2
        for: 5m
        annotations:
          summary: "95th percentile latency above 200ms"

      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.01
        for: 5m
        annotations:
          summary: "Error rate above 1%"

      - alert: ModelAccuracyDrop
        expr: ml_model_accuracy < 0.75
        for: 1h
        annotations:
          summary: "Model accuracy dropped below 75%"
```

---

## Cost Analysis

### Compute (Cloud Run)
- 2 vCPUs, 2GB RAM
- Avg request duration: 100ms
- 10K users × 10 requests/day = 100K requests/day
- 100K × 0.1s = 10,000 vCPU-seconds/day = 300K/month
- Cost: ~$150/month

### Database (Cloud SQL PostgreSQL)
- db-custom-2-7680 (2 vCPUs, 7.5GB RAM)
- Cost: ~$50/month

### Redis (MemoryStore)
- 1GB instance
- Cost: ~$30/month

### Neo4j (Self-hosted on Compute Engine)
- e2-standard-2 (2 vCPUs, 8GB RAM)
- Cost: ~$50/month

### OpenAI API
- 1M tokens/month for health insights
- Cost: ~$100/month

### Storage (Cloud Storage)
- Models, embeddings: 5GB
- Cost: ~$20/month

**Total: $400/month**

---

## Success Metrics

### Technical KPIs
- Job match latency p95: <100ms ✅
- Career health calc time: <5s ✅
- Model accuracy: >80% ✅
- Cache hit rate: >90% ✅
- Uptime: >99.9% ✅

### Business KPIs
- User engagement: +50% (more job views)
- Application rate: +30% (better matches)
- User retention: +40% (health score engagement)
- Premium conversion: +25% (value demonstration)

---

## Next Steps

1. **Week 1**: Start with Layer 1 & 2 (filtering + semantic)
2. **Week 2**: Complete Layer 3 (experience matching)
3. **Week 3**: Implement Layer 4 (career health)
4. **Week 4**: Build background jobs + alerts
5. **Week 5**: ML training pipeline
6. **Week 6**: A/B testing framework
7. **Week 7**: Performance optimization + load testing
8. **Week 8**: Production deployment + monitoring

## Questions?

Contact: engineering@nextci.com
