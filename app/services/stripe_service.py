import stripe # Stripe Python library
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from fastapi import HTTPException # For error handling

from app.core.config import settings
from app.models.user_models import User
from app.models.subscription_models import Subscription
from datetime import datetime # For current_period_end

# Initialize Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_stripe_checkout_session(user: User, price_id: str, db_session: Session) -> str:
    """
    Creates a Stripe Checkout session for a user to subscribe to a given price ID.
    Retrieves or creates a Stripe customer ID for the user.
    """

    stripe_customer_id: Optional[str] = None

    # Check if user already has a subscription record and thus a stripe_customer_id
    subscription_record = db_session.exec(
        select(Subscription).where(Subscription.user_id == user.id)
    ).first()

    if subscription_record and subscription_record.stripe_customer_id:
        stripe_customer_id = subscription_record.stripe_customer_id
    else:
        # Create a new Stripe customer
        try:
            customer = stripe.Customer.create(
                email=user.email,
                # name=str(user.id), # Optional: set user ID or other info as name
                metadata={"user_id": str(user.id)} # Store app's user_id in Stripe customer metadata
            )
            stripe_customer_id = customer.id

            # If creating a new customer, ensure a subscription record exists or is created
            # to store this new stripe_customer_id.
            if subscription_record:
                subscription_record.stripe_customer_id = stripe_customer_id
            else:
                # This case implies a user might not have any subscription record yet.
                # Depending on desired flow, one might be created here with a status like 'pending_checkout'.
                # For now, we'll assume a subscription record might be created more definitively
                # by the webhook after successful checkout.session.completed.
                # However, storing the customer_id now is good.
                # Let's create a minimal one if it doesn't exist, webhook will update status.
                subscription_record = Subscription(
                    user_id=user.id,
                    stripe_customer_id=stripe_customer_id,
                    status="pending_checkout", # Initial status
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            db_session.add(subscription_record)
            db_session.commit()
            db_session.refresh(subscription_record)

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=500, detail=f"Stripe customer creation failed: {str(e)}")

    if not stripe_customer_id: # Should not happen if logic above is correct
            raise HTTPException(status_code=500, detail="Failed to retrieve or create Stripe customer ID.")

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_DOMAIN}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_DOMAIN}/payment/cancel",
            # Pass user_id in metadata to simplify linking in webhook if customer metadata isn't used/reliable for this
            subscription_data={
                "metadata": {"user_id": str(user.id)}
            }
            # metadata={"user_id": str(user.id)} # For one-time payments, not subscription_data
        )
        return checkout_session.url
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe checkout session creation failed: {str(e)}")


