from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User
from app.core.security import decode_access_token
from app.core.redis import is_token_blacklisted

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Проверяем blacklist
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user


def role_required(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions."
            )
        return current_user
    return role_checker


async def premium_required(current_user: User = Depends(get_current_user)):
    if not current_user.paid_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium membership is required for this action."
        )
    return current_user