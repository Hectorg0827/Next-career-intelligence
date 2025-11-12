"""
Subscription Management API
Handles subscription plans, billing, and access control
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
import uuid
import stripe

from pydantic import BaseModel
from app.db.supabase import get_supabase_client
from app.core.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# Models
class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionRequest(BaseModel):
    user_id: str
    plan_id: str
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    payment_method_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    subscription_id: str
    user_id: str
    plan_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    price: float
    billing_cycle: str
    features: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PlanResponse(BaseModel):
    id: str
    name: str
    price: float
    period: str
    features: List[str]
    limits: Dict[str, Any]


# Router
router = APIRouter(prefix="/subscription", tags=["Subscription Management"])

# Plan definitions
PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "period": "monthly",
        "features": [
            "5 career analyses per month",
            "Basic job search",
            "2 interview practice sessions",
            "Community access",
        ],
        "limits": {
            "analyses_per_month": 5,
            "job_searches_per_day": 10,
            "interview_sessions_per_month": 2,
            "api_calls_per_day": 100,
        },
    },
    "pro": {
        "name": "Pro",
        "price_monthly": 29.99,
        "price_yearly": 299.99,
        "features": [
            "Unlimited career analyses",
            "Advanced job search with AI matching",
            "Unlimited interview practice",
            "24/7 career coach access",
            "Monthly skill assessment",
            "Priority email support",
            "Resume optimization tool",
            "Salary negotiation guide",
        ],
        "limits": {
            "analyses_per_month": float("inf"),
            "job_searches_per_day": float("inf"),
            "interview_sessions_per_month": float("inf"),
            "api_calls_per_day": 10000,
        },
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 99.99,
        "price_yearly": 999.99,
        "features": [
            "Everything in Pro",
            "Team management",
            "Custom training programs",
            "Dedicated account manager",
            "24/7 phone support",
            "API access",
            "Advanced analytics",
            "Custom integrations",
        ],
        "limits": {
            "analyses_per_month": float("inf"),
            "job_searches_per_day": float("inf"),
            "interview_sessions_per_month": float("inf"),
            "api_calls_per_day": float("inf"),
        },
    },
}

# API Endpoints


@router.get("/plans", response_model=List[PlanResponse])
async def get_available_plans():
    """Get all available subscription plans"""
    try:
        plans = []
        for plan_id, plan_data in PLANS.items():
            plans.append(
                PlanResponse(
                    id=plan_id,
                    name=plan_data["name"],
                    price=plan_data.get("price", plan_data.get("price_monthly", 0)),
                    period=plan_data.get("period", "monthly"),
                    features=plan_data.get("features", []),
                    limits=plan_data.get("limits", {}),
                )
            )
        return plans
    except Exception as e:
        logger.error(f"Failed to get plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch subscription plans"
        )


@router.get("/current/{user_id}", response_model=Optional[SubscriptionResponse])
async def get_current_subscription(user_id: str):
    """Get current subscription for a user"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(500, "Database connection failed")

        response = (
            client.table("subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            # User is on free plan by default
            return SubscriptionResponse(
                subscription_id="",
                user_id=user_id,
                plan_id="free",
                status="active",
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                price=0,
                billing_cycle="monthly",
                features=PLANS["free"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

        subscription = response.data[0]
        plan_data = PLANS.get(subscription.get("plan_id", "free"), PLANS["free"])

        return SubscriptionResponse(
            subscription_id=subscription["id"],
            user_id=subscription["user_id"],
            plan_id=subscription["plan_id"],
            status=subscription["status"],
            current_period_start=datetime.fromisoformat(subscription["current_period_start"]),
            current_period_end=datetime.fromisoformat(subscription["current_period_end"]),
            price=subscription.get("price", 0),
            billing_cycle=subscription.get("billing_cycle", "monthly"),
            features=plan_data,
            created_at=datetime.fromisoformat(subscription["created_at"]),
            updated_at=datetime.fromisoformat(subscription["updated_at"]),
        )

    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch subscription")


@router.post("/upgrade")
async def upgrade_subscription(request: SubscriptionRequest):
    """Upgrade or change subscription plan"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(500, "Database connection failed")

        if request.plan_id not in PLANS:
            raise HTTPException(400, f"Invalid plan: {request.plan_id}")

        # Get plan pricing
        plan = PLANS[request.plan_id]
        price = plan.get("price", 0)  # Free plan
        if request.billing_cycle == BillingCycle.MONTHLY:
            price = plan.get("price_monthly", price)
        else:
            price = plan.get("price_yearly", price)

        # Create new subscription
        subscription_id = str(uuid.uuid4())
        now = datetime.utcnow()
        period_end = now + (timedelta(days=365) if request.billing_cycle == BillingCycle.YEARLY else timedelta(days=30))

        new_subscription = {
            "id": subscription_id,
            "user_id": request.user_id,
            "plan_id": request.plan_id,
            "status": "active",
            "current_period_start": now.isoformat(),
            "current_period_end": period_end.isoformat(),
            "price": price,
            "billing_cycle": request.billing_cycle,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        # Insert subscription
        response = client.table("subscriptions").insert([new_subscription]).execute()

        logger.info(f"User {request.user_id} upgraded to {request.plan_id}")

        return {
            "status": "success",
            "message": f"Successfully upgraded to {plan['name']} plan",
            "subscription_id": subscription_id,
        }

    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upgrade subscription")


@router.post("/cancel/{user_id}")
async def cancel_subscription(user_id: str):
    """Cancel user subscription"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(500, "Database connection failed")

        # Update active subscription to canceled
        response = (
            client.table("subscriptions")
            .update({"status": "canceled", "updated_at": datetime.utcnow().isoformat()})
            .eq("user_id", user_id)
            .eq("status", "active")
            .execute()
        )

        logger.info(f"Subscription canceled for user {user_id}")

        return {"status": "success", "message": "Subscription canceled successfully"}

    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel subscription")


@router.get("/usage/{user_id}")
async def get_usage(user_id: str):
    """Get current usage for a user"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(500, "Database connection failed")

        # Get current subscription
        sub_response = (
            client.table("subscriptions").select("*").eq("user_id", user_id).eq("status", "active").single().execute()
        )

        subscription = sub_response.data if sub_response.data else None
        plan_id = subscription.get("plan_id", "free") if subscription else "free"
        plan = PLANS.get(plan_id, PLANS["free"])
        limits = plan.get("limits", {})

        # Get current usage
        today = datetime.utcnow().date()

        analyses_response = (
            client.table("analyses")
            .select("count", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", f"{today}T00:00:00")
            .execute()
        )
        analyses_count = analyses_response.count or 0

        # Calculate monthly
        month_start = today.replace(day=1)
        monthly_analyses_response = (
            client.table("analyses")
            .select("count", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", f"{month_start}T00:00:00")
            .execute()
        )
        monthly_analyses_count = monthly_analyses_response.count or 0

        return {
            "plan_id": plan_id,
            "plan_name": plan.get("name", "Free"),
            "limits": limits,
            "usage": {
                "analyses_today": analyses_count,
                "analyses_this_month": monthly_analyses_count,
                "api_calls_today": 0,  # TODO: Implement API call tracking
            },
            "usage_percentage": {
                "analyses_monthly": (
                    min(100, (monthly_analyses_count / limits.get("analyses_per_month", 5)) * 100)
                    if limits.get("analyses_per_month") != float("inf")
                    else 0
                ),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch usage information"
        )


@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,
    billing_cycle: str,
    user_id: str,
    success_url: str = "http://localhost:3000/subscription/success",
    cancel_url: str = "http://localhost:3000/subscription",
):
    """
    Create a Stripe checkout session for subscription upgrade
    """
    try:
        if not stripe.api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment processing not configured"
            )

        # Map plan and billing cycle to Stripe price
        price_mapping = {
            "pro_monthly": settings.STRIPE_PRICE_ID_PRO_MONTHLY or "price_pro_monthly",
            "pro_yearly": settings.STRIPE_PRICE_ID_PRO_YEARLY or "price_pro_yearly",
            "enterprise_monthly": settings.STRIPE_PRICE_ID_ENTERPRISE or "price_enterprise",
        }

        price_key = f"{plan}_{billing_cycle}"
        price_id = price_mapping.get(price_key)

        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid plan/billing combination: {price_key}"
            )

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            client_reference_id=user_id,
            metadata={"user_id": user_id, "plan": plan, "billing_cycle": billing_cycle},
        )

        logger.info(f"Created checkout session for user {user_id}: {checkout_session.id}")

        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Payment processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create checkout session"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events with signature verification

    Security: Validates webhook signature to prevent spoofed events
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        # Check webhook secret configuration
        if not settings.STRIPE_WEBHOOK_SECRET:
            # Production: Fail fast if webhook secret not configured
            if settings.ENVIRONMENT == "production":
                logger.error("❌ STRIPE_WEBHOOK_SECRET not configured in production")
                raise HTTPException(status_code=503, detail="Webhook not configured")

            # Development: Allow without signature verification with warning
            logger.warning("⚠️ Stripe webhook processing without signature verification (DEV MODE ONLY)")
            event = stripe.Event.construct_from(await request.json(), stripe.api_key)
        else:
            # Verify webhook signature
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
                logger.info(f"✅ Webhook signature verified: {event['type']}")
            except ValueError as e:
                # Invalid payload
                logger.error(f"❌ Invalid webhook payload: {e}")
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError as e:
                # Invalid signature
                logger.error(f"❌ Invalid webhook signature: {e}")
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            await handle_successful_payment(session)

        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            await handle_subscription_update(subscription)

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            await handle_subscription_cancellation(subscription)

        return JSONResponse(content={"status": "success"})

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def handle_successful_payment(session: Dict):
    """Handle successful payment from Stripe checkout"""
    try:
        user_id = session.get("client_reference_id") or session["metadata"].get("user_id")
        plan = session["metadata"].get("plan")
        billing_cycle = session["metadata"].get("billing_cycle")

        supabase = get_supabase_client()
        if not supabase:
            logger.error("Supabase client not available")
            return

        # Update user subscription in database
        now = datetime.utcnow()
        period_end = now + timedelta(days=365 if billing_cycle == "yearly" else 30)

        supabase.table("user_subscriptions").upsert(
            {
                "user_id": user_id,
                "plan_id": plan,
                "status": "active",
                "stripe_subscription_id": session.get("subscription"),
                "stripe_customer_id": session.get("customer"),
                "current_period_start": now.isoformat(),
                "current_period_end": period_end.isoformat(),
                "billing_cycle": billing_cycle,
                "updated_at": now.isoformat(),
            }
        ).execute()

        logger.info(f"Updated subscription for user {user_id} to {plan}")

    except Exception as e:
        logger.error(f"Failed to handle successful payment: {e}")


async def handle_subscription_update(subscription: Dict):
    """Handle subscription update webhook"""
    try:
        customer_id = subscription.get("customer")
        status = subscription.get("status")

        supabase = get_supabase_client()
        if not supabase:
            return

        # Update subscription status in database
        supabase.table("user_subscriptions").update({"status": status, "updated_at": datetime.utcnow().isoformat()}).eq(
            "stripe_customer_id", customer_id
        ).execute()

        logger.info(f"Updated subscription status for customer {customer_id}: {status}")

    except Exception as e:
        logger.error(f"Failed to handle subscription update: {e}")


async def handle_subscription_cancellation(subscription: Dict):
    """Handle subscription cancellation webhook"""
    try:
        customer_id = subscription.get("customer")

        supabase = get_supabase_client()
        if not supabase:
            return

        # Downgrade to free plan
        supabase.table("user_subscriptions").update(
            {"plan_id": "free", "status": "cancelled", "updated_at": datetime.utcnow().isoformat()}
        ).eq("stripe_customer_id", customer_id).execute()

        logger.info(f"Cancelled subscription for customer {customer_id}")

    except Exception as e:
        logger.error(f"Failed to handle subscription cancellation: {e}")
