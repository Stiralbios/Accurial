import uuid

from backend.exceptions import QuestionNotAllowedProblem, QuestionNotFoundProblem, UserNotAllowedProblem
from backend.question.constants import QuestionStatus
from backend.question.schemas import (
    QuestionCreateInternal,
    QuestionDeleteInternal,
    QuestionFilter,
    QuestionInternal,
    QuestionUpdateInternal,
)
from backend.question.stores import QuestionStore


class QuestionService:
    def __init__(self) -> None:
        self.store = QuestionStore

    async def retrieve(self, question_uuid: uuid.UUID) -> QuestionInternal:
        question = await self.store.retrieve(question_uuid)
        if question is None:
            raise QuestionNotFoundProblem(f"Question {question_uuid} not found")
        return question

    async def create(self, question: QuestionCreateInternal) -> QuestionInternal:
        return await self.store.create(question)

    async def list(
        self,
        question_filter: QuestionFilter,
    ) -> list[QuestionInternal]:
        return await self.store.list(question_filter)

    async def update(self, question: QuestionUpdateInternal) -> QuestionInternal:
        question_retrieved = await self.store.retrieve(question.context.id)
        if question_retrieved and question.context.user_id != question_retrieved.owner_id:
            raise UserNotAllowedProblem(
                f"User {question.context.user_id} is not allowed to update question {question.context.id}."
            )
        return await self.store.update(question)

    async def delete(self, question: QuestionDeleteInternal) -> None:
        question_retrieved = await self.store.retrieve(question.id)
        if question_retrieved:
            if question.context.user_id != question_retrieved.owner_id:
                raise UserNotAllowedProblem(
                    f"User {question.context.user_id} is not allowed to delete question {question.id}."
                )
            if question_retrieved.status != QuestionStatus.DRAFT:
                raise QuestionNotAllowedProblem(f"Question {question.id} isn't in draft, you should archive it")
        await self.store.delete(question.id)
        return None
