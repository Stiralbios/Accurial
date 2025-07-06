import uuid

from backend.exceptions import CustomNotAllowedError, CustomNotFoundError
from backend.question.schemas import QuestionCreateInternal, QuestionFilter, QuestionInternal, QuestionUpdateInternal
from backend.question.stores import QuestionStore


class QuestionManager:
    def __init__(self, store: QuestionStore = QuestionStore) -> None:
        self.store = store

    async def retrieve(self, question_uuid: uuid.UUID) -> QuestionInternal:
        question = await self.store.retrieve(question_uuid)
        if question is None:
            raise CustomNotFoundError(f"Question {question_uuid} not found")
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
        if not question_retrieved:
            raise CustomNotFoundError(f"Question {question.context.id} not found")
        elif question.context.user_id != question_retrieved.owner_id:
            raise CustomNotAllowedError(
                f"User {question.context.user_id} is not allowed to update question {question.context.id}."
            )

        return await self.store.update(question)
