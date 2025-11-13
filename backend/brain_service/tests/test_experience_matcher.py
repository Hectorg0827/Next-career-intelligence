"""
Comprehensive tests for Experience Level Matcher

Tests cover:
- Years extraction (various patterns)
- Seniority classification
- Appropriate matches vs mismatches
- Edge cases
"""
import pytest

from brain_service.app.services.experience_matcher import (
    ExperienceMatcher,
    SeniorityLevel,
    get_experience_matcher
)


@pytest.fixture
def matcher():
    """Create an experience matcher instance for tests"""
    return ExperienceMatcher()


class TestYearsExtraction:
    """Test years of experience extraction from job descriptions"""

    def test_range_pattern(self, matcher):
        """Test '5-7 years' pattern"""
        desc = "We're looking for someone with 5-7 years of experience"
        title = "Software Engineer"

        min_years, max_years = matcher.extract_years_requirement(desc, title)

        assert min_years == 5
        assert max_years == 7

    def test_plus_pattern(self, matcher):
        """Test '5+ years' pattern"""
        desc = "Must have 5+ years experience in software development"
        title = "Engineer"

        min_years, max_years = matcher.extract_years_requirement(desc, title)

        assert min_years == 5
        assert max_years >= 5  # Should be flexible upper bound

    def test_minimum_pattern(self, matcher):
        """Test 'minimum 3 years' pattern"""
        desc = "Minimum 3 years of industry experience required"
        title = "Developer"

        min_years, max_years = matcher.extract_years_requirement(desc, title)

        assert min_years == 3
        assert max_years > min_years

    def test_exact_pattern(self, matcher):
        """Test '5 years of experience' pattern"""
        desc = "Looking for 5 years of experience in the field"
        title = "Engineer"

        min_years, max_years = matcher.extract_years_requirement(desc, title)

        assert 4 <= min_years <= 5
        assert 5 <= max_years <= 7

    def test_no_years_specified(self, matcher):
        """Test fallback to seniority inference when no years specified"""
        desc = "Great opportunity for experienced professionals"
        title = "Senior Software Engineer"

        min_years, max_years = matcher.extract_years_requirement(desc, title)

        # Should infer from 'Senior' in title
        assert min_years >= 5
        assert max_years >= 10


