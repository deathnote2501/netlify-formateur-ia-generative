import stripe
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from app.core.config import settings
from app.models.user_models import User
from app.models.subscription_models import Subscription
from datetime import datetime

import logging # New import
logger = logging.getLogger("AnimeMateApp.StripeService") # Specific logger

stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_stripe_checkout_session(user: User, price_id: str, db_session: Session) -> str:
    logger.info(f"Creating Stripe checkout session for user_id: {user.id}, price_id: {price_id}")

    stripe_customer_id: Optional[str] = None
    subscription_record = db_session.exec(
        select(Subscription).where(Subscription.user_id == user.id)
    ).first()

    if subscription_record and subscription_record.stripe_customer_id:
        stripe_customer_id = subscription_record.stripe_customer_id
        logger.info(f"Found existing stripe_customer_id: {stripe_customer_id} for user_id: {user.id}")
    else:
        logger.info(f"No existing stripe_customer_id for user_id: {user.id}. Creating new Stripe Customer.")
        try:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)}
            )
            stripe_customer_id = customer.id
            logger.info(f"Stripe Customer {stripe_customer_id} created for user_id: {user.id}")

            if subscription_record:
                subscription_record.stripe_customer_id = stripe_customer_id
            else:
                subscription_record = Subscription(
                    user_id=user.id,
                    stripe_customer_id=stripe_customer_id,
                    status="pending_checkout",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            db_session.add(subscription_record)
            db_session.commit()
            db_session.refresh(subscription_record)
            logger.info(f"Subscription record updated/created for user_id: {user.id} with stripe_customer_id: {stripe_customer_id}")

        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed for user_id {user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Stripe customer creation failed: {str(e)}")

    if not stripe_customer_id:
            logger.error(f"Failed to retrieve or create Stripe customer ID for user_id: {user.id}")
            raise HTTPException(status_code=500, detail="Failed to retrieve or create Stripe customer ID.")

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_DOMAIN}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_DOMAIN}/payment/cancel",
            subscription_data={
                "metadata": {"user_id": str(user.id)}
            }
        )
        logger.info(f"Stripe checkout session {checkout_session.id} created for user_id: {user.id}")
        return checkout_session.url
    except stripe.error.StripeError as e:
        logger.error(f"Stripe checkout session creation failed for user_id {user.id}, customer_id {stripe_customer_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stripe checkout session creation failed: {str(e)}")


