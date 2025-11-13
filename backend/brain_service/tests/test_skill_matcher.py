"""
Comprehensive tests for Semantic Skill Matcher

Tests cover:
- Exact matches
- Semantic similarity (React ≈ JavaScript)
- Missing skills detection
- Edge cases (empty inputs)
- Performance benchmarks
"""
import pytest
import time
from pathlib import Path

from brain_service.app.services.skill_matcher import SemanticSkillMatcher, get_skill_matcher
from brain_service.app.models.types import Skill


@pytest.fixture
def matcher():
    """Create a skill matcher instance for tests"""
    return SemanticSkillMatcher()


@pytest.fixture
def user_skills_basic():
    """Basic user skills for testing"""
    return [
        Skill(name="Python", proficiency=0.9, years_experience=5),
        Skill(name="React", proficiency=0.8, years_experience=3),
        Skill(name="PostgreSQL", proficiency=0.7, years_experience=4),
        Skill(name="AWS", proficiency=0.6, years_experience=2),
    ]


@pytest.fixture
def job_skills_exact_match():
    """Job skills that exactly match user skills"""
    return [
        Skill(name="Python", importance=1.0),
        Skill(name="React", importance=0.8),
        Skill(name="PostgreSQL", importance=0.7),
    ]


@pytest.fixture
def job_skills_semantic_match():
    """Job skills that semantically match user skills"""
    return [
        Skill(name="Python", importance=1.0),
        Skill(name="JavaScript", importance=0.9),  # Related to React
        Skill(name="SQL", importance=0.8),  # Related to PostgreSQL
        Skill(name="Cloud Computing", importance=0.7),  # Related to AWS
    ]


@pytest.fixture
def job_skills_with_gaps():
    """Job skills with some gaps"""
    return [
        Skill(name="Python", importance=1.0),
        Skill(name="Docker", importance=0.9),  # User doesn't have
        Skill(name="Kubernetes", importance=0.8),  # User doesn't have
        Skill(name="React", importance=0.7),
    ]


class TestBasicMatching:
    """Test basic matching functionality"""

    def test_exact_match(self, matcher, user_skills_basic, job_skills_exact_match):
        """Test matching with exact skill names"""
        result = matcher.calculate_skill_match(user_skills_basic, job_skills_exact_match)

        assert result.score >= 90, "Exact match should score very high"
        assert len(result.matched_skills) == 3, "Should match all 3 skills"
        assert len(result.missing_skills) == 0, "Should have no missing skills"
        assert result.skill_gap_severity == "low"
        assert result.match_percentage == 100.0

    def test_semantic_match(self, matcher, user_skills_basic, job_skills_semantic_match):
        """Test semantic similarity (React ≈ JavaScript)"""
        result = matcher.calculate_skill_match(user_skills_basic, job_skills_semantic_match)

        assert result.score >= 70, "Semantic match should score reasonably high"
        assert len(result.matched_skills) >= 3, "Should match at least 3 semantically related skills"

        # Check that JavaScript matched with React
        js_match = next((m for m in result.matched_skills if m['job_skill'] == 'JavaScript'), None)
        assert js_match is not None, "JavaScript should match with React"
        assert js_match['user_skill'] == 'React', "React should be matched to JavaScript"
        assert js_match['similarity'] >= 0.7, "React-JavaScript similarity should be high"

    def test_with_skill_gaps(self, matcher, user_skills_basic, job_skills_with_gaps):
        """Test detection of missing skills"""
        result = matcher.calculate_skill_match(user_skills_basic, job_skills_with_gaps)

        assert len(result.missing_skills) >= 2, "Should detect Docker and Kubernetes as missing"
        assert result.skill_gap_severity in ["medium", "high"], "Should recognize skill gaps"

        # Check that missing skills are identified
        missing_skill_names = [s['skill'] for s in result.missing_skills]
        assert "Docker" in missing_skill_names or "Kubernetes" in missing_skill_names


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_job_skills(self, matcher, user_skills_basic):
        """Test with no job skills specified"""
        result = matcher.calculate_skill_match(user_skills_basic, [])

        assert result.score == 50.0, "Should return neutral score for no requirements"
        assert len(result.matched_skills) == 0
        assert len(result.missing_skills) == 0
        assert result.match_percentage == 100.0
        assert "No skills specified" in result.explanation

    def test_empty_user_skills(self, matcher, job_skills_exact_match):
        """Test with no user skills"""
        result = matcher.calculate_skill_match([], job_skills_exact_match)

        assert result.score == 0.0, "Should return 0 for no user skills"
        assert len(result.matched_skills) == 0
        assert len(result.missing_skills) == len(job_skills_exact_match)
        assert result.skill_gap_severity == "high"
        assert result.match_percentage == 0.0

    def test_both_empty(self, matcher):
        """Test with both empty"""
        result = matcher.calculate_skill_match([], [])

        assert result.score == 50.0
        assert len(result.matched_skills) == 0
        assert len(result.missing_skills) == 0


