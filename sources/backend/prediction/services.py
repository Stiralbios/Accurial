import uuid

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
        if prediction_retrieved and prediction.context.user_id != prediction_retrieved.owner_id:
            raise UserNotAllowedProblem(
                f"User {prediction.context.user_id} is not allowed to update prediction {prediction.context.id}."
            )
        if (
            prediction_retrieved
            and prediction_retrieved.status != PredictionStatus.DRAFT
            and any([prediction.title, prediction.description, prediction.value])
        ):
            raise PredictionNotAllowedProblem(
                f"Cannot change the title, description, value for prediction in status {prediction.status}."
            )

        return await self.store.update(prediction)
