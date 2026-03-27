from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.device_token import DeviceToken
from app.services.security import hash_token

security = HTTPBearer(auto_error=False)


def get_current_device_id(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> str:
    if not creds:
        raise HTTPException(status_code=401, detail="missing_device_token")

    token = creds.credentials
    token_h = hash_token(token)

    rec: DeviceToken | None = db.query(DeviceToken).filter(DeviceToken.token_hash == token_h).one_or_none()
    if not rec:
        raise HTTPException(status_code=401, detail="invalid_device_token")

    return rec.device_id
