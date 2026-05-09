# Data Flow

How requests flow through the Accurial backend.

## Request Lifecycle

```
HTTP Request
    |
    v
FastAPI Router (apis.py)
    |
    v
OAuth2 + JWT Validation (dependencies.py)
    |
    v
External Schema Validation (schemas.py - external)
    |
    v
[API Layer] Convert to Internal Schema
    - Inject user_id
    - Add context (user_id, permissions)
    |
    v
Service Layer (services.py)
    - Validate permissions
    - Validate state transitions
    - Business logic
    |
    v
Store Layer (stores.py)
    - CRUD operations
    - Query execution
    |
    v
Database (database.py)
    - SQLAlchemy ORM
    - PostgreSQL via asyncpg
    |
    v
Response flows back:
    DB -> Store returns Internal Schema
    Store -> Service returns Internal Schema
    Service -> API returns Internal Schema
    API -> Router converts to Read Schema
    Router -> Client receives Read/External Schema
```

## Layer Boundaries

### API Layer Rules

- Receive **external schemas** (`Create`, `Update`, `Filter`) from the client
- Convert to **internal schemas** (`CreateInternal`, `UpdateInternal`) before calling services
- Inject ownership/permission data (e.g., `owner_id = current_user.id`)
- Return **Read schemas** to the client
- May call multiple services only as a last resort

Example - injecting `owner_id`:
```python
question_internal = QuestionCreateInternal.model_validate(
    {**question.model_dump(exclude_unset=True), "owner_id": user.id}
)
```

Example - adding `context`:
```python
class QuestionUpdateContext(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

class QuestionUpdateInternal(QuestionUpdate):
    context: QuestionUpdateContext
```

### Service Layer Rules

- May call **multiple stores** to compose data operations
- **Never calls other services** (extract shared logic to business functions instead)
- Validates permissions using `context` data
- Validates state machine transitions
- Returns internal schemas

### Store Layer Rules

- Writes to **only one model** per store
- Specialized read classes (QueryStore) may read from multiple models
- All methods are `@staticmethod` + `@with_async_session`
- Handles basic `IntegrityError` via `handle_foreign_key_violation`

## Context Pattern

`context` in schemas holds data needed by services for business logic but **not needed by stores** for CRUD:

- `QuestionUpdateContext` carries `id` and `user_id` for permission checks
- `QuestionDeleteContext` carries `user_id`
- Stores ignore `context` fields (excluded via `model_dump(exclude={"context"})`)
- Services use `context` to validate ownership before allowing mutations

## Session Management

The `@with_async_session` decorator in `database.py` handles session lifecycle:

- If a `session: AsyncSession` argument is already provided, uses it directly
- Otherwise, creates a new session with transaction management
- This allows stores to participate in parent transactions when needed

```python
@with_async_session
async def create(session: AsyncSession, ...) -> ...:
    # session is managed automatically
    ...
```
