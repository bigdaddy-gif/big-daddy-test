from pydantic import BaseModel


class EntitlementStatus(BaseModel):
    active: bool
    sku: str | None = None
