"""
Safety & Privacy Module
Comprehensive guardrails for AI agents and privacy compliance
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from loguru import logger
from enum import Enum


class PrivacyRegion(str, Enum):
    """Supported privacy regions with different compliance requirements"""

    US = "US"
    EU = "EU"  # GDPR
    UK = "UK"  # UK GDPR
    CALIFORNIA = "CA"  # CCPA
    SINGAPORE = "SG"  # PDPA
    JAPAN = "JP"  # APPI
    CHINA = "CN"  # PIPL
    CANADA = "CA"  # PIPEDA
    AUSTRALIA = "AU"  # Privacy Act
    BRAZIL = "BR"  # LGPD


class AIAgentScope(str, Enum):
    """Defined scopes for specialized AI agents"""

    RESUME_STUDIO = "resume_studio"
    CAREER_COACH = "career_coach"
    INTERVIEWER = "interviewer"
    SKILL_ANALYZER = "skill_analyzer"


class SafetyGuardrails:
    """
    Enforce AI agent scope boundaries and content safety.
    Prevents misuse and ensures agents stay within defined responsibilities.
    """

    # ===== SCOPE ENFORCEMENT =====

    AGENT_SCOPES = {
        AIAgentScope.RESUME_STUDIO: {
            "allowed": [
                "resume parsing",
                "cv analysis",
                "work history",
                "skills extraction",
                "job descriptions",
                "cover letters",
                "ats optimization",
                "career documents",
            ],
            "forbidden": [
                "general knowledge",
                "creative writing",
                "code generation",
                "personal advice",
                "medical advice",
                "legal advice",
                "financial advice",
            ],
        },
        AIAgentScope.CAREER_COACH: {
            "allowed": [
                "career guidance",
                "skill development",
                "goal setting",
                "career paths",
                "professional development",
                "job search strategy",
                "networking advice",
            ],
            "forbidden": [
                "therapy",
                "counseling",
                "personal relationships",
                "life coaching",
                "financial planning",
                "legal advice",
                "medical advice",
            ],
        },
        AIAgentScope.INTERVIEWER: {
            "allowed": [
                "interview practice",
                "behavioral questions",
                "star method",
                "technical questions",
                "role-specific questions",
                "feedback",
            ],
            "forbidden": [
                "personal questions",
                "discriminatory questions",
                "illegal questions",
                "sensitive attributes",
                "general conversation",
            ],
        },
    }

    # Out-of-scope patterns (expanded)
    OUT_OF_SCOPE_PATTERNS = [
        # Medical/Health
        r"\b(medical|health|diagnosis|prescription|therapy|treatment|disease|symptom|medicine)\b",
        # Legal
        r"\b(legal advice|lawsuit|attorney|litigation|sue|court case|lawyer)\b",
        # Financial
        r"\b(financial advice|investment|stock|crypto|trading|loan|mortgage|tax planning)\b",
        # Political
        r"\b(political|election|vote|campaign|party affiliation|political opinion)\b",
        # Religious
        r"\b(religion|religious|spiritual guidance|faith|prayer)\b",
        # Academic integrity
        r"\b(write (my )?essay|do (my )?homework|assignment|cheat|plagiarize)\b",
        # Jailbreak attempts
        r"\b(ignore (previous |all )?instructions?|disregard (your )?system prompt|forget (your )?rules)\b",
        r"\b(you are now|act as|pretend (to be|you\'?re)|roleplay as)\s+(?!career|resume|job|interviewer|coach)",
        r"\b(enable developer mode|dev mode|debug mode|admin mode)\b",
        # Relationships/Personal
        r"\b(dating advice|relationship|romance|love life|personal problems)\b",
        # Creative/Entertainment
        r"\b(write (a )?story|poem|song|creative writing|fiction)\b",
    ]

    # Harmful content patterns (expanded)
    HARMFUL_PATTERNS = [
        # Discrimination
        r"\b(discrimination|discriminate|racist|racism|sexist|sexism|homophobic|homophobia)\b",
        r"\b(xenophobic|xenophobia|ageist|ageism|transphobic)\b",
        # Violence
        r"\b(violence|violent|weapon|bomb|attack|assault|harm|kill|murder)\b",
        # Illegal activity
        r"\b(illegal|fraud|scam|fake credentials|forged|counterfeit)\b",
        r"\b(money laundering|tax evasion|insider trading)\b",
        # Hate speech
        r"\b(hate speech|slur|offensive|derogatory|insult)\b",
        # Self-harm
        r"\b(self-harm|suicide|suicidal|end my life)\b",
        # Explicit content
        r"\b(explicit|pornographic|sexual content|nsfw)\b",
    ]

    # Fake credential indicators
    FAKE_CREDENTIAL_PATTERNS = [
        r"\bfake\b.*\b(degree|certification|diploma|credential|experience|reference)\b",
        r"\bmake up\b.*\b(work history|experience|job|employer|skill)\b",
        r"\binvent\b.*\b(skill|qualification|achievement|award|publication)\b",
        r"\bfabricate\b.*\b(resume|cv|experience|education)\b",
        r"\b(forge|forged|counterfeit)\b.*\b(document|certificate|letter)\b",
        r"\b(lie about|lying about|misrepresent)\b.*\b(experience|education|skill)\b",
    ]

    @staticmethod
    def check_agent_scope(text: str, agent: AIAgentScope) -> Tuple[bool, Optional[str], List[str]]:
        """
        Comprehensive scope check for AI agent.

        Returns:
            (is_in_scope, violation_type, suggestions)
        """
        text_lower = text.lower()

        # Check for out-of-scope patterns
        for pattern in SafetyGuardrails.OUT_OF_SCOPE_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return (
                    False,
                    "out_of_scope",
                    [
                        f"This request appears to be about '{match.group()}' which is outside my specialization.",
                        "I'm focused on career-related assistance only.",
                        "Please rephrase your request to focus on career documents, job search, or professional development.",
                    ],
                )

        # Check if request aligns with agent's allowed scope
        scope_config = SafetyGuardrails.AGENT_SCOPES.get(agent)
        if scope_config:
            # Check forbidden topics
            for forbidden in scope_config["forbidden"]:
                if forbidden.lower() in text_lower:
                    return (
                        False,
                        "forbidden_topic",
                        [
                            f"I cannot assist with {forbidden}.",
                            f"My expertise is limited to: {', '.join(scope_config['allowed'][:3])}.",
                        ],
                    )

        return True, None, []

    @staticmethod
    def check_safety(text: str) -> Tuple[bool, List[str], str]:
        """
        Check for harmful, illegal, or inappropriate content.

        Returns:
            (is_safe, flags, severity)
        """
        flags = []
        text_lower = text.lower()
        severity = "none"

        for pattern in SafetyGuardrails.HARMFUL_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                flags.append(f"Harmful content detected: {match.group()}")
                severity = "high"

        # Special check for self-harm - immediate escalation
        if re.search(r"\b(self-harm|suicide|suicidal|end my life)\b", text_lower):
            severity = "critical"
            flags.append("CRITICAL: Self-harm content detected")

        return len(flags) == 0, flags, severity

    @staticmethod
    def check_fake_credentials(text: str) -> Tuple[bool, List[str]]:
        """
        Detect requests for fabricated credentials or false information.

        Returns:
            (is_legitimate, warnings)
        """
        warnings = []
        text_lower = text.lower()

        for pattern in SafetyGuardrails.FAKE_CREDENTIAL_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                warnings.append(f"Request involves potentially false credentials: '{match.group()}'")

        if warnings:
            warnings.append("I can only work with truthful, verifiable career information.")

        return len(warnings) == 0, warnings

    @staticmethod
    def check_jailbreak_attempt(text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect attempts to bypass safety guardrails.

        Returns:
            (is_legitimate, attack_type)
        """
        text_lower = text.lower()

        jailbreak_patterns = {
            "instruction_override": r"\b(ignore|disregard|forget|override|bypass)\s+(instructions?|rules?|guidelines?|restrictions?)\b",
            "role_manipulation": r"\b(you are now|from now on|pretend|act as|roleplay)\b(?!.*\b(career|resume|interview)\b)",
            "privilege_escalation": r"\b(admin|root|sudo|superuser|developer|debug)\s+(mode|access|rights?)\b",
            "prompt_injection": r"(\[SYSTEM\]|\[INST\]|\<\|system\|\>|\{system\})",
        }

        for attack_type, pattern in jailbreak_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, attack_type

        return True, None

    @staticmethod
    def sanitize_output(text: str) -> str:
        """
        Clean AI output to remove any leaked system prompts or internal info.
        """
        # Remove potential system prompt leaks
        sanitized = re.sub(
            r"(system prompt|developer instructions?|internal guidelines?):.*?(\n\n|\Z)",
            "[REDACTED]",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove any [INTERNAL] markers
        sanitized = re.sub(r"\[INTERNAL\].*?\[/INTERNAL\]", "", sanitized, flags=re.DOTALL)

        return sanitized


class PrivacyFilter:
    """
    Handle PII detection, redaction, and privacy compliance.
    Supports GDPR, CCPA, PDPA, APPI, PIPL, and other regulations.
    """

    # ===== PII PATTERNS =====

    # Identity numbers
    SSN_PATTERN = r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"  # US SSN
    UK_NI_PATTERN = r"\b[A-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-Z]\b"  # UK National Insurance
    SG_NRIC_PATTERN = r"\b[STFG]\d{7}[A-Z]\b"  # Singapore NRIC

    # Contact info
    EMAIL_PATTERN = r"\b[\w\.-]+@[\w\.-]+\.\w+\b"
    PHONE_PATTERN = r"\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"

    # Addresses
    FULL_ADDRESS_PATTERN = (
        r"\d+\s+[\w\s,]+(?:street|st\.?|avenue|ave\.?|road|rd\.?|drive|dr\.?|lane|ln\.?|boulevard|blvd\.?)"
    )

    # Financial
    CREDIT_CARD_PATTERN = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
    IBAN_PATTERN = r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"

    # Government IDs
    PASSPORT_PATTERN = r"\b[A-Z]{1,2}\d{6,9}\b"

    # Protected categories (GDPR Article 9, CCPA sensitive categories)
    PROTECTED_CATEGORIES = {
        "race_ethnicity": r"\b(african american|asian|caucasian|hispanic|latino|race|ethnicity|ethnic origin)\b",
        "religion": r"\b(christian|muslim|jewish|hindu|buddhist|atheist|religious belief)\b",
        "political": r"\b(democrat|republican|liberal|conservative|political affiliation|political view)\b",
        "sexual_orientation": r"\b(gay|lesbian|bisexual|heterosexual|lgbt|sexual orientation)\b",
        "health": r"\b(medical condition|health status|disability|mental health|diagnosis)\b",
        "genetic": r"\b(genetic|dna|hereditary|genetic predisposition)\b",
        "biometric": r"\b(fingerprint|facial recognition|iris scan|biometric)\b",
        "union_membership": r"\b(union member|trade union|labor union)\b",
    }

    @staticmethod
    def detect_pii(text: str) -> Dict[str, List[str]]:
        """
        Detect all PII in text.

        Returns:
            Dictionary of PII type -> list of matches
        """
        detections = {}

        patterns = {
            "ssn": PrivacyFilter.SSN_PATTERN,
            "uk_ni": PrivacyFilter.UK_NI_PATTERN,
            "sg_nric": PrivacyFilter.SG_NRIC_PATTERN,
            "email": PrivacyFilter.EMAIL_PATTERN,
            "phone": PrivacyFilter.PHONE_PATTERN,
            "address": PrivacyFilter.FULL_ADDRESS_PATTERN,
            "credit_card": PrivacyFilter.CREDIT_CARD_PATTERN,
            "iban": PrivacyFilter.IBAN_PATTERN,
            "passport": PrivacyFilter.PASSPORT_PATTERN,
        }

        for pii_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detections[pii_type] = matches

        return detections

    @staticmethod
    def redact_pii(
        text: str, region: PrivacyRegion = PrivacyRegion.US, keep_partial: bool = True
    ) -> Tuple[str, List[str]]:
        """
        Redact PII based on regional requirements.

        Args:
            text: Text to redact
            region: Privacy region (affects strictness)
            keep_partial: Whether to keep partial info (e.g., email domain)

        Returns:
            (redacted_text, list of redaction summaries)
        """
        redactions = []
        cleaned_text = text

        # SSN/National ID - always redact fully
        if re.search(PrivacyFilter.SSN_PATTERN, cleaned_text):
            cleaned_text = re.sub(PrivacyFilter.SSN_PATTERN, "[ID-REDACTED]", cleaned_text)
            redactions.append("National ID numbers redacted")

        # UK National Insurance
        if re.search(PrivacyFilter.UK_NI_PATTERN, cleaned_text):
            cleaned_text = re.sub(PrivacyFilter.UK_NI_PATTERN, "[NI-REDACTED]", cleaned_text)
            redactions.append("UK National Insurance numbers redacted")

        # Singapore NRIC
        if re.search(PrivacyFilter.SG_NRIC_PATTERN, cleaned_text):
            cleaned_text = re.sub(PrivacyFilter.SG_NRIC_PATTERN, "[NRIC-REDACTED]", cleaned_text)
            redactions.append("Singapore NRIC redacted")

        # Email - region-dependent
        if region in [PrivacyRegion.EU, PrivacyRegion.UK]:
            # GDPR: Stricter - redact fully or keep domain only
            if keep_partial:
                cleaned_text = re.sub(PrivacyFilter.EMAIL_PATTERN, r"[email]@\1", cleaned_text)
                redactions.append("Email addresses partially redacted (GDPR)")
            else:
                cleaned_text = re.sub(PrivacyFilter.EMAIL_PATTERN, "[EMAIL]", cleaned_text)
                redactions.append("Email addresses fully redacted (GDPR)")

        # Phone numbers - redact fully
        if re.search(PrivacyFilter.PHONE_PATTERN, cleaned_text):
            cleaned_text = re.sub(PrivacyFilter.PHONE_PATTERN, "[PHONE]", cleaned_text)
            redactions.append("Phone numbers redacted")

        # Addresses - keep city/state only
        if re.search(PrivacyFilter.FULL_ADDRESS_PATTERN, cleaned_text, re.IGNORECASE):
            cleaned_text = re.sub(
                PrivacyFilter.FULL_ADDRESS_PATTERN, "[City, State]", cleaned_text, flags=re.IGNORECASE
            )
            redactions.append("Full street addresses redacted to city/state")

        # Credit cards - always redact
        if re.search(PrivacyFilter.CREDIT_CARD_PATTERN, cleaned_text):
            cleaned_text = re.sub(PrivacyFilter.CREDIT_CARD_PATTERN, "[CARD-XXXX]", cleaned_text)
            redactions.append("Credit card numbers redacted")

        # Passports
        if re.search(PrivacyFilter.PASSPORT_PATTERN, cleaned_text):
            cleaned_text = re.sub(PrivacyFilter.PASSPORT_PATTERN, "[PASSPORT]", cleaned_text)
            redactions.append("Passport numbers redacted")

        return cleaned_text, redactions

    @staticmethod
    def detect_protected_categories(text: str) -> Dict[str, List[str]]:
        """
        Detect GDPR Article 9 / CCPA sensitive categories.

        Returns:
            Dictionary of category -> list of matches
        """
        detected = {}
        text_lower = text.lower()

        for category, pattern in PrivacyFilter.PROTECTED_CATEGORIES.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                detected[category] = matches

        return detected

    @staticmethod
    def redact_protected_categories(text: str) -> Tuple[str, List[str]]:
        """
        Remove references to protected categories (GDPR Article 9).
        """
        redactions = []
        cleaned_text = text

        for category, pattern in PrivacyFilter.PROTECTED_CATEGORIES.items():
            if re.search(pattern, cleaned_text, re.IGNORECASE):
                cleaned_text = re.sub(pattern, f"[REDACTED-{category.upper()}]", cleaned_text, flags=re.IGNORECASE)
                redactions.append(f"Protected category redacted: {category}")

        return cleaned_text, redactions

    @staticmethod
    def verify_consent(
        consent: Dict[str, bool], operation: str, region: PrivacyRegion = PrivacyRegion.US
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify user has granted necessary consent for operation.
        Requirements vary by region.
        """
        # Define consent requirements by operation and region
        requirements = {
            "ingest": {
                PrivacyRegion.EU: ["store_profile", "ai_processing", "data_retention"],
                PrivacyRegion.UK: ["store_profile", "ai_processing", "data_retention"],
                PrivacyRegion.CALIFORNIA: ["store_profile", "ai_processing"],
                PrivacyRegion.US: ["ai_processing"],
            },
            "tailor": {
                PrivacyRegion.EU: ["ai_processing"],
                PrivacyRegion.UK: ["ai_processing"],
                PrivacyRegion.US: ["ai_processing"],
            },
            "apply_suggestion": {
                PrivacyRegion.EU: ["store_profile", "ai_processing"],
                PrivacyRegion.UK: ["store_profile", "ai_processing"],
                PrivacyRegion.US: ["store_profile"],
            },
        }

        required = requirements.get(operation, {}).get(region, [])

        for consent_item in required:
            if not consent.get(consent_item, False):
                return False, f"Missing required consent: {consent_item} (Region: {region})"

        return True, None

    @staticmethod
    def get_retention_policy(region: PrivacyRegion) -> Dict[str, Any]:
        """
        Get data retention policy based on region.
        """
        policies = {
            PrivacyRegion.EU: {
                "max_retention_days": 730,  # 2 years
                "auto_delete": True,
                "right_to_erasure": True,
                "right_to_portability": True,
                "breach_notification_hours": 72,
                "dpo_required": True,  # Data Protection Officer
                "legal_basis": "Explicit consent",
            },
            PrivacyRegion.UK: {
                "max_retention_days": 730,
                "auto_delete": True,
                "right_to_erasure": True,
                "right_to_portability": True,
                "breach_notification_hours": 72,
                "dpo_required": True,
                "legal_basis": "Explicit consent",
            },
            PrivacyRegion.CALIFORNIA: {
                "max_retention_days": 1095,  # 3 years
                "auto_delete": False,
                "right_to_erasure": True,  # CCPA Right to Delete
                "right_to_portability": True,
                "breach_notification_hours": None,
                "opt_out_sale": True,
                "legal_basis": "Opt-in consent",
            },
            PrivacyRegion.SINGAPORE: {
                "max_retention_days": 1095,
                "auto_delete": True,
                "right_to_erasure": True,
                "right_to_portability": True,
                "breach_notification_hours": 72,
                "purpose_limitation": True,
                "legal_basis": "Consent",
            },
            PrivacyRegion.JAPAN: {
                "max_retention_days": 1095,
                "auto_delete": True,
                "right_to_erasure": True,
                "right_to_portability": False,
                "breach_notification_hours": 24,
                "cross_border_restrictions": True,
                "legal_basis": "Consent",
            },
            PrivacyRegion.CHINA: {
                "max_retention_days": 1095,
                "auto_delete": True,
                "right_to_erasure": True,
                "right_to_portability": True,
                "breach_notification_hours": 72,
                "data_localization": True,
                "security_assessment_required": True,
                "legal_basis": "Explicit consent",
            },
            PrivacyRegion.US: {
                "max_retention_days": 1825,  # 5 years
                "auto_delete": False,
                "right_to_erasure": False,
                "right_to_portability": False,
                "breach_notification_hours": None,
                "legal_basis": "Implied consent",
            },
        }

        return policies.get(region, policies[PrivacyRegion.US])

    @staticmethod
    def calculate_data_hash(data: str) -> str:
        """
        Generate SHA-256 hash for audit trail (non-reversible).
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()[:32]

    @staticmethod
    def should_delete_data(created_at: datetime, region: PrivacyRegion) -> Tuple[bool, Optional[str]]:
        """
        Check if data should be auto-deleted based on retention policy.
        """
        policy = PrivacyFilter.get_retention_policy(region)

        if not policy.get("auto_delete", False):
            return False, "Auto-delete not enabled for this region"

        max_days = policy.get("max_retention_days", 1825)
        retention_deadline = created_at + timedelta(days=max_days)

        if datetime.utcnow() >= retention_deadline:
            return True, f"Data exceeded {max_days}-day retention limit"

        return False, None


class AuditLogger:
    """
    Comprehensive audit logging for compliance.
    """

    @staticmethod
    def log_access(
        user_id: str,
        resource: str,
        action: str,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log data access for audit trail"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": ip_address,
            "metadata": metadata or {},
        }
        logger.info(f"AUDIT: {entry}")
        # TODO: Write to dedicated audit log storage

    @staticmethod
    def log_consent_change(user_id: str, consent_type: str, granted: bool, region: PrivacyRegion):
        """Log consent changes"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "consent_type": consent_type,
            "granted": granted,
            "region": region,
            "event": "consent_change",
        }
        logger.info(f"CONSENT: {entry}")

    @staticmethod
    def log_data_erasure(user_id: str, reason: str):
        """Log GDPR erasure requests"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": "data_erasure",
            "reason": reason,
            "event": "gdpr_erasure",
        }
        logger.warning(f"ERASURE: {entry}")


# ===== SAFETY RESPONSE TEMPLATES =====

SAFETY_REFUSAL_MESSAGES = {
    "out_of_scope": """I'm specialized in career documents and professional development. I can help with:
• Resume and CV optimization
• Cover letter writing
• Job application strategy
• Career planning and skill development
• Interview preparation

For other topics, please consult appropriate specialized resources.""",
    "harmful_content": """I cannot process this request as it contains content that may be harmful or inappropriate. 

I'm here to help with professional career development in a safe, respectful manner. Please rephrase your request to focus on career-related assistance.""",
    "privacy_violation": """This request involves sensitive personal information that requires additional privacy protections.

Please review your privacy settings and ensure you've granted necessary consent for this operation.""",
    "fake_credentials": """I cannot assist with creating false, misleading, or fabricated credentials.

All career information must be truthful and verifiable. I'm happy to help you present your genuine experience and skills in the best possible light.""",
    "insufficient_consent": """Insufficient privacy consent for this operation.

To proceed, please review and grant the necessary permissions in your privacy settings.""",
    "jailbreak_detected": """I've detected an attempt to bypass my safety guidelines.

I'm designed to assist specifically with career development tasks. Let me know how I can help with your resume, job search, or professional growth!""",
}
