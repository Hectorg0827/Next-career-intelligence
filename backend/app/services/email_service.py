"""
SendGrid Email Service
Handles sending verification and password reset emails
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.core.config import settings
from typing import Optional
from loguru import logger


class EmailService:
    """Email service using SendGrid"""
    
    def __init__(self):
        """Initialize SendGrid client"""
        try:
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.from_email = settings.SENDGRID_FROM_EMAIL
            logger.info(f"✅ SendGrid email service initialized (from: {self.from_email})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SendGrid: {str(e)}")
            raise
    
    async def send_verification_email(self, 
                                     email: str, 
                                     full_name: str,
                                     verification_code: str) -> bool:
        """
        Send email verification code
        
        Args:
            email: Recipient email address
            full_name: Recipient's full name
            verification_code: 6-digit verification code
            
        Returns:
            True if successful
        """
        try:
            subject = "Verify Your Email - NEXT Career Intelligence"
            
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                        .content {{ background: #f7f7f7; padding: 30px; }}
                        .code-box {{ background: white; border: 2px solid #667eea; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0; }}
                        .code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
                        .footer {{ background: #333; color: #999; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 8px 8px; }}
                        .warning {{ color: #999; font-size: 13px; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome to NEXT! 🚀</h1>
                            <p>Verify Your Email Address</p>
                        </div>
                        
                        <div class="content">
                            <p>Hi {full_name},</p>
                            
                            <p>Thanks for signing up to NEXT Career Intelligence. We're thrilled to have you on board!</p>
                            
                            <p>To complete your registration, please verify your email address using the code below:</p>
                            
                            <div class="code-box">
                                <div class="code">{verification_code}</div>
                            </div>
                            
                            <p>This code will expire in 24 hours. If you didn't create an account, please disregard this email.</p>
                            
                            <p>
                                <strong>Why verify?</strong><br>
                                Email verification helps us keep your account secure and ensures we can reach you with important updates.
                            </p>
                            
                            <p>Questions? Contact our support team at support@nextcareer.ai</p>
                        </div>
                        
                        <div class="footer">
                            <p>© 2025 NEXT Career Intelligence. All rights reserved.</p>
                            <p style="margin-top: 10px; color: #666;">This is an automated email. Please don't reply directly.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.from_email, "NEXT Career Intelligence"),
                to_emails=To(email, full_name),
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Verification email sent to {email} (Code: {verification_code[:3]}...)")
                return True
            else:
                logger.warning(f"⚠️ Unexpected SendGrid response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending verification email: {str(e)}")
            raise
    
    async def send_password_reset_email(self, 
                                       email: str, 
                                       full_name: str,
                                       reset_url: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: Recipient email address
            full_name: Recipient's full name
            reset_url: Password reset URL with token
            
        Returns:
            True if successful
        """
        try:
            subject = "Reset Your Password - NEXT Career Intelligence"
            
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                        .content {{ background: #f7f7f7; padding: 30px; }}
                        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; text-align: center; }}
                        .button:hover {{ opacity: 0.9; }}
                        .footer {{ background: #333; color: #999; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 8px 8px; }}
                        .warning {{ color: #d32f2f; font-size: 13px; margin-top: 20px; background: #ffebee; padding: 10px; border-radius: 4px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Password Reset Request 🔐</h1>
                        </div>
                        
                        <div class="content">
                            <p>Hi {full_name},</p>
                            
                            <p>We received a request to reset the password for your NEXT Career Intelligence account. Click the button below to reset your password:</p>
                            
                            <div style="text-align: center;">
                                <a href="{reset_url}" class="button">Reset Password</a>
                            </div>
                            
                            <p>Or copy and paste this link in your browser:</p>
                            <p style="word-break: break-all; color: #666; background: white; padding: 10px; border-radius: 4px; font-size: 12px;">
                                {reset_url}
                            </p>
                            
                            <div class="warning">
                                <strong>⚠️ Security Warning:</strong> This link will expire in 1 hour. If you didn't request a password reset, please ignore this email or contact support immediately.
                            </div>
                            
                            <p style="margin-top: 20px;">
                                <strong>Why did you get this email?</strong><br>
                                For security reasons, we never send passwords via email. If this wasn't you, please secure your account by changing your password immediately.
                            </p>
                            
                            <p>Questions? Contact our support team at support@nextcareer.ai</p>
                        </div>
                        
                        <div class="footer">
                            <p>© 2025 NEXT Career Intelligence. All rights reserved.</p>
                            <p style="margin-top: 10px; color: #666;">This is an automated email. Please don't reply directly.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.from_email, "NEXT Career Intelligence"),
                to_emails=To(email, full_name),
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Password reset email sent to {email}")
                return True
            else:
                logger.warning(f"⚠️ Unexpected SendGrid response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending password reset email: {str(e)}")
            raise
    
    async def send_welcome_email(self, 
                                email: str, 
                                full_name: str) -> bool:
        """
        Send welcome email after successful verification
        
        Args:
            email: Recipient email address
            full_name: Recipient's full name
            
        Returns:
            True if successful
        """
        try:
            subject = "Welcome to NEXT Career Intelligence! 🚀"
            
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                        .content {{ background: #f7f7f7; padding: 30px; }}
                        .feature {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; border-radius: 4px; }}
                        .feature-icon {{ font-size: 20px; margin-right: 10px; }}
                        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; text-align: center; }}
                        .footer {{ background: #333; color: #999; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 8px 8px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome Aboard, {full_name}! 🎉</h1>
                            <p>Your account is now verified and ready to use</p>
                        </div>
                        
                        <div class="content">
                            <p>Thanks for verifying your email! You're all set to start your career intelligence journey with NEXT.</p>
                            
                            <h2>What You Can Do Now:</h2>
                            
                            <div class="feature">
                                <span class="feature-icon">🎯</span>
                                <strong>Take a Career Scan</strong> - Analyze your current career trajectory and identify opportunities
                            </div>
                            
                            <div class="feature">
                                <span class="feature-icon">📚</span>
                                <strong>Complete Your Profile</strong> - Tell us about your skills, experience, and career goals
                            </div>
                            
                            <div class="feature">
                                <span class="feature-icon">💡</span>
                                <strong>Get AI Coaching</strong> - Receive personalized insights and recommendations
                            </div>
                            
                            <div class="feature">
                                <span class="feature-icon">🚀</span>
                                <strong>Explore Opportunities</strong> - Find courses, jobs, and learning resources tailored to you
                            </div>
                            
                            <div style="text-align: center;">
                                <a href="{settings.APP_URL}/dashboard" class="button">Go to Dashboard</a>
                            </div>
                            
                            <p style="margin-top: 20px; color: #666;">
                                <strong>Next Step:</strong> Complete your onboarding profile to unlock personalized recommendations.
                            </p>
                            
                            <p>If you have any questions, feel free to reach out to support@nextcareer.ai</p>
                        </div>
                        
                        <div class="footer">
                            <p>© 2025 NEXT Career Intelligence. All rights reserved.</p>
                            <p style="margin-top: 10px; color: #666;">This is an automated email. Please don't reply directly.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.from_email, "NEXT Career Intelligence"),
                to_emails=To(email, full_name),
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Welcome email sent to {email}")
                return True
            else:
                logger.warning(f"⚠️ Unexpected SendGrid response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending welcome email: {str(e)}")
            raise


# Create singleton instance
email_service = None


def get_email_service() -> EmailService:
    """
    Get or create email service instance
    
    Returns:
        EmailService instance
    """
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service
