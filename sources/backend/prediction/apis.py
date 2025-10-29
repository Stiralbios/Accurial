import uuid

from backend.auth.dependencies import get_current_active_user
from backend.prediction.schemas import (
    PredictionCreate,
    PredictionCreateInternal,
    PredictionFilter,
    PredictionRead,
    PredictionUpdate,
    PredictionUpdateContext,
    PredictionUpdateInternal,
)
from backend.prediction.services import PredictionService
from backend.user.schemas import UserInternal
from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends

router = APIRouter(prefix="/api/prediction", tags=["prediction"])


@router.post("", response_model=PredictionRead)
async def create_prediction(
    prediction: PredictionCreate, user: UserInternal = Depends(get_current_active_user)
) -> PredictionRead:
    prediction_internal = PredictionCreateInternal.model_validate(
        {**prediction.model_dump(exclude_unset=True), "owner_id": user.id}
    )
    return await PredictionService().create(prediction_internal)


@router.get(path="/{prediction_id}", response_model=PredictionRead)
async def retrieve_prediction(
    prediction_id: uuid.UUID, user: UserInternal = Depends(get_current_active_user)
) -> PredictionRead:
    return await PredictionService().retrieve(prediction_id)


@router.get(path="/", response_model=list[PredictionRead])
async def list_prediction(
    prediction_filter: PredictionFilter = FilterDepends(PredictionFilter),
    user: UserInternal = Depends(get_current_active_user),
) -> list[PredictionRead]:
    return await PredictionService().list(prediction_filter)


@router.patch(path="/{prediction_id}", response_model=PredictionRead)
async def update_prediction(
    prediction_id: uuid.UUID, prediction: PredictionUpdate, user: UserInternal = Depends(get_current_active_user)
) -> PredictionRead:
    context = PredictionUpdateContext(
        id=prediction_id,
        user_id=user.id,
    )
    prediction_internal = PredictionUpdateInternal.model_validate(
        {**prediction.model_dump(exclude_unset=True), "context": context}
    )
    return await PredictionService().update(prediction_internal)
