# Backend Structure

The backend follows a **feature-based** organization pattern. Each feature is a self-contained directory under `sources/backend/<feature>/`.

## Feature Directory Pattern

Every feature follows the same file structure:

```
sources/backend/<feature>/
├── models.py       # SQLAlchemy ORM models (Data Objects)
├── schemas.py      # Pydantic models (validation/serialization)
├── stores.py       # Database CRUD operations
├── services.py     # Business logic layer
├── apis.py         # FastAPI routers and endpoints
├── dependencies.py # FastAPI dependencies (auth, etc.)
└── constants.py    # Enums, constants, state machines
```

## File Responsibilities

### models.py

SQLAlchemy declarative models mapped to PostgreSQL tables.

Example from `question/models.py`:
```python
class QuestionDO(Base):
    __tablename__ = "question"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid6.uuid7)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String())
    status: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
```

Rules:
- Table names are lowercase singular (e.g., `question`, not `questions`)
- Primary keys use `uuid6.uuid7()` by default
- Relationships use `back_populates` for bidirectional access

### schemas.py

Pydantic models for request/response validation.

Schema naming convention:
- `FeatureBase` - Shared fields
- `FeatureRead` - Full representation returned to client
- `FeatureInternal` - Internal representation used between API and Service
- `FeatureCreate` / `FeatureCreateInternal` - Creation input
- `FeatureUpdate` / `FeatureUpdateInternal` - Update input
- `FeatureFilter` - Query filter parameters

Example:
```python
class QuestionRead(QuestionBase):
    id: uuid.UUID
    status: QuestionStatus
    owner_id: uuid.UUID

class QuestionCreateInternal(QuestionCreate):
    status: QuestionStatus = Field(default=QuestionStatus.DRAFT)
    owner_id: uuid.UUID  # injected by API layer
```

### stores.py

Database operations with `with_async_session` decorator for automatic session management.

```python
class QuestionStore:
    @staticmethod
    @with_async_session
    async def create(session: AsyncSession, question: QuestionCreateInternal) -> QuestionInternal:
        orm_object = QuestionDO(**question.model_dump())
        session.add(orm_object)
        await session.flush()
        return QuestionInternal.model_validate(orm_object)
```

Rules:
- Stores are stateless (all methods are `@staticmethod`)
- One store writes to **one model only**
- Complex reads across models belong in specialized **QueryStore** classes
- Use `@with_async_session` for automatic transaction handling

### services.py

Business logic layer. Services may call multiple stores.

Rules:
- Services **may NOT call other services**
- Shared business logic must be extracted to standalone business functions
- Business functions should only call stores (avoid circular loops)
- Services validate permissions and state transitions

Example:
```python
class QuestionService:
    async def update(self, question: QuestionUpdateInternal) -> QuestionInternal:
        # Permission check
        if question.context.user_id != owner_id:
            raise UserNotAllowedProblem(...)
        # State machine validation
        if question.status and not QuestionStatus.can_transition_to(current, new):
            raise QuestionNotAllowedProblem(...)
        return await self.store.update(question)
```

### apis.py

FastAPI routers with endpoints.

Rules:
- Receive **external schemas** from frontend
- Return **external schemas** (`Read`, `Create`) to frontend
- Convert external to **internal schemas** before calling services
- Inject `user_id`, `context` in the API layer
- Use `Depends(get_current_active_user)` for authentication

Example:
```python
@router.post("", response_model=QuestionRead)
async def create_question(
    question: QuestionCreate, user: UserInternal = Depends(get_current_active_user)
) -> QuestionRead:
    question_internal = QuestionCreateInternal.model_validate(
        {**question.model_dump(exclude_unset=True), "owner_id": user.id}
    )
    return await QuestionService().create(question_internal)
```

### constants.py

Enums and state machine definitions. State machines inherit from `StatusFSM`.

Example:
```python
class QuestionStatus(StatusFSM, StrEnum):
    DRAFT = auto()
    OPEN = auto()
    CLOSED = auto()
    ARCHIVED = auto()

    @classmethod
    def _get_transitions(cls) -> dict[Self, list[Self]]:
        return {
            cls.DRAFT: [cls.OPEN],
            cls.OPEN: [cls.CLOSED, cls.ARCHIVED],
            cls.CLOSED: [cls.ARCHIVED],
            cls.ARCHIVED: [],
        }
```

## Feature List

| Feature | Status | Description |
|---------|--------|-------------|
| `auth` | Active | JWT login/token generation |
| `user` | Active | User CRUD, registration |
| `question` | Active | Forecasting questions (draft -> open -> closed -> archived) |
| `prediction` | Active | User forecasts with values (status: draft -> published -> closed) |
| `resolution` | Active | Question resolutions with values |
| `debug` | Active | Healthcheck endpoint |

## Test Structure

Tests mirror the backend structure:

```
tests/backend/
├── conftest.py          # Test database setup, fixtures
├── config.py
├── <feature>/
│   ├── factories.py     # Factory Boy factories for model creation
│   └── test_apis.py     # API integration tests
```

Each test file has an equivalent in `sources/backend/<feature>/`.
