"""
Job Data Quality Pipeline
Validates, enriches, and normalizes job posting data
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator, ValidationError
from loguru import logger
import re
from enum import Enum
import difflib


class DataQualityStatus(str, Enum):
    """Data quality status levels"""
    EXCELLENT = "excellent"  # 90%+ complete, all critical fields
    GOOD = "good"            # 70-89% complete
    FAIR = "fair"            # 50-69% complete
    POOR = "poor"            # < 50% complete
    REJECTED = "rejected"    # Critical validation failures


class JobDataValidator(BaseModel):
    """
    Comprehensive job data validation model
    Ensures all job postings meet quality standards
    """

    # Required fields
    title: str = Field(..., min_length=3, max_length=200)
    company: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=100, max_length=10000)

    # Location fields
    location: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    remote_type: Optional[str] = Field(None, regex="^(remote|hybrid|on_site|Remote|Hybrid|On-site)$")

    # Salary fields
    salary_min: Optional[int] = Field(None, ge=0, le=1000000)
    salary_max: Optional[int] = Field(None, ge=0, le=1000000)
    salary_currency: str = Field(default="USD", regex="^[A-Z]{3}$")
    salary_period: Optional[str] = Field(None, regex="^(hourly|monthly|yearly)$")

    # Job details
    required_skills: List[str] = Field(default_factory=list, max_items=50)
    nice_to_have_skills: Optional[List[str]] = Field(default_factory=list, max_items=30)
    responsibilities: Optional[List[str]] = Field(default_factory=list, max_items=20)
    requirements: Optional[List[str]] = Field(default_factory=list, max_items=20)
    benefits: Optional[List[str]] = Field(default_factory=list, max_items=20)

    experience_level: Optional[str] = Field(None, regex="^(entry|mid|senior|lead|executive)$")
    years_experience_min: Optional[int] = Field(None, ge=0, le=50)
    years_experience_max: Optional[int] = Field(None, ge=0, le=50)

    job_type: Optional[str] = Field(None, regex="^(full_time|part_time|contract|temporary|internship)$")

    # Metadata
    source: str = Field(..., max_length=100)
    external_id: Optional[str] = Field(None, max_length=200)
    job_url: Optional[str] = Field(None, max_length=1000)
    company_logo_url: Optional[str] = Field(None, max_length=1000)
    application_url: Optional[str] = Field(None, max_length=1000)

    posted_date: Optional[datetime] = None
    expires_date: Optional[datetime] = None

    is_active: bool = True

    @validator('title')
    def validate_title(cls, v):
        """Validate job title quality"""
        # Remove excessive whitespace
        v = re.sub(r'\s+', ' ', v.strip())

        # Check for spam patterns
        spam_patterns = [
            r'\$\$\$',
            r'WORK FROM HOME!!!',
            r'CLICK HERE',
            r'\b(viagra|cialis|casino)\b',
        ]
        for pattern in spam_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Job title contains spam pattern: {pattern}")

        # Check for all caps (likely spam)
        if v.isupper() and len(v) > 10:
            raise ValueError("Job title is all caps (potential spam)")

        return v

    @validator('description')
    def validate_description(cls, v):
        """Validate description quality"""
        # Check minimum word count
        word_count = len(v.split())
        if word_count < 20:
            raise ValueError(f"Description too short ({word_count} words, minimum 20)")

        # Check for excessive special characters (spam indicator)
        special_char_ratio = len(re.findall(r'[^\w\s]', v)) / len(v)
        if special_char_ratio > 0.3:
            raise ValueError("Description has excessive special characters")

        # Check for minimum unique words (not just repeated keywords)
        unique_words = len(set(v.lower().split()))
        if unique_words < 15:
            raise ValueError("Description lacks diversity (keyword stuffing)")

        return v

    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        """Ensure salary_max >= salary_min"""
        if v and 'salary_min' in values and values['salary_min']:
            if v < values['salary_min']:
                raise ValueError(f"salary_max ({v}) must be >= salary_min ({values['salary_min']})")
        return v

    @validator('years_experience_max')
    def validate_experience_range(cls, v, values):
        """Ensure years_experience_max >= years_experience_min"""
        if v and 'years_experience_min' in values and values['years_experience_min']:
            if v < values['years_experience_min']:
                raise ValueError(f"years_experience_max ({v}) must be >= years_experience_min ({values['years_experience_min']})")
        return v

    @validator('required_skills')
    def validate_skills(cls, v):
        """Validate skills list quality"""
        if not v or len(v) == 0:
            logger.warning("No required skills provided")
            return v

        # Remove duplicates (case-insensitive)
        seen = set()
        unique_skills = []
        for skill in v:
            skill_lower = skill.lower().strip()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill.strip())

        # Check for generic/vague skills
        generic_skills = ['good communication', 'team player', 'hard working', 'motivated']
        for skill in unique_skills:
            if skill.lower() in generic_skills:
                logger.warning(f"Generic skill detected: {skill}")

        return unique_skills

    @validator('expires_date')
    def validate_expiration(cls, v, values):
        """Ensure expiration date is in the future"""
        if v:
            posted = values.get('posted_date', datetime.utcnow())
            if v < posted:
                raise ValueError("Expiration date must be after posting date")

            # Warn if expiration is more than 6 months out
            if v > posted + timedelta(days=180):
                logger.warning(f"Unusually long expiration period: {(v - posted).days} days")

        return v


class JobDataQualityPipeline:
    """
    Job data quality pipeline
    Validates, enriches, normalizes, and scores job data
    """

    # Standard skill taxonomy (normalized names)
    SKILL_TAXONOMY = {
        # Programming Languages
        'python': ['python', 'python3', 'py'],
        'javascript': ['javascript', 'js', 'ecmascript'],
        'typescript': ['typescript', 'ts'],
        'java': ['java', 'java8', 'java11'],
        'c++': ['c++', 'cpp', 'cplusplus'],
        'c#': ['c#', 'csharp', 'c sharp'],
        'go': ['go', 'golang'],
        'rust': ['rust'],
        'ruby': ['ruby', 'ruby on rails'],
        'php': ['php', 'php7', 'php8'],
        'swift': ['swift', 'swift 5'],
        'kotlin': ['kotlin'],
        'scala': ['scala'],

        # Frameworks & Libraries
        'react': ['react', 'reactjs', 'react.js'],
        'angular': ['angular', 'angularjs', 'angular.js'],
        'vue': ['vue', 'vuejs', 'vue.js'],
        'django': ['django'],
        'flask': ['flask'],
        'fastapi': ['fastapi', 'fast api'],
        'express': ['express', 'expressjs', 'express.js'],
        'spring': ['spring', 'spring boot', 'springboot'],
        'node.js': ['node', 'nodejs', 'node.js'],

        # Databases
        'postgresql': ['postgresql', 'postgres', 'psql'],
        'mysql': ['mysql'],
        'mongodb': ['mongodb', 'mongo'],
        'redis': ['redis'],
        'elasticsearch': ['elasticsearch', 'elastic search'],
        'cassandra': ['cassandra'],

        # Cloud & DevOps
        'aws': ['aws', 'amazon web services'],
        'azure': ['azure', 'microsoft azure'],
        'gcp': ['gcp', 'google cloud platform', 'google cloud'],
        'docker': ['docker'],
        'kubernetes': ['kubernetes', 'k8s'],
        'terraform': ['terraform'],
        'jenkins': ['jenkins'],
        'github actions': ['github actions', 'gh actions'],

        # Data & ML
        'tensorflow': ['tensorflow', 'tf'],
        'pytorch': ['pytorch', 'torch'],
        'scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
        'pandas': ['pandas'],
        'numpy': ['numpy'],
        'spark': ['spark', 'apache spark'],

        # Soft Skills
        'leadership': ['leadership', 'team leadership'],
        'communication': ['communication', 'verbal communication', 'written communication'],
        'problem solving': ['problem solving', 'problem-solving'],
        'collaboration': ['collaboration', 'teamwork', 'team work'],
    }

    # Location normalization
    US_STATES = {
        'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA',
        'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA',
        'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
        'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
        'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
        'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH',
        'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC',
        'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA',
        'rhode island': 'RI', 'south carolina': 'SC', 'south dakota': 'SD', 'tennessee': 'TN',
        'texas': 'TX', 'utah': 'UT', 'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA',
        'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY'
    }

    def __init__(self):
        self.validation_stats = {
            'total_processed': 0,
            'passed': 0,
            'failed': 0,
            'enriched': 0
        }

    # ==================== VALIDATION ====================

    def validate_job(self, job_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Validate job data against quality standards

        Args:
            job_data: Raw job data dictionary

        Returns:
            Tuple of (is_valid, validated_data, errors)
        """
        errors = []

        try:
            # Validate using Pydantic model
            validated = JobDataValidator(**job_data)

            self.validation_stats['total_processed'] += 1
            self.validation_stats['passed'] += 1

            return True, validated.dict(), []

        except ValidationError as e:
            self.validation_stats['total_processed'] += 1
            self.validation_stats['failed'] += 1

            for error in e.errors():
                field = '.'.join(str(x) for x in error['loc'])
                message = error['msg']
                errors.append(f"{field}: {message}")

            logger.warning(f"Job validation failed: {errors}")
            return False, None, errors

    # ==================== ENRICHMENT ====================

    def enrich_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich job data with additional information

        - Normalize skills
        - Extract location details
        - Infer missing fields
        - Add quality scores

        Args:
            job_data: Validated job data

        Returns:
            Enriched job data
        """
        enriched = job_data.copy()

        # Normalize skills
        if 'required_skills' in enriched and enriched['required_skills']:
            enriched['required_skills'] = self._normalize_skills(enriched['required_skills'])

        if 'nice_to_have_skills' in enriched and enriched['nice_to_have_skills']:
            enriched['nice_to_have_skills'] = self._normalize_skills(enriched['nice_to_have_skills'])

        # Parse and normalize location
        if 'location' in enriched and enriched['location']:
            location_details = self._parse_location(enriched['location'])
            enriched.update(location_details)

        # Infer experience level from title
        if not enriched.get('experience_level'):
            enriched['experience_level'] = self._infer_experience_level(enriched['title'])

        # Extract salary from description if missing
        if not enriched.get('salary_min') and 'description' in enriched:
            salary_range = self._extract_salary_from_text(enriched['description'])
            if salary_range:
                enriched['salary_min'] = salary_range[0]
                enriched['salary_max'] = salary_range[1]

        # Infer remote type
        if not enriched.get('remote_type'):
            enriched['remote_type'] = self._infer_remote_type(
                enriched.get('title', '') + ' ' + enriched.get('description', '')
            )

        # Calculate quality score
        enriched['quality_score'] = self._calculate_quality_score(enriched)
        enriched['quality_status'] = self._get_quality_status(enriched['quality_score'])

        # Add enrichment timestamp
        enriched['enriched_at'] = datetime.utcnow().isoformat()

        self.validation_stats['enriched'] += 1

        return enriched

    # ==================== NORMALIZATION ====================

    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize skills to standard taxonomy

        Args:
            skills: List of raw skill names

        Returns:
            List of normalized skill names
        """
        normalized = []

        for skill in skills:
            skill_lower = skill.lower().strip()

            # Find best match in taxonomy
            matched = False
            for standard_name, variants in self.SKILL_TAXONOMY.items():
                if skill_lower in variants or skill_lower == standard_name:
                    normalized.append(standard_name)
                    matched = True
                    break

            # If no match, use fuzzy matching
            if not matched:
                best_match = self._fuzzy_match_skill(skill_lower)
                if best_match:
                    normalized.append(best_match)
                    logger.info(f"Fuzzy matched '{skill}' to '{best_match}'")
                else:
                    # Keep original if no match found
                    normalized.append(skill.strip())

        # Remove duplicates while preserving order
        seen = set()
        unique_normalized = []
        for skill in normalized:
            if skill not in seen:
                seen.add(skill)
                unique_normalized.append(skill)

        return unique_normalized

    def _fuzzy_match_skill(self, skill: str) -> Optional[str]:
        """
        Fuzzy match skill to taxonomy using string similarity

        Args:
            skill: Skill name to match

        Returns:
            Best matching standard skill name or None
        """
        best_match = None
        best_ratio = 0.0

        for standard_name, variants in self.SKILL_TAXONOMY.items():
            # Check against standard name
            ratio = difflib.SequenceMatcher(None, skill, standard_name).ratio()
            if ratio > best_ratio and ratio >= 0.8:  # 80% similarity threshold
                best_ratio = ratio
                best_match = standard_name

            # Check against variants
            for variant in variants:
                ratio = difflib.SequenceMatcher(None, skill, variant).ratio()
                if ratio > best_ratio and ratio >= 0.8:
                    best_ratio = ratio
                    best_match = standard_name

        return best_match

    def _parse_location(self, location: str) -> Dict[str, Optional[str]]:
        """
        Parse location string into city, state, country

        Args:
            location: Location string (e.g., "San Francisco, CA, USA")

        Returns:
            Dict with city, state, country
        """
        result = {
            'city': None,
            'state': None,
            'country': None
        }

        # Check for "Remote"
        if re.search(r'\bremote\b', location, re.IGNORECASE):
            result['city'] = 'Remote'
            return result

        # Split by comma
        parts = [p.strip() for p in location.split(',')]

        if len(parts) == 1:
            # Just city or state
            result['city'] = parts[0]
        elif len(parts) == 2:
            # City, State or City, Country
            result['city'] = parts[0]

            # Check if second part is US state
            state_normalized = self.US_STATES.get(parts[1].lower())
            if state_normalized or len(parts[1]) == 2:
                result['state'] = state_normalized or parts[1].upper()
                result['country'] = 'USA'
            else:
                result['country'] = parts[1]
        elif len(parts) >= 3:
            # City, State, Country
            result['city'] = parts[0]
            result['state'] = parts[1]
            result['country'] = parts[2]

        return result

    def _infer_experience_level(self, title: str) -> str:
        """
        Infer experience level from job title

        Args:
            title: Job title

        Returns:
            Experience level: entry, mid, senior, lead, executive
        """
        title_lower = title.lower()

        if any(word in title_lower for word in ['intern', 'junior', 'entry', 'associate', 'jr']):
            return 'entry'
        elif any(word in title_lower for word in ['senior', 'sr', 'principal', 'staff']):
            return 'senior'
        elif any(word in title_lower for word in ['lead', 'manager', 'head']):
            return 'lead'
        elif any(word in title_lower for word in ['director', 'vp', 'chief', 'cto', 'ceo']):
            return 'executive'
        else:
            return 'mid'

    def _extract_salary_from_text(self, text: str) -> Optional[Tuple[int, int]]:
        """
        Extract salary range from text

        Args:
            text: Text containing salary information

        Returns:
            Tuple of (min_salary, max_salary) or None
        """
        # Pattern: $100,000 - $150,000 or $100k - $150k
        pattern1 = r'\$\s?([\d,]+)k?\s*-\s*\$?\s?([\d,]+)k?'
        match = re.search(pattern1, text, re.IGNORECASE)

        if match:
            min_sal = int(re.sub(r'[,$]', '', match.group(1)))
            max_sal = int(re.sub(r'[,$]', '', match.group(2)))

            # Handle 'k' notation
            if 'k' in match.group(0).lower():
                if min_sal < 1000:
                    min_sal *= 1000
                if max_sal < 1000:
                    max_sal *= 1000

            return (min_sal, max_sal)

        return None

    def _infer_remote_type(self, text: str) -> str:
        """
        Infer remote work type from text

        Args:
            text: Text to analyze

        Returns:
            Remote type: remote, hybrid, on_site
        """
        text_lower = text.lower()

        if any(word in text_lower for word in ['fully remote', '100% remote', 'remote-first', 'work from home', 'wfh']):
            return 'remote'
        elif any(word in text_lower for word in ['hybrid', 'flexible', '2 days on-site', '3 days remote']):
            return 'hybrid'
        else:
            return 'on_site'

    # ==================== QUALITY SCORING ====================

    def _calculate_quality_score(self, job_data: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0-100)

        Scoring criteria:
        - Field completeness (40%)
        - Data richness (30%)
        - Data accuracy (30%)

        Args:
            job_data: Job data to score

        Returns:
            Quality score 0-100
        """
        score = 0.0

        # Field completeness (40 points)
        critical_fields = ['title', 'company', 'description', 'location', 'required_skills']
        optional_fields = ['salary_min', 'salary_max', 'experience_level', 'job_type', 'remote_type', 'responsibilities', 'requirements']

        completeness = sum(1 for field in critical_fields if job_data.get(field)) / len(critical_fields)
        score += completeness * 25  # Critical fields: 25 points

        completeness_optional = sum(1 for field in optional_fields if job_data.get(field)) / len(optional_fields)
        score += completeness_optional * 15  # Optional fields: 15 points

        # Data richness (30 points)
        # Description word count
        if 'description' in job_data:
            word_count = len(job_data['description'].split())
            score += min(word_count / 100 * 10, 10)  # Up to 10 points for description

        # Skills count
        skills_count = len(job_data.get('required_skills', []))
        score += min(skills_count / 10 * 10, 10)  # Up to 10 points for skills

        # Responsibilities/requirements count
        resp_count = len(job_data.get('responsibilities', []))
        req_count = len(job_data.get('requirements', []))
        score += min((resp_count + req_count) / 10 * 10, 10)  # Up to 10 points

        # Data accuracy (30 points)
        # Salary range validity
        if job_data.get('salary_min') and job_data.get('salary_max'):
            if job_data['salary_max'] >= job_data['salary_min']:
                score += 10

        # Location validity
        if job_data.get('city') and job_data.get('country'):
            score += 10

        # Normalized skills (indicates quality enrichment)
        if job_data.get('required_skills'):
            normalized_count = sum(1 for skill in job_data['required_skills'] if skill in self.SKILL_TAXONOMY)
            normalization_ratio = normalized_count / len(job_data['required_skills'])
            score += normalization_ratio * 10  # Up to 10 points

        return round(min(score, 100), 2)

    def _get_quality_status(self, score: float) -> str:
        """Get quality status from score"""
        if score >= 90:
            return DataQualityStatus.EXCELLENT
        elif score >= 70:
            return DataQualityStatus.GOOD
        elif score >= 50:
            return DataQualityStatus.FAIR
        else:
            return DataQualityStatus.POOR

    # ==================== DEDUPLICATION ====================

    def find_duplicates(self, job_data: Dict[str, Any], existing_jobs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find duplicate job postings

        Duplicate criteria:
        - Same company + title (90% similarity)
        - Same external_id
        - Same job_url

        Args:
            job_data: New job to check
            existing_jobs: List of existing jobs

        Returns:
            Duplicate job dict or None
        """
        # Check external_id
        if job_data.get('external_id'):
            for existing in existing_jobs:
                if existing.get('external_id') == job_data['external_id']:
                    return existing

        # Check job_url
        if job_data.get('job_url'):
            for existing in existing_jobs:
                if existing.get('job_url') == job_data['job_url']:
                    return existing

        # Check company + title similarity
        for existing in existing_jobs:
            if existing.get('company') == job_data.get('company'):
                title_similarity = difflib.SequenceMatcher(
                    None,
                    job_data.get('title', '').lower(),
                    existing.get('title', '').lower()
                ).ratio()

                if title_similarity >= 0.9:
                    logger.info(f"Found duplicate: {job_data['title']} at {job_data['company']} (similarity: {title_similarity:.2f})")
                    return existing

        return None

    # ==================== STATISTICS ====================

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation pipeline statistics"""
        return {
            **self.validation_stats,
            'success_rate': self.validation_stats['passed'] / self.validation_stats['total_processed'] * 100 if self.validation_stats['total_processed'] > 0 else 0,
            'enrichment_rate': self.validation_stats['enriched'] / self.validation_stats['passed'] * 100 if self.validation_stats['passed'] > 0 else 0
        }


# Create singleton instance
job_quality_pipeline = JobDataQualityPipeline()
