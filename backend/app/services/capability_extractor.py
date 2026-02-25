"""
Semantic Capability Extractor
Extracts structured capabilities from job descriptions using Gemini.

Extracts beyond simple keyword tags:
- Explicit skills (tools, frameworks, languages)
- Implicit capabilities (leadership, ownership, collaboration signals)
- Cultural signals (fast-paced, startup, structured)
- Growth trajectory signals (0-to-1, scale, build vs maintain)
- Risk signals (ambiguous, unclear, high churn)
"""

import json
import re
from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.config import settings


class CapabilityExtractor:
    """
    Extracts semantic capabilities from job description text using Gemini.
    Designed to run asynchronously during job ingestion.
    """

    def __init__(self):
        self._model = None

    def _get_model(self):
        """Lazy-initialize Gemini model (cheaper: use flash for extraction)."""
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                # Use flash model for cost-efficient extraction
                self._model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini for CapabilityExtractor: {e}")
        return self._model

    async def extract(self, description: str, title: str = "") -> Dict[str, Any]:
        """
        Extract structured capabilities from a job description.

        Returns:
        {
            "explicit_skills": ["Python", "Kubernetes", "PostgreSQL"],
            "implicit_capabilities": ["high ownership", "cross-functional leadership"],
            "cultural_signals": ["fast-paced", "startup environment"],
            "growth_signals": ["build from scratch", "define the roadmap"],
            "risk_signals": ["ambiguous requirements", "unclear career path"],
            "seniority_signals": ["senior", "lead", "staff"],
            "remote_signals": ["fully remote", "async-first"],
            "extracted_at": "ISO timestamp"
        }
        """
        if not description or len(description.strip()) < 50:
            return self._empty_result()

        model = self._get_model()
        if not model:
            return self._keyword_fallback(description)

        try:
            prompt = self._build_extraction_prompt(description, title)
            response = model.generate_content(prompt)
            result = self._parse_response(response.text)
            from datetime import datetime
            result["extracted_at"] = datetime.utcnow().isoformat()
            return result

        except Exception as e:
            logger.warning(f"Gemini capability extraction failed: {e} — using keyword fallback")
            return self._keyword_fallback(description)

    def _build_extraction_prompt(self, description: str, title: str) -> str:
        # Truncate description to keep token cost low
        truncated = description[:3000] if len(description) > 3000 else description

        return f"""Analyze this job posting and extract structured capability signals. Be precise — only extract what is genuinely present in the text.

Job Title: {title or 'Not specified'}

Job Description:
{truncated}

Return ONLY valid JSON with exactly these keys:

{{
  "explicit_skills": ["list of specific tools, languages, frameworks, platforms mentioned"],
  "implicit_capabilities": ["inferred capabilities like 'high ownership', 'stakeholder management', 'technical strategy'"],
  "cultural_signals": ["culture/environment descriptors like 'fast-paced', 'startup', 'enterprise', 'async-first'"],
  "growth_signals": ["growth opportunity signals like 'build from scratch', '0-to-1', 'define the roadmap', 'greenfield'"],
  "risk_signals": ["warning signals like 'ambiguous requirements', 'wear many hats', 'undefined process'"],
  "seniority_signals": ["seniority level signals like 'senior', 'lead', 'staff', 'principal', 'junior', 'entry-level'"],
  "remote_signals": ["work arrangement signals like 'fully remote', 'hybrid', 'on-site', 'async-first', 'timezone flexible'"]
}}

Rules:
- Return ONLY JSON, no explanation
- Use empty arrays [] if a category has no signals
- Limit each array to 10 items maximum
- Be specific, not generic (e.g. "React 18" not "frontend")"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini."""
        try:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return self._validate_structure(data)
        except Exception as e:
            logger.warning(f"Failed to parse capability extraction JSON: {e}")
        return self._empty_result()

    def _validate_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all expected keys are present with correct types."""
        keys = [
            "explicit_skills", "implicit_capabilities", "cultural_signals",
            "growth_signals", "risk_signals", "seniority_signals", "remote_signals",
        ]
        result = {}
        for key in keys:
            value = data.get(key, [])
            if isinstance(value, list):
                result[key] = [str(item) for item in value[:10]]
            else:
                result[key] = []
        return result

    def _keyword_fallback(self, description: str) -> Dict[str, Any]:
        """
        Simple keyword-based extraction when Gemini is unavailable.
        Less accurate than LLM extraction but better than nothing.
        """
        desc_lower = description.lower()

        # Explicit skills: common tech keywords
        tech_keywords = [
            "python", "javascript", "typescript", "react", "node", "java", "golang", "rust",
            "kubernetes", "docker", "aws", "gcp", "azure", "postgresql", "redis", "kafka",
            "tensorflow", "pytorch", "spark", "airflow", "dbt", "terraform", "graphql",
        ]
        explicit_skills = [k for k in tech_keywords if k in desc_lower]

        # Seniority signals
        seniority_map = {
            "senior": ["senior", "sr."],
            "lead": ["lead", "tech lead"],
            "staff": ["staff", "principal"],
            "junior": ["junior", "jr.", "entry-level", "entry level"],
        }
        seniority_signals = []
        for level, terms in seniority_map.items():
            if any(t in desc_lower for t in terms):
                seniority_signals.append(level)

        # Cultural signals
        cultural_keywords = {
            "fast-paced": ["fast-paced", "fast paced", "move fast"],
            "startup environment": ["startup", "early stage", "series a", "series b"],
            "collaborative": ["collaborative", "cross-functional"],
            "remote-first": ["remote-first", "remote first", "async"],
        }
        cultural_signals = [k for k, terms in cultural_keywords.items() if any(t in desc_lower for t in terms)]

        # Growth signals
        growth_terms = {
            "build from scratch": ["0 to 1", "0-to-1", "build from scratch", "greenfield"],
            "define the roadmap": ["define the roadmap", "shape the direction", "strategic ownership"],
        }
        growth_signals = [k for k, terms in growth_terms.items() if any(t in desc_lower for t in terms)]

        # Remote signals
        remote_signals = []
        if "fully remote" in desc_lower or "100% remote" in desc_lower:
            remote_signals.append("fully remote")
        elif "hybrid" in desc_lower:
            remote_signals.append("hybrid")
        elif "on-site" in desc_lower or "in-office" in desc_lower:
            remote_signals.append("on-site")

        from datetime import datetime
        return {
            "explicit_skills": explicit_skills[:10],
            "implicit_capabilities": [],
            "cultural_signals": cultural_signals,
            "growth_signals": growth_signals,
            "risk_signals": [],
            "seniority_signals": seniority_signals,
            "remote_signals": remote_signals,
            "extracted_at": datetime.utcnow().isoformat(),
        }

    def _empty_result(self) -> Dict[str, Any]:
        from datetime import datetime
        return {
            "explicit_skills": [],
            "implicit_capabilities": [],
            "cultural_signals": [],
            "growth_signals": [],
            "risk_signals": [],
            "seniority_signals": [],
            "remote_signals": [],
            "extracted_at": datetime.utcnow().isoformat(),
        }
