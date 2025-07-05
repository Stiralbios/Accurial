import uuid

from backend.exceptions import CustomNotAllowedError, CustomNotFoundError
from backend.question.schemas import QuestionCreateInternal, QuestionFilter, QuestionInternal, QuestionUpdateInternal
from backend.question.stores import QuestionStore
from backend.user.schemas import UserInternal


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
    async def update(question: QuestionUpdateInternal, user: UserInternal) -> QuestionInternal:
        question_retrived = await QuestionStore.retrieve(question.id)
        if not question_retrived:
            raise CustomNotFoundError(f"Question {question.id} not found")
        elif user.id != question_retrived.owner_id:
            raise CustomNotAllowedError(
                f"User {user.id} is not allowed to update question {question.id}. "
                f"Owner id: {question_retrived.owner_id}"
            )

        return await QuestionStore.update(question)
