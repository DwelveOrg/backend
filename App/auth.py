from __future__ import annotations
import random
import time
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from DataBase.db_ext import get_db
from DataBase.user import User
from .schemas import (
    RegisterStart, RegisterVerify, RegisterComplete,
    LoginRequest, MsgResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Временное хранилище (как и было)
PENDING_REGISTRATIONS: Dict[str, Dict[str, Any]] = {}
PENDING_TTL_SECONDS = 10 * 60


def _cleanup_pending(email: str) -> Dict[str, Any] | None:
    data = PENDING_REGISTRATIONS.get(email)
    if not data:
        return None
    if time.time() > data["expires_at"]:
        del PENDING_REGISTRATIONS[email]
        return None
    return data


@router.post("/register/start", response_model=MsgResponse)
async def register_start(payload: RegisterStart, db: AsyncSession = Depends(get_db)):
    # Проверка существования пользователя
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already exists.")

    code = str(random.randint(100000, 999999))

    PENDING_REGISTRATIONS[payload.email] = {
        "full_name": payload.full_name,
        "role": payload.role,
        "verified": False,
        "code": code,
        "expires_at": time.time() + PENDING_TTL_SECONDS,
    }

    # В FastAPI логирование обычно через стандартный logging или Loguru
    print(f"Verification code for {payload.email}: {code}")

    return {"message": "Verification code sent."}


@router.post("/register/verify", response_model=MsgResponse)
async def register_verify(payload: RegisterVerify):
    data = _cleanup_pending(payload.email)
    if not data:
        raise HTTPException(status_code=404, detail="Registration session expired or not found.")

    if data["code"] != payload.code:
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    data["verified"] = True
    return {"message": "Email verified successfully."}


@router.post("/register/complete", status_code=status.HTTP_201_CREATED)
async def register_complete(payload: RegisterComplete, db: AsyncSession = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    if not payload.accept_terms:
        raise HTTPException(status_code=400, detail="You must accept the terms.")

    # Проверка уникальности
    email_check = await db.execute(select(User).where(User.email == payload.email))
    if email_check.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already exists.")

    data = _cleanup_pending(payload.email)
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

    del PENDING_REGISTRATIONS[payload.email]
    return {"message": "Account created successfully."}


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # В FastAPI вместо login_user(user) обычно возвращают JWT-токен
    # Для простоты пока вернем успех, но подразумевается генерация токена
    return {"message": "Login success", "access_token": "some-jwt-token"}