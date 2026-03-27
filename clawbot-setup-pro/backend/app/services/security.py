import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def random_token(n_bytes: int = 32) -> str:
    return base64.urlsafe_b64encode(os.urandom(n_bytes)).decode("utf-8").rstrip("=")


def random_numeric_code(length: int = 6) -> str:
    # Not cryptographically perfect, but sufficient for short-lived pairing codes.
    digits = "0123456789"
    return "".join(digits[b % 10] for b in os.urandom(length))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_ttl_minutes)
    payload = {
        "iss": settings.jwt_issuer,
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
