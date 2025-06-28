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
from fastapi import APIRouter, HTTPException
from fastapi_filter import FilterDepends
from starlette import status

router = APIRouter(prefix="/api/question", tags=["question"])


# todo add user connected check


@router.post("", response_model=QuestionRead)
async def create_question(question: QuestionCreate) -> QuestionRead:
    question_internal = QuestionCreateInternal(**question.model_dump(exclude_unset=True))
    return await QuestionManager.create(question_internal)


@router.get(path="/{question_id}", response_model=QuestionRead)
async def retrieve_question(question_id: uuid.UUID) -> QuestionRead:
    try:
        return await QuestionManager.retrieve(question_id)
    except CustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.get(path="/", response_model=list[QuestionRead])
async def list_question(
    question_filter: QuestionFilter = FilterDepends(QuestionFilter),
) -> list[QuestionRead]:
    return await QuestionManager.list(question_filter)


@router.patch(path="/{question_id}", response_model=QuestionRead)
async def update_question(question_id: uuid.UUID, question: QuestionUpdate) -> QuestionRead:
    question_internal = QuestionUpdateInternal(id=question_id, **question.model_dump(exclude_unset=True))
    try:
        return await QuestionManager.update(question_internal)
    except CustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
