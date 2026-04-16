from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from DataBase.db_ext import get_db
from DataBase.user import User


# Это временная функция-заглушка.
# Когда внедришь JWT, она будет декодировать токен и доставать user_id.
async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    # Пример логики (в реальности берем ID из токена):
    # user_id = decode_jwt(token)
    user_id = 1
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user


# Замена role_required
def role_required(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions"
            )
        return current_user

    return role_checker


# Замена premium_required
async def premium_required(current_user: User = Depends(get_current_user)):
    if not current_user.paid_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium membership is required for this action."
        )
    return current_user