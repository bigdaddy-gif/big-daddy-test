from pydantic import BaseModel


class PairCodeResponse(BaseModel):
    code: str
    expires_in_seconds: int


class DeviceStatusResponse(BaseModel):
    device_id: str
    status: str
    last_seen_at: str | None = None
