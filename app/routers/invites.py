import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User, UserRole
from db.models.invite import TeacherInvite, ClassCode
from db.models.study_group import StudyGroup
from db.models.membership import GroupMembership
from db.models.school import SchoolTeacher
from app.schemas import MsgResponse
from app.dependencies.auth_deps import get_current_user
from app.core.email import send_verification_email

router = APIRouter(prefix="/invites", tags=["invites"])


@router.post("/teacher", status_code=status.HTTP_201_CREATED)
async def create_teacher_invite(
    email: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Школа создаёт одноразовый инвайт для учителя"""
    if current_user.role != UserRole.school:
        raise HTTPException(status_code=403, detail="Only schools can invite teachers.")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    invite = TeacherInvite(
        token=token,
        email=email,
        expires_at=expires_at,
        created_by_id=current_user.id
    )
    db.add(invite)
    await db.commit()

    # Отправляем инвайт на email
    invite_link = f"https://yourdomain.com/invite/teacher?token={token}"
    # await send_verification_email(email, f"You are invited as a teacher. Link: {invite_link}")

    return {
        "message": "Teacher invite created.",
        "token": token,
        "expires_at": expires_at
    }


@router.post("/teacher/accept", response_model=MsgResponse)
async def accept_teacher_invite(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    invite = (await db.execute(
        select(TeacherInvite).where(TeacherInvite.token == token)
    )).scalar_one_or_none()

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found.")
    if invite.is_used:
        raise HTTPException(status_code=400, detail="Invite already used.")
    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite expired.")
    if invite.email != current_user.email:
        raise HTTPException(status_code=403, detail="This invite is not for you.")

    current_user.role = UserRole.teacher
    invite.is_used = True
    await db.commit()
    return {"message": "You are now a teacher!"}


@router.post("/class-code", status_code=status.HTTP_201_CREATED)
async def create_class_code(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Учитель или школа создаёт class code для группы"""
    if not current_user.can_create_groups:
        raise HTTPException(status_code=403, detail="Only teachers and schools can create class codes.")

    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    if group.owner_id != current_user.id and current_user.role != UserRole.school:
        raise HTTPException(status_code=403, detail="You are not the owner of this group.")

    # Генерируем короткий код
    code = secrets.token_hex(4).upper()

    class_code = ClassCode(
        code=code,
        group_id=group_id,
        created_by_id=current_user.id
    )
    db.add(class_code)
    await db.commit()

    return {"message": "Class code created.", "code": code}


@router.post("/class-code/join", status_code=status.HTTP_201_CREATED)
async def join_by_class_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Студент вступает в группу по class code"""
    class_code = (await db.execute(
        select(ClassCode).where(ClassCode.code == code)
    )).scalar_one_or_none()

    if not class_code or not class_code.is_active:
        raise HTTPException(status_code=404, detail="Invalid or inactive class code.")

    # Проверяем что ещё не в группе
    existing = (await db.execute(
        select(GroupMembership).where(
            GroupMembership.user_id == current_user.id,
            GroupMembership.group_id == class_code.group_id
        )
    )).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=409, detail="You already joined this group.")

    # Меняем роль с pending на student
    if current_user.role == UserRole.pending:
        current_user.role = UserRole.student
    elif current_user.role == UserRole.teacher:
        pass  # учитель может вступать в группы без смены роли
    elif current_user.role not in (UserRole.student,):
        raise HTTPException(status_code=403, detail="You cannot join a group with your current role.")

    membership = GroupMembership(
        user_id=current_user.id,
        group_id=class_code.group_id
    )
    db.add(membership)
    await db.commit()

    return {"message": "Successfully joined the group via class code."}

@router.post("/teacher/accept", response_model=MsgResponse)
async def accept_teacher_invite(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Пользователь принимает инвайт и становится учителем данной школы"""
    invite = (await db.execute(
        select(TeacherInvite).where(TeacherInvite.token == token)
    )).scalar_one_or_none()

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found.")
    if invite.is_used:
        raise HTTPException(status_code=400, detail="Invite already used.")
    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite expired.")
    if invite.email != current_user.email:
        raise HTTPException(status_code=403, detail="This invite is not for you.")

    # Меняем роль на teacher (если ещё не teacher/school)
    if current_user.role == UserRole.pending:
        current_user.role = UserRole.teacher

    # Создаём связь школа-учитель (если ещё нет)
    existing_link = (await db.execute(
        select(SchoolTeacher).where(
            SchoolTeacher.school_id == invite.created_by_id,
            SchoolTeacher.teacher_id == current_user.id
        )
    )).scalar_one_or_none()

    if not existing_link:
        link = SchoolTeacher(
            school_id=invite.created_by_id,
            teacher_id=current_user.id
        )
        db.add(link)

    invite.is_used = True
    await db.commit()

    return {"message": "You are now a teacher at this school!"}