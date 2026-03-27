from fastapi import APIRouter

from app.schemas.device import PairCodeResponse, DeviceStatusResponse

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/pair", response_model=PairCodeResponse)
def create_pair_code():
    # TODO: auth + store pairing code
    return PairCodeResponse(code="DEMO-PAIR", expires_in_seconds=300)


@router.get("/{device_id}/status", response_model=DeviceStatusResponse)
def device_status(device_id: str):
    # TODO: auth + device lookup
    return DeviceStatusResponse(device_id=device_id, status="offline", last_seen_at=None)
