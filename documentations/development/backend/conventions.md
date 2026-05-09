# Conventions

Coding conventions for the Accurial backend.

## Python Style

- **Line length**: 120 characters (enforced by ruff/flake8)
- **Type hints**: Required on all function signatures
- **No inline comments**: Use docstrings for SwaggerUI only
- **No imports inside methods/functions**: All imports at top of file
- **PEP8 compliance**: Enforced by ruff

## Docstrings

Write docstrings for SwaggerUI / OpenAPI documentation:

```python
async def create_question(
    question: QuestionCreate, user: UserInternal = Depends(get_current_active_user)
) -> QuestionRead:
    """Create a new forecasting question."""
    ...
```

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| SQLAlchemy models | `<Feature>DO` | `QuestionDO`, `UserDO` |
| Pydantic schemas | `<Feature><Variant>` | `QuestionRead`, `QuestionCreateInternal` |
| Store classes | `<Feature>Store` | `QuestionStore` |
| Service classes | `<Feature>Service` | `QuestionService` |
| API routers | `<feature>.router` | `question.router` |
| Table names | lowercase singular | `question`, `prediction`, `resolution` |
| Endpoint functions | `<action>_<feature>` | `create_question`, `list_prediction` |

## File Organization

- One feature = one directory in `sources/backend/<feature>/`
- Each feature has: `models.py`, `schemas.py`, `stores.py`, `services.py`, `apis.py`, `constants.py`
- `dependencies.py` only if auth or other FastAPI deps are needed
- Shared utilities go in `sources/backend/utils/`

## Architecture Rules

1. **Stores write to one model only**
2. **Services may call multiple stores**
3. **Services never call other services**
4. **Business logic shared across services** should be extracted to standalone functions that call stores
5. **API may call multiple services** only as last resort
6. **API converts** external schemas to internal before passing to services
7. **Internal schemas** contain `context` for business logic, `owner_id` for ownership

## Schema Rules

- `Base` = shared fields
- `Read` = full representation for API responses
- `Internal` = used between API, Service, and Store
- `Create` = request body for POST
- `CreateInternal` = adds default values + `owner_id`
- `Update` = all Optional, with `prevent_explicit_none` validator
- `UpdateInternal` = adds `context`
- `Filter` = query parameters for list endpoints

## Error Handling

- Raise `BaseProblem` subclasses, do not raise raw HTTPException in business logic
- Use `handle_foreign_key_violation()` for integrity errors in stores
- Each entity has `NotFound`, `AlreadyExist`, `NotAllowed` variants

## Testing

- One test file per feature: `tests/backend/<feature>/test_apis.py`
- Factories for test data: `tests/backend/<feature>/factories.py`
- Status FSM tested separately: `test_status_fsm.py`
- Use `client_fixture` for authenticated HTTPX client
