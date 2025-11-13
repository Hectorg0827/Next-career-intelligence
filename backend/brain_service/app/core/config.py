"""
Configuration for Brain Service
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
MODELS_DIR = DATA_DIR / "models"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Model configurations
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"  # Fast, 80MB, good accuracy
SKILL_EMBEDDING_CACHE_PATH = CACHE_DIR / "skill_embeddings.pkl"

# Matching thresholds
SKILL_SIMILARITY_THRESHOLD = 0.7  # 0-1, minimum similarity to consider a match
MIN_MATCH_SCORE_TO_SHOW = 60.0  # 0-100, minimum score to show job to user

# Experience level mappings
SENIORITY_LEVELS = {
    'intern': 0,
    'junior': 1,
    'mid': 2,
    'senior': 3,
    'lead': 4,
    'staff': 5,
    'principal': 6,
    'director': 7,
    'vp': 8,
    'executive': 9
}

# Career Health weights
CAREER_HEALTH_WEIGHTS = {
    'skill_relevance': 0.30,
    'experience_trajectory': 0.20,
    'market_positioning': 0.20,
    'learning_velocity': 0.15,
    'automation_resilience': 0.15
}

# Match score component weights
MATCH_SCORE_WEIGHTS = {
    'hard_skills': 0.30,
    'soft_skills': 0.15,
    'experience': 0.20,
    'goal_alignment': 0.15,
    'automation_safety': 0.10,
    'trajectory': 0.05,
    'preferences': 0.05
}

# Performance settings
BATCH_SIZE = 100  # Number of jobs to process at once
MAX_WORKERS = 4  # Parallel processing workers

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
