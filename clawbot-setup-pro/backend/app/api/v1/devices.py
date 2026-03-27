from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.device import Device
from app.schemas.device import DeviceStatusResponse
from app.schemas.pairing import DeviceLogOut
from app.services.auth import get_current_user_id

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/{device_id}/status", response_model=DeviceStatusResponse)
def device_status(
    device_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    device: Device | None = db.query(Device).filter(Device.id == device_id, Device.user_id == user_id).one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="device_not_found")

    last_seen = device.last_seen_at.isoformat() if device.last_seen_at else None
    return DeviceStatusResponse(device_id=device.id, status=device.status, last_seen_at=last_seen)


@router.get("/{device_id}/logs", response_model=list[DeviceLogOut])
def device_logs(
    device_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = 200,
):
    device: Device | None = db.query(Device).filter(Device.id == device_id, Device.user_id == user_id).one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="device_not_found")

    from app.models.device_log import DeviceLog

    rows = (
        db.query(DeviceLog)
        .filter(DeviceLog.device_id == device_id)
        .order_by(DeviceLog.ts.desc())
        .limit(max(1, min(limit, 1000)))
        .all()
    )

    # return ascending for UI readability
    rows = list(reversed(rows))
    return [DeviceLogOut(level=r.level, message=r.message, ts=r.ts.isoformat()) for r in rows]
