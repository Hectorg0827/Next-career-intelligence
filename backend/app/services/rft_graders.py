"""
RFT Grader Functions

Deterministic scoring functions that evaluate AI-generated content quality.
These graders provide immediate feedback and generate training signals for RFT.

Graders are designed to be:
1. Deterministic (same input = same output)
2. Explainable (show why score was given)
3. Actionable (provide specific improvement suggestions)
"""

from typing import Dict, List
import re
from loguru import logger


class ResumeBulletGrader:
    """
    Scores resume bullets for quality and job match

    Checks for:
    - Action verbs (O*NET taxonomy)
    - Quantifiable metrics
    - Keyword match with job description
    - STAR structure
    - Appropriate length
    """

    # Strong action verbs from O*NET taxonomy
    STRONG_ACTION_VERBS = [
        "achieved",
        "improved",
        "reduced",
        "increased",
        "launched",
        "built",
        "designed",
        "led",
        "managed",
        "optimized",
        "delivered",
        "created",
        "implemented",
        "established",
        "spearheaded",
        "developed",
        "engineered",
        "architected",
        "streamlined",
        "automated",
        "scaled",
        "transformed",
        "drove",
        "executed",
        "directed",
        "initiated",
        "pioneered",
        "revolutionized",
        "facilitated",
        "coordinated",
    ]

    def score_bullet(self, bullet: str, job_description: str = None) -> Dict:
        """
        Score a resume bullet (0-100)

        Args:
            bullet: Resume bullet point text
            job_description: Optional job description for keyword matching

        Returns:
            {
                "overall_score": int (0-100),
                "breakdown": dict of component scores,
                "suggestions": list of improvement suggestions,
                "grade": str (A-F)
            }
        """
        scores = {}
        suggestions = []

        if not bullet or not bullet.strip():
            return {"overall_score": 0, "breakdown": {}, "suggestions": ["Bullet point is empty"], "grade": "F"}

        # 1. Action Verb Check (20 points)
        first_word = bullet.strip().split()[0].lower().rstrip(".,;:")
        if first_word in self.STRONG_ACTION_VERBS:
            scores["action_verb"] = 20
        else:
            scores["action_verb"] = 0
            suggestions.append(f"Start with a strong action verb (e.g., {', '.join(self.STRONG_ACTION_VERBS[:3])})")

        # 2. Quantifiable Metrics (30 points)
        has_numbers = bool(re.search(r"\d+", bullet))
        has_percentage = bool(re.search(r"\d+%", bullet))
        has_currency = bool(re.search(r"\$[\d,]+", bullet))

        metric_score = 0
        if has_numbers:
            metric_score += 10
        if has_percentage:
            metric_score += 10
        if has_currency:
            metric_score += 10

        scores["quantifiable"] = metric_score

        if metric_score < 20:
            suggestions.append("Add quantifiable metrics (numbers, %, or $ amounts) to show impact")

        # 3. Keyword Match (25 points) - if job description provided
        if job_description:
            jd_keywords = self._extract_keywords(job_description)
            bullet_keywords = set(bullet.lower().split())
            matches = bullet_keywords.intersection(jd_keywords)

            keyword_score = min(25, len(matches) * 5)
            scores["keyword_match"] = keyword_score

            if keyword_score < 15:
                missing_keywords = list(jd_keywords - bullet_keywords)[:3]
                if missing_keywords:
                    suggestions.append(f"Include key skills from job description: {', '.join(missing_keywords)}")
        else:
            scores["keyword_match"] = 0

        # 4. STAR Structure (15 points)
        # Check for Situation/Task, Action, Result components
        has_context = any(word in bullet.lower() for word in ["to", "by", "for", "across", "while"])
        has_action = first_word in self.STRONG_ACTION_VERBS
        has_result = has_numbers or "resulting in" in bullet.lower() or "led to" in bullet.lower()

        star_score = 0
        if has_context:
            star_score += 5
        if has_action:
            star_score += 5
        if has_result:
            star_score += 5

        scores["star_structure"] = star_score

        if star_score < 10:
            suggestions.append("Use STAR format: Situation → Action → Result")

        # 5. Length Check (10 points)
        word_count = len(bullet.split())
        if 10 <= word_count <= 25:
            scores["length"] = 10
        elif word_count < 10:
            scores["length"] = 5
            suggestions.append("Bullet is too short - add more detail about your impact")
        else:
            scores["length"] = 5
            suggestions.append("Bullet is too long - be more concise")

        overall_score = sum(scores.values())

        return {
            "overall_score": overall_score,
            "breakdown": scores,
            "suggestions": suggestions,
            "grade": self._score_to_grade(overall_score),
            "has_metrics": metric_score >= 20,
            "has_action_verb": scores["action_verb"] == 20,
        }

    def _extract_keywords(self, text: str) -> set:
        """Extract important keywords from text (simple version)"""
        # Remove common stopwords
        stopwords = {
            "the",
            "a",
            "an",
            "in",
            "to",
            "for",
            "of",
            "and",
            "or",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "with",
            "from",
            "at",
        }

        words = re.findall(r"\b\w+\b", text.lower())
        keywords = {w for w in words if w not in stopwords and len(w) > 3}

        return keywords

    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"


