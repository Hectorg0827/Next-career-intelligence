"""
Model Router
Routes AI tasks to appropriate models based on complexity and cost.

Strategy:
- gemini-1.5-flash: Fast, cheap — used for extraction, scoring, summarization
- gemini-1.5-pro: High quality — used for synthesis, strategy, complex reasoning
- text-embedding-004: Always used for embeddings
- OpenAI GPT-4o: Fallback when Gemini is rate-limited (optional)
"""

from typing import Optional
from loguru import logger
from app.core.config import settings


# Task type → model mapping
ROUTING_TABLE = {
    # High-quality reasoning tasks: use Pro
    "sdr_synthesis": "gemini-1.5-pro",
    "negotiation_strategy": "gemini-1.5-pro",
    "negotiation_meso": "gemini-1.5-pro",
    "displacement_risk_justification": "gemini-1.5-pro",
    "career_path_analysis": "gemini-1.5-pro",
    "resume_tailoring": "gemini-1.5-pro",
    "cover_letter_generation": "gemini-1.5-pro",
    "offer_analysis": "gemini-1.5-pro",
    "company_research_summary": "gemini-1.5-pro",
    # Fast, cheap tasks: use Flash
    "capability_extraction": "gemini-1.5-flash",
    "skill_gap_summary": "gemini-1.5-flash",
    "job_match_score": "gemini-1.5-flash",
    "demand_trend_summary": "gemini-1.5-flash",
    "profile_completeness_check": "gemini-1.5-flash",
    "layoff_risk_summary": "gemini-1.5-flash",
    "recommendation_ranking": "gemini-1.5-flash",
    "salary_summary": "gemini-1.5-flash",
    # Embeddings
    "embedding": "text-embedding-004",
}

# OpenAI fallback routing (used when Gemini is rate-limited)
OPENAI_FALLBACK_TABLE = {
    "sdr_synthesis": "gpt-4o",
    "negotiation_strategy": "gpt-4o",
    "negotiation_meso": "gpt-4o",
    "resume_tailoring": "gpt-4o",
    "cover_letter_generation": "gpt-4o",
    "offer_analysis": "gpt-4o",
}


class ModelRouter:
    """
    Routes AI tasks to the appropriate model.
    Centralizes model selection so we can optimize cost vs quality globally.
    """

    def get_gemini_model(self, task_type: str) -> str:
        """
        Get the appropriate Gemini model ID for a task type.
        Falls back to the configured default (typically flash).
        """
        model = ROUTING_TABLE.get(task_type, settings.GEMINI_MODEL)
        logger.debug(f"Model routing: task={task_type} → {model}")
        return model

    def get_openai_model(self, task_type: str) -> Optional[str]:
        """
        Get the OpenAI fallback model for a task type.
        Returns None if no OpenAI fallback is configured for this task.
        """
        if not settings.OPENAI_API_KEY:
            return None
        return OPENAI_FALLBACK_TABLE.get(task_type)

    def should_use_pro(self, task_type: str) -> bool:
        """Quick check: does this task need the Pro model?"""
        return ROUTING_TABLE.get(task_type, "") == "gemini-1.5-pro"

    def get_generative_model(self, task_type: str):
        """
        Get an initialized Gemini GenerativeModel for a task type.
        Handles model initialization with the correct model ID.
        """
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model_id = self.get_gemini_model(task_type)
            return genai.GenerativeModel(model_id)
        except Exception as e:
            logger.error(f"Failed to initialize model for task={task_type}: {e}")
            raise


# Singleton instance
model_router = ModelRouter()
