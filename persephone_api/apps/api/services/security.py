from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlmodel import Session

from ..repositories.users import UserRepository
from ..settings import settings
from ..deps import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def _sign_value(value: str) -> str:
    digest = hmac.new(settings.auth_secret.encode(), value.encode(), hashlib.sha256)
    return digest.hexdigest()


def encode_session(user_id: int) -> str:
    raw = str(user_id).encode()
    token = base64.urlsafe_b64encode(raw).decode()
    signature = _sign_value(token)
    return f"{token}.{signature}"


def decode_session(token: str) -> Optional[int]:
    try:
        token_part, signature = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(signature, _sign_value(token_part)):
        return None
    try:
        raw = base64.urlsafe_b64decode(token_part.encode())
        return int(raw.decode())
    except Exception:  # pragma: no cover - defensive
        return None


async def get_current_user(
    session_token: Optional[str] = Cookie(None, alias=settings.auth_cookie_name),
    db: Session = Depends(get_session),
) -> dict:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = decode_session(session_token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return {"id": user.id, "email": user.email}
