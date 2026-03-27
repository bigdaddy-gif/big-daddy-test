from pydantic import BaseModel


class PairCreateResponse(BaseModel):
    code: str
    expires_in_seconds: int


class DeviceActivateRequest(BaseModel):
    code: str
    name: str
    platform: str  # windows|macos


class DeviceActivateResponse(BaseModel):
    device_id: str
    device_token: str


class DeviceLogIn(BaseModel):
    level: str = "info"  # info|warn|error
    message: str
    ts: str | None = None


class DeviceLogOut(BaseModel):
    level: str
    message: str
    ts: str