class TestSeniorityExtraction:
    """Test seniority level extraction from job titles"""

    def test_intern_titles(self, matcher):
        """Test intern detection"""
        titles = [
            "Software Engineer Intern",
            "Internship - Data Science",
            "Summer Intern"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.INTERN, f"Failed for: {title}"

    def test_junior_titles(self, matcher):
        """Test junior level detection"""
        titles = [
            "Junior Software Engineer",
            "Jr. Developer",
            "Entry-Level Analyst",
            "Associate Engineer"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.JUNIOR, f"Failed for: {title}"

    def test_mid_titles(self, matcher):
        """Test mid-level detection"""
        titles = [
            "Software Engineer",
            "Mid-Level Developer",
            "Intermediate Analyst"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level in [SeniorityLevel.MID], f"Failed for: {title}"

    def test_senior_titles(self, matcher):
        """Test senior level detection"""
        titles = [
            "Senior Software Engineer",
            "Sr. Developer",
            "Senior Analyst"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.SENIOR, f"Failed for: {title}"

    def test_lead_titles(self, matcher):
        """Test lead level detection"""
        titles = [
            "Lead Engineer",
            "Tech Lead",
            "Team Lead - Engineering"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.LEAD, f"Failed for: {title}"

    def test_staff_titles(self, matcher):
        """Test staff level detection"""
        titles = [
            "Staff Engineer",
            "Staff Software Engineer"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.STAFF, f"Failed for: {title}"

    def test_principal_titles(self, matcher):
        """Test principal level detection"""
        titles = [
            "Principal Engineer",
            "Principal Software Engineer"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.PRINCIPAL, f"Failed for: {title}"

    def test_director_titles(self, matcher):
        """Test director level detection"""
        titles = [
            "Director of Engineering",
            "Engineering Director",
            "Head of Product"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.DIRECTOR, f"Failed for: {title}"

    def test_vp_titles(self, matcher):
        """Test VP level detection"""
        titles = [
            "VP of Engineering",
            "Vice President - Product",
            "VP, Technology"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.VP, f"Failed for: {title}"

    def test_executive_titles(self, matcher):
        """Test executive level detection"""
        titles = [
            "Chief Technology Officer",
            "CTO",
            "Chief Executive Officer",
            "CEO"
        ]

        for title in titles:
            level = matcher.extract_seniority_from_title(title)
            assert level == SeniorityLevel.EXECUTIVE, f"Failed for: {title}"


class TestExperienceMatching:
    """Test complete experience matching"""

    def test_perfect_match(self, matcher):
        """Test perfect experience match"""
        result = matcher.calculate_experience_match(
            user_years=6,
            user_title="Senior Software Engineer",
            job_description="Looking for 5-7 years of experience",
            job_title="Senior Software Engineer"
        )

        assert result.score >= 90, "Perfect match should score very high"
        assert result.is_appropriate is True
        assert len(result.concerns) == 0
        assert "Perfect" in result.explanation or "perfect" in result.explanation

    def test_promotion_match(self, matcher):
        """Test match for promotion (one level up)"""
        result = matcher.calculate_experience_match(
            user_years=5,
            user_title="Software Engineer",
            job_description="5+ years required",
            job_title="Senior Software Engineer"
        )

        assert result.score >= 85, "Promotion match should score well"
        assert result.is_appropriate is True
        assert "promotion" in result.explanation.lower() or "next step" in result.explanation.lower()

    def test_underqualified(self, matcher):
        """Test underqualified scenario"""
        result = matcher.calculate_experience_match(
            user_years=2,
            user_title="Junior Engineer",
            job_description="Requires 5-7 years",
            job_title="Senior Engineer"
        )

        assert result.score < 70, "Underqualified should score lower"
        assert "Underqualified" in result.concerns[0] if result.concerns else True
        assert result.is_appropriate is False

    def test_overqualified(self, matcher):
        """Test overqualified scenario"""
        result = matcher.calculate_experience_match(
            user_years=15,
            user_title="Principal Engineer",
            job_description="2-4 years required",
            job_title="Software Engineer"
        )

        assert result.score < 90, "Overqualified should have some penalty"
        assert any("overqualified" in c.lower() for c in result.concerns)

    def test_lateral_move(self, matcher):
        """Test lateral move (same level)"""
        result = matcher.calculate_experience_match(
            user_years=6,
            user_title="Senior Engineer at CompanyA",
            job_description="5-7 years",
            job_title="Senior Engineer"
        )

        assert result.score >= 85
        assert "Lateral" in result.explanation or "lateral" in result.explanation

    def test_step_backward(self, matcher):
        """Test step backward in seniority"""
        result = matcher.calculate_experience_match(
            user_years=10,
            user_title="Senior Engineer",
            job_description="2-4 years",
            job_title="Junior Engineer"
        )

        assert result.score < 80
        assert any("step down" in c.lower() or "backward" in c.lower() for c in result.concerns)


class TestScoreComponents:
    """Test individual scoring components"""

    def test_years_score_in_range(self, matcher):
        """Test years score when in range"""
        result = matcher.calculate_experience_match(
            user_years=6,
            user_title="Engineer",
            job_description="5-7 years",
            job_title="Engineer"
        )

        assert result.years_score == 100.0

    def test_years_score_below_range(self, matcher):
        """Test years score when below minimum"""
        result = matcher.calculate_experience_match(
            user_years=2,
            user_title="Engineer",
            job_description="5-7 years",
            job_title="Engineer"
        )

        # Should lose points (20 per year short)
        assert result.years_score < 100.0
        assert result.years_score >= 0.0

    def test_years_score_above_range(self, matcher):
        """Test years score when above maximum"""
        result = matcher.calculate_experience_match(
            user_years=10,
            user_title="Engineer",
            job_description="5-7 years",
            job_title="Engineer"
        )

        # Should lose some points but not as much as underqualified
        assert 50.0 <= result.years_score < 100.0

    def test_seniority_exact_match(self, matcher):
        """Test seniority score with exact match"""
        result = matcher.calculate_experience_match(
            user_years=6,
            user_title="Senior Engineer",
            job_description="Looking for Senior level",
            job_title="Senior Engineer"
        )

        assert result.seniority_score == 100.0

    def test_seniority_one_level_diff(self, matcher):
        """Test seniority score with one level difference"""
        result = matcher.calculate_experience_match(
            user_years=5,
            user_title="Software Engineer",
            job_description="Looking for senior level",
            job_title="Senior Software Engineer"
        )

        assert 80.0 <= result.seniority_score < 100.0

    def test_trajectory_promotion(self, matcher):
        """Test trajectory score for promotion"""
        result = matcher.calculate_experience_match(
            user_years=5,
            user_title="Software Engineer",
            job_description="Senior role",
            job_title="Senior Software Engineer"
        )

        assert result.trajectory_score >= 90.0


class TestEdgeCases:
    """Test edge cases"""

    def test_zero_years_experience(self, matcher):
        """Test with 0 years experience"""
        result = matcher.calculate_experience_match(
            user_years=0,
            user_title="Entry-Level Engineer",
            job_description="0-2 years",
            job_title="Junior Engineer"
        )

        assert result.score >= 70  # Should be appropriate for entry-level

    def test_very_high_experience(self, matcher):
        """Test with 30+ years experience"""
        result = matcher.calculate_experience_match(
            user_years=30,
            user_title="CTO",
            job_description="15+ years",
            job_title="VP of Engineering"
        )

        assert result.score >= 60  # Should be reasonable

    def test_empty_job_description(self, matcher):
        """Test with minimal job description"""
        result = matcher.calculate_experience_match(
            user_years=5,
            user_title="Software Engineer",
            job_description="",  # No years specified
            job_title="Senior Software Engineer"
        )

        # Should infer from title
        assert result.score > 0
        assert isinstance(result.explanation, str)


class TestSingleton:
    """Test singleton pattern"""

    def test_get_experience_matcher_singleton(self):
        """Test that get_experience_matcher returns same instance"""
        matcher1 = get_experience_matcher()
        matcher2 = get_experience_matcher()

        assert matcher1 is matcher2


class TestConcerns:
    """Test concern generation"""

    def test_no_concerns_for_good_match(self, matcher):
        """Test that good matches have no concerns"""
        result = matcher.calculate_experience_match(
            user_years=6,
            user_title="Senior Engineer",
            job_description="5-7 years",
            job_title="Senior Engineer"
        )

        assert len(result.concerns) == 0

    def test_concerns_for_underqualified(self, matcher):
        """Test that underqualified generates concerns"""
        result = matcher.calculate_experience_match(
            user_years=2,
            user_title="Junior Engineer",
            job_description="5-7 years",
            job_title="Senior Engineer"
        )

        assert len(result.concerns) > 0
        assert any("underqualified" in c.lower() for c in result.concerns)

    def test_concerns_for_big_jump(self, matcher):
        """Test that big seniority jump generates concerns"""
        result = matcher.calculate_experience_match(
            user_years=3,
            user_title="Junior Engineer",
            job_description="10+ years",
            job_title="Director of Engineering"
        )

        assert len(result.concerns) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
