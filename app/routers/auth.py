import os
import random
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User
from app.schemas import (
    RegisterStart, RegisterVerify, RegisterComplete,
    LoginRequest, MsgResponse, RefreshTokenRequest
)
from app.core.email import send_verification_email
from app.core.redis import (
    set_pending_registration,
    get_pending_registration,
    delete_pending_registration,
    blacklist_token,
    store_refresh_token,
    get_refresh_token,
    delete_refresh_token,
)
from app.dependencies.auth_deps import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
security = HTTPBearer()

if os.environ.get("TESTING"):
    class _FakeLimiter:
        def limit(self, *args, **kwargs):
            return lambda f: f
    limiter = _FakeLimiter()
else:
    limiter = Limiter(key_func=get_remote_address)


@router.post("/register/start", response_model=MsgResponse)
@limiter.limit("5/minute")
async def register_start(request: Request, payload: RegisterStart, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already exists.")

    code = str(random.randint(100000, 999999))

    await set_pending_registration(payload.email, {
        "full_name": payload.full_name,
        "role": payload.role,
        "verified": False,
        "code": code,
    })

    await send_verification_email(payload.email, code)
    return {"message": "Verification code sent."}


@router.post("/register/verify", response_model=MsgResponse)
@limiter.limit("10/minute")
async def register_verify(request: Request, payload: RegisterVerify):
    data = await get_pending_registration(payload.email)
    if not data:
        raise HTTPException(status_code=404, detail="Registration session expired or not found.")

    if data["code"] != payload.code:
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    data["verified"] = True
    await set_pending_registration(payload.email, data)
    return {"message": "Email verified successfully."}


@router.post("/register/complete", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_complete(request: Request, payload: RegisterComplete, db: AsyncSession = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    if not payload.accept_terms:
        raise HTTPException(status_code=400, detail="You must accept the terms.")

    email_check = await db.execute(select(User).where(User.email == payload.email))
    if email_check.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already exists.")

    data = await get_pending_registration(payload.email)
    if not data or not data["verified"]:
        raise HTTPException(status_code=400, detail="Email is not verified.")

    new_user = User(
        full_name=data["full_name"],
        email=payload.email,
        role=data["role"]
    )
    new_user.set_password(payload.password)

    db.add(new_user)
    await db.commit()

    await delete_pending_registration(payload.email)
    return {"message": "Account created successfully."}


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    await store_refresh_token(user.id, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
async def refresh(payload: RefreshTokenRequest):
    token_data = decode_access_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    stored_token = await get_refresh_token(int(user_id))
    if not stored_token or stored_token != payload.refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked.")

    new_access_token = create_access_token(data={"sub": user_id})
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.post("/logout", response_model=MsgResponse)
@limiter.limit("10/minute")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(get_current_user)
):
    token = credentials.credentials
    await blacklist_token(token)
    await delete_refresh_token(current_user.id)
    return {"message": "Successfully logged out."}