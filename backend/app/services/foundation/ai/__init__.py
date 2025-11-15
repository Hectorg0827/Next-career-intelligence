"""
AI Package - Autonomous Agents Layer

This package provides AI-powered intelligence on top of the event foundation:

Modules:
- memory: Semantic memory system that learns from events
- recommendations: AI-powered job recommendations
- guidance: Proactive user guidance system
- predictions: Predictive analytics (churn, success, engagement)
- profile_assistant: Smart profile completion assistant

Architecture:
Events → Memory Formation → AI Context → Intelligent Actions

Usage:
    from app.services.foundation.ai import (
        ai_memory,
        recommendation_engine,
        proactive_guidance,
        predictive_analytics,
        profile_assistant
    )
    
    # Form memory from events
    memory = await ai_memory.form_memory_from_events(user_id, "JOB", days=7)
    
    # Get recommendations
    recs = await recommendation_engine.get_recommendations(user_id, limit=10)
    
    # Get proactive guidance
    guidance = await proactive_guidance.get_guidance_for_user(user_id)
    
    # Predict churn
    churn = await predictive_analytics.predict_churn(user_id)
    
    # Analyze profile
    analysis = await profile_assistant.analyze_profile(user_id)
"""

from .memory import ai_memory, AIMemoryLayer, MemoryEmbedding
from .recommendations import recommendation_engine, RecommendationEngine, JobRecommendation
from .guidance import proactive_guidance, ProactiveGuidanceSystem, GuidanceMessage, GuidanceType
from .predictions import (
    predictive_analytics,
    PredictiveAnalytics,
    ChurnPrediction,
    SuccessPrediction,
    EngagementForecast,
    RiskLevel
)
from .profile_assistant import (
    profile_assistant,
    SmartProfileAssistant,
    ProfileAnalysis,
    ProfileSuggestion,
    ProfileCompletenessLevel
)

__all__ = [
    # Memory
    "ai_memory",
    "AIMemoryLayer",
    "MemoryEmbedding",
    
    # Recommendations
    "recommendation_engine",
    "RecommendationEngine",
    "JobRecommendation",
    
    # Guidance
    "proactive_guidance",
    "ProactiveGuidanceSystem",
    "GuidanceMessage",
    "GuidanceType",
    
    # Predictions
    "predictive_analytics",
    "PredictiveAnalytics",
    "ChurnPrediction",
    "SuccessPrediction",
    "EngagementForecast",
    "RiskLevel",
    
    # Profile Assistant
    "profile_assistant",
    "SmartProfileAssistant",
    "ProfileAnalysis",
    "ProfileSuggestion",
    "ProfileCompletenessLevel"
]
