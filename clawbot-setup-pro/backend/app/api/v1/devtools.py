from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.magic_link import MagicLinkToken

router = APIRouter(prefix="/dev", tags=["dev"])


@router.get("/magic-token")
def get_latest_magic_token(email: str, db: Session = Depends(get_db)):
    # Safety: only enable when explicitly in dev mode.
    if settings.jwt_secret != "dev-secret-change-me":
        raise HTTPException(status_code=404, detail="not_found")

    rec: MagicLinkToken | None = (
        db.query(MagicLinkToken)
        .filter(MagicLinkToken.email == email.lower())
        .order_by(MagicLinkToken.created_at.desc())
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="not_found")

    # This returns the hash only; the plain token is not stored.
    # For dev convenience, we instruct users to temporarily enable Resend or add a separate dev flow.
    return {"token_hash": rec.token_hash, "note": "Plain token is not stored. For end-to-end testing, enable Resend or add a dev-only plaintext token mode."}
