# AGENTS.md

Guidelines for agentic coding assistants working on this repository.

## Project Overview

**Accurial** is a self-hosted web application for personal forecasting practice, inspired by the principles in *"Superforecasting: The Art and Science of Prediction"* by Philip Tetlock and Dan Gardner. Users create prediction questions, make probabilistic forecasts with confidence intervals, and track their calibration over time to improve their predictive abilities.

### Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 (async PostgreSQL via asyncpg) — Python 3.13
- **Frontend**: React 19 + TypeScript + Vite
- **Auth**: JWT via OAuth2 Password Bearer, Argon2id password hashing
- **Database**: PostgreSQL with connection pooling
- **Testing**: pytest with async support, factory-boy, pytest-mock, freezegun
- **Infra**: devbox, Poetry, Docker Compose
- **Code Quality**: ruff, flake8, mypy, bandit, pre-commit hooks

## General Agent Rules

- Use the **same language** as the user
- **Use tools** to create and modify files — never describe changes in text only
- Make **minimal changes** to achieve the goal
- Follow the **existing code style** of the project
- **Always** perform commits through the [`git-commit-pusher`](.opencode/agents/git-commit-pusher.md) agent. Only the user should invoke git-commit-pusher.
- **Never install** or delete anything outside the working directory without confirmation

## Backend Critical Conventions

- **Line length**: 120 characters (enforced by ruff and flake8)
- **Type hints**: Required on all function signatures
- **No inline comments** — use docstrings for SwaggerUI only
- **No imports inside methods or functions** — all imports at top of file
- **Layer rules**:
  - **Stores** write to one model only (QueryStore may do complex reads across models)
  - **Services** may call multiple stores but **never call other services**
  - **API** may call multiple services only as a last resort
  - **API** converts external schemas to internal before passing to services
  - **Internal schemas** carry `context` (for business logic) and `owner_id`
- **Error handling**: Raise `BaseProblem` subclasses — never raw `HTTPException` in business logic
- **Naming conventions**:
  | Type | Pattern | Example |
  |------|---------|---------|
  | SQLAlchemy models | `<Feature>DO` | `QuestionDO`, `UserDO` |
  | Pydantic schemas | `<Feature><Variant>` | `QuestionRead`, `QuestionCreateInternal` |
  | Store classes | `<Feature>Store` | `QuestionStore` |
  | Service classes | `<Feature>Service` | `QuestionService` |
  | Table names | lowercase singular | `question`, `prediction`, `resolution` |
- **Testing**: One test file per feature in `tests/backend/<feature>/test_apis.py` — factories in `tests/backend/<feature>/factories.py`

## Common Commands

| Command | Description |
|---------|-------------|
| `devbox shell` | Enter the development environment |
| `poetry install` | Install Python dependencies |
| `make run_dev_env` | Start Docker dev stack (API + PostgreSQL + pgweb) |
| `make run_dev_frontend` | Start the Vite frontend dev server |
| `make test` | Run the backend test suite |
| `make run_precommit` | Run all code quality checks |
| `make clean_dev_env` | Stop and remove Docker containers |

## Documentation

All detailed documentation lives in the [`documentations/`](./documentations/) directory.

| Document | Purpose |
|---|---|
| `.opencode/agents/backend.md` | Backend agent deep-dive (conventions, patterns, architecture guidelines) |
| `.opencode/agents/git-commit-pusher.md` | Git workflow conventions for committing and pushing |
| `documentations/architecture/overview.md` | High-level system design |
| `documentations/architecture/backend-structure.md` | Feature directory pattern and file responsibilities |
| `documentations/architecture/data-flow.md` | Request lifecycle and layer boundaries |
| `documentations/architecture/schema-strategy.md` | Internal vs external schemas, context pattern |
| `documentations/architecture/database.md` | Database design rules, model naming, session management |
| `documentations/development/backend/conventions.md` | Coding conventions, naming, file organization |
| `documentations/development/backend/adding-a-feature.md` | Step-by-step TDD guide for adding a new backend feature |
| `documentations/development/tooling.md` | Makefile commands, ruff, mypy, bandit, pre-commit |
| `documentations/backend/testing.md` | pytest setup, fixtures, factories, running tests |
| `documentations/backend/error-handling.md` | Exception hierarchy, BaseProblem, adding new exceptions |
| `documentations/backend/features.md` | Backend features and internals |
| `documentations/backend/auth.md` | Authentication and authorization |
| `documentations/backend/user.md` | User management |
| `documentations/frontend/setup.md` | Frontend tech stack, project structure, dev server |
| `documentations/getting-started/index.md` | Environment setup and first run |
| `documentations/deployment/docker.md` | Docker Compose development stack |
| `documentations/api/openapi.md` | SwaggerUI, endpoint prefixes, OpenAPI schema |
