from fastapi import APIRouter, Request, Header, Depends, HTTPException
from sqlmodel import Session
import stripe
from typing import Optional

from app.db.session import get_session
from app.services import stripe_service

import logging # New import
logger = logging.getLogger("AnimeMateApp.StripeWebhooks") # Specific logger

router = APIRouter()

@router.post("/stripe")
async def webhook_received(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_session)
):
    logger.info(f"Stripe webhook received. Signature: {'Present' if stripe_signature else 'Missing'}")
    if stripe_signature is None:
        logger.warning("Missing Stripe-Signature header in webhook request.")
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()

    try:
        logger.debug(f"Attempting to process Stripe webhook payload: {payload[:500].decode('utf-8', errors='ignore')}...")
        result = await stripe_service.handle_stripe_webhook(
            payload=payload.decode('utf-8'),
            sig_header=stripe_signature,
            db_session=db
        )
        logger.info(f"Stripe webhook processed successfully. Result: {result}")
        return result

    except HTTPException as e:
        logger.error(f"HTTPException during Stripe webhook processing: {e.detail}", exc_info=True)
        raise e
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe signature verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")
    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error during webhook processing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stripe API error: {str(e)}")
    except Exception as e:
        logger.critical(f"Critical unhandled error during Stripe webhook processing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing webhook.")
