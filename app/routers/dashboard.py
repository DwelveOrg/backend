from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User
from db.models.study_group import StudyGroup
from db.models.membership import GroupMembership
from db.models.submission import TestSubmission
from app.schemas import DashboardResponse
from app.dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
async def dashboard(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role == "teacher":
        stmt = select(StudyGroup).where(StudyGroup.owner_id == current_user.id)
        result = await db.execute(stmt)
        my_groups = result.scalars().all()

        return {
            "user": current_user,
            "groups_created": my_groups
        }

    # Студент
    sub_stmt = select(TestSubmission).where(TestSubmission.user_id == current_user.id)
    sub_res = await db.execute(sub_stmt)
    submissions = sub_res.scalars().all()

    group_stmt = (
        select(StudyGroup)
        .join(GroupMembership)
        .where(GroupMembership.user_id == current_user.id)
    )
    group_res = await db.execute(group_stmt)
    joined_groups = group_res.scalars().all()

    return {
        "user": current_user,
        "submissions": submissions,
        "groups_joined": joined_groups
    }