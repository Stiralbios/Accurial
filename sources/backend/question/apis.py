import uuid

from backend.exceptions import CustomNotAllowedError, CustomNotFoundError
from backend.question.managers import QuestionManager
from backend.question.schemas import (
    QuestionCreate,
    QuestionCreateInternal,
    QuestionFilter,
    QuestionRead,
    QuestionUpdate,
    QuestionUpdateContext,
    QuestionUpdateInternal,
)
from backend.user.auth import current_active_user
from backend.user.schemas import UserInternal
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from starlette import status

router = APIRouter(prefix="/api/question", tags=["question"])


@router.post("", response_model=QuestionRead)
async def create_question(question: QuestionCreate, user: UserInternal = Depends(current_active_user)) -> QuestionRead:
    question_internal = QuestionCreateInternal(**question.model_dump(exclude_unset=True), owner_id=user.id)
    return await QuestionManager.create(question_internal)


@router.get(path="/{question_id}", response_model=QuestionRead)
async def retrieve_question(question_id: uuid.UUID, user: UserInternal = Depends(current_active_user)) -> QuestionRead:
    try:
        return await QuestionManager.retrieve(question_id)
    except CustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.get(path="/", response_model=list[QuestionRead])
async def list_question(
    question_filter: QuestionFilter = FilterDepends(QuestionFilter), user: UserInternal = Depends(current_active_user)
) -> list[QuestionRead]:
    return await QuestionManager.list(question_filter)


@router.patch(path="/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: uuid.UUID, question: QuestionUpdate, user: UserInternal = Depends(current_active_user)
) -> QuestionRead:
    context = QuestionUpdateContext(
        id=question_id,
        user_id=user.id,
    )
    question_internal = QuestionUpdateInternal(context=context, **question.model_dump(exclude_unset=True))
    try:
        return await QuestionManager.update(question_internal)
    except CustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except CustomNotAllowedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
