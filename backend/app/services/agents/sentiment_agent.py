"""
Sentiment Agent - Motivation & Emotion Analysis
Extracts what the user loves, hates, fears, and aspires to
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.models.user_profile import (
    UserProfile,
    MotivationSignal,
    UserPreference,
    PreferenceCategory,
    CareerGoal,
    RiskFactor,
)


class SentimentAgent:
    """
    Sentiment Agent - The emotional intelligence layer

    Responsibilities:
    - Extract motivation signals from conversations
    - Detect preferences, goals, and risk signals
    - Monitor burnout and confidence levels
    - Answer: "What does this person truly want and need emotionally?"
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def analyze_conversation(self, user_profile: UserProfile, conversation_text: str) -> Dict[str, Any]:
        """
        Analyze a conversation to extract emotional and motivational insights

        Returns updates for:
        - motivation_signals
        - preferences
        - goals
        - risk_signals
        - burnout_level
        - confidence_level
        """

        try:
            prompt = self._build_sentiment_analysis_prompt(user_profile, conversation_text)

            response = self.model.generate_content(prompt)

            insights = self._parse_sentiment_response(response.text)

            logger.info(f"Extracted {len(insights.get('motivation_signals', []))} motivation signals from conversation")

            return insights

        except Exception as e:
            logger.error(f"Error analyzing conversation sentiment: {e}")
            return self._create_empty_insights()

    def _build_sentiment_analysis_prompt(self, user_profile: UserProfile, conversation_text: str) -> str:
        """Build prompt for sentiment analysis"""

        current_signals = [f"{s.signal_type}: {s.description}" for s in user_profile.motivation_signals[:5]]

        prompt = f"""You are an empathetic career coach analyzing a conversation to understand what truly drives this person.

Current known signals:
{chr(10).join(current_signals) if current_signals else 'None yet'}

Recent conversation:
{conversation_text}

Extract NEW insights about:
1. What they ENJOY doing (signal_type: "enjoy")
2. What they HATE or can't stand (signal_type: "hate")
3. What they FEAR losing (signal_type: "fear_losing")
4. What they ASPIRE to become (signal_type: "aspire_to")
5. Their preferences (work style, location, team type, etc.)
6. Their career goals (short-term, mid-term, long-term)
7. Risk signals (burnout, toxic environment, etc.)
8. Burnout level (0-10, where 0=energized, 10=critical)
9. Confidence level (0-10, where 0=none, 10=very confident)

Return ONLY a JSON object with this structure:
{{
  "motivation_signals": [
    {{
      "signal_type": "enjoy" | "hate" | "fear_losing" | "aspire_to",
      "description": "Brief description",
      "intensity": 1-10
    }}
  ],
  "preferences": [
    {{
      "category": "work_style" | "team_type" | "location" | "compensation" | "work_life_balance" | "career_values",
      "preference": "Description",
      "strength": 1-10,
      "is_dealbreaker": true | false
    }}
  ],
  "goals": [
    {{
      "timeframe": "short-term" | "mid-term" | "long-term",
      "description": "Goal description",
      "priority": 1-10
    }}
  ],
  "risk_signals": [
    {{
      "type": "burnout" | "toxic_environment" | "layoff_risk" | "market_decline" | "automation",
      "description": "Risk description",
      "severity": 1-10
    }}
  ],
  "burnout_level": 0-10,
  "confidence_level": 0-10
}}

Only extract what is CLEARLY stated or strongly implied. Don't invent. Output ONLY valid JSON."""

        return prompt

    def _parse_sentiment_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI sentiment analysis into structured data"""

        import json
        import re
        from datetime import datetime

        try:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group())

                # Convert to Pydantic models
                insights = {}

                # Motivation signals
                motivation_signals = []
                for signal_data in data.get("motivation_signals", []):
                    motivation_signals.append(
                        MotivationSignal(
                            signal_type=signal_data["signal_type"],
                            description=signal_data["description"],
                            intensity=signal_data.get("intensity", 5),
                            source="conversation",
                        )
                    )
                insights["motivation_signals"] = motivation_signals

                # Preferences
                preferences = []
                for pref_data in data.get("preferences", []):
                    # Map string to enum
                    category_map = {
                        "work_style": PreferenceCategory.WORK_STYLE,
                        "team_type": PreferenceCategory.TEAM_TYPE,
                        "location": PreferenceCategory.LOCATION,
                        "compensation": PreferenceCategory.COMPENSATION,
                        "work_life_balance": PreferenceCategory.WORK_LIFE_BALANCE,
                        "career_values": PreferenceCategory.CAREER_VALUES,
                    }
                    category = category_map.get(pref_data["category"], PreferenceCategory.WORK_STYLE)

                    preferences.append(
                        UserPreference(
                            category=category,
                            preference=pref_data["preference"],
                            strength=pref_data.get("strength", 5),
                            is_dealbreaker=pref_data.get("is_dealbreaker", False),
                        )
                    )
                insights["preferences"] = preferences

                # Goals
                goals = []
                for goal_data in data.get("goals", []):
                    goals.append(
                        CareerGoal(
                            timeframe=goal_data["timeframe"],
                            description=goal_data["description"],
                            priority=goal_data.get("priority", 5),
                        )
                    )
                insights["goals"] = goals

                # Risk signals
                risk_signals = []
                for risk_data in data.get("risk_signals", []):
                    risk_signals.append(
                        RiskFactor(
                            type=risk_data["type"],
                            description=risk_data["description"],
                            severity=risk_data.get("severity", 5),
                            detected_at=datetime.utcnow(),
                        )
                    )
                insights["risk_signals"] = risk_signals

                # Burnout and confidence
                insights["burnout_level"] = data.get("burnout_level")
                insights["confidence_level"] = data.get("confidence_level")

                return insights
            else:
                raise ValueError("No JSON found")

        except Exception as e:
            logger.error(f"Error parsing sentiment response: {e}")
            return self._create_empty_insights()

    def _create_empty_insights(self) -> Dict[str, Any]:
        """Return empty insights structure"""

        return {
            "motivation_signals": [],
            "preferences": [],
            "goals": [],
            "risk_signals": [],
            "burnout_level": None,
            "confidence_level": None,
        }

    async def detect_job_rejection_patterns(self, user_profile: UserProfile) -> List[str]:
        """
        Analyze rejection reasons to find patterns
        This helps refine future recommendations
        """

        if not user_profile.rejection_reasons:
            return []

        rejection_texts = list(user_profile.rejection_reasons.values())

        if len(rejection_texts) < 3:
            return []  # Not enough data

        try:
            prompt = f"""Analyze these job rejection reasons to find common patterns:

{chr(10).join(rejection_texts)}

What are the common themes? Return ONLY a JSON array of 2-4 pattern descriptions.

Example: ["User consistently rejects roles requiring extensive travel", "Dislikes high-pressure sales environments"]

Output ONLY valid JSON array."""

            response = self.model.generate_content(prompt)

            import json
            import re

            json_match = re.search(r"\[.*\]", response.text, re.DOTALL)

            if json_match:
                patterns = json.loads(json_match.group())
                return patterns

            return []

        except Exception as e:
            logger.error(f"Error detecting rejection patterns: {e}")
            return []