async def handle_stripe_webhook(payload: str, sig_header: str, db_session: Session):
    event: Optional[stripe.Event] = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid Stripe webhook payload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe webhook signature: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")
    except Exception as e:
        logger.error(f"Stripe webhook construction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Webhook construction error: {str(e)}")

    if event is None:
        logger.critical("Webhook event construction failed unexpectedly after try-except block.") # Should be caught above
        raise HTTPException(status_code=500, detail="Webhook event construction failed unexpectedly.")

    logger.info(f"Processing Stripe event: {event.type}, id: {event.id}")

    if event.type == 'checkout.session.completed':
        session_data = event.data.object
        stripe_customer_id = session_data.customer
        stripe_subscription_id = session_data.subscription
        user_id_str = None
        if session_data.subscription_data and session_data.subscription_data.metadata:
                user_id_str = session_data.subscription_data.metadata.get("user_id")
        if not user_id_str and session_data.metadata:
                user_id_str = session_data.metadata.get("user_id")

        if not user_id_str:
            sub_record_by_cust_id = db_session.exec(
                select(Subscription).where(Subscription.stripe_customer_id == stripe_customer_id)
            ).first()
            if sub_record_by_cust_id:
                user_id_str = str(sub_record_by_cust_id.user_id)
                logger.info(f"Found user_id {user_id_str} by stripe_customer_id {stripe_customer_id} for checkout.session.completed {session_data.id}")
            else:
                logger.error(f"Webhook Error: checkout.session.completed - user_id not found in metadata or by customer_id for session {session_data.id}")
                return {"status": "error", "message": "User ID not found in session metadata"}

        if session_data.payment_status == "paid" and user_id_str:
            user_id = int(user_id_str)
            try:
                subscription_details = stripe.Subscription.retrieve(stripe_subscription_id) if stripe_subscription_id else None
                if not subscription_details:
                    logger.error(f"Webhook Error: Could not retrieve subscription details for {stripe_subscription_id} (user_id: {user_id})")
                    return {"status": "error", "message": "Subscription details not found"}

                existing_subscription = db_session.exec(
                    select(Subscription).where(Subscription.user_id == user_id)
                ).first()

                if existing_subscription:
                    logger.info(f"Updating existing subscription for user_id: {user_id} from checkout.session.completed.")
                    existing_subscription.stripe_customer_id = stripe_customer_id
                    existing_subscription.stripe_subscription_id = stripe_subscription_id
                    existing_subscription.status = subscription_details.status
                    existing_subscription.current_period_end = datetime.fromtimestamp(subscription_details.current_period_end)
                    existing_subscription.updated_at = datetime.utcnow()
                else:
                    logger.info(f"Creating new subscription for user_id: {user_id} from checkout.session.completed.")
                    new_subscription = Subscription(
                        user_id=user_id,
                        stripe_customer_id=stripe_customer_id,
                        stripe_subscription_id=stripe_subscription_id,
                        status=subscription_details.status,
                        current_period_end=datetime.fromtimestamp(subscription_details.current_period_end),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db_session.add(new_subscription)
                db_session.commit()
                logger.info(f"Subscription created/updated for user {user_id} via checkout.session.completed {session_data.id}.")
            except stripe.error.StripeError as e:
                logger.error(f"Stripe API error during checkout.session.completed processing for user {user_id_str}: {str(e)}", exc_info=True)
                # Not re-raising HTTPException here as Stripe might retry. Acknowledging event with 200.
                return {"status": "error", "message": f"Stripe API error: {str(e)}"}


    elif event.type in ['customer.subscription.updated', 'customer.subscription.deleted', 'customer.subscription.created']:
        subscription_data = event.data.object
        stripe_subscription_id = subscription_data.id
        stripe_customer_id = subscription_data.customer
        logger.info(f"Processing {event.type} for sub_id: {stripe_subscription_id}, cust_id: {stripe_customer_id}")

        db_subscription = db_session.exec(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        ).first()

        if not db_subscription:
            if stripe_customer_id:
                db_subscription_by_customer = db_session.exec(
                    select(Subscription).where(Subscription.stripe_customer_id == stripe_customer_id)
                ).first()
                if db_subscription_by_customer:
                    db_subscription = db_subscription_by_customer
                    db_subscription.stripe_subscription_id = stripe_subscription_id
                    logger.info(f"Linked existing subscription for cust_id {stripe_customer_id} to sub_id {stripe_subscription_id}.")
                else:
                    user_id_str = subscription_data.metadata.get("user_id")
                    if event.type == 'customer.subscription.created' and user_id_str:
                        logger.info(f"Creating new subscription for user_id {user_id_str} from {event.type} (sub_id: {stripe_subscription_id}).")
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
                    else:
                        logger.warning(f"Webhook Info: No subscription found for sub_id {stripe_subscription_id} or cust_id {stripe_customer_id}. Event {event.type} for user_id {user_id_str if user_id_str else 'UNKNOWN'}. Cannot process.")
                        return {"status": "info", "message": "Subscription not found and could not be created from webhook."}
            else: # No customer_id on event (should be rare for these events)
                logger.warning(f"Webhook Info: No customer_id on {event.type} event for sub_id {stripe_subscription_id}. Cannot reliably link.")
                return {"status": "info", "message": "Subscription not found (no customer_id)."}


        if db_subscription:
            db_subscription.status = subscription_data.status
            db_subscription.current_period_end = datetime.fromtimestamp(subscription_data.current_period_end) if subscription_data.current_period_end else None
            if event.type == 'customer.subscription.deleted':
                db_subscription.status = "canceled"
            db_subscription.updated_at = datetime.utcnow()
            db_session.add(db_subscription)
            db_session.commit()
            logger.info(f"Subscription {stripe_subscription_id} for user {db_subscription.user_id} status updated to {db_subscription.status} due to {event.type}.")
    else:
        logger.info(f"Received unhandled Stripe event type: {event.type}, id: {event.id}")

    return {"status": "success", "event_type_received": event.type}
