import uuid

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.entitlement import Entitlement
from app.schemas.billing import CheckoutSessionRequest, CheckoutSessionResponse
from app.services.stripe_service import StripeService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(payload: CheckoutSessionRequest, db: Session = Depends(get_db)):
    # TODO: require auth; look up user
    # Temporary stub user
    user_id = "dev-user"
    user_email = "dev@example.com"

    try:
        url = StripeService().create_checkout_session(
            user_id=user_id,
            user_email=user_email,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CheckoutSessionResponse(url=url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET not set")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="missing_signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_signature")

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata") or {}
        user_id = metadata.get("user_id")
        sku = metadata.get("sku", "setup_1000")

        if user_id:
            ent: Entitlement | None = (
                db.query(Entitlement)
                .filter(Entitlement.user_id == user_id, Entitlement.sku == sku)
                .one_or_none()
            )
            if ent:
                ent.active = True
            else:
                db.add(
                    Entitlement(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        sku=sku,
                        active=True,
                    )
                )
            db.commit()

    return {"ok": True}
