import uuid

from backend.exceptions import (
    QuestionNotFoundProblem,
    ResolutionNotAllowedProblem,
    ResolutionNotFoundProblem,
    UserNotAllowedProblem,
)
from backend.question.constants import QuestionStatus
from backend.question.schemas import QuestionUpdateContext, QuestionUpdateInternal
from backend.question.stores import QuestionStore
from backend.resolution.schemas import (
    ResolutionCreateInternal,
    ResolutionDeleteInternal,
    ResolutionFilter,
    ResolutionInternal,
    ResolutionUpdateInternal,
)
from backend.resolution.stores import ResolutionStore


class ResolutionService:
    def __init__(self) -> None:
        self.store = ResolutionStore
        self.question_store = QuestionStore

    async def retrieve(self, resolution_uuid: uuid.UUID) -> ResolutionInternal:
        resolution = await self.store.retrieve(resolution_uuid)
        if resolution is None:
            raise ResolutionNotFoundProblem(f"Resolution {resolution_uuid} not found")
        return resolution

    async def create(self, resolution: ResolutionCreateInternal) -> ResolutionInternal:
        question = await self.question_store.retrieve(resolution.question_id)

        if question is None:
            raise QuestionNotFoundProblem(f"Question {resolution.question_id} not found")
        if question.owner_id != resolution.owner_id:
            raise UserNotAllowedProblem(
                f"User {resolution.owner_id} is not allowed to create a resolution for question {question.id}."
            )

        if question.status not in [QuestionStatus.OPEN]:
            raise ResolutionNotAllowedProblem(
                f"Question {resolution.question_id} must be in OPEN or CLOSED status to be resolved"
            )

        created_resolution = await self.store.create(resolution)

        question_update_context = QuestionUpdateContext(id=question.id, user_id=resolution.owner_id)
        question_update = QuestionUpdateInternal(
            context=question_update_context,
            status=QuestionStatus.CLOSED,
        )
        await self.question_store.update(question_update)

        return created_resolution

    async def list(
        self,
        resolution_filter: ResolutionFilter,
    ) -> list[ResolutionInternal]:
        return await self.store.list(resolution_filter)

    async def update(self, resolution: ResolutionUpdateInternal) -> ResolutionInternal:
        resolution_retrieved = await self.store.retrieve(resolution.context.id)
        if resolution_retrieved:
            if resolution.context.user_id != resolution_retrieved.owner_id:
                raise UserNotAllowedProblem(
                    f"User {resolution.context.user_id} is not allowed to update resolution {resolution.context.id}."
                )
        return await self.store.update(resolution)

    async def delete(self, resolution: ResolutionDeleteInternal) -> None:
        resolution_retrieved = await self.store.retrieve(resolution.id)
        if resolution_retrieved:
            if resolution.context.user_id != resolution_retrieved.owner_id:
                raise UserNotAllowedProblem(
                    f"User {resolution.context.user_id} is not allowed to delete resolution {resolution.id}."
                )
        await self.store.delete(resolution.id)
        return None
