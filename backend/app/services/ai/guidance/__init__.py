"""
Proactive Guidance System

Detects user needs and provides timely, intelligent assistance
without waiting to be asked.
"""

from .guidance_detector import GuidanceDetector
from .intervention_engine import InterventionEngine
from .proactive_coach import ProactiveCoach

# Singleton instance
proactive_coach = ProactiveCoach()

__all__ = [
    "GuidanceDetector",
    "InterventionEngine",
    "ProactiveCoach",
    "proactive_coach"
]
