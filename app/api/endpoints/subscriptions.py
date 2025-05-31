from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel # Ensure SQLModel is imported for response models
from typing import Optional
from pydantic import BaseModel # For request body

from app.db.session import get_session
from app.services import stripe_service # Your Stripe service
from app.models.user_models import User
from app.models.subscription_models import Subscription # To query local subscription status
from app.core.config import settings # For default PRICE_ID

# fastapi-users dependency for current_user
import fastapi_users
current_active_user = fastapi_users.current_user(active=True)

router = APIRouter()

class CheckoutSessionRequest(BaseModel): # Request body model
    price_id: Optional[str] = None

class CheckoutSessionResponse(SQLModel): # Schema for the response
    checkout_url: str

class SubscriptionStatusResponse(SQLModel): # Schema for subscription status
    status: Optional[str] = None
    current_period_end: Optional[str] = None # Use str for ISO format datetime
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session_endpoint(
    request_data: CheckoutSessionRequest, # Request body
    user: User = Depends(current_active_user), # Protected route
    db: Session = Depends(get_session)
):
    """
    Creates a Stripe Checkout session for the authenticated user.
    Client can optionally send a price_id, otherwise a default is used.
    """
    selected_price_id = request_data.price_id or settings.STRIPE_PRICE_ID_MONTHLY # Default to monthly if not provided

    if not selected_price_id:
        raise HTTPException(
            status_code=400,
            detail="No price ID provided and no default monthly price ID configured in settings."
        )

    try:
        checkout_url = await stripe_service.create_stripe_checkout_session(
            user=user,
            price_id=selected_price_id,
            db_session=db
        )
        return CheckoutSessionResponse(checkout_url=checkout_url)
    except HTTPException as e: # Re-raise HTTPExceptions from the service
        raise e
    except Exception as e: # Catch any other unexpected errors
        # Log the full error for server-side debugging
        print(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session.")


@router.get("/subscription-status", response_model=SubscriptionStatusResponse)
async def get_subscription_status_endpoint(
    user: User = Depends(current_active_user), # Protected route
    db: Session = Depends(get_session)
):
    """
    Retrieves the current user's subscription status from the local database.
    """
    subscription = db.exec(
        select(Subscription).where(Subscription.user_id == user.id)
    ).first()

    if not subscription:
        return SubscriptionStatusResponse(status="not_subscribed") # Or simply return empty if preferred

    return SubscriptionStatusResponse(
        status=subscription.status,
        current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        stripe_customer_id=subscription.stripe_customer_id,
        stripe_subscription_id=subscription.stripe_subscription_id,
    )
