# Adding a Backend Feature

Step-by-step guide for adding a new backend feature, following a TDD workflow.

## TDD Workflow

The recommended approach is to write tests first, then implement the feature.

```
1. Write failing tests
2. Implement the minimal code to pass
3. Refactor
4. Repeat
```

## Checklist

### 1. Write Tests First

```bash
mkdir tests/backend/<featurename>
touch tests/backend/<featurename>/__init__.py
```

Create `factories.py` and `test_apis.py`. Start with the API contract you want:

```python
# tests/backend/featurename/test_apis.py
async def test_create_feature(client_fixture):
    response = await client_fixture.post("/api/featurename", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

Run the test to confirm it fails:
```bash
poetry run pytest tests/backend/featurename/test_apis.py -v
```

### 2. Define Constants (`constants.py`)

Create enums and state machines:

```python
from enum import StrEnum, auto
from typing import Self
from backend.utils.status import StatusFSM

class FeatureStatus(StatusFSM, StrEnum):
    DRAFT = auto()
    ACTIVE = auto()
    CLOSED = auto()

    @classmethod
    def _get_transitions(cls) -> dict[Self, list[Self]]:
        return {
            cls.DRAFT: [cls.ACTIVE],
            cls.ACTIVE: [cls.CLOSED],
            cls.CLOSED: [],
        }
```

### 3. Define Model (`models.py`)

```python
import uuid
import uuid6
from backend.database import Base
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

class FeatureDO(Base):
    __tablename__ = "featurename"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid6.uuid7)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    owner = relationship("UserDO", back_populates="features")
```

Add relationship to `UserDO` if needed.

### 4. Define Schemas (`schemas.py`)

Follow the naming convention:

```python
import uuid
from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, ConfigDict, Field

class FeatureBase(BaseModel):
    name: str = Field(max_length=255)

