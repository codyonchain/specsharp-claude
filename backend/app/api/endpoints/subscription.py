from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import stripe
import os
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import User
from app.api.endpoints.auth import get_current_user
from app.core.config import settings

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

# Constants
FREE_ESTIMATE_LIMIT = 3
MONTHLY_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_specsharp_monthly")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


@router.post("/create")
async def create_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a Stripe subscription for the current user's team"""
    try:
        # Import Team model
        from app.db.team_models import Team
        
        # Check if user has a team
        if not current_user.current_team_id:
            # Create a default team for the user
            team = Team(
                name=f"{current_user.full_name}'s Team",
                slug=f"team-{current_user.id}",
                owner_id=current_user.id,
                seats_included=3
            )
            db.add(team)
            db.flush()
            
            # Add user as admin
            from app.db.team_models import team_members
            db.execute(
                team_members.insert().values(
                    user_id=current_user.id,
                    team_id=team.id,
                    role='admin'
                )
            )
            
            current_user.current_team_id = team.id
            db.flush()
        else:
            team = db.query(Team).filter(Team.id == current_user.current_team_id).first()
        
        # Check if team already has a subscription
        if team.subscription_status == "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team already has an active subscription"
            )
        
        # Create or retrieve Stripe customer for the team
        if not team.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=team.name,
                metadata={
                    "team_id": str(team.id),
                    "owner_id": str(team.owner_id)
                }
            )
            team.stripe_customer_id = customer.id
            db.flush()
        
        # Create payment intent for subscription
        subscription = stripe.Subscription.create(
            customer=team.stripe_customer_id,
            items=[{"price": MONTHLY_PRICE_ID}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
            metadata={
                "team_id": str(team.id),
                "seats_included": str(team.seats_included)
            }
        )
        
        # Update team subscription info
        team.stripe_subscription_id = subscription.id
        db.commit()
        
        return {
            "clientSecret": subscription.latest_invoice.payment_intent.client_secret,
            "subscriptionId": subscription.id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.post("/confirm")
async def confirm_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Confirm subscription payment and activate user subscription"""
    try:
        # Retrieve subscription from Stripe
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        if subscription.status == "active":
            # Update user subscription status
            current_user.is_subscribed = True
            current_user.subscription_status = "active"
            current_user.subscription_started_at = datetime.utcnow()
            current_user.subscription_ends_at = datetime.utcnow() + timedelta(days=30)
            db.commit()
            
            return {
                "status": "success",
                "message": "Subscription activated successfully"
            }
        else:
            return {
                "status": "pending",
                "message": f"Subscription status: {subscription.status}"
            }
            
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm subscription: {str(e)}"
        )


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Cancel user's subscription"""
    try:
        if not current_user.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        # Cancel subscription at period end
        subscription = stripe.Subscription.modify(
            current_user.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update user status
        current_user.subscription_status = "cancelled"
        db.commit()
        
        return {
            "status": "success",
            "message": "Subscription will be cancelled at the end of the billing period",
            "ends_at": subscription.current_period_end
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current user's subscription status and usage"""
    return {
        "is_subscribed": current_user.is_subscribed,
        "subscription_status": current_user.subscription_status,
        "estimate_count": current_user.estimate_count,
        "free_estimates_remaining": max(0, FREE_ESTIMATE_LIMIT - current_user.estimate_count),
        "subscription_ends_at": current_user.subscription_ends_at.isoformat() if current_user.subscription_ends_at else None,
        "has_completed_onboarding": current_user.has_completed_onboarding
    }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks for subscription events"""
    # Get the raw body
    try:
        payload = await request.body()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    
    # Verify webhook signature
    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")
    else:
        # No webhook secret configured, parse event directly (not recommended for production)
        import json
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    event_type = event.get("type")
    
    if event_type == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        
        # Find user by customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = subscription["status"]
            if subscription["status"] == "active":
                user.is_subscribed = True
            elif subscription["status"] in ["cancelled", "unpaid"]:
                user.is_subscribed = False
            db.commit()
    
    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        
        # Find user by customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.is_subscribed = False
            user.subscription_status = "expired"
            db.commit()
    
    return {"status": "success"}