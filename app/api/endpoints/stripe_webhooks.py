from fastapi import APIRouter, Request, Header, Depends, HTTPException
from sqlmodel import Session
import stripe # Import stripe for stripe.error types
from typing import Optional # Added Optional

from app.db.session import get_session
from app.services import stripe_service # Import your stripe service

router = APIRouter()

@router.post("/stripe") # Endpoint path: /webhooks/stripe (prefix will be /webhooks)
async def webhook_received(
    request: Request, # Use Request to get raw body
    stripe_signature: Optional[str] = Header(None), # Stripe-Signature header
    db: Session = Depends(get_session)
):
    """
    Endpoint to receive Stripe webhooks.
    It verifies the signature and passes the event to the stripe_service.
    """
    if stripe_signature is None:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body() # Get raw payload

    try:
        # The handle_stripe_webhook function in the service already raises
        # HTTPException for signature errors or payload issues.
        # It will also handle other Stripe-specific errors if they occur during event processing.
        result = await stripe_service.handle_stripe_webhook(
            payload=payload.decode('utf-8'), # Decode payload from bytes to string
            sig_header=stripe_signature,
            db_session=db
        )
        # Webhook handler should return a dict with status, or raise HTTPException for errors
        # For successful processing, Stripe expects a 200 OK.
        return result # Or simply return {"status": "success"} if service doesn't return detailed dict

    except HTTPException as e:
        # Re-raise HTTPExceptions that occurred within handle_stripe_webhook
        # (like signature verification, invalid payload)
        raise e
    except stripe.error.StripeError as e: # Catch other potential Stripe errors not caught in service
        # This is a fallback, ideally service layer catches Stripe specific errors
        print(f"Webhook - Stripe API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stripe API error: {str(e)}")
    except Exception as e:
        # Catch-all for any other unexpected errors during webhook processing
        print(f"Webhook - Internal Server Error: {str(e)}")
        # Do not send detailed error message to Stripe to prevent info leak
        raise HTTPException(status_code=500, detail="Internal server error processing webhook.")
