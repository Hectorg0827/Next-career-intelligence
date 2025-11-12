"""
Stripe Payment Service
Complete payment processing for subscriptions
"""

import stripe
from loguru import logger
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Stripe payment service for subscription management"""

    @staticmethod
    async def create_customer(email: str, name: str, user_id: str) -> Optional[str]:
        """
        Create a Stripe customer

        Args:
            email: Customer email
            name: Customer name
            user_id: Internal user ID

        Returns:
            Stripe customer ID or None
        """
        try:
            customer = stripe.Customer.create(email=email, name=name, metadata={"user_id": user_id})
            logger.info(f"✅ Created Stripe customer: {customer.id} for {email}")
            return customer.id
        except Exception as e:
            logger.error(f"❌ Failed to create Stripe customer: {e}")
            return None

    @staticmethod
    async def create_checkout_session(
        customer_id: str, price_id: str, success_url: str, cancel_url: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe checkout session

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            user_id: Internal user ID

        Returns:
            Checkout session data or None
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"user_id": user_id},
                allow_promotion_codes=True,
                billing_address_collection="auto",
            )
            logger.info(f"✅ Created checkout session: {session.id}")
            return {"session_id": session.id, "url": session.url}
        except Exception as e:
            logger.error(f"❌ Failed to create checkout session: {e}")
            return None

    @staticmethod
    async def create_portal_session(customer_id: str, return_url: str) -> Optional[str]:
        """
        Create a customer portal session for subscription management

        Args:
            customer_id: Stripe customer ID
            return_url: Return URL after portal session

        Returns:
            Portal session URL or None
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            logger.info(f"✅ Created portal session for customer: {customer_id}")
            return session.url
        except Exception as e:
            logger.error(f"❌ Failed to create portal session: {e}")
            return None

    @staticmethod
    async def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription details

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Subscription data or None
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan": subscription.plan.id,
                "amount": subscription.plan.amount / 100,
                "currency": subscription.plan.currency,
                "interval": subscription.plan.interval,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get subscription: {e}")
            return None

    @staticmethod
    async def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> bool:
        """
        Cancel a subscription

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Cancel at period end or immediately

        Returns:
            True if successful, False otherwise
        """
        try:
            if at_period_end:
                stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                stripe.Subscription.delete(subscription_id)
            logger.info(f"✅ Cancelled subscription: {subscription_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel subscription: {e}")
            return False

    @staticmethod
    async def reactivate_subscription(subscription_id: str) -> bool:
        """
        Reactivate a cancelled subscription

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            True if successful, False otherwise
        """
        try:
            stripe.Subscription.modify(subscription_id, cancel_at_period_end=False)
            logger.info(f"✅ Reactivated subscription: {subscription_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to reactivate subscription: {e}")
            return False

    @staticmethod
    async def handle_webhook(payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
        """
        Handle Stripe webhook events

        Args:
            payload: Raw request payload
            sig_header: Stripe signature header

        Returns:
            Event data or None
        """
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
            logger.info(f"📥 Received webhook: {event['type']}")
            return event
        except ValueError as e:
            logger.error(f"❌ Invalid webhook payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"❌ Invalid webhook signature: {e}")
            return None


# Create singleton instance
stripe_service = StripeService()
