"""
PDF NEXUS - Security Utilities
Bcrypt password hashing, JWT authorization, and path traversal prevention.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Any
import bcrypt
import jwt
from fastapi import HTTPException, status, Header
from app.core.config import settings

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Extract user payload if Authorization bearer header is present, else None (guest mode)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    return decode_access_token(token)

def safe_resolve_path(base_dir: Path, filename: str) -> Path:
    """
    Prevents path traversal attacks by resolving path and verifying that
    the target stays strictly within the intended directory.
    """
    clean_name = Path(filename).name
    target = (base_dir / clean_name).resolve()
    if not str(target).startswith(str(base_dir.resolve())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: path traversal attempted."
        )
    return target
