import uuid

from backend.exceptions import CustomNotFoundError
from backend.question.managers import QuestionManager
from backend.question.schemas import (
    QuestionCreate,
    QuestionCreateInternal,
    QuestionFilter,
    QuestionRead,
    QuestionUpdate,
    QuestionUpdateInternal,
)
from backend.user.auth import current_active_user
from backend.user.models import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from starlette import status

router = APIRouter(prefix="/api/question", tags=["question"])


@router.post("", response_model=QuestionRead)
async def create_question(question: QuestionCreate, user: User = Depends(current_active_user)) -> QuestionRead:
    question_internal = QuestionCreateInternal(**question.model_dump(exclude_unset=True))
    return await QuestionManager.create(question_internal)


@router.get(path="/{question_id}", response_model=QuestionRead)
async def retrieve_question(question_id: uuid.UUID, user: User = Depends(current_active_user)) -> QuestionRead:
    try:
        return await QuestionManager.retrieve(question_id)
    except CustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.get(path="/", response_model=list[QuestionRead])
async def list_question(
    question_filter: QuestionFilter = FilterDepends(QuestionFilter), user: User = Depends(current_active_user)
) -> list[QuestionRead]:
    return await QuestionManager.list(question_filter)


@router.patch(path="/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: uuid.UUID, question: QuestionUpdate, user: User = Depends(current_active_user)
) -> QuestionRead:
    question_internal = QuestionUpdateInternal(id=question_id, **question.model_dump(exclude_unset=True))
    try:
        return await QuestionManager.update(question_internal)
    except CustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
