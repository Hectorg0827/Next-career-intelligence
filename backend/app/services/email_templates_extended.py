"""
Extended Email Service Methods
Additional email types using HTML templates
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from app.core.config import settings
from app.services.email_template_renderer import get_template_renderer
from typing import Optional, Dict, Any, List
from loguru import logger
from datetime import datetime, timedelta


class ExtendedEmailService:
    """Extended email methods using HTML templates"""

    def __init__(self, sendgrid_client: SendGridAPIClient, from_email: str):
        """
        Initialize extended email service

        Args:
            sendgrid_client: SendGrid API client instance
            from_email: Sender email address
        """
        self.client = sendgrid_client
        self.from_email = from_email
        self.renderer = get_template_renderer()

    async def send_payment_confirmation(
        self,
        email: str,
        user_name: str,
        plan_name: str,
        amount_paid: float,
        currency: str = "USD",
        card_last4: str = "****",
        transaction_id: str = "",
        billing_period: str = "Monthly",
        features: List[str] = None,
    ) -> bool:
        """
        Send payment confirmation email

        Args:
            email: Recipient email
            user_name: User's name
            plan_name: Subscription plan name
            amount_paid: Amount charged
            currency: Currency code
            card_last4: Last 4 digits of card
            transaction_id: Payment transaction ID
            billing_period: Billing period (Monthly/Yearly)
            features: List of features included

        Returns:
            True if sent successfully
        """
        try:
            subject = f"Payment Confirmation - {plan_name} Plan"

            # Prepare features list HTML
            if features is None:
                features = [
                    "Unlimited resume tailoring",
                    "AI career coaching",
                    "Mock interview practice",
                    "Premium job recommendations",
                ]

            features_html = self.renderer.render_list_items(features)

            # Calculate next billing date
            next_billing = (datetime.now() + timedelta(days=30 if billing_period == "Monthly" else 365)).strftime(
                "%B %d, %Y"
            )

            html_content = self.renderer.render_template(
                "payment_confirmation",
                {
                    "user_name": user_name,
                    "plan_name": plan_name,
                    "billing_period": billing_period,
                    "card_last4": card_last4,
                    "transaction_id": transaction_id or "N/A",
                    "payment_date": datetime.now().strftime("%B %d, %Y"),
                    "next_billing_date": next_billing,
                    "amount_paid": f"{amount_paid:.2f}",
                    "currency": currency,
                    "features_list": features_html,
                    "dashboard_url": f"{settings.APP_URL}/dashboard",
                    "billing_url": f"{settings.APP_URL}/settings/billing",
                },
            )

            message = Mail(
                from_email=Email(self.from_email, "NEXT Billing"),
                to_emails=To(email, user_name),
                subject=subject,
                html_content=html_content,
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Payment confirmation sent to {email}")
                return True
            else:
                logger.warning(f"⚠️ Unexpected SendGrid response: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending payment confirmation: {e}")
            raise

    async def send_payment_failed(
        self,
        email: str,
        user_name: str,
        plan_name: str,
        amount: float,
        currency: str = "USD",
        failure_reason: str = "Card declined",
        next_attempt_date: Optional[str] = None,
        retry_days: int = 3,
    ) -> bool:
        """
        Send payment failure notification

        Args:
            email: Recipient email
            user_name: User's name
            plan_name: Subscription plan
            amount: Failed payment amount
            currency: Currency code
            failure_reason: Reason for failure
            next_attempt_date: Date of next retry
            retry_days: Days until next retry

        Returns:
            True if sent successfully
        """
        try:
            subject = "Payment Failed - Action Required"

            if next_attempt_date is None:
                next_attempt_date = (datetime.now() + timedelta(days=retry_days)).strftime("%B %d, %Y")

            downgrade_date = (datetime.now() + timedelta(days=14)).strftime("%B %d, %Y")

            html_content = self.renderer.render_template(
                "payment_failed",
                {
                    "user_name": user_name,
                    "plan_name": plan_name,
                    "amount": f"{amount:.2f}",
                    "currency": currency,
                    "payment_date": datetime.now().strftime("%B %d, %Y"),
                    "failure_reason": failure_reason,
                    "next_attempt_date": next_attempt_date,
                    "retry_days": retry_days,
                    "downgrade_date": downgrade_date,
                    "update_payment_url": f"{settings.APP_URL}/settings/billing",
                },
            )

            message = Mail(
                from_email=Email(self.from_email, "NEXT Billing"),
                to_emails=To(email, user_name),
                subject=subject,
                html_content=html_content,
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Payment failed notification sent to {email}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error sending payment failed email: {e}")
            raise

    async def send_subscription_changed(
        self,
        email: str,
        user_name: str,
        old_plan: str,
        new_plan: str,
        old_price: float,
        new_price: float,
        change_type: str = "Upgrade",  # or "Downgrade"
        new_features: List[str] = None,
        proration_amount: Optional[float] = None,
    ) -> bool:
        """Send subscription change notification"""
        try:
            subject = f"Subscription {change_type}d - {new_plan}"

            if new_features is None:
                new_features = []

            features_html = (
                self.renderer.render_list_items(new_features) if new_features else "<li>All previous features</li>"
            )

            proration_msg = ""
            if proration_amount:
                proration_msg = (
                    f"<p><strong>Prorated Credit:</strong> ${proration_amount:.2f} applied to your next invoice</p>"
                )

            html_content = self.renderer.render_template(
                "subscription_changed",
                {
                    "user_name": user_name,
                    "change_type": change_type,
                    "change_type_lower": change_type.lower(),
                    "old_plan": old_plan,
                    "new_plan": new_plan,
                    "old_price": f"{old_price:.2f}",
                    "new_price": f"{new_price:.2f}",
                    "effective_date": datetime.now().strftime("%B %d, %Y"),
                    "next_billing_date": (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y"),
                    "proration_message": proration_msg,
                    "new_features": features_html,
                    "dashboard_url": f"{settings.APP_URL}/dashboard",
                    "billing_url": f"{settings.APP_URL}/settings/billing",
                },
            )

            message = Mail(
                from_email=Email(self.from_email, "NEXT Team"),
                to_emails=To(email, user_name),
                subject=subject,
                html_content=html_content,
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Subscription change notification sent to {email}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error sending subscription change email: {e}")
            raise

    async def send_weekly_digest(
        self,
        email: str,
        user_name: str,
        week_stats: Dict[str, int],
        recommended_jobs: List[Dict[str, str]],
        recommended_courses: List[Dict[str, str]],
        career_health_score: int,
        ai_recommendations: str,
    ) -> bool:
        """Send weekly career digest email"""
        try:
            subject = f"Your Weekly Career Digest - Week of {datetime.now().strftime('%b %d')}"

            # Render job cards
            jobs_html = (
                self.renderer.render_card_list(recommended_jobs)
                if recommended_jobs
                else "<p>No new jobs this week.</p>"
            )

            # Render course cards
            courses_html = (
                self.renderer.render_card_list(recommended_courses)
                if recommended_courses
                else "<p>Complete your profile to get course recommendations.</p>"
            )

            # Health score trend
            health_trend = (
                "↗️ Improving"
                if career_health_score >= 70
                else "→ Stable" if career_health_score >= 50 else "↘️ Needs attention"
            )

            html_content = self.renderer.render_template(
                "weekly_digest",
                {
                    "user_name": user_name,
                    "week_range": f"{(datetime.now() - timedelta(days=7)).strftime('%b %d')} - {datetime.now().strftime('%b %d, %Y')}",
                    "applications_count": week_stats.get("applications", 0),
                    "interviews_count": week_stats.get("interviews", 0),
                    "jobs_saved": week_stats.get("saved_jobs", 0),
                    "recommended_jobs": jobs_html,
                    "recommended_courses": courses_html,
                    "career_health_score": career_health_score,
                    "health_score_trend": health_trend,
                    "ai_recommendations": ai_recommendations,
                    "dashboard_url": f"{settings.APP_URL}/dashboard",
                    "unsubscribe_url": f"{settings.APP_URL}/settings/notifications",
                },
            )

            message = Mail(
                from_email=Email(self.from_email, "NEXT Career Digest"),
                to_emails=To(email, user_name),
                subject=subject,
                html_content=html_content,
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Weekly digest sent to {email}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error sending weekly digest: {e}")
            raise

    async def send_interview_reminder(
        self,
        email: str,
        user_name: str,
        interview_date: str,
        interview_time: str,
        interview_type: str,
        duration: int = 45,
        focus_area: str = "Behavioral Questions",
        interview_url: str = "",
    ) -> bool:
        """Send mock interview reminder"""
        try:
            subject = f"Mock Interview Reminder - {interview_type}"

            html_content = self.renderer.render_template(
                "interview_reminder",
                {
                    "user_name": user_name,
                    "interview_date": interview_date,
                    "interview_time": interview_time,
                    "interview_type": interview_type,
                    "duration": duration,
                    "focus_area": focus_area,
                    "interview_url": interview_url or f"{settings.APP_URL}/interview",
                    "reschedule_url": f"{settings.APP_URL}/interview/reschedule",
                },
            )

            message = Mail(
                from_email=Email(self.from_email, "NEXT Interview Prep"),
                to_emails=To(email, user_name),
                subject=subject,
                html_content=html_content,
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Interview reminder sent to {email}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error sending interview reminder: {e}")
            raise

    async def send_resume_feedback(
        self,
        email: str,
        user_name: str,
        job_title: str,
        ats_score: int,
        strengths: List[str],
        improvements: List[str],
        recommendations: str,
    ) -> bool:
        """Send resume analysis feedback"""
        try:
            subject = f"Your Resume Analysis for {job_title}"

            score_interpretation = (
                "Excellent! Your resume is highly optimized."
                if ats_score >= 80
                else (
                    "Good, but there's room for improvement."
                    if ats_score >= 60
                    else "Needs work to pass ATS screening."
                )
            )

            strengths_html = self.renderer.render_list_items(strengths)
            improvements_html = self.renderer.render_list_items(improvements)

            html_content = self.renderer.render_template(
                "resume_feedback",
                {
                    "user_name": user_name,
                    "job_title": job_title,
                    "ats_score": ats_score,
                    "score_interpretation": score_interpretation,
                    "strengths_list": strengths_html,
                    "improvements_list": improvements_html,
                    "recommendations": recommendations,
                    "resume_url": f"{settings.APP_URL}/resume-studio",
                },
            )

            message = Mail(
                from_email=Email(self.from_email, "NEXT Resume Studio"),
                to_emails=To(email, user_name),
                subject=subject,
                html_content=html_content,
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Resume feedback sent to {email}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error sending resume feedback: {e}")
            raise

    async def send_feature_announcement(
        self,
        email: str,
        user_name: str,
        feature_name: str,
        tagline: str,
        feature_description: str,
        features: List[Dict[str, str]],
        benefits_description: str,
        cta_description: str,
        feature_url: str,
    ) -> bool:
        """Send new feature announcement"""
        try:
            subject = f"🚀 New Feature: {feature_name}"

            # Render feature cards
            features_html = ""
            for feature in features:
                features_html += f"""
                <div class="feature-card">
                    <div class="feature-icon">{feature.get('icon', '✨')}</div>
                    <div class="feature-title">{feature['title']}</div>
                    <div class="feature-desc">{feature['description']}</div>
                </div>
                """

            html_content = self.renderer.render_template(
                "feature_announcement",
                {
                    "user_name": user_name,
                    "feature_name": feature_name,
                    "tagline": tagline,
                    "value_proposition": "navigate your career with confidence",
                    "feature_description": feature_description,
                    "features_html": features_html,
                    "benefits_description": benefits_description,
                    "cta_description": cta_description,
                    "feature_url": feature_url,
                    "docs_url": f"{settings.APP_URL}/help",
                    "tutorial_url": f"{settings.APP_URL}/tutorials/{feature_name.lower()}",
                    "unsubscribe_url": f"{settings.APP_URL}/settings/notifications",
                },
            )

            message = Mail(
                from_email=Email(self.from_email, "NEXT Product Team"),
                to_emails=To(email, user_name),
                subject=subject,
                html_content=html_content,
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Feature announcement sent to {email}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error sending feature announcement: {e}")
            raise
