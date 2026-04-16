from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.db_ext import get_db
from DataBase import User, TestSubmission
from .schemas import TestSubmissionCreate, MsgResponse
from .auth_deps import role_required

router = APIRouter(prefix="/test", tags=["tests"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_test(
        payload: TestSubmissionCreate,
        current_user: User = Depends(role_required("student")),
        db: AsyncSession = Depends(get_db)
):
    # Данные уже валидированы Pydantic к этому моменту
    new_submission = TestSubmission(
        title=payload.title,
        topic=payload.topic,
        notes=payload.notes,
        user_id=current_user.id
    )

    db.add(new_submission)
    await db.commit()
    await db.refresh(new_submission)

    return {
        "message": "Submission created successfully.",
        "id": new_submission.id
    }