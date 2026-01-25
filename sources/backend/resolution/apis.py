import uuid

from backend.auth.dependencies import get_current_active_user
from backend.resolution.schemas import (
    ResolutionCreate,
    ResolutionCreateInternal,
    ResolutionDeleteContext,
    ResolutionDeleteInternal,
    ResolutionFilter,
    ResolutionRead,
    ResolutionUpdate,
    ResolutionUpdateContext,
    ResolutionUpdateInternal,
)
from backend.resolution.services import ResolutionService
from backend.user.schemas import UserInternal
from fastapi import APIRouter, Depends
from starlette import status

router = APIRouter(prefix="/api/resolutions", tags=["resolution"])


@router.post("", response_model=ResolutionRead)
async def create_resolution(
    resolution: ResolutionCreate, user: UserInternal = Depends(get_current_active_user)
) -> ResolutionRead:
    resolution_internal = ResolutionCreateInternal.model_validate(
        {**resolution.model_dump(exclude_unset=True), "owner_id": user.id}
    )

    return await ResolutionService().create(resolution_internal)


@router.get("/{resolution_id}", response_model=ResolutionRead)
async def get_resolution(
    resolution_id: uuid.UUID, user: UserInternal = Depends(get_current_active_user)
) -> ResolutionRead:
    return await ResolutionService().retrieve(resolution_id)


@router.get("", response_model=list[ResolutionRead])
async def list_resolutions(
    question_id: uuid.UUID | None = None,
    user: UserInternal = Depends(get_current_active_user),
) -> list[ResolutionRead]:
    resolution_filter = ResolutionFilter(question_id=question_id)
    return await ResolutionService().list(resolution_filter)


@router.patch("/{resolution_id}", response_model=ResolutionRead)
async def update_resolution(
    resolution_id: uuid.UUID,
    resolution: ResolutionUpdate,
    user: UserInternal = Depends(get_current_active_user),
) -> ResolutionRead:
    resolution_update_internal = ResolutionUpdateInternal.model_validate(
        {
            **resolution.model_dump(exclude_unset=True),
            "context": ResolutionUpdateContext(id=resolution_id, user_id=user.id),
        }
    )
    return await ResolutionService().update(resolution_update_internal)


@router.delete(path="/{resolution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resolution(resolution_id: uuid.UUID, user: UserInternal = Depends(get_current_active_user)) -> None:
    resolution_delete_internal = ResolutionDeleteInternal(
        id=resolution_id, context=ResolutionDeleteContext(user_id=user.id)
    )
    await ResolutionService().delete(resolution_delete_internal)
