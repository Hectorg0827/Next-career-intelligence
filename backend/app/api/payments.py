"""
Payment processing endpoints (Stripe integration)
Handles subscription webhooks and payment status
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger
import stripe
import os

from app.db.database import get_db
from app.models.database import User

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/payments/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events for subscription changes
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid Stripe payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_successful_payment(session, db)
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        await handle_subscription_update(subscription, db)
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancelled(subscription, db)
    
    return {"status": "success"}


async def handle_successful_payment(session: dict, db: Session):
    """
    Handle successful payment - upgrade user to Pro
    """
    try:
        customer_id = session.get('customer')
        
        # Find user by Stripe customer ID or email
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        
        if not user:
            # Try to find by email in session metadata
            email = session.get('customer_email')
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                user.stripe_customer_id = customer_id
        
        if user:
            user.subscription_status = 'pro'
            user.subscription_updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"User {user.email} upgraded to Pro")
        else:
            logger.warning(f"User not found for Stripe customer {customer_id}")
            
    except Exception as e:
        logger.error(f"Failed to handle successful payment: {e}")
        db.rollback()


async def handle_subscription_update(subscription: dict, db: Session):
    """
    Handle subscription updates (e.g., plan changes)
    """
    try:
        customer_id = subscription.get('customer')
        status = subscription.get('status')
        
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        
        if user:
            if status == 'active':
                user.subscription_status = 'pro'
            elif status in ['past_due', 'unpaid']:
                user.subscription_status = 'free'
            
            user.subscription_updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Subscription updated for {user.email}: {status}")
            
    except Exception as e:
        logger.error(f"Failed to handle subscription update: {e}")
        db.rollback()


async def handle_subscription_cancelled(subscription: dict, db: Session):
    """
    Handle subscription cancellation - downgrade to free
    """
    try:
        customer_id = subscription.get('customer')
        
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        
        if user:
            user.subscription_status = 'free'
            user.subscription_updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"User {user.email} downgraded to Free")
            
    except Exception as e:
        logger.error(f"Failed to handle subscription cancellation: {e}")
        db.rollback()


@router.get("/payments/subscription-status")
async def get_subscription_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current subscription status for a user
    """
    try:
        user = db.query(User).filter(User.firebase_uid == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "subscription_status": user.subscription_status or "free",
            "stripe_customer_id": user.stripe_customer_id,
            "subscription_updated_at": user.subscription_updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch subscription status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription status"
        )


@router.post("/payments/create-checkout-session")
async def create_checkout_session(
    firebase_uid: str,
    price_id: str,
    db: Session = Depends(get_db)
):
    """
    Create a Stripe checkout session for upgrading to Pro
    """
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create or retrieve Stripe customer
        if user.stripe_customer_id:
            customer_id = user.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'firebase_uid': firebase_uid}
            )
            customer_id = customer.id
            user.stripe_customer_id = customer_id
            db.commit()
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.getenv('APP_URL')}/dashboard?payment=success",
            cancel_url=f"{os.getenv('APP_URL')}/pricing?payment=cancelled",
        )
        
        return {"checkout_url": session.url}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )
