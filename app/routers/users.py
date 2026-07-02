from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import or_
from fastapi import Query
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User
from app.schemas import UserBaseInfo, UserUpdateProfile, UserChangePassword
from app.dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserBaseInfo)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Мой профиль"""
    return current_user


@router.get("/{user_id}", response_model=UserBaseInfo)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Профиль любого пользователя"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/me", response_model=UserBaseInfo)
async def update_my_profile(
    payload: UserUpdateProfile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Редактировать свой профиль"""
    if payload.full_name:
        current_user.full_name = payload.full_name

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.patch("/me/password")
async def change_password(
    payload: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Смена пароля"""
    if not current_user.verify_password(payload.old_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect.")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    current_user.set_password(payload.new_password)
    await db.commit()
    return {"message": "Password changed successfully."}

@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=2),
    role: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Поиск пользователей по имени или email"""
    stmt = select(User).where(
        or_(
            User.full_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%")
        )
    )
    if role:
        stmt = stmt.where(User.role == role)

    stmt = stmt.limit(20)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return [
        {"id": u.id, "full_name": u.full_name, "role": u.role}
        for u in users
    ]