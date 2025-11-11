"""
Payment Edge Case Handling
Comprehensive handling for all Stripe payment scenarios
"""

import stripe
from loguru import logger
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from app.core.config import settings
from app.services.supabase_client import get_supabase
from app.services.email_service import get_email_service
from app.core.circuit_breaker import get_circuit_breaker

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Circuit breaker for Stripe API
stripe_circuit_breaker = get_circuit_breaker(
    name="stripe",
    failure_threshold=3,
    recovery_timeout=45,
    expected_exception=stripe.error.StripeError
)


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class SubscriptionStatus(str, Enum):
    """Subscription status enum"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELLED = "cancelled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    PAUSED = "paused"


class PaymentEdgeCaseHandler:
    """Handle all payment edge cases and failure scenarios"""

    def __init__(self):
        self.supabase = get_supabase()
        self.email_service = get_email_service()

    # ==================== PAYMENT FAILURES ====================

    async def handle_payment_failed(self, payment_intent: Dict[str, Any]) -> bool:
        """
        Handle failed payment (card declined, insufficient funds, etc.)

        Edge cases:
        - Card declined
        - Insufficient funds
        - Card expired
        - Network error
        - 3D Secure failed

        Args:
            payment_intent: Stripe PaymentIntent object

        Returns:
            True if handled successfully
        """
        try:
            user_id = payment_intent['metadata'].get('user_id')
            failure_code = payment_intent.get('last_payment_error', {}).get('code', 'unknown')
            failure_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')

            logger.error(f"Payment failed for user {user_id}: {failure_code} - {failure_message}")

            # Log payment failure
            await self._log_payment_event(
                user_id=user_id,
                event_type="payment_failed",
                payment_intent_id=payment_intent['id'],
                failure_code=failure_code,
                failure_message=failure_message
            )

            # Get user details
            user = await self._get_user(user_id)
            if not user:
                return False

            # Send failure email with specific instructions
            failure_reason = self._get_user_friendly_failure_reason(failure_code)
            await self.email_service.send_payment_failed_email(
                email=user['email'],
                name=user.get('full_name', 'User'),
                failure_reason=failure_reason,
                retry_url=f"{settings.APP_URL}/subscription/retry?payment_intent={payment_intent['id']}"
            )

            # Handle specific failure codes
            if failure_code in ['card_declined', 'insufficient_funds']:
                # Retry with exponential backoff (3 attempts over 7 days)
                await self._schedule_payment_retry(
                    user_id=user_id,
                    payment_intent_id=payment_intent['id'],
                    attempt_number=1
                )

            elif failure_code == 'expired_card':
                # Prompt user to update payment method
                await self._request_payment_method_update(user_id, user['email'])

            elif failure_code in ['authentication_required', 'requires_action']:
                # 3D Secure failed - send link to complete authentication
                await self._send_authentication_link(user_id, payment_intent['id'])

            return True

        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            return False

    async def handle_subscription_past_due(self, subscription: Dict[str, Any]) -> bool:
        """
        Handle past due subscription (grace period)

        Edge cases:
        - First payment failure (grace period: 3 days)
        - Second payment failure (grace period: 7 days)
        - Third payment failure (cancel subscription)

        Args:
            subscription: Stripe Subscription object

        Returns:
            True if handled successfully
        """
        try:
            user_id = subscription['metadata'].get('user_id')
            logger.warning(f"Subscription past due for user {user_id}")

            # Get payment failure count
            failure_count = await self._get_payment_failure_count(subscription['id'])

            # Get user
            user = await self._get_user(user_id)
            if not user:
                return False

            if failure_count == 1:
                # First failure - 3 day grace period
                await self.email_service.send_email(
                    to_email=user['email'],
                    subject="Payment Failed - Your Subscription is in Grace Period",
                    template="payment_retry_reminder",
                    variables={
                        "name": user.get('full_name', 'User'),
                        "grace_period_days": 3,
                        "update_payment_url": f"{settings.APP_URL}/subscription/payment-method"
                    }
                )

            elif failure_count == 2:
                # Second failure - 7 day grace period
                await self.email_service.send_email(
                    to_email=user['email'],
                    subject="Urgent: Update Your Payment Method",
                    template="payment_urgent_reminder",
                    variables={
                        "name": user.get('full_name', 'User'),
                        "grace_period_days": 7,
                        "cancellation_date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
                        "update_payment_url": f"{settings.APP_URL}/subscription/payment-method"
                    }
                )

            elif failure_count >= 3:
                # Third failure - cancel subscription
                logger.warning(f"Cancelling subscription {subscription['id']} after 3 failures")
                await self._cancel_subscription_due_to_non_payment(subscription['id'], user_id)

            return True

        except Exception as e:
            logger.error(f"Error handling past due subscription: {e}")
            return False

    # ==================== WEBHOOK EDGE CASES ====================

    async def handle_duplicate_webhook(self, event_id: str) -> bool:
        """
        Handle duplicate webhook delivery

        Stripe may send webhooks multiple times.
        Use idempotency to prevent duplicate processing.

        Args:
            event_id: Stripe event ID

        Returns:
            True if duplicate (already processed), False if new
        """
        try:
            # Check if event already processed
            result = await self.supabase.table("stripe_events")\
                .select("id")\
                .eq("event_id", event_id)\
                .execute()

            if result.data and len(result.data) > 0:
                logger.info(f"Duplicate webhook detected: {event_id}")
                return True

            # Mark event as processed
            await self.supabase.table("stripe_events").insert({
                "event_id": event_id,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "processing"
            }).execute()

            return False

        except Exception as e:
            logger.error(f"Error checking duplicate webhook: {e}")
            return False

    async def handle_webhook_processing_failure(
        self,
        event: Dict[str, Any],
        error: Exception
    ) -> bool:
        """
        Handle webhook processing failure with retry logic

        Edge cases:
        - Database connection failure
        - Email service failure
        - Invalid webhook data

        Args:
            event: Stripe event object
            error: Exception that occurred

        Returns:
            True if retry scheduled
        """
        try:
            event_id = event['id']
            event_type = event['type']

            logger.error(f"Webhook processing failed for {event_type}: {error}")

            # Log failure
            await self.supabase.table("stripe_events").update({
                "status": "failed",
                "error_message": str(error),
                "retry_count": self.supabase.raw("retry_count + 1"),
                "next_retry_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }).eq("event_id", event_id).execute()

            # Schedule retry (max 5 attempts)
            retry_count = await self._get_webhook_retry_count(event_id)
            if retry_count < 5:
                # TODO: Implement retry queue (Celery, Bull, etc.)
                logger.info(f"Scheduling retry #{retry_count + 1} for webhook {event_id}")
                return True
            else:
                logger.error(f"Max retries exceeded for webhook {event_id}")
                # Alert dev team
                await self._alert_webhook_failure(event_id, event_type)
                return False

        except Exception as e:
            logger.error(f"Error handling webhook failure: {e}")
            return False

    # ==================== SUBSCRIPTION EDGE CASES ====================

    async def handle_subscription_downgrade_timing(
        self,
        user_id: str,
        from_plan: str,
        to_plan: str
    ) -> Dict[str, Any]:
        """
        Handle subscription downgrade timing issues

        Edge cases:
        - User downgrades mid-cycle (proration)
        - User downgrades then immediately upgrades
        - User has pending invoices

        Args:
            user_id: User ID
            from_plan: Current plan
            to_plan: New plan

        Returns:
            Dict with downgrade details
        """
        try:
            # Get current subscription
            subscription = await self._get_user_subscription(user_id)
            if not subscription:
                return {"error": "No active subscription found"}

            # Check for pending invoices
            pending_invoices = await self._get_pending_invoices(user_id)
            if pending_invoices:
                return {
                    "error": "Cannot downgrade with pending invoices",
                    "pending_invoices": pending_invoices,
                    "action_required": "Please pay pending invoices before downgrading"
                }

            # Calculate proration
            current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
            days_remaining = (current_period_end - datetime.utcnow()).days

            # Downgrade at period end (no immediate change)
            await stripe_circuit_breaker.call(
                stripe.Subscription.modify,
                subscription['id'],
                proration_behavior='none',  # No proration for downgrades
                items=[{
                    'id': subscription['items']['data'][0]['id'],
                    'price': self._get_price_id(to_plan)
                }]
            )

            logger.info(f"Scheduled downgrade for user {user_id}: {from_plan} → {to_plan}")

            return {
                "success": True,
                "effective_date": current_period_end.isoformat(),
                "days_remaining": days_remaining,
                "message": f"Your subscription will change to {to_plan} on {current_period_end.strftime('%B %d, %Y')}"
            }

        except Exception as e:
            logger.error(f"Error handling subscription downgrade: {e}")
            return {"error": str(e)}

    async def handle_proration_dispute(
        self,
        user_id: str,
        subscription_id: str
    ) -> Dict[str, Any]:
        """
        Handle user dispute about proration charges

        Edge cases:
        - User disputes unexpected charge
        - User upgrades/downgrades multiple times in same period
        - Proration calculation incorrect

        Args:
            user_id: User ID
            subscription_id: Stripe subscription ID

        Returns:
            Dict with proration details
        """
        try:
            # Get subscription history
            subscription = await stripe_circuit_breaker.call(
                stripe.Subscription.retrieve,
                subscription_id,
                expand=['latest_invoice']
            )

            # Get proration line items from latest invoice
            invoice = subscription['latest_invoice']
            proration_items = [
                item for item in invoice['lines']['data']
                if item.get('proration', False)
            ]

            # Calculate proration breakdown
            proration_breakdown = []
            for item in proration_items:
                proration_breakdown.append({
                    "description": item['description'],
                    "amount": item['amount'] / 100,
                    "period_start": datetime.fromtimestamp(item['period']['start']).isoformat(),
                    "period_end": datetime.fromtimestamp(item['period']['end']).isoformat(),
                    "proration": True
                })

            return {
                "subscription_id": subscription_id,
                "invoice_id": invoice['id'],
                "total_amount": invoice['amount_paid'] / 100,
                "proration_items": proration_breakdown,
                "explanation": "Proration charges reflect unused time on previous plan and prorated time on new plan"
            }

        except Exception as e:
            logger.error(f"Error handling proration dispute: {e}")
            return {"error": str(e)}

    # ==================== REFUND EDGE CASES ====================

    async def handle_refund_request(
        self,
        user_id: str,
        payment_intent_id: str,
        amount: Optional[float] = None,
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """
        Handle refund request with validation

        Edge cases:
        - Partial refunds
        - Refund after subscription period
        - Multiple refund requests
        - Refund limits (120 days for Stripe)

        Args:
            user_id: User ID
            payment_intent_id: Stripe PaymentIntent ID
            amount: Refund amount (None = full refund)
            reason: Refund reason

        Returns:
            Dict with refund details
        """
        try:
            # Get payment intent
            payment_intent = await stripe_circuit_breaker.call(
                stripe.PaymentIntent.retrieve,
                payment_intent_id
            )

            # Validate refund eligibility
            payment_date = datetime.fromtimestamp(payment_intent['created'])
            days_since_payment = (datetime.utcnow() - payment_date).days

            if days_since_payment > 120:
                return {
                    "error": "Refund window expired (120 days)",
                    "eligible": False,
                    "payment_date": payment_date.isoformat()
                }

            # Check if already refunded
            if payment_intent.get('amount_refunded', 0) > 0:
                refunded_amount = payment_intent['amount_refunded'] / 100
                return {
                    "error": f"Payment already partially refunded (${refunded_amount})",
                    "eligible": False,
                    "refunded_amount": refunded_amount
                }

            # Process refund
            refund_amount = amount or (payment_intent['amount'] / 100)
            refund = await stripe_circuit_breaker.call(
                stripe.Refund.create,
                payment_intent=payment_intent_id,
                amount=int(refund_amount * 100) if amount else None,
                reason=reason,
                metadata={'user_id': user_id}
            )

            logger.info(f"Refund processed for user {user_id}: ${refund_amount}")

            # Log refund
            await self._log_payment_event(
                user_id=user_id,
                event_type="refund_processed",
                payment_intent_id=payment_intent_id,
                refund_id=refund['id'],
                refund_amount=refund_amount
            )

            # Cancel subscription if full refund
            if not amount:
                subscription_id = payment_intent['metadata'].get('subscription_id')
                if subscription_id:
                    await self._cancel_subscription_with_refund(subscription_id, user_id)

            # Send refund confirmation email
            user = await self._get_user(user_id)
            await self.email_service.send_email(
                to_email=user['email'],
                subject="Refund Confirmation",
                template="refund_confirmation",
                variables={
                    "name": user.get('full_name', 'User'),
                    "refund_amount": refund_amount,
                    "refund_id": refund['id'],
                    "processing_days": "5-10 business days"
                }
            )

            return {
                "success": True,
                "refund_id": refund['id'],
                "amount": refund_amount,
                "status": refund['status'],
                "estimated_arrival": "5-10 business days"
            }

        except stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid refund request: {e}")
            return {"error": str(e), "eligible": False}
        except Exception as e:
            logger.error(f"Error processing refund: {e}")
            return {"error": str(e)}

    # ==================== DISPUTE/CHARGEBACK HANDLING ====================

    async def handle_payment_dispute(
        self,
        dispute: Dict[str, Any]
    ) -> bool:
        """
        Handle payment dispute/chargeback

        Edge cases:
        - Fraudulent charge claim
        - Product/service not received
        - Duplicate charge
        - Subscription cancelled but charged

        Args:
            dispute: Stripe Dispute object

        Returns:
            True if handled successfully
        """
        try:
            user_id = dispute['metadata'].get('user_id')
            dispute_reason = dispute.get('reason', 'unknown')
            dispute_amount = dispute['amount'] / 100

            logger.warning(f"Payment dispute for user {user_id}: {dispute_reason} (${dispute_amount})")

            # Log dispute
            await self._log_payment_event(
                user_id=user_id,
                event_type="payment_disputed",
                dispute_id=dispute['id'],
                dispute_reason=dispute_reason,
                dispute_amount=dispute_amount
            )

            # Suspend account during dispute
            await self._suspend_account(user_id, reason="payment_dispute")

            # Alert finance team
            await self._alert_payment_dispute(
                user_id=user_id,
                dispute_id=dispute['id'],
                reason=dispute_reason,
                amount=dispute_amount
            )

            # Send dispute notification to user
            user = await self._get_user(user_id)
            await self.email_service.send_email(
                to_email=user['email'],
                subject="Payment Dispute Received",
                template="dispute_notification",
                variables={
                    "name": user.get('full_name', 'User'),
                    "dispute_id": dispute['id'],
                    "amount": dispute_amount,
                    "reason": dispute_reason,
                    "support_email": "support@nextcareer.ai"
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error handling payment dispute: {e}")
            return False

    # ==================== HELPER METHODS ====================

    async def _log_payment_event(self, user_id: str, event_type: str, **kwargs) -> bool:
        """Log payment event to database"""
        try:
            await self.supabase.table("payment_events").insert({
                "user_id": user_id,
                "event_type": event_type,
                "event_data": kwargs,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error logging payment event: {e}")
            return False

    async def _get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from database"""
        try:
            result = await self.supabase.table("users")\
                .select("*")\
                .eq("id", user_id)\
                .single()\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def _get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's active subscription"""
        try:
            result = await self.supabase.table("subscriptions")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "active")\
                .single()\
                .execute()

            if result.data:
                subscription_id = result.data.get('stripe_subscription_id')
                return await stripe_circuit_breaker.call(
                    stripe.Subscription.retrieve,
                    subscription_id
                )
            return None
        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            return None

    async def _get_payment_failure_count(self, subscription_id: str) -> int:
        """Get payment failure count for subscription"""
        try:
            result = await self.supabase.table("payment_events")\
                .select("count", count='exact')\
                .eq("event_data->>subscription_id", subscription_id)\
                .eq("event_type", "payment_failed")\
                .execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error getting failure count: {e}")
            return 0

    def _get_user_friendly_failure_reason(self, failure_code: str) -> str:
        """Convert Stripe error code to user-friendly message"""
        error_messages = {
            'card_declined': 'Your card was declined. Please try a different card or contact your bank.',
            'insufficient_funds': 'Your card has insufficient funds. Please try a different card.',
            'expired_card': 'Your card has expired. Please update your payment method.',
            'incorrect_cvc': 'The CVC code was incorrect. Please check your card details.',
            'processing_error': 'A processing error occurred. Please try again.',
            'authentication_required': 'Additional authentication is required. Please complete 3D Secure verification.',
            'card_velocity_exceeded': 'You have exceeded the number of allowed transactions. Please try again later.',
            'fraudulent': 'This transaction was flagged as potentially fraudulent.',
        }
        return error_messages.get(failure_code, 'Your payment could not be processed. Please try again or use a different payment method.')

    async def _schedule_payment_retry(
        self,
        user_id: str,
        payment_intent_id: str,
        attempt_number: int
    ) -> bool:
        """Schedule automatic payment retry with exponential backoff"""
        try:
            # Calculate retry delay: 1 day, 3 days, 7 days
            retry_delays = {1: 1, 2: 3, 3: 7}
            delay_days = retry_delays.get(attempt_number, 7)

            retry_at = datetime.utcnow() + timedelta(days=delay_days)

            await self.supabase.table("payment_retries").insert({
                "user_id": user_id,
                "payment_intent_id": payment_intent_id,
                "attempt_number": attempt_number,
                "scheduled_at": retry_at.isoformat(),
                "status": "scheduled"
            }).execute()

            logger.info(f"Scheduled payment retry #{attempt_number} for {retry_at.isoformat()}")
            return True
        except Exception as e:
            logger.error(f"Error scheduling payment retry: {e}")
            return False

    async def _request_payment_method_update(self, user_id: str, email: str) -> bool:
        """Send email requesting payment method update"""
        try:
            await self.email_service.send_email(
                to_email=email,
                subject="Please Update Your Payment Method",
                template="payment_method_update",
                variables={
                    "update_url": f"{settings.APP_URL}/subscription/payment-method",
                    "support_email": "support@nextcareer.ai"
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error requesting payment method update: {e}")
            return False

    async def _send_authentication_link(self, user_id: str, payment_intent_id: str) -> bool:
        """Send link to complete 3D Secure authentication"""
        try:
            payment_intent = await stripe_circuit_breaker.call(
                stripe.PaymentIntent.retrieve,
                payment_intent_id
            )

            auth_url = payment_intent.get('next_action', {}).get('redirect_to_url', {}).get('url')
            if not auth_url:
                return False

            user = await self._get_user(user_id)
            await self.email_service.send_email(
                to_email=user['email'],
                subject="Complete Payment Authentication",
                template="payment_authentication",
                variables={
                    "name": user.get('full_name', 'User'),
                    "auth_url": auth_url
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error sending authentication link: {e}")
            return False

    async def _cancel_subscription_due_to_non_payment(
        self,
        subscription_id: str,
        user_id: str
    ) -> bool:
        """Cancel subscription after multiple payment failures"""
        try:
            await stripe_circuit_breaker.call(
                stripe.Subscription.delete,
                subscription_id
            )

            await self.supabase.table("subscriptions").update({
                "status": "cancelled",
                "cancellation_reason": "non_payment",
                "cancelled_at": datetime.utcnow().isoformat()
            }).eq("stripe_subscription_id", subscription_id).execute()

            user = await self._get_user(user_id)
            await self.email_service.send_email(
                to_email=user['email'],
                subject="Your Subscription Has Been Cancelled",
                template="subscription_cancelled_nonpayment",
                variables={
                    "name": user.get('full_name', 'User'),
                    "reactivate_url": f"{settings.APP_URL}/subscription/reactivate"
                }
            )

            return True
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False

    async def _cancel_subscription_with_refund(
        self,
        subscription_id: str,
        user_id: str
    ) -> bool:
        """Cancel subscription with refund"""
        try:
            await stripe_circuit_breaker.call(
                stripe.Subscription.delete,
                subscription_id
            )

            await self.supabase.table("subscriptions").update({
                "status": "cancelled",
                "cancellation_reason": "refund",
                "cancelled_at": datetime.utcnow().isoformat()
            }).eq("stripe_subscription_id", subscription_id).execute()

            return True
        except Exception as e:
            logger.error(f"Error cancelling subscription with refund: {e}")
            return False

    async def _suspend_account(self, user_id: str, reason: str) -> bool:
        """Suspend user account"""
        try:
            await self.supabase.table("users").update({
                "account_status": "suspended",
                "suspension_reason": reason,
                "suspended_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error suspending account: {e}")
            return False

    async def _get_pending_invoices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending invoices for user"""
        try:
            subscription = await self._get_user_subscription(user_id)
            if not subscription:
                return []

            invoices = await stripe_circuit_breaker.call(
                stripe.Invoice.list,
                customer=subscription['customer'],
                status='open'
            )

            return invoices['data']
        except Exception as e:
            logger.error(f"Error getting pending invoices: {e}")
            return []

    async def _get_webhook_retry_count(self, event_id: str) -> int:
        """Get webhook retry count"""
        try:
            result = await self.supabase.table("stripe_events")\
                .select("retry_count")\
                .eq("event_id", event_id)\
                .single()\
                .execute()
            return result.data.get('retry_count', 0) if result.data else 0
        except Exception as e:
            logger.error(f"Error getting retry count: {e}")
            return 0

    async def _alert_webhook_failure(self, event_id: str, event_type: str) -> bool:
        """Alert dev team about webhook failure"""
        try:
            # Send to Sentry
            from app.core.monitoring import capture_exception
            capture_exception(
                Exception(f"Webhook max retries exceeded: {event_type}"),
                {"webhook": {"event_id": event_id, "event_type": event_type}}
            )
            return True
        except Exception as e:
            logger.error(f"Error alerting webhook failure: {e}")
            return False

    async def _alert_payment_dispute(
        self,
        user_id: str,
        dispute_id: str,
        reason: str,
        amount: float
    ) -> bool:
        """Alert finance team about payment dispute"""
        try:
            from app.core.monitoring import capture_exception
            capture_exception(
                Exception(f"Payment dispute: {reason}"),
                {
                    "dispute": {
                        "user_id": user_id,
                        "dispute_id": dispute_id,
                        "reason": reason,
                        "amount": amount
                    }
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error alerting payment dispute: {e}")
            return False

    def _get_price_id(self, plan: str) -> str:
        """Get Stripe price ID for plan"""
        price_ids = {
            'pro_monthly': settings.STRIPE_PRICE_ID_PRO_MONTHLY,
            'pro_yearly': settings.STRIPE_PRICE_ID_PRO_YEARLY,
            'enterprise': settings.STRIPE_PRICE_ID_ENTERPRISE
        }
        return price_ids.get(plan, '')


# Create singleton instance
payment_edge_case_handler = PaymentEdgeCaseHandler()
