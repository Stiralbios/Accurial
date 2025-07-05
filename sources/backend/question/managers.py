import uuid

from backend.exceptions import CustomNotFoundError
from backend.question.schemas import QuestionCreateInternal, QuestionFilter, QuestionInternal, QuestionUpdateInternal
from backend.question.stores import QuestionStore


class QuestionManager:
    @staticmethod
    async def retrieve(question_uuid: uuid.UUID) -> QuestionInternal:
        question = await QuestionStore.retrieve(question_uuid)
        if question is None:
            raise CustomNotFoundError(f"Question {question_uuid} not found")
        return question

    @staticmethod
    async def create(question: QuestionCreateInternal) -> QuestionInternal:
        return await QuestionStore.create(question)

    @staticmethod
    async def list(
        question_filter: QuestionFilter,
    ) -> list[QuestionInternal]:
        return await QuestionStore.list(question_filter)

    @staticmethod
    async def update(question: QuestionUpdateInternal) -> QuestionInternal:
        try:
            return await QuestionStore.update(question)
        except RuntimeError:
            raise CustomNotFoundError(f"Question {question.id} not found")
