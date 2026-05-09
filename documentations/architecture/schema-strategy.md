# Schema Strategy

How request/response schemas are organized in Accurial.

## Schema Naming Convention

Every feature defines the following schema types:

| Type | Purpose | Used By |
|------|---------|---------|
| `FeatureBase` | Shared fields between all schemas | Inherited |
| `FeatureRead` | Full object returned to clients | API responses |
| `FeatureInternal` | Superset used internally (API -> Service -> Store) | Internal flow |
| `FeatureCreate` | Request body for creation | Client POST |
| `FeatureCreateInternal` | Internal creation with injected fields | API -> Service |
| `FeatureUpdate` | Request body for updates (all Optional) | Client PATCH |
| `FeatureUpdateInternal` | Internal update with context | API -> Service |
| `FeatureFilter` | Query parameters for listing | GET /?params |

## External vs Internal

### External Schemas

- Sent/received between frontend and backend
- Do not contain internal-only fields (e.g., `owner_id`)
- Validated by FastAPI's request/response handling

Example - `QuestionCreate` (external):
```python
class QuestionCreate(QuestionBase):
    model_config = ConfigDict(extra="forbid")
    # Only contains fields the user provides
```

### Internal Schemas

- Used in service and store layers
- May contain fields injected by the API layer
- Include `context` for business logic

Example - `QuestionCreateInternal` (internal):
```python
class QuestionCreateInternal(QuestionCreate):
    status: QuestionStatus = Field(default=QuestionStatus.DRAFT)
    owner_id: uuid.UUID = Field(default=None)  # injected by API
```

## Context Pattern

The API layer injects a `context` object into internal schemas to pass operation metadata to services:

Example:
```python
class QuestionUpdateContext(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

class QuestionUpdateInternal(QuestionUpdate):
    context: QuestionUpdateContext
```

`context` is never used by stores. It is excluded during `model_dump()`:
```python
for field, value in question_update.model_dump(exclude_unset=True, exclude={"context"}).items():
    setattr(orm_object, field, value)
```

## Common Patterns

### Preventing Explicit None in Updates

Example - Update schemas use `field_validator` to reject explicit `None` values:
```python
@field_validator("title", "description", mode="before")
def prevent_explicit_none(cls, value: Any) -> Any:
    if value is None:
        raise ValueError("Explicit None is not allowed for this field")
    return value
```

This ensures PATCH only updates specified fields while preventing accidental clearing.

### Factory Pattern for Conversion

Example - The API layer combines external schema with injected fields using `model_validate`:
```python
question_internal = QuestionCreateInternal.model_validate(
    {**question.model_dump(exclude_unset=True), "owner_id": user.id}
)
```

### Filter Schemas

Example - Filters inherit from `fastapi_filter.contrib.sqlalchemy.Filter`:
```python
class QuestionFilter(Filter):
    status: Optional[QuestionStatus] = Field(default=None)
    prediction_type: Optional[PredictionType] = Field(default=None)

    class Constants(Filter.Constants):
        model = QuestionDO
```

Example - Used in list endpoints with `FilterDepends`:
```python
@router.get(path="/", response_model=list[QuestionRead])
async def list_question(
    question_filter: QuestionFilter = FilterDepends(QuestionFilter),
    ...
) -> list[QuestionRead]: ...
```
