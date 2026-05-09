# Features

Core domain features of the Accurial backend.

## Question

Forecasting questions - the central entity users create and manage.

### Status Lifecycle

```
DRAFT -> OPEN -> CLOSED -> ARCHIVED
              -> ARCHIVED
```

- `DRAFT` - Being composed, not yet visible
- `OPEN` - Accepting predictions
- `CLOSED` - No longer accepting predictions
- `ARCHIVED` - Final state, preserved for history

### Business Rules

- Only the owner can update/delete their questions
- Questions can only be deleted in `DRAFT` status
- Status transitions are validated by the state machine
- Each question has a `prediction_type` (currently `BINARY` only)

### Files

`sources/backend/question/`

## Prediction

User forecasts submitted on questions.

### Status Lifecycle

```
DRAFT -> PUBLISHED -> CLOSED
```

- `DRAFT` - Being composed
- `PUBLISHED` - Visible and counted
- `CLOSED` - Finalized

### Business Rules

- Predictions store their value as JSONB (e.g., probability for binary predictions)
- `published_at` is set when transitioning to `PUBLISHED`
- Belongs to both a user and a question

### Files

`sources/backend/prediction/`

## Resolution

The actual outcome of a question, used for scoring and calibration.

### Business Rules

- One question has at most one resolution (unique FK constraint)
- Contains the resolved `value`, `date`, and a `description`
- Enables Brier score calculation and calibration tracking

### Files

`sources/backend/resolution/`

## Common Patterns

All three features follow the same architecture:

- Status state machine via `StatusFSM` base class
- CRUD endpoints with auth
- Ownership checks in services
- Filter support on list endpoints
- Full test coverage with factories
