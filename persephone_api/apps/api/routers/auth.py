from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from ..deps import get_session
from ..repositories.users import UserRepository
from ..schemas.auth import LoginRequest, UserOut
from ..services.security import (
    encode_session,
    get_current_user,
    verify_password,
)
from ..settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_session)) -> UserOut:
    repo = UserRepository(db)
    user = repo.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    session_token = encode_session(int(user.id))
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=session_token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
    )
    return UserOut(id=int(user.id), email=user.email)


@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)) -> UserOut:
    return UserOut(**current_user)


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(settings.auth_cookie_name)
    return {"ok": True}
