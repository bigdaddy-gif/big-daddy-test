import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.magic_link import MagicLinkToken
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.dev import DevLoginRequest
from app.services.security import create_access_token

router = APIRouter(prefix="/dev", tags=["dev"])


def _ensure_dev_mode():
    # Safety: only enable when explicitly in dev mode.
    if settings.jwt_secret != "dev-secret-change-me":
        raise HTTPException(status_code=404, detail="not_found")


@router.post("/login", response_model=TokenResponse)
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)):
    _ensure_dev_mode()

    email = payload.email.lower()
    user: User | None = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        user = User(id=str(uuid.uuid4()), email=email)
        db.add(user)
        db.commit()

    access = create_access_token(subject=user.id)
    return TokenResponse(access_token=access)


@router.get("/magic-token")
def get_latest_magic_token(email: str, db: Session = Depends(get_db)):
    _ensure_dev_mode()

    rec: MagicLinkToken | None = (
        db.query(MagicLinkToken)
        .filter(MagicLinkToken.email == email.lower())
        .order_by(MagicLinkToken.created_at.desc())
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="not_found")

    return {"token_hash": rec.token_hash}
