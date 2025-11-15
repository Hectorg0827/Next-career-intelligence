"""
AI Recommendation Engine

Intelligent recommendation system that learns from user behavior
to provide personalized job, skill, and learning recommendations.
"""

from .job_recommender import JobRecommender
from .skill_recommender import SkillRecommender
from .learning_recommender import LearningRecommender
from .recommendation_engine import RecommendationEngine

# Singleton instance
recommendation_engine = RecommendationEngine()

__all__ = [
    "JobRecommender",
    "SkillRecommender",
    "LearningRecommender",
    "RecommendationEngine",
    "recommendation_engine"
]
