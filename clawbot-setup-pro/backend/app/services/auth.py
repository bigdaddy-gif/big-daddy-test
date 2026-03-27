from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

security = HTTPBearer(auto_error=False)


def get_current_user_id(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if not creds:
        raise HTTPException(status_code=401, detail="missing_token")

    token = creds.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid_token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="invalid_token")

    return str(sub)