class FeatureRead(FeatureBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: FeatureStatus

class FeatureInternal(FeatureRead):
    pass

class FeatureCreate(FeatureBase):
    model_config = ConfigDict(extra="forbid")

class FeatureCreateInternal(FeatureCreate):
    status: FeatureStatus = Field(default=FeatureStatus.DRAFT)
    owner_id: uuid.UUID

class FeatureUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(default=None)
    status: Optional[FeatureStatus] = Field(default=None)

class FeatureUpdateContext(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

class FeatureUpdateInternal(FeatureUpdate):
    context: FeatureUpdateContext

class FeatureFilter(Filter):
    status: Optional[FeatureStatus] = Field(default=None)
```

### 5. Create Store (`stores.py`)

```python
import uuid
from backend.database import with_async_session
from backend.exceptions import FeatureNotFoundProblem
from backend.featurename.models import FeatureDO
from backend.featurename.schemas import FeatureCreateInternal, FeatureFilter, FeatureInternal, FeatureUpdateInternal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class FeatureStore:
    @staticmethod
    @with_async_session
    async def create(session: AsyncSession, feature: FeatureCreateInternal) -> FeatureInternal:
        orm_object = FeatureDO(**feature.model_dump())
        session.add(orm_object)
        await session.flush()
        await session.refresh(orm_object)
        return FeatureInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def retrieve(session: AsyncSession, feature_uuid: uuid.UUID) -> FeatureInternal | None:
        orm_object = await session.get(FeatureDO, feature_uuid)
        return None if orm_object is None else FeatureInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def update(session: AsyncSession, feature_update: FeatureUpdateInternal) -> FeatureInternal:
        orm_object = await session.get(FeatureDO, feature_update.context.id)
        if not orm_object:
            raise FeatureNotFoundProblem(f"Feature with ID {feature_update.context.id} does not exist.")
        for field, value in feature_update.model_dump(exclude_unset=True, exclude={"context"}).items():
            setattr(orm_object, field, value)
        await session.flush()
        await session.refresh(orm_object)
        return FeatureInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def list(session: AsyncSession, feature_filter: FeatureFilter) -> list[FeatureInternal]:
        query = feature_filter.filter(select(FeatureDO))
        res = await session.execute(query)
        return [FeatureInternal.model_validate(orm_object) for orm_object in res.scalars().all()]

    @staticmethod
    @with_async_session
    async def delete(session: AsyncSession, feature_uuid: uuid.UUID) -> None:
        orm_object = await session.get(FeatureDO, feature_uuid)
        if orm_object is None:
            raise FeatureNotFoundProblem(f"Feature with ID {feature_uuid} does not exist.")
        await session.delete(orm_object)
        await session.flush()
```

### 6. Create Service (`services.py`)

```python
import uuid
from backend.exceptions import FeatureNotAllowedProblem, FeatureNotFoundProblem, UserNotAllowedProblem
from backend.featurename.constants import FeatureStatus
from backend.featurename.schemas import FeatureCreateInternal, FeatureDeleteInternal, FeatureFilter, FeatureInternal, FeatureUpdateInternal
from backend.featurename.stores import FeatureStore

class FeatureService:
    def __init__(self) -> None:
        self.store = FeatureStore

    async def retrieve(self, feature_uuid: uuid.UUID) -> FeatureInternal:
        feature = await self.store.retrieve(feature_uuid)
        if feature is None:
            raise FeatureNotFoundProblem(f"Feature {feature_uuid} not found")
        return feature

    async def create(self, feature: FeatureCreateInternal) -> FeatureInternal:
        return await self.store.create(feature)

    async def list(self, feature_filter: FeatureFilter) -> list[FeatureInternal]:
        return await self.store.list(feature_filter)

    async def update(self, feature: FeatureUpdateInternal) -> FeatureInternal:
        feature_retrieved = await self.store.retrieve(feature.context.id)
        if feature_retrieved and feature.context.user_id != feature_retrieved.owner_id:
            raise UserNotAllowedProblem("User not allowed to update feature")
        if feature.status and feature_retrieved.status != feature.status:
            if not FeatureStatus.can_transition_to(feature_retrieved.status, feature.status):
                raise FeatureNotAllowedProblem("Invalid status transition")
        return await self.store.update(feature)

    async def delete(self, feature: FeatureDeleteInternal) -> None:
        feature_retrieved = await self.store.retrieve(feature.id)
        if feature_retrieved and feature.context.user_id != feature_retrieved.owner_id:
            raise UserNotAllowedProblem("User not allowed to delete feature")
        await self.store.delete(feature.id)
```

### 7. Create API Router (`apis.py`)

```python
import uuid
from backend.auth.dependencies import get_current_active_user
from backend.featurename.schemas import FeatureCreate, FeatureCreateInternal, FeatureRead, FeatureUpdate, FeatureUpdateContext, FeatureUpdateInternal, FeatureFilter
from backend.featurename.services import FeatureService
from backend.user.schemas import UserInternal
from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from starlette import status

router = APIRouter(prefix="/api/featurename", tags=["featurename"])

@router.post("", response_model=FeatureRead)
async def create_feature(feature: FeatureCreate, user: UserInternal = Depends(get_current_active_user)) -> FeatureRead:
    feature_internal = FeatureCreateInternal.model_validate(
        {**feature.model_dump(exclude_unset=True), "owner_id": user.id}
    )
    return await FeatureService().create(feature_internal)

@router.get("/{feature_id}", response_model=FeatureRead)
async def retrieve_feature(feature_id: uuid.UUID, user: UserInternal = Depends(get_current_active_user)) -> FeatureRead:
    return await FeatureService().retrieve(feature_id)

@router.get("/", response_model=list[FeatureRead])
async def list_feature(feature_filter: FeatureFilter = FilterDepends(FeatureFilter), user: UserInternal = Depends(get_current_active_user)) -> list[FeatureRead]:
    return await FeatureService().list(feature_filter)

@router.patch("/{feature_id}", response_model=FeatureRead)
async def update_feature(feature_id: uuid.UUID, feature: FeatureUpdate, user: UserInternal = Depends(get_current_active_user)) -> FeatureRead:
    feature_internal = FeatureUpdateInternal.model_validate(
        {**feature.model_dump(exclude_unset=True), "context": FeatureUpdateContext(id=feature_id, user_id=user.id)}
    )
    return await FeatureService().update(feature_internal)

@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(feature_id: uuid.UUID, user: UserInternal = Depends(get_current_active_user)) -> None:
    await FeatureService().delete(FeatureDeleteInternal(id=feature_id, context=FeatureDeleteContext(user_id=user.id)))
```

### 8. Register Router in `main.py`

```python
from backend.featurename import apis as featurename
app.include_router(featurename.router)
```

### 9. Add Exceptions

Add to `sources/backend/exceptions.py`:
```python
class FeatureNotFoundProblem(BaseProblem): ...
class FeatureAlreadyExistProblem(BaseProblem): ...
class FeatureNotAllowedProblem(BaseProblem): ...
```

### 10. Run Tests and Quality Checks

```bash
make test
make run_precommit
```
