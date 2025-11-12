"""
Stripe Subscription Management
Handles subscription creation, updates, and webhooks
"""

import stripe
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Subscription tiers and pricing
SUBSCRIPTION_PLANS = {
    "premium": {
        "name": "Premium",
        "price_monthly": 2900,  # $29.00 in cents
        "price_yearly": 29000,  # $290.00 in cents (save ~17%)
        "features": [
            "Unlimited Resume Studio access",
            "Unlimited Career Coach sessions",
            "Unlimited Interview practice",
            "Career goal tracking",
            "AI-powered suggestions",
            "Priority support",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 9900,  # $99.00 in cents
        "price_yearly": 99000,  # $990.00 in cents
        "features": [
            "All Premium features",
            "Team management",
            "Custom integrations",
            "Dedicated account manager",
            "API access",
            "Advanced analytics",
        ],
    },
}


class StripeManager:
    """Manage Stripe subscriptions and payments"""

    @staticmethod
    async def create_checkout_session(
        user_id: str,
        email: str,
        plan: str,
        billing_period: str = "monthly",
        success_url: str = None,
        cancel_url: str = None,
    ) -> Dict[str, Any]:
        """
        Create Stripe Checkout session for subscription

        Args:
            user_id: User's Firebase UID
            email: User's email
            plan: 'premium' or 'enterprise'
            billing_period: 'monthly' or 'yearly'
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel

        Returns:
            Dict with checkout session details
        """
        if not stripe.api_key:
            logger.warning("⚠️ Stripe not configured")
            return {"error": "Payment system not configured"}

        try:
            # Get price ID based on plan and billing period
            price_id = os.getenv(f"STRIPE_PRICE_{plan.upper()}_{billing_period.upper()}")

            if not price_id:
                raise ValueError(f"Price ID not configured for {plan} {billing_period}")

            # Create checkout session
            session = stripe.checkout.Session.create(
                customer_email=email,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url
                or f"{os.getenv('FRONTEND_URL')}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=cancel_url or f"{os.getenv('FRONTEND_URL')}/subscription/cancel",
                metadata={"user_id": user_id, "plan": plan, "billing_period": billing_period},
                subscription_data={"metadata": {"user_id": user_id, "plan": plan}},
            )

            logger.info(f"✅ Created checkout session for {email} - {plan}")

            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "plan": plan,
                "billing_period": billing_period,
            }

        except Exception as e:
            logger.error(f"❌ Checkout session creation failed: {e}")
            return {"error": str(e)}

    @staticmethod
    async def create_customer_portal_session(customer_id: str, return_url: str = None) -> Dict[str, Any]:
        """
        Create Stripe Customer Portal session for managing subscription

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session

        Returns:
            Dict with portal URL
        """
        if not stripe.api_key:
            return {"error": "Payment system not configured"}

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id, return_url=return_url or f"{os.getenv('FRONTEND_URL')}/subscription"
            )

            return {"portal_url": session.url}

        except Exception as e:
            logger.error(f"❌ Portal session creation failed: {e}")
            return {"error": str(e)}

    @staticmethod
    async def handle_checkout_completed(session: Dict[str, Any]) -> bool:
        """
        Handle successful checkout completion
        Updates user's subscription in database

        Args:
            session: Stripe checkout session object

        Returns:
            Success boolean
        """
        from app.db.supabase import get_supabase_client

        try:
            user_id = session["metadata"]["user_id"]
            plan = session["metadata"]["plan"]
            subscription_id = session["subscription"]
            customer_id = session["customer"]

            # Get subscription details from Stripe
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Calculate expiry date
            expires_at = datetime.fromtimestamp(subscription.current_period_end)

            # Update database
            client = get_supabase_client()
            if not client:
                logger.error("Database unavailable")
                return False

            # Upsert subscription
            result = (
                client.table("subscriptions")
                .upsert(
                    {
                        "user_id": user_id,
                        "tier": plan,
                        "status": "active",
                        "stripe_subscription_id": subscription_id,
                        "stripe_customer_id": customer_id,
                        "started_at": datetime.utcnow().isoformat(),
                        "expires_at": expires_at.isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .execute()
            )

            logger.info(f"✅ Subscription activated for user {user_id} - {plan}")
            return True

        except Exception as e:
            logger.error(f"❌ Checkout completion handler failed: {e}")
            return False

    @staticmethod
    async def handle_subscription_updated(subscription: Dict[str, Any]) -> bool:
        """
        Handle subscription update webhook
        """
        from app.db.supabase import get_supabase_client

        try:
            user_id = subscription["metadata"].get("user_id")
            if not user_id:
                logger.warning("Subscription missing user_id in metadata")
                return False

            status_map = {
                "active": "active",
                "past_due": "active",  # Grace period
                "unpaid": "cancelled",
                "canceled": "cancelled",
                "incomplete": "cancelled",
                "incomplete_expired": "cancelled",
                "trialing": "active",
            }

            status = status_map.get(subscription["status"], "cancelled")
            expires_at = datetime.fromtimestamp(subscription["current_period_end"])

            client = get_supabase_client()
            if not client:
                return False

            client.table("subscriptions").update(
                {"status": status, "expires_at": expires_at.isoformat(), "updated_at": datetime.utcnow().isoformat()}
            ).eq("stripe_subscription_id", subscription["id"]).execute()

            logger.info(f"✅ Subscription updated for user {user_id} - {status}")
            return True

        except Exception as e:
            logger.error(f"❌ Subscription update handler failed: {e}")
            return False

    @staticmethod
    async def handle_subscription_deleted(subscription: Dict[str, Any]) -> bool:
        """
        Handle subscription cancellation webhook
        """
        from app.db.supabase import get_supabase_client

        try:
            user_id = subscription["metadata"].get("user_id")
            if not user_id:
                return False

            client = get_supabase_client()
            if not client:
                return False

            client.table("subscriptions").update(
                {
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("stripe_subscription_id", subscription["id"]).execute()

            logger.info(f"✅ Subscription cancelled for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Subscription deletion handler failed: {e}")
            return False

    @staticmethod
    async def get_user_subscription(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's current subscription details

        Args:
            user_id: User's Firebase UID

        Returns:
            Subscription dict or None
        """
        from app.db.supabase import get_supabase_client

        try:
            client = get_supabase_client()
            if not client:
                return None

            response = client.table("subscriptions").select("*").eq("user_id", user_id).single().execute()

            return response.data if response.data else None

        except Exception as e:
            logger.error(f"Get subscription error: {e}")
            return None

    @staticmethod
    async def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> bool:
        """
        Cancel a subscription

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at end of billing period

        Returns:
            Success boolean
        """
        if not stripe.api_key:
            return False

        try:
            if at_period_end:
                # Cancel at end of period (user keeps access until expiry)
                stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                # Cancel immediately
                stripe.Subscription.delete(subscription_id)

            logger.info(f"✅ Subscription cancelled: {subscription_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Subscription cancellation failed: {e}")
            return False


# Webhook endpoint will use these handlers
stripe_manager = StripeManager()
