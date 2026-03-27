from datetime import datetime, timedelta, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.magic_link import MagicLinkToken
from app.models.user import User
from app.schemas.auth import MagicLinkRequest, MagicLinkVerifyRequest, TokenResponse
from app.services.resend_client import ResendClient
from app.services.security import create_access_token, hash_token, random_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/magic-link")
async def request_magic_link(payload: MagicLinkRequest, db: Session = Depends(get_db)):
    # Always respond 200 to avoid email enumeration
    token = random_token(32)
    token_h = hash_token(token)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.magic_link_ttl_minutes)

    db.add(
        MagicLinkToken(
            id=str(uuid.uuid4()),
            email=payload.email.lower(),
            token_hash=token_h,
            consumed=False,
            expires_at=expires_at,
        )
    )
    db.commit()

    link = f"{settings.app_base_url}/auth/magic?token={token}"
    await ResendClient().send_magic_link(payload.email, link)

    return {"ok": True}


@router.post("/verify", response_model=TokenResponse)
def verify_magic_link(payload: MagicLinkVerifyRequest, db: Session = Depends(get_db)):
    token_h = hash_token(payload.token)

    rec: MagicLinkToken | None = (
        db.query(MagicLinkToken)
        .filter(MagicLinkToken.token_hash == token_h)
        .one_or_none()
    )

    if not rec or rec.consumed:
        raise HTTPException(status_code=400, detail="invalid_token")

    if rec.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="expired_token")

    rec.consumed = True

    email = rec.email.lower()
    user: User | None = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        user = User(id=str(uuid.uuid4()), email=email)
        db.add(user)

    db.commit()

    access = create_access_token(subject=user.id)
    return TokenResponse(access_token=access)