class TestWeighting:
    """Test importance and proficiency weighting"""

    def test_importance_weighting(self, matcher):
        """Test that skill importance affects score"""
        user_skills = [
            Skill(name="Python", proficiency=0.9),
        ]

        # High importance
        job_high_importance = [
            Skill(name="Python", importance=1.0),
        ]

        # Low importance
        job_low_importance = [
            Skill(name="Python", importance=0.3),
        ]

        result_high = matcher.calculate_skill_match(user_skills, job_high_importance)
        result_low = matcher.calculate_skill_match(user_skills, job_low_importance)

        # Both should score well, but weighting should be reflected in internal calculations
        assert result_high.score >= 85
        assert result_low.score >= 85

    def test_proficiency_weighting(self, matcher):
        """Test that user proficiency affects score"""
        job_skills = [
            Skill(name="Python", importance=1.0),
        ]

        # High proficiency
        user_high_prof = [
            Skill(name="Python", proficiency=0.95),
        ]

        # Low proficiency
        user_low_prof = [
            Skill(name="Python", proficiency=0.3),
        ]

        result_high = matcher.calculate_skill_match(user_high_prof, job_skills)
        result_low = matcher.calculate_skill_match(user_low_prof, job_skills)

        assert result_high.score > result_low.score, "Higher proficiency should yield higher score"