async def handle_stripe_webhook(payload: str, sig_header: str, db_session: Session):
    """
    Handles incoming Stripe webhooks.
    Verifies signature and processes relevant events.
    """
    event: Optional[stripe.Event] = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e: # Invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e: # Invalid signature
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")
    except Exception as e: # Other construction errors
        raise HTTPException(status_code=400, detail=f"Webhook construction error: {str(e)}")

    if event is None: # Should not happen if exceptions are caught
        raise HTTPException(status_code=500, detail="Webhook event construction failed unexpectedly.")

    # Handle the event
    if event.type == 'checkout.session.completed':
        session_data = event.data.object # This is a stripe.checkout.Session
        stripe_customer_id = session_data.customer
        stripe_subscription_id = session_data.subscription

        # Retrieve user_id from subscription_data metadata if available
        # This is more reliable than client or customer metadata for this specific checkout
        user_id_str = None
        if session_data.subscription_data and session_data.subscription_data.metadata:
                user_id_str = session_data.subscription_data.metadata.get("user_id")

        if not user_id_str and session_data.metadata: # Fallback to session metadata
                user_id_str = session_data.metadata.get("user_id")

        if not user_id_str:
                # Fallback: Try to find user by stripe_customer_id if metadata linking failed
            sub_record_by_cust_id = db_session.exec(
                select(Subscription).where(Subscription.stripe_customer_id == stripe_customer_id)
            ).first()
            if sub_record_by_cust_id:
                user_id_str = str(sub_record_by_cust_id.user_id)
            else: # If still no user_id, log and skip. This shouldn't happen with proper metadata.
                print(f"Webhook Error: checkout.session.completed - user_id not found in metadata for session {session_data.id}")
                # Consider raising an error or specific handling if user_id is critical and missing
                return {"status": "error", "message": "User ID not found in session metadata"}


        if session_data.payment_status == "paid" and user_id_str:
            user_id = int(user_id_str)
            subscription_details = stripe.Subscription.retrieve(stripe_subscription_id) if stripe_subscription_id else None

            if not subscription_details:
                    print(f"Webhook Error: Could not retrieve subscription details for {stripe_subscription_id}")
                    return {"status": "error", "message": "Subscription details not found"}

            existing_subscription = db_session.exec(
                select(Subscription).where(Subscription.user_id == user_id)
            ).first()

            if existing_subscription:
                existing_subscription.stripe_customer_id = stripe_customer_id # Ensure it's up-to-date
                existing_subscription.stripe_subscription_id = stripe_subscription_id
                existing_subscription.status = subscription_details.status # e.g. "active"
                existing_subscription.current_period_end = datetime.fromtimestamp(subscription_details.current_period_end)
                existing_subscription.updated_at = datetime.utcnow()
            else:
                new_subscription = Subscription(
                    user_id=user_id,
                    stripe_customer_id=stripe_customer_id,
                    stripe_subscription_id=stripe_subscription_id,
                    status=subscription_details.status,
                    current_period_end=datetime.fromtimestamp(subscription_details.current_period_end),
                    created_at=datetime.utcnow(), # Or from Stripe event if preferred
                    updated_at=datetime.utcnow()
                )
                db_session.add(new_subscription)

            db_session.commit()
            print(f"Subscription created/updated for user {user_id} via checkout.session.completed.")

    elif event.type in ['customer.subscription.updated', 'customer.subscription.deleted', 'customer.subscription.created']: # Added created for completeness
        subscription_data = event.data.object # This is a stripe.Subscription
        stripe_subscription_id = subscription_data.id
        stripe_customer_id = subscription_data.customer

        # Find subscription in DB by stripe_subscription_id
        db_subscription = db_session.exec(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        ).first()

        if not db_subscription:
            # If not found by subscription_id, maybe it's a new subscription not yet linked via checkout (less common for 'updated')
            # or customer_id was stored first.
            # For 'created', this might be the primary way it's identified if checkout.session.completed is missed.
            if stripe_customer_id:
                    db_subscription_by_customer = db_session.exec(
                    select(Subscription).where(Subscription.stripe_customer_id == stripe_customer_id)
                    ).first()
                    if db_subscription_by_customer:
                        db_subscription = db_subscription_by_customer
                        db_subscription.stripe_subscription_id = stripe_subscription_id # Link it now
                    else: # No record by customer_id either
                        print(f"Webhook Info: No subscription found for stripe_subscription_id {stripe_subscription_id} or customer_id {stripe_customer_id}. May need manual linking or setup via checkout first.")
                        # Potentially create a new one if event type is 'customer.subscription.created' and user_id is in metadata
                        user_id_str = subscription_data.metadata.get("user_id")
                        if event.type == 'customer.subscription.created' and user_id_str:
                            db_subscription = Subscription(
                                user_id=int(user_id_str),
                                stripe_customer_id=stripe_customer_id,
                                stripe_subscription_id=stripe_subscription_id,
                                status=subscription_data.status,
                                current_period_end=datetime.fromtimestamp(subscription_data.current_period_end) if subscription_data.current_period_end else None,
                                created_at=datetime.fromtimestamp(subscription_data.created) if subscription_data.created else datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            db_session.add(db_subscription)
                        else: # No user_id in metadata, cannot create
                            return {"status": "info", "message": "Subscription not found and could not be created from webhook."}

        if db_subscription: # If found or created
            db_subscription.status = subscription_data.status
            db_subscription.current_period_end = datetime.fromtimestamp(subscription_data.current_period_end) if subscription_data.current_period_end else None
            if event.type == 'customer.subscription.deleted': # Or 'canceled' if that's the status Stripe uses for actual deletion vs. end of period cancel
                db_subscription.status = "canceled" # Or map Stripe's status directly
            db_subscription.updated_at = datetime.utcnow()
            db_session.add(db_subscription) # Add to session to ensure it's tracked for commit
            db_session.commit()
            print(f"Subscription {stripe_subscription_id} for user {db_subscription.user_id} status updated to {db_subscription.status}.")
    else:
        print(f"Unhandled event type {event.type}")

    return {"status": "success", "event_type_received": event.type}
