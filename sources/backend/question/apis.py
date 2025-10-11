import uuid

from backend.auth.dependencies import get_current_active_user
from backend.question.schemas import (
    QuestionCreate,
    QuestionCreateInternal,
    QuestionDeleteContext,
    QuestionDeleteInternal,
    QuestionFilter,
    QuestionRead,
    QuestionUpdate,
    QuestionUpdateContext,
    QuestionUpdateInternal,
)
from backend.question.services import QuestionService
from backend.user.schemas import UserInternal
from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from starlette import status

router = APIRouter(prefix="/api/question", tags=["question"])


@router.post("", response_model=QuestionRead)
async def create_question(
    question: QuestionCreate, user: UserInternal = Depends(get_current_active_user)
) -> QuestionRead:
    question_internal = QuestionCreateInternal.model_validate(
        {**question.model_dump(exclude_unset=True), "owner_id": user.id}
    )
    return await QuestionService().create(question_internal)


@router.get(path="/{question_id}", response_model=QuestionRead)
async def retrieve_question(
    question_id: uuid.UUID, user: UserInternal = Depends(get_current_active_user)
) -> QuestionRead:
    return await QuestionService().retrieve(question_id)


@router.get(path="/", response_model=list[QuestionRead])
async def list_question(
    question_filter: QuestionFilter = FilterDepends(QuestionFilter),
    user: UserInternal = Depends(get_current_active_user),
) -> list[QuestionRead]:
    return await QuestionService().list(question_filter)


@router.patch(path="/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: uuid.UUID, question: QuestionUpdate, user: UserInternal = Depends(get_current_active_user)
) -> QuestionRead:
    context = QuestionUpdateContext(
        id=question_id,
        user_id=user.id,
    )
    question_internal = QuestionUpdateInternal.model_validate(
        {**question.model_dump(exclude_unset=True), "context": context}
    )
    return await QuestionService().update(question_internal)


@router.delete(path="/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: uuid.UUID, user: UserInternal = Depends(get_current_active_user)):
    question_delete = QuestionDeleteInternal(id=question_id, context=QuestionDeleteContext(user_id=user.id))
    await QuestionService().delete(question_delete)
