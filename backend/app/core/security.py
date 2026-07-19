from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from jose import jwt
import bcrypt
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    pwd_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* password."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT token payload schema
# ---------------------------------------------------------------------------


class TokenPayload(BaseModel):
    """Claims embedded in every access token.

    - ``sub``    — user UUID (string)
    - ``org_id`` — active organisation UUID (string); may be empty string
                   if the user has not yet joined any organisation.
    - ``role``   — membership role within *org_id* ("owner"|"admin"|"member"|"")
    - ``exp``    — standard expiry timestamp
    """

    sub: str  # user UUID
    org_id: str = ""  # active org UUID
    role: str = ""  # membership role
    exp: datetime


# ---------------------------------------------------------------------------
# Token creation & decoding
# ---------------------------------------------------------------------------


def create_access_token(
    *,
    subject: uuid.UUID | str,
    org_id: uuid.UUID | str = "",
    role: str = "",
    expires_delta: timedelta | None = None,
) -> str:
    """Mint a signed HS256 JWT access token.

    Args:
        subject:      The user's UUID.
        org_id:       The organisation the token is scoped to (empty = none).
        role:         The user's role within *org_id*.
        expires_delta: Custom TTL; defaults to ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        A compact, URL-safe JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(UTC) + expires_delta
    payload: dict = {
        "sub": str(subject),
        "org_id": str(org_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JWT access token.

    Raises:
        jose.JWTError: If the token is expired, tampered, or otherwise invalid.
    """
    raw = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    return TokenPayload(**raw)


__all__ = [
    "TokenPayload",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
