from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User, UserRole
from db.models.study_group import StudyGroup
from db.models.membership import GroupMembership
from db.models.submission import TestSubmission
from db.models.assignment import Assignment
from db.models.grade import Grade
from app.schemas import DashboardResponse
from app.dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
async def dashboard(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role in (UserRole.teacher, UserRole.school):
        # Группы созданные учителем/школой
        stmt = select(StudyGroup).where(StudyGroup.owner_id == current_user.id)
        result = await db.execute(stmt)
        my_groups = result.scalars().all()

        # Задания созданные учителем/школой
        assignments_stmt = select(Assignment).where(Assignment.creator_id == current_user.id)
        assignments_res = await db.execute(assignments_stmt)
        my_assignments = assignments_res.scalars().all()

        return {
            "user": current_user,
            "groups_created": my_groups,
            "assignments_created": my_assignments,
        }

    # Студент
    sub_stmt = select(TestSubmission).where(TestSubmission.user_id == current_user.id)
    sub_res = await db.execute(sub_stmt)
    submissions = sub_res.scalars().all()

    # Группы студента
    group_stmt = (
        select(StudyGroup)
        .join(GroupMembership)
        .where(GroupMembership.user_id == current_user.id)
    )
    group_res = await db.execute(group_stmt)
    joined_groups = group_res.scalars().all()

    # Задания из групп студента
    assignments_stmt = (
        select(Assignment)
        .join(GroupMembership, Assignment.group_id == GroupMembership.group_id)
        .where(GroupMembership.user_id == current_user.id)
    )
    assignments_res = await db.execute(assignments_stmt)
    my_assignments = assignments_res.scalars().all()

    # Оценки студента
    grades_stmt = select(Grade).where(Grade.student_id == current_user.id)
    grades_res = await db.execute(grades_stmt)
    my_grades = grades_res.scalars().all()

    return {
        "user": current_user,
        "submissions": submissions,
        "groups_joined": joined_groups,
        "assignments": my_assignments,
        "grades": my_grades,
    }