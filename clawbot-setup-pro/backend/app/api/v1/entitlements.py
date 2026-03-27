from fastapi import APIRouter

from app.schemas.entitlement import EntitlementStatus

router = APIRouter(prefix="/entitlements", tags=["entitlements"])


@router.get("/me", response_model=EntitlementStatus)
def my_entitlement():
    # TODO: auth + real DB lookup
    return EntitlementStatus(active=False, sku=None)