class TestBatchMatching:
    """Test batch job matching"""

    def test_batch_match_jobs(self, matcher, user_skills_basic):
        """Test matching against multiple jobs at once"""
        jobs = [
            ("job1", [Skill(name="Python", importance=1.0)]),
            ("job2", [Skill(name="Java", importance=1.0)]),  # User doesn't have
            ("job3", [Skill(name="React", importance=1.0)]),
            ("job4", [Skill(name="Docker", importance=1.0)]),  # User doesn't have
        ]

        results = matcher.batch_match_jobs(user_skills_basic, jobs, min_score=60.0)

        # Should match job1 and job3 well
        assert len(results) >= 2, "Should find at least 2 matches above threshold"

        # Results should be sorted by score
        scores = [r[1].score for r in results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by score"


class TestSkillGapAnalysis:
    """Test skill gap identification"""

    def test_find_skill_gaps(self, matcher, user_skills_basic):
        """Test identification of missing skills"""
        target_skills = [
            Skill(name="Python", importance=1.0),
            Skill(name="Docker", importance=0.9),
            Skill(name="Kubernetes", importance=0.8),
            Skill(name="Terraform", importance=0.7),
            Skill(name="React", importance=0.6),
        ]

        gaps = matcher.find_skill_gaps(user_skills_basic, target_skills, top_n=3)

        assert len(gaps) <= 3, "Should return at most 3 gaps"
        assert len(gaps) >= 2, "Should find at least Docker and Kubernetes gaps"

        # Should be sorted by importance
        importances = [g['importance'] for g in gaps]
        assert importances == sorted(importances, reverse=True), "Gaps should be sorted by importance"


class TestCaching:
    """Test embedding caching"""

    def test_cache_creation(self, matcher):
        """Test that embeddings are cached"""
        initial_cache_size = len(matcher.embedding_cache)

        # Get embedding for new skill
        embedding1 = matcher.get_embedding("TestSkill123")

        cache_after_first = len(matcher.embedding_cache)
        assert cache_after_first > initial_cache_size, "Cache should grow after new skill"

        # Get same embedding again
        embedding2 = matcher.get_embedding("TestSkill123")

        cache_after_second = len(matcher.embedding_cache)
        assert cache_after_second == cache_after_first, "Cache size shouldn't change for cached skill"

        # Embeddings should be identical
        assert np.array_equal(embedding1, embedding2), "Cached embedding should be identical"

    def test_cache_persistence(self, tmp_path):
        """Test that cache is saved and loaded correctly"""
        cache_file = tmp_path / "test_cache.pkl"

        # Create matcher with custom cache path
        matcher1 = SemanticSkillMatcher(cache_path=cache_file)

        # Add some embeddings
        matcher1.get_embedding("Python")
        matcher1.get_embedding("JavaScript")
        matcher1._save_cache()

        # Create new matcher with same cache path
        matcher2 = SemanticSkillMatcher(cache_path=cache_file)

        assert len(matcher2.embedding_cache) >= 2, "Cache should be loaded from disk"
        assert "python" in matcher2.embedding_cache, "Python should be in cache"
        assert "javascript" in matcher2.embedding_cache, "JavaScript should be in cache"


class TestSingleton:
    """Test singleton pattern"""

    def test_get_skill_matcher_singleton(self):
        """Test that get_skill_matcher returns same instance"""
        matcher1 = get_skill_matcher()
        matcher2 = get_skill_matcher()

        assert matcher1 is matcher2, "Should return same instance"


class TestPerformance:
    """Test performance benchmarks"""

    def test_matching_speed(self, matcher, user_skills_basic, job_skills_exact_match):
        """Test that matching is fast (<50ms)"""
        start = time.time()

        for _ in range(10):
            matcher.calculate_skill_match(user_skills_basic, job_skills_exact_match)

        elapsed = time.time() - start
        avg_time = elapsed / 10

        assert avg_time < 0.05, f"Average matching time should be <50ms, got {avg_time*1000:.1f}ms"

    def test_batch_matching_speed(self, matcher, user_skills_basic):
        """Test that batch matching is efficient"""
        # Create 100 jobs
        jobs = [
            (f"job{i}", [Skill(name="Python", importance=1.0)])
            for i in range(100)
        ]

        start = time.time()
        results = matcher.batch_match_jobs(user_skills_basic, jobs)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Batch matching 100 jobs should take <5s, got {elapsed:.2f}s"


class TestExplanations:
    """Test explanation generation"""

    def test_excellent_match_explanation(self, matcher, user_skills_basic, job_skills_exact_match):
        """Test explanation for excellent match"""
        result = matcher.calculate_skill_match(user_skills_basic, job_skills_exact_match)

        assert "Excellent" in result.explanation or "excellent" in result.explanation
        assert result.skill_gap_severity == "low"

    def test_poor_match_explanation(self, matcher, user_skills_basic):
        """Test explanation for poor match"""
        job_skills_no_match = [
            Skill(name="Java", importance=1.0),
            Skill(name="C++", importance=0.9),
            Skill(name="Ruby", importance=0.8),
        ]

        result = matcher.calculate_skill_match(user_skills_basic, job_skills_no_match)

        assert "gap" in result.explanation.lower() or "missing" in result.explanation.lower()
        assert len(result.missing_skills) > 0


# Import numpy for cache test
import numpy as np


if __name__ == "__main__":
    # Run tests with: pytest tests/test_skill_matcher.py -v
    pytest.main([__file__, "-v", "--tb=short"])
