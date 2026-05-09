# Database

Guidelines for database design and SQLAlchemy usage in Accurial.

## Connection Setup

Configured in `sources/backend/database.py`:

- **Driver**: `postgresql+psycopg_async`
- **Pool size**: 10 connections
- **Max overflow**: 10 additional connections
- **Pool timeout**: 30 seconds
- **Pool recycle**: 1800 seconds (30 minutes, before PostgreSQL's 1h limit)

## Model Design Rules

### Naming

- Table names: lowercase singular (e.g., `question`, not `questions`)
- Model classes: `<Feature>DO` suffix (e.g., `QuestionDO`, `UserDO`)
- Primary keys: `id` column, UUID type

### Primary Keys

- Use `uuid6.uuid7()` by default for time-ordered UUIDs (better index locality)
- Use `uuid.uuid4()` when randomness is preferred (e.g., `UserDO`)
- Always indexed: `mapped_column(Uuid, primary_key=True, index=True, default=uuid6.uuid7)`

### Relationships

- Use `back_populates` for bidirectional access
- Define relationships on both sides when possible
- Foreign keys are `nullable=False` by default unless explicitly optional
- Relationship names match the related model's relationship attribute

### Column Types

- Strings: use explicit `String(length)` with reasonable limits
- Text: use `String()` (unlimited) for descriptions, content
- JSON data: use `JSONB` for structured values (e.g., prediction values)
- Dates: use `DateTime` with timezone awareness
- Status fields: stored as `String` but validated via `StrEnum` schemas

## Session Management

### `with_async_session` Decorator

Applied to all store methods. Handles session lifecycle automatically:

- Creates a new session with transaction management when called without a session
- Reuses an existing session when one is passed (allows nested transactions)

### Transaction Boundaries

- Each store method is a transaction boundary by default
- Services compose multiple store calls; each call is its own transaction
- For multi-store atomic operations, pass a session explicitly

## Table Creation

Tables are auto-created on startup via `create_db_and_tables()` in `main.py` lifespan. Alembic is a dependency but not actively used for migrations in development.

## Rules Summary

| Rule | Rationale |
|------|-----------|
| One store writes to one model | Prevents tight coupling, enables reuse |
| Use `uuid6.uuid7()` for PKs | Time-ordered UUIDs = better B-tree locality |
| `back_populates` on relationships | Bidirectional navigation, consistency |
| `nullable=False` by default | Explicit opt-in for nullable fields |
| `JSONB` for structured data | PostgreSQL-native, indexable, efficient |
