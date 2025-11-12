"""
Skill Inference Engine - Detect transferable and adjacent skills
Analyzes user skills to identify hidden strengths and growth opportunities
"""

from typing import List, Dict, Any, Set
from openai import AsyncOpenAI
from loguru import logger
import json

from app.core.config import settings


class SkillInferenceEngine:
    """
    Intelligent skill analysis system that identifies:
    1. Skill clusters (Technical, Business, Soft Skills)
    2. Transferable/adjacent skills
    3. Hidden implicit skills
    4. High-value skill gaps for career growth
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Comprehensive skill taxonomy - will expand over time
        self.skill_taxonomy = {
            "Technical": {
                "Programming": [
                    "Python",
                    "Java",
                    "JavaScript",
                    "TypeScript",
                    "C++",
                    "C#",
                    "Ruby",
                    "Go",
                    "Rust",
                    "PHP",
                    "Swift",
                    "Kotlin",
                    "R",
                    "MATLAB",
                    "Scala",
                ],
                "Data & Analytics": [
                    "SQL",
                    "Data Analysis",
                    "Excel",
                    "Tableau",
                    "Power BI",
                    "Looker",
                    "Data Visualization",
                    "Statistical Analysis",
                    "A/B Testing",
                    "Google Analytics",
                    "ETL",
                    "Data Modeling",
                ],
                "AI & Machine Learning": [
                    "Machine Learning",
                    "Deep Learning",
                    "NLP",
                    "Computer Vision",
                    "TensorFlow",
                    "PyTorch",
                    "Scikit-learn",
                    "Neural Networks",
                    "AI Ethics",
                    "Prompt Engineering",
                    "LLMs",
                ],
                "Cloud & Infrastructure": [
                    "AWS",
                    "Azure",
                    "GCP",
                    "Docker",
                    "Kubernetes",
                    "Terraform",
                    "CI/CD",
                    "DevOps",
                    "Linux",
                    "Networking",
                    "Security",
                ],
                "Web & Mobile": [
                    "React",
                    "Angular",
                    "Vue.js",
                    "Node.js",
                    "HTML/CSS",
                    "REST APIs",
                    "GraphQL",
                    "Mobile Development",
                    "iOS",
                    "Android",
                    "Flutter",
                ],
                "Database": [
                    "PostgreSQL",
                    "MySQL",
                    "MongoDB",
                    "Redis",
                    "Elasticsearch",
                    "Database Design",
                    "Query Optimization",
                    "NoSQL",
                ],
            },
            "Business": {
                "Management": [
                    "Project Management",
                    "Team Leadership",
                    "Agile",
                    "Scrum",
                    "Program Management",
                    "Change Management",
                    "Resource Planning",
                    "Risk Management",
                    "Vendor Management",
                ],
                "Strategy": [
                    "Business Strategy",
                    "Market Analysis",
                    "Strategic Planning",
                    "Competitive Analysis",
                    "Business Development",
                    "Roadmap Planning",
                    "OKRs",
                    "KPI Management",
                ],
                "Finance": [
                    "Financial Analysis",
                    "Budgeting",
                    "Forecasting",
                    "Accounting",
                    "Financial Modeling",
                    "P&L Management",
                    "Cost Analysis",
                    "Investment Analysis",
                ],
                "Sales & Marketing": [
                    "Sales",
                    "Business Development",
                    "Negotiation",
                    "CRM",
                    "Marketing",
                    "Digital Marketing",
                    "SEO/SEM",
                    "Content Marketing",
                    "Social Media",
                    "Brand Management",
                    "Customer Acquisition",
                ],
                "Product": [
                    "Product Management",
                    "Product Strategy",
                    "User Research",
                    "Product Analytics",
                    "Roadmap Planning",
                    "Pricing Strategy",
                    "Go-to-Market Strategy",
                ],
            },
            "Soft Skills": {
                "Communication": [
                    "Presentation",
                    "Technical Writing",
                    "Stakeholder Management",
                    "Executive Communication",
                    "Public Speaking",
                    "Documentation",
                    "Cross-functional Collaboration",
                ],
                "Problem Solving": [
                    "Critical Thinking",
                    "Analytical Thinking",
                    "Innovation",
                    "Creative Problem Solving",
                    "Systems Thinking",
                    "Debugging",
                    "Root Cause Analysis",
                ],
                "Interpersonal": [
                    "Collaboration",
                    "Mentoring",
                    "Conflict Resolution",
                    "Empathy",
                    "Active Listening",
                    "Emotional Intelligence",
                    "Team Building",
                    "Feedback Delivery",
                ],
                "Leadership": [
                    "People Management",
                    "Coaching",
                    "Influence",
                    "Decision Making",
                    "Vision Setting",
                    "Delegation",
                    "Performance Management",
                ],
            },
            "Domain Expertise": {
                "Industries": [
                    "Healthcare",
                    "Finance",
                    "E-commerce",
                    "SaaS",
                    "Education",
                    "Manufacturing",
                    "Retail",
                    "Telecommunications",
                    "Energy",
                ],
                "Specialized": [
                    "Compliance",
                    "Legal",
                    "HR",
                    "Operations",
                    "Supply Chain",
                    "Quality Assurance",
                    "Customer Success",
                    "UX Design",
                ],
            },
        }

        # Skill relationship map - defines which skills lead to others
        self.skill_relationships = {
            # Programming
            "Python": [
                ("Data Analysis", 0.85),
                ("Machine Learning", 0.80),
                ("Backend Development", 0.75),
                ("Automation", 0.70),
                ("Data Engineering", 0.75),
                ("API Development", 0.70),
            ],
            "JavaScript": [
                ("React", 0.85),
                ("Node.js", 0.80),
                ("TypeScript", 0.75),
                ("Frontend Development", 0.90),
                ("Full-Stack Development", 0.70),
            ],
            "SQL": [
                ("Data Analysis", 0.90),
                ("Database Design", 0.85),
                ("Business Intelligence", 0.75),
                ("Data Engineering", 0.70),
                ("ETL", 0.65),
            ],
            # Management
            "Project Management": [
                ("Agile", 0.90),
                ("Team Leadership", 0.85),
                ("Scrum", 0.80),
                ("Product Management", 0.70),
                ("Program Management", 0.75),
                ("Resource Planning", 0.80),
            ],
            "Agile": [
                ("Scrum", 0.95),
                ("Project Management", 0.85),
                ("Team Leadership", 0.75),
                ("Change Management", 0.70),
            ],
            # Data & Analytics
            "Data Analysis": [
                ("SQL", 0.85),
                ("Excel", 0.80),
                ("Tableau", 0.75),
                ("Business Intelligence", 0.80),
                ("Data Visualization", 0.85),
                ("Statistical Analysis", 0.70),
            ],
            "Machine Learning": [
                ("Python", 0.90),
                ("Data Analysis", 0.85),
                ("Deep Learning", 0.75),
                ("TensorFlow", 0.70),
                ("Statistical Analysis", 0.75),
            ],
            # Business
            "Business Strategy": [
                ("Market Analysis", 0.85),
                ("Strategic Planning", 0.90),
                ("Competitive Analysis", 0.80),
                ("Business Development", 0.75),
            ],
            "Product Management": [
                ("Product Strategy", 0.85),
                ("User Research", 0.80),
                ("Agile", 0.75),
                ("Data Analysis", 0.70),
                ("Roadmap Planning", 0.85),
            ],
            # Add more relationships as needed
        }

    async def infer_adjacent_skills(
        self, current_skills: List[str], job_title: str = "", years_experience: int = 0
    ) -> Dict[str, Any]:
        """
        Main analysis function - infers all skill insights

        Returns comprehensive skill intelligence including clusters,
        transferable skills, hidden skills, and growth opportunities
        """

        logger.info(f"Analyzing skills for {job_title}: {len(current_skills)} skills provided")

        # Step 1: Cluster existing skills
        skill_clusters = self._cluster_skills(current_skills)

        # Step 2: Find adjacent skills using relationships
        adjacent_skills = self._find_adjacent_skills(current_skills)

        # Step 3: Use AI to infer hidden/implicit skills
        hidden_skills = await self._infer_hidden_skills(current_skills, job_title, years_experience)

        # Step 4: Identify skill gaps for high-growth roles
        skill_gaps = await self._identify_skill_gaps(current_skills, adjacent_skills, job_title)

        # Step 5: Calculate skill strength scores
        skill_strength = self._calculate_skill_strength(skill_clusters, years_experience)

        result = {
            "skill_clusters": skill_clusters,
            "transferable_to": adjacent_skills,
            "hidden_skills": hidden_skills,
            "skill_gaps_for_growth": skill_gaps,
            "skill_strength_score": skill_strength,
            "total_skills_identified": len(current_skills) + len(hidden_skills),
            "analysis_timestamp": "now",
        }

        logger.info(
            f"Skill analysis complete: {len(adjacent_skills)} adjacent skills, "
            f"{len(hidden_skills)} hidden skills, {len(skill_gaps)} skill gaps"
        )

        return result

    def _cluster_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Group skills into meaningful categories"""

        clusters = {"Technical": [], "Business": [], "Soft Skills": [], "Domain Expertise": [], "Uncategorized": []}

        skills_lower = {s.lower(): s for s in skills}  # Preserve original casing

        for skill_original in skills:
            skill_lower = skill_original.lower()
            categorized = False

            # Check each category and subcategory
            for category, subcategories in self.skill_taxonomy.items():
                for subcat, skill_list in subcategories.items():
                    # Check for exact match or partial match
                    for taxonomy_skill in skill_list:
                        if (
                            skill_lower == taxonomy_skill.lower()
                            or skill_lower in taxonomy_skill.lower()
                            or taxonomy_skill.lower() in skill_lower
                        ):

                            if category not in clusters:
                                clusters[category] = []
                            clusters[category].append(skill_original)
                            categorized = True
                            break
                    if categorized:
                        break
                if categorized:
                    break

            if not categorized:
                clusters["Uncategorized"].append(skill_original)

        # Remove empty clusters and sort skills
        return {k: sorted(list(set(v))) for k, v in clusters.items() if v}

    def _find_adjacent_skills(self, current_skills: List[str]) -> List[Dict[str, Any]]:
        """Find related skills based on predefined relationships"""

        adjacent = {}
        skills_lower = [s.lower() for s in current_skills]

        for skill in current_skills:
            # Check both exact match and fuzzy match
            for rel_skill, relationships in self.skill_relationships.items():
                if (
                    skill.lower() == rel_skill.lower()
                    or skill.lower() in rel_skill.lower()
                    or rel_skill.lower() in skill.lower()
                ):

                    for related_skill, confidence in relationships:
                        # Don't suggest skills user already has
                        if related_skill.lower() not in skills_lower:
                            if related_skill not in adjacent:
                                adjacent[related_skill] = {"confidence": confidence, "source_skills": [skill]}
                            else:
                                # Multiple paths to same skill - boost confidence
                                old_conf = adjacent[related_skill]["confidence"]
                                adjacent[related_skill]["confidence"] = (old_conf + confidence) / 2
                                adjacent[related_skill]["source_skills"].append(skill)

        # Sort by confidence and return top 10
        sorted_skills = sorted(adjacent.items(), key=lambda x: x[1]["confidence"], reverse=True)[:10]

        return [
            {
                "skill": skill,
                "confidence": round(data["confidence"], 2),
                "reasoning": f"Highly related to your {', '.join(data['source_skills'][:2])} skills",
                "source_skills": data["source_skills"],
            }
            for skill, data in sorted_skills
        ]

    async def _infer_hidden_skills(self, current_skills: List[str], job_title: str, years_experience: int) -> List[str]:
        """Use AI to identify implicit skills from job title + explicit skills"""

        if not job_title or not settings.OPENAI_API_KEY:
            return []

        prompt = f"""
Analyze a professional with this profile:

Job Title: {job_title}
Years of Experience: {years_experience}
Explicitly Listed Skills: {', '.join(current_skills)}

Identify 3-5 IMPLICIT or HIDDEN skills this person likely has developed but hasn't explicitly listed.

These are skills that professionals in this role typically develop through their work but don't always put on their resume.

Examples of hidden skills:
- A Project Manager with "Agile" likely has "Stakeholder Management", "Risk Assessment", and "Budget Planning"
- A Software Engineer with "Python" likely has "Debugging", "Code Review", and "Version Control (Git)"
- A Data Analyst with "SQL" likely has "Data Cleaning", "Problem Solving", and "Business Communication"

Rules:
1. Only suggest skills that are VERY LIKELY based on the role and experience level
2. Focus on practical, job-specific skills
3. Don't suggest skills they've already listed
4. Consider their experience level (senior roles have more soft skills)

Return ONLY a JSON object with a "hidden_skills" array:
{{"hidden_skills": ["Skill 1", "Skill 2", "Skill 3"]}}
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model for extraction
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career analyst who identifies implicit professional skills.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            hidden_skills = result.get("hidden_skills", [])

            # Validate - don't duplicate existing skills
            current_skills_lower = [s.lower() for s in current_skills]
            hidden_skills = [s for s in hidden_skills if s.lower() not in current_skills_lower]

            logger.info(f"Inferred {len(hidden_skills)} hidden skills")
            return hidden_skills[:5]  # Max 5

        except Exception as e:
            logger.error(f"Failed to infer hidden skills: {e}")
            return []

    async def _identify_skill_gaps(
        self, current_skills: List[str], adjacent_skills: List[Dict], job_title: str
    ) -> List[Dict[str, Any]]:
        """Identify high-value skills to learn for career growth"""

        # Use adjacent skills as base, prioritize by multiple factors
        skill_gaps = []

        for adj_skill in adjacent_skills[:8]:  # Top 8 adjacent skills
            confidence = adj_skill["confidence"]

            # Calculate priority based on confidence and market demand (simplified)
            if confidence > 0.80:
                priority = "Critical"
                learn_difficulty = "Easy"  # High confidence = easy transition
                learning_time = "1-2 months"
            elif confidence > 0.70:
                priority = "High"
                learn_difficulty = "Moderate"
                learning_time = "2-3 months"
            else:
                priority = "Medium"
                learn_difficulty = "Moderate"
                learning_time = "3-4 months"

            skill_gaps.append(
                {
                    "skill": adj_skill["skill"],
                    "priority": priority,
                    "learn_difficulty": learn_difficulty,
                    "market_demand": "High",  # TODO: Integrate with market data in Phase 2
                    "estimated_learning_time": learning_time,
                    "confidence_score": confidence,
                    "why_important": adj_skill["reasoning"],
                }
            )

        return skill_gaps

    def _calculate_skill_strength(self, skill_clusters: Dict[str, List[str]], years_experience: int) -> Dict[str, Any]:
        """Calculate overall skill profile strength"""

        total_skills = sum(len(skills) for skills in skill_clusters.values())

        # Weight different skill types
        weights = {"Technical": 0.35, "Business": 0.25, "Soft Skills": 0.25, "Domain Expertise": 0.15}

        weighted_score = 0
        category_scores = {}

        for category, skills in skill_clusters.items():
            if category in weights:
                # More skills + experience = higher score
                category_score = min(len(skills) * 10 + years_experience * 2, 100)
                category_scores[category] = category_score
                weighted_score += category_score * weights[category]

        # Calculate diversity bonus (having skills across categories is good)
        diversity_bonus = len(skill_clusters) * 5

        overall_score = min(weighted_score + diversity_bonus, 100)

        return {
            "overall_score": round(overall_score, 1),
            "category_scores": category_scores,
            "total_skills": total_skills,
            "skill_diversity": len(skill_clusters),
            "interpretation": self._interpret_strength_score(overall_score),
        }

    def _interpret_strength_score(self, score: float) -> str:
        """Human-readable interpretation of skill strength"""

        if score >= 85:
            return "Exceptional - You have a world-class skill profile"
        elif score >= 75:
            return "Strong - Your skills are well-developed and diverse"
        elif score >= 60:
            return "Solid - Good foundation with room for strategic growth"
        elif score >= 45:
            return "Developing - Focus on building depth in key areas"
        else:
            return "Early Stage - Great opportunity to develop high-value skills"


async def enhance_analysis_with_skills(
    analyzer_result: Dict[str, Any], current_skills: List[str], job_title: str, years_experience: int = 0
) -> Dict[str, Any]:
    """
    Wrapper function to enhance existing analysis with skill inference
    Call this from your analyze endpoint
    """

    engine = SkillInferenceEngine()
    skill_insights = await engine.infer_adjacent_skills(current_skills, job_title, years_experience)

    # Merge with existing analysis
    analyzer_result["skill_insights"] = skill_insights

    return analyzer_result
