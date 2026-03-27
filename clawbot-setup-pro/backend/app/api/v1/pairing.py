import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.device import Device
from app.models.device_token import DeviceToken
from app.models.pairing_code import PairingCode
from app.schemas.pairing import (
    DeviceActivateRequest,
    DeviceActivateResponse,
    DeviceLogIn,
    PairCreateResponse,
)
from app.services.auth import get_current_user_id
from app.services.device_auth import get_current_device_id
from app.services.security import hash_token, random_numeric_code, random_token

router = APIRouter(prefix="/devices", tags=["devices"])

PAIR_TTL_SECONDS = 600


@router.post("/pair", response_model=PairCreateResponse)
def create_pair_code(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # generate 6-digit numeric code; retry if collision
    for _ in range(5):
        code = random_numeric_code(6)
        exists = db.query(PairingCode).filter(PairingCode.code == code, PairingCode.consumed == False).one_or_none()  # noqa: E712
        if not exists:
            break
    else:
        raise HTTPException(status_code=500, detail="pair_code_generation_failed")

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=PAIR_TTL_SECONDS)

    db.add(
        PairingCode(
            id=str(uuid.uuid4()),
            user_id=user_id,
            code=code,
            consumed=False,
            expires_at=expires_at,
        )
    )
    db.commit()

    return PairCreateResponse(code=code, expires_in_seconds=PAIR_TTL_SECONDS)


@router.post("/activate", response_model=DeviceActivateResponse)
def activate_device(
    payload: DeviceActivateRequest,
    db: Session = Depends(get_db),
):
    rec: PairingCode | None = (
        db.query(PairingCode)
        .filter(PairingCode.code == payload.code)
        .one_or_none()
    )

    if not rec or rec.consumed:
        raise HTTPException(status_code=400, detail="invalid_code")

    if rec.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="expired_code")

    rec.consumed = True

    device_id = str(uuid.uuid4())
    device = Device(
        id=device_id,
        user_id=rec.user_id,
        name=payload.name,
        platform=payload.platform,
        status="online",
        last_seen_at=datetime.now(timezone.utc),
    )
    db.add(device)

    # issue device token
    device_token = random_token(32)
    db.add(
        DeviceToken(
            id=str(uuid.uuid4()),
            device_id=device_id,
            token_hash=hash_token(device_token),
        )
    )

    db.commit()

    return DeviceActivateResponse(device_id=device_id, device_token=device_token)


@router.post("/{device_id}/logs")
def post_logs(
    device_id: str,
    payload: DeviceLogIn,
    authed_device_id: str = Depends(get_current_device_id),
):
    if authed_device_id != device_id:
        raise HTTPException(status_code=403, detail="device_mismatch")

    # TODO: persist logs
    return {"ok": True}