class InterviewAnswerGrader:
    """
    Scores interview answers for quality

    Focuses on:
    - STAR structure
    - Specificity and detail
    - Confidence markers
    - Filler word reduction
    - Relevance to question
    """

    # Confidence markers
    WEAK_PHRASES = ["i think", "maybe", "sort of", "kind of", "i guess", "probably", "possibly", "somewhat", "perhaps"]

    FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "actually", "literally", "honestly"]

    SITUATION_MARKERS = ["when i", "at my previous", "while working", "during my time", "in my role", "at", "when"]

    TASK_MARKERS = ["needed to", "responsible for", "tasked with", "challenged to", "had to", "was asked to"]

    ACTION_MARKERS = [
        "i decided",
        "i implemented",
        "i created",
        "i led",
        "i built",
        "i designed",
        "i developed",
        "i analyzed",
    ]

    RESULT_MARKERS = ["which resulted", "leading to", "achieved", "improved by", "reduced", "increased", "successfully"]

    def score_answer(self, question: str, answer: str) -> Dict:
        """
        Score an interview answer (0-100)

        Args:
            question: The interview question asked
            answer: User's answer

        Returns:
            {
                "overall_score": int (0-100),
                "breakdown": dict of component scores,
                "suggestions": list of improvements,
                "grade": str (A-F)
            }
        """
        scores = {}
        suggestions = []

        if not answer or not answer.strip():
            return {"overall_score": 0, "breakdown": {}, "suggestions": ["Answer is empty"], "grade": "F"}

        answer_lower = answer.lower()

        # 1. STAR Structure (40 points)
        has_situation = any(marker in answer_lower for marker in self.SITUATION_MARKERS)
        has_task = any(marker in answer_lower for marker in self.TASK_MARKERS)
        has_action = any(marker in answer_lower for marker in self.ACTION_MARKERS)
        has_result = any(marker in answer_lower for marker in self.RESULT_MARKERS)

        star_score = (has_situation * 10) + (has_task * 10) + (has_action * 10) + (has_result * 10)
        scores["star_structure"] = star_score

        if star_score < 30:
            missing = []
            if not has_situation:
                missing.append("Situation")
            if not has_task:
                missing.append("Task")
            if not has_action:
                missing.append("Action")
            if not has_result:
                missing.append("Result")

            suggestions.append(f"Add STAR components: {', '.join(missing)}")

        # 2. Specificity (30 points)
        has_numbers = bool(re.search(r"\d+", answer))
        has_specific_tools = bool(
            re.search(
                r"(python|java|react|aws|sql|docker|kubernetes|" r"typescript|javascript|node|fastapi|django)",
                answer_lower,
            )
        )
        word_count = len(answer.split())
        is_detailed = word_count >= 50

        specificity_score = 0
        if has_numbers:
            specificity_score += 10
        if has_specific_tools:
            specificity_score += 10
        if is_detailed:
            specificity_score += 10

        scores["specificity"] = specificity_score

        if not has_numbers:
            suggestions.append("Add specific metrics to quantify your impact")
        if not has_specific_tools:
            suggestions.append("Mention specific tools, technologies, or methodologies you used")
        if word_count < 50:
            suggestions.append("Provide more detail - aim for 50-100 words")

        # 3. Confidence (20 points)
        weak_count = sum(answer_lower.count(phrase) for phrase in self.WEAK_PHRASES)
        confidence_score = max(0, 20 - (weak_count * 5))
        scores["confidence"] = confidence_score

        if weak_count > 2:
            suggestions.append(f"Reduce hedging language (found {weak_count} instances) - be more confident!")

        # 4. Filler Word Penalty (10 points deduction)
        filler_count = sum(answer_lower.count(filler) for filler in self.FILLER_WORDS)
        filler_penalty = min(10, filler_count * 2)
        scores["filler_penalty"] = -filler_penalty

        if filler_count > 3:
            suggestions.append(f"Reduce filler words (found {filler_count})")

        # 5. Length Appropriateness (10 points)
        if 50 <= word_count <= 150:
            scores["length"] = 10
        elif 30 <= word_count < 50:
            scores["length"] = 7
            suggestions.append("Answer could be more detailed")
        elif 150 < word_count <= 200:
            scores["length"] = 7
            suggestions.append("Answer is a bit long - be more concise")
        else:
            scores["length"] = 5
            if word_count < 30:
                suggestions.append("Answer is too short")
            else:
                suggestions.append("Answer is too long - focus on key points")

        overall_score = max(0, sum(scores.values()))

        return {
            "overall_score": overall_score,
            "breakdown": scores,
            "suggestions": suggestions,
            "grade": self._score_to_grade(overall_score),
            "word_count": word_count,
            "has_star": star_score >= 30,
        }

    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"


# Global instances
resume_bullet_grader = ResumeBulletGrader()
interview_answer_grader = InterviewAnswerGrader()
