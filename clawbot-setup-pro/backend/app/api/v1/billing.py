from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
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
async def stripe_webhook(request: Request):
    # TODO: verify signature + upsert entitlements
    # placeholder so mobile/backend contract exists
    _ = await request.body()
    return {"ok": True}
