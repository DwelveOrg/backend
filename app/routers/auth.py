import random
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User
from app.schemas import (
    RegisterStart, RegisterVerify, RegisterComplete,
    LoginRequest, MsgResponse
)
from app.core.email import send_verification_email
from app.core.redis import (
    set_pending_registration,
    get_pending_registration,
    delete_pending_registration,
    blacklist_token,
)

from app.dependencies.auth_deps import get_current_user

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from app.core.security import create_access_token

security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/register/start", response_model=MsgResponse)
@limiter.limit("5/minute")  # максимум 5 раз в минуту
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
@limiter.limit("10/minute")  # защита от брутфорса
async def login(request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
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
    return {"message": "Successfully logged out."}