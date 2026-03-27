from pydantic import BaseModel


class JobStartRequest(BaseModel):
    device_id: str
    plan: dict


class JobStartResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    device_id: str
    status: str
    progress: int
    result: dict | None = None


class JobProgressIn(BaseModel):
    progress: int
    message: str | None = None


class JobCompleteIn(BaseModel):
    status: str  # succeeded|failed
    result: dict | None = None
