"""
Email Notification Service
Sends automated emails for job matches, application updates, and alerts
"""

from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime
import os
import json

# Email providers - support multiple options
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Try SendGrid first
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = bool(SENDGRID_API_KEY)
except ImportError:
    logger.warning("SendGrid not installed. Install with: pip install sendgrid")
    SENDGRID_AVAILABLE = False

# Fallback to Resend
try:
    import resend
    RESEND_AVAILABLE = bool(RESEND_API_KEY)
    if RESEND_AVAILABLE:
        resend.api_key = RESEND_API_KEY
except ImportError:
    logger.warning("Resend not installed. Install with: pip install resend")
    RESEND_AVAILABLE = False


class EmailNotificationService:
    """Service for sending email notifications"""

    def __init__(self):
        self.from_email = os.getenv("FROM_EMAIL", "noreply@careercopilot.ai")
        self.from_name = os.getenv("FROM_NAME", "Career Copilot")
        
        # Determine which email service to use
        if SENDGRID_AVAILABLE:
            self.provider = "sendgrid"
            self.client = SendGridAPIClient(SENDGRID_API_KEY)
            logger.info("Using SendGrid for emails")
        elif RESEND_AVAILABLE:
            self.provider = "resend"
            logger.info("Using Resend for emails")
        else:
            self.provider = "mock"
            logger.warning("No email service configured - using mock mode")

    def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False

    def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email via Resend"""
        try:
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            }
            
            email = resend.Emails.send(params)
            logger.info(f"Email sent successfully to {to_email}: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Resend error: {e}")
            return False

    def _mock_send(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Mock email sending for development"""
        logger.info(f"""
        📧 MOCK EMAIL
        To: {to_email}
        Subject: {subject}
        Text: {text_content[:100]}...
        """)
        return True

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email using configured provider
        
        Returns:
            bool: True if sent successfully
        """
        if not text_content:
            # Strip HTML tags for text version
            import re
            text_content = re.sub('<[^<]+?>', '', html_content)
        
        if self.provider == "sendgrid":
            return self._send_via_sendgrid(to_email, subject, html_content, text_content)
        elif self.provider == "resend":
            return self._send_via_resend(to_email, subject, html_content, text_content)
        else:
            return self._mock_send(to_email, subject, html_content, text_content)

    # ========================================================================
    # Email Templates
    # ========================================================================

    def send_job_match_notification(
        self,
        to_email: str,
        user_name: str,
        job_title: str,
        company: str,
        match_score: float,
        job_url: str
    ) -> bool:
        """Send notification about a new job match"""
        
        subject = f"🎯 New {match_score:.0f}% Match: {job_title} at {company}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎯 New Job Match!</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Hi {user_name},</h2>
                
                <p style="font-size: 16px; color: #555;">
                    We found a great opportunity that matches your skills and preferences!
                </p>
                
                <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="margin-top: 0; color: #667eea;">{job_title}</h3>
                    <p style="font-size: 18px; color: #333; margin: 10px 0;">
                        <strong>{company}</strong>
                    </p>
                    <p style="font-size: 24px; color: #28a745; margin: 15px 0;">
                        <strong>{match_score:.0f}% Match</strong>
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{job_url}" style="background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        View Job Details
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #777; margin-top: 30px;">
                    <em>This job matches your skills, experience level, and career goals.</em>
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>Career Copilot - Your AI Career Intelligence Platform</p>
                <p><a href="#" style="color: #667eea;">Manage Email Preferences</a></p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        🎯 New Job Match!
        
        Hi {user_name},
        
        We found a great opportunity that matches your skills:
        
        {job_title} at {company}
        Match Score: {match_score:.0f}%
        
        View details: {job_url}
        
        This job matches your skills, experience level, and career goals.
        
        Career Copilot - Your AI Career Intelligence Platform
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

    def send_application_update(
        self,
        to_email: str,
        user_name: str,
        job_title: str,
        company: str,
        status: str,
        app_url: str
    ) -> bool:
        """Send notification about application status change"""
        
        status_emojis = {
            "screening": "👀",
            "interview": "🎤",
            "assessment": "📝",
            "offer": "🎉",
            "accepted": "✅",
            "rejected": "❌"
        }
        
        emoji = status_emojis.get(status, "📬")
        subject = f"{emoji} Application Update: {job_title}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #667eea; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">{emoji} Application Update</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Hi {user_name},</h2>
                
                <p style="font-size: 16px; color: #555;">
                    There's an update on your application:
                </p>
                
                <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="margin-top: 0; color: #667eea;">{job_title}</h3>
                    <p style="font-size: 18px; color: #333;">at <strong>{company}</strong></p>
                    <p style="font-size: 20px; color: #28a745; margin: 15px 0;">
                        Status: <strong>{status.upper()}</strong>
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}" style="background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        View Application
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>Career Copilot - Track your job search progress</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        {emoji} Application Update
        
        Hi {user_name},
        
        Your application has been updated:
        
        {job_title} at {company}
        Status: {status.upper()}
        
        View details: {app_url}
        
        Career Copilot
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

    def send_interview_reminder(
        self,
        to_email: str,
        user_name: str,
        job_title: str,
        company: str,
        interview_date: datetime,
        app_url: str
    ) -> bool:
        """Send interview reminder notification"""
        
        date_str = interview_date.strftime("%B %d, %Y at %I:%M %p")
        subject = f"🎤 Upcoming Interview: {job_title}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #28a745; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎤 Interview Reminder</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Hi {user_name},</h2>
                
                <p style="font-size: 16px; color: #555;">
                    You have an upcoming interview scheduled:
                </p>
                
                <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="margin-top: 0; color: #28a745;">{job_title}</h3>
                    <p style="font-size: 18px; color: #333;">at <strong>{company}</strong></p>
                    <p style="font-size: 20px; color: #667eea; margin: 15px 0;">
                        📅 {date_str}
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}" style="background: #28a745; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        View Interview Details
                    </a>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;">
                        <strong>💡 Tip:</strong> Review the job description and prepare questions about the role and company culture.
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>Career Copilot - Good luck with your interview!</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        🎤 Interview Reminder
        
        Hi {user_name},
        
        You have an upcoming interview:
        
        {job_title} at {company}
        Date: {date_str}
        
        View details: {app_url}
        
        💡 Tip: Review the job description and prepare questions.
        
        Good luck!
        Career Copilot
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

    def send_weekly_digest(
        self,
        to_email: str,
        user_name: str,
        new_matches_count: int,
        application_updates_count: int,
        dashboard_url: str
    ) -> bool:
        """Send weekly activity digest"""
        
        subject = f"📊 Your Weekly Career Update - {new_matches_count} New Matches"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">📊 Weekly Career Digest</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Hi {user_name},</h2>
                
                <p style="font-size: 16px; color: #555;">
                    Here's what happened this week:
                </p>
                
                <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="margin: 20px 0;">
                        <h3 style="color: #667eea; margin: 10px 0;">🎯 {new_matches_count} New Job Matches</h3>
                        <p style="color: #777;">Fresh opportunities tailored to your profile</p>
                    </div>
                    
                    <div style="margin: 20px 0; padding-top: 20px; border-top: 1px solid #eee;">
                        <h3 style="color: #667eea; margin: 10px 0;">📬 {application_updates_count} Application Updates</h3>
                        <p style="color: #777;">Status changes on your applications</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{dashboard_url}" style="background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        View Dashboard
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>Career Copilot - Your weekly career intelligence</p>
                <p><a href="#" style="color: #667eea;">Manage Email Preferences</a></p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        📊 Weekly Career Digest
        
        Hi {user_name},
        
        Here's your weekly update:
        
        🎯 {new_matches_count} New Job Matches
        📬 {application_updates_count} Application Updates
        
        View your dashboard: {dashboard_url}
        
        Career Copilot
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
