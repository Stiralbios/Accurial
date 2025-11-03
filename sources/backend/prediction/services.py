import uuid
from datetime import datetime, timezone

from backend.exceptions import PredictionNotAllowedProblem, PredictionNotFoundProblem, UserNotAllowedProblem
from backend.prediction.constants import PredictionStatus
from backend.prediction.schemas import (
    PredictionCreateInternal,
    PredictionFilter,
    PredictionInternal,
    PredictionUpdateInternal,
)
from backend.prediction.stores import PredictionStore


class PredictionService:
    def __init__(self) -> None:
        self.store = PredictionStore

    async def retrieve(self, prediction_uuid: uuid.UUID) -> PredictionInternal:
        prediction = await self.store.retrieve(prediction_uuid)
        if prediction is None:
            raise PredictionNotFoundProblem(f"Prediction {prediction_uuid} not found")
        return prediction

    async def create(self, prediction: PredictionCreateInternal) -> PredictionInternal:
        return await self.store.create(prediction)

    async def list(
        self,
        prediction_filter: PredictionFilter,
    ) -> list[PredictionInternal]:
        return await self.store.list(prediction_filter)

    async def update(self, prediction: PredictionUpdateInternal) -> PredictionInternal:
        prediction_retrieved = await self.store.retrieve(prediction.context.id)
        await self._ensure_update_is_possible(prediction, prediction_retrieved)

        if (
            prediction_retrieved
            and prediction_retrieved.status == PredictionStatus.DRAFT
            and prediction.status == PredictionStatus.PUBLISHED
        ):
            prediction.published_at = datetime.now(timezone.utc)

        return await self.store.update(prediction)

    async def _ensure_update_is_possible(
        self, prediction_update: PredictionUpdateInternal, prediction_retrieved: PredictionInternal | None
    ) -> None:
        if not prediction_retrieved:
            raise PredictionNotFoundProblem(f"Prediction {prediction_update.context.id} does not exist.")
        if prediction_update.context.user_id != prediction_retrieved.owner_id:
            raise UserNotAllowedProblem(
                f"User {prediction_update.context.user_id} is "
                f"not allowed to update prediction {prediction_update.context.id}."
            )
        if (
            prediction_retrieved
            and prediction_retrieved.status != PredictionStatus.DRAFT
            and any([prediction_update.title, prediction_update.description, prediction_update.value])
        ):
            raise PredictionNotAllowedProblem(
                f"Cannot change the title, description, value for prediction in status {prediction_update.status}."
            )
