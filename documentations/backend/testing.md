# Testing

Backend testing with pytest.

## Test Configuration

- **Framework**: pytest with async support (`pytest-asyncio`)
- **Mode**: `auto` (async fixtures/tests detected automatically)
- **Coverage**: pytest-cov with 5% minimum (`pyproject.toml`)
- **Factories**: factory-boy
- **Mocking**: pytest-mock
- **Time freezing**: freezegun

## Test Database

Tests use a separate PostgreSQL instance at `localhost:5434`.

### Database Setup (`conftest.py`)

- Uses `psycopg_async` engine
- **TRUNCATE** all tables between tests (faster than drop/create)
- Falls back to drop/create if new tables/columns are added
- Patches `backend.database._engine_instance` and `_async_sessionmaker` for isolation

### Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `mock_engine_and_session` | function | Isolated DB engine, truncates tables |
| `client_fixture` | function | HTTPX async client with auth override |
| `anyio_backend` | session | Fixes double test issue with anyio |

### Auth Override

Tests automatically create an authenticated admin user:
```python
admin@test.lan / password (hashed)
```

The `client_fixture` overrides `get_current_active_user` dependency for tests. Can be disabled with `@pytest.mark.parametrize("client_fixture", [False], indirect=True)`.

## Test File Structure

```
tests/backend/
├── conftest.py
├── config.py
├── debug/
│   └── test_apis.py
├── user/
│   ├── facories.py
│   └── test_apis.py
├── question/
│   ├── factories.py
│   └── test_apis.py
├── prediction/
│   ├── factories.py
│   ├── test_apis.py
│   └── test_status_fsm.py
└── resolution/
    ├── factories.py
    └── test_apis.py
```

## Running Tests

```bash
# All tests
make test

# With coverage
poetry run pytest --cov

# Specific file
poetry run pytest tests/backend/question/test_apis.py

# Specific test
poetry run pytest tests/backend/question/test_apis.py::test_create_question -v
```

## Status FSM Tests

Each feature with a status state machine has `test_status_fsm.py`:

```python
# Example: tests/backend/prediction/test_status_fsm.py
# Tests valid/invalid transitions for PredictionStatus
```

## Factory Pattern

Factories use `factory_boy` for test data creation:

```python
import factory
from backend.question.models import QuestionDO

class QuestionFactory(factory.Factory):
    class Meta:
        model = QuestionDO

    title = factory.Sequence(lambda n: f"Question {n}")
    description = "Test description"
    status = QuestionStatus.DRAFT
    prediction_type = PredictionType.BINARY
```

## Files

- `tests/backend/conftest.py` - Global fixtures
- `tests/backend/config.py` - Test config
- `tests/backend/<feature>/factories.py` - Feature factories
- `tests/backend/<feature>/test_apis.py` - API tests
