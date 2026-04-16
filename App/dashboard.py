from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from DataBase.db_ext import get_db
from DataBase import User, StudyGroup, GroupMembership, TestSubmission
from .schemas import DashboardResponse
# Здесь должна быть твоя функция проверки JWT или сессии
from .auth_deps import get_current_user

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # Базовая информация о пользователе уже есть в current_user
    user_data = current_user

    if current_user.is_teacher:
        # Получаем группы, созданные учителем
        stmt = select(StudyGroup).where(StudyGroup.owner_id == current_user.id)
        result = await db.execute(stmt)
        my_groups = result.scalars().all()

        return {
            "user": user_data,
            "groups_created": my_groups
        }

    # Если студент: получаем сабмишены
    sub_stmt = select(TestSubmission).where(TestSubmission.user_id == current_user.id)
    sub_res = await db.execute(sub_stmt)
    submissions = sub_res.scalars().all()

    # Получаем группы, в которых состоит студент (через Join)
    group_stmt = (
        select(StudyGroup)
        .join(GroupMembership)
        .where(GroupMembership.user_id == current_user.id)
    )
    group_res = await db.execute(group_stmt)
    joined_groups = group_res.scalars().all()

    return {
        "user": user_data,
        "submissions": submissions,
        "groups_joined": joined_groups
    }