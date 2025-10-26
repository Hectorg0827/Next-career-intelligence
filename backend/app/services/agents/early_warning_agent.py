"""
Early Warning Agent - Proactive Risk Detection & Alert System
Monitors for threats to career stability and opportunities
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.user_profile import UserProfile


class EarlyWarningAgent:
    """
    Early Warning Agent - The sentinel
    
    Responsibilities:
    - Monitor for layoff risks in user's company/industry
    - Detect skill obsolescence signals
    - Identify when user's role is being automated
    - Flag declining demand for user's current position
    - Answer: "What threats should I be aware of?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def scan_for_threats(
        self,
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive threat scan for user's career
        
        Returns list of identified threats with severity and recommendations
        """
        try:
            threats = []
            
            # Skill obsolescence check
            skill_threats = await self._check_skill_obsolescence(user_profile)
            threats.extend(skill_threats)
            
            # Industry stability check
            industry_threats = await self._check_industry_stability(user_profile)
            threats.extend(industry_threats)
            
            # Automation risk check
            automation_threats = await self._check_automation_risk(user_profile)
            threats.extend(automation_threats)
            
            # Sort by severity
            threats.sort(key=lambda x: self._severity_score(x.get('severity', 'low')), reverse=True)
            
            logger.info(f"Identified {len(threats)} threats for user")
            
            return threats[:10]  # Return top 10 most critical
            
        except Exception as e:
            logger.error(f"Threat scan failed: {e}")
            return []
    
    async def _check_skill_obsolescence(
        self,
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Check if user's skills are becoming obsolete"""
        threats = []
        
        if not user_profile.skills:
            threats.append({
                "type": "incomplete_profile",
                "severity": "medium",
                "title": "Profile Skills Not Listed",
                "description": "Without skill data, we cannot assess obsolescence risk",
                "impact": "Unable to provide personalized risk assessment",
                "recommendations": [
                    "Add your current skills to your profile",
                    "Include both technical and soft skills"
                ],
                "urgency": "medium",
                "detected_at": datetime.utcnow().isoformat()
            })
            return threats
        
        try:
            prompt = f"""
            Analyze skill obsolescence risk for these skills:
            {', '.join(user_profile.skills[:20])}
            
            Role Context: {user_profile.job_title or 'Not specified'}
            Industry: {user_profile.industry or 'General'}
            
            Identify:
            1. Skills at risk of becoming obsolete (next 1-2 years)
            2. Severity level (critical/high/medium/low)
            3. Replacement skills or technologies
            4. Timeline for action
            
            Return JSON array with: skill, severity, replacement, timeline, reason
            """
            
            response = self.model.generate_content(prompt)
            obsolescence_data = self._parse_obsolescence_response(response.text)
            
            for item in obsolescence_data:
                if item.get('severity') in ['critical', 'high']:
                    threats.append({
                        "type": "skill_obsolescence",
                        "severity": item.get('severity', 'medium'),
                        "title": f"Skill Risk: {item.get('skill')}",
                        "description": item.get('reason', 'This skill may be declining in relevance'),
                        "impact": f"Replacement: {item.get('replacement', 'Modern alternatives')}",
                        "recommendations": [
                            f"Learn {item.get('replacement', 'modern alternatives')}",
                            "Start transition within " + item.get('timeline', '6-12 months')
                        ],
                        "urgency": "high" if item.get('severity') == 'critical' else "medium",
                        "detected_at": datetime.utcnow().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Skill obsolescence check failed: {e}")
        
        return threats
    
    async def _check_industry_stability(
        self,
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Check stability of user's industry"""
        threats = []
        
        industry = user_profile.industry or "General"
        
        try:
            prompt = f"""
            Assess current stability and outlook for {industry} industry.
            
            Consider:
            - Recent layoffs or downsizing
            - Industry growth/decline trends
            - Market disruptions
            - Regulatory changes
            
            If there are significant risks, return JSON object with:
            severity (critical/high/medium/low), description, impact, recommendations
            
            If industry is stable, return: {{"severity": "low", "stable": true}}
            """
            
            response = self.model.generate_content(prompt)
            stability_data = self._parse_stability_response(response.text)
            
            if stability_data.get('severity') in ['critical', 'high', 'medium']:
                threats.append({
                    "type": "industry_instability",
                    "severity": stability_data.get('severity', 'medium'),
                    "title": f"{industry} Industry Risk",
                    "description": stability_data.get('description', 'Industry facing headwinds'),
                    "impact": stability_data.get('impact', 'Potential job market challenges'),
                    "recommendations": stability_data.get('recommendations', [
                        "Monitor industry news closely",
                        "Build transferable skills",
                        "Network in adjacent industries"
                    ]),
                    "urgency": "medium",
                    "detected_at": datetime.utcnow().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Industry stability check failed: {e}")
        
        return threats
    
    async def _check_automation_risk(
        self,
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Check automation/AI replacement risk"""
        threats = []
        
        role = user_profile.job_title
        if not role:
            return threats
        
        try:
            prompt = f"""
            Assess AI/automation displacement risk for: {role}
            
            Provide:
            1. Risk Level (critical/high/medium/low)
            2. Timeline (immediate/1-2 years/3-5 years/5+ years)
            3. Specific tasks at risk
            4. Human-advantage areas
            
            Return JSON with: risk_level, timeline, tasks_at_risk, human_advantages
            """
            
            response = self.model.generate_content(prompt)
            automation_data = self._parse_automation_response(response.text)
            
            risk_level = automation_data.get('risk_level', 'low')
            
            if risk_level in ['critical', 'high']:
                threats.append({
                    "type": "automation_risk",
                    "severity": risk_level,
                    "title": f"Automation Risk for {role}",
                    "description": f"AI/automation could impact this role within {automation_data.get('timeline', '3-5 years')}",
                    "impact": f"Tasks at risk: {', '.join(automation_data.get('tasks_at_risk', ['routine tasks'])[:3])}",
                    "recommendations": [
                        "Focus on " + ', '.join(automation_data.get('human_advantages', ['creative', 'strategic'])[:2]),
                        "Develop AI collaboration skills",
                        "Consider transitioning to adjacent roles"
                    ],
                    "urgency": "high" if risk_level == 'critical' else "medium",
                    "detected_at": datetime.utcnow().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Automation risk check failed: {e}")
        
        return threats
    
    async def generate_risk_report(
        self,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk report
        
        Returns summary of all identified risks with action plan
        """
        try:
            threats = await self.scan_for_threats(user_profile)
            
            # Categorize threats
            critical = [t for t in threats if t.get('severity') == 'critical']
            high = [t for t in threats if t.get('severity') == 'high']
            medium = [t for t in threats if t.get('severity') == 'medium']
            low = [t for t in threats if t.get('severity') == 'low']
            
            # Overall risk score (0-100)
            risk_score = (
                len(critical) * 25 +
                len(high) * 15 +
                len(medium) * 8 +
                len(low) * 3
            )
            risk_score = min(risk_score, 100)
            
            return {
                "overall_risk_score": risk_score,
                "risk_level": self._categorize_risk_score(risk_score),
                "threat_count": len(threats),
                "threats_by_severity": {
                    "critical": len(critical),
                    "high": len(high),
                    "medium": len(medium),
                    "low": len(low)
                },
                "threats": threats,
                "top_priority_actions": self._extract_top_actions(threats),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Risk report generation failed: {e}")
            return {
                "overall_risk_score": 50,
                "risk_level": "medium",
                "threat_count": 0,
                "threats": [],
                "top_priority_actions": ["Complete your profile for personalized risk assessment"],
                "generated_at": datetime.utcnow().isoformat()
            }
    
    # Helper methods
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting"""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(severity.lower(), 0)
    
    def _categorize_risk_score(self, score: int) -> str:
        """Categorize overall risk score"""
        if score >= 75:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 25:
            return "medium"
        else:
            return "low"
    
    def _extract_top_actions(self, threats: List[Dict[str, Any]]) -> List[str]:
        """Extract top priority actions from threats"""
        actions = []
        for threat in threats[:3]:  # Top 3 threats
            recs = threat.get('recommendations', [])
            if recs:
                actions.append(recs[0])
        return actions[:5]  # Max 5 actions
    
    def _parse_obsolescence_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse skill obsolescence response"""
        try:
            import json
            import re
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return []
    
    def _parse_stability_response(self, response_text: str) -> Dict[str, Any]:
        """Parse industry stability response"""
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {"severity": "low", "stable": True}
    
    def _parse_automation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse automation risk response"""
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {
            "risk_level": "medium",
            "timeline": "3-5 years",
            "tasks_at_risk": ["Routine tasks"],
            "human_advantages": ["Critical thinking", "Creativity"]
        }
