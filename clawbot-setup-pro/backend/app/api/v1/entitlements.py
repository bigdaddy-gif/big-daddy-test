from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entitlement import Entitlement
from app.schemas.entitlement import EntitlementStatus
from app.services.auth import get_current_user_id

router = APIRouter(prefix="/entitlements", tags=["entitlements"])


@router.get("/me", response_model=EntitlementStatus)
def my_entitlement(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    ent: Entitlement | None = (
        db.query(Entitlement)
        .filter(Entitlement.user_id == user_id, Entitlement.active == True)  # noqa: E712
        .order_by(Entitlement.created_at.desc())
        .first()
    )

    if not ent:
        return EntitlementStatus(active=False, sku=None)

    return EntitlementStatus(active=True, sku=ent.sku)
