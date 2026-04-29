from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User, UserRole
from db.models.study_group import StudyGroup
from db.models.assignment import Assignment
from db.models.membership import GroupMembership
from db.models.grade import Grade
from app.schemas import AssignmentCreate, AssignmentResponse, GradeCreate, GradeResponse
from app.dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/{group_id}", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    group_id: int,
    payload: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Учитель или школа создаёт задание для группы"""
    if not current_user.can_create_groups:
        raise HTTPException(status_code=403, detail="Only teachers and schools can create assignments.")

    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    assignment = Assignment(
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        group_id=group_id,
        creator_id=current_user.id
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return {"message": "Assignment created successfully.", "id": assignment.id}


@router.get("/{group_id}", response_model=list[AssignmentResponse])
async def list_assignments(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Список заданий группы — только для членов группы"""
    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    # Проверяем что пользователь состоит в группе
    if current_user.role == UserRole.student:
        membership = await db.execute(
            select(GroupMembership).where(
                GroupMembership.user_id == current_user.id,
                GroupMembership.group_id == group_id
            )
        )
        if not membership.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="You are not a member of this group.")

    result = await db.execute(
        select(Assignment).where(Assignment.group_id == group_id)
    )
    return result.scalars().all()


@router.post("/{assignment_id}/grade", status_code=status.HTTP_201_CREATED)
async def grade_student(
    assignment_id: int,
    payload: GradeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Учитель или школа ставит оценку ученику"""
    if not current_user.can_create_groups:
        raise HTTPException(status_code=403, detail="Only teachers and schools can grade.")

    assignment = await db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    # Проверяем что такой оценки ещё нет
    existing = await db.execute(
        select(Grade).where(
            Grade.assignment_id == assignment_id,
            Grade.student_id == payload.student_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Student already graded for this assignment.")

    grade = Grade(
        assignment_id=assignment_id,
        student_id=payload.student_id,
        grader_id=current_user.id,
        score=payload.score,
        comment=payload.comment
    )
    db.add(grade)
    await db.commit()
    await db.refresh(grade)
    return {"message": "Grade added successfully.", "id": grade.id}


@router.get("/{assignment_id}/grades", response_model=list[GradeResponse])
async def list_grades(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Список оценок за задание"""
    assignment = await db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    # Ученик видит только свои оценки
    if current_user.role == UserRole.student:
        result = await db.execute(
            select(Grade).where(
                Grade.assignment_id == assignment_id,
                Grade.student_id == current_user.id
            )
        )
    else:
        result = await db.execute(
            select(Grade).where(Grade.assignment_id == assignment_id)
        )

    return result.scalars().all()