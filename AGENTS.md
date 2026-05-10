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

## Frontend Critical Conventions

- **Line length**: 120 characters (enforced by ESLint + Prettier)
- **Type safety**: TS `strict: true`. No `any`. Type-only imports where applicable.
- **No default exports** outside route files and Vite config
- **Folder layout**: feature-based under `sources/frontend/app/features/<feature>/` mirroring the backend
- **Layer rules**:
  - **Components** call feature **hooks** only — never `fetch` directly, never the generated client directly
  - **Feature hooks** wrap **Orval-generated** TanStack Query hooks; they may compose multiple generated hooks but **never call hooks of another feature**
  - **Server state** lives in **TanStack Query** only; never mirror it in Zustand
  - **Client state** lives in **Zustand** only; never store auth tokens in JS (httpOnly cookies are the target)
  - **Routes** are thin shells; business logic lives in feature components and hooks
  - **Generated client** (`app/services/api/generated/`) is read-only — regenerate via `npm run generate:api`
- **Forms**: React Hook Form + Zod resolver, schemas in `features/<feature>/schemas.ts`
- **Styling**: Tailwind CSS only; design tokens in `tailwind.config.ts`; no global CSS rules outside `@layer base`
- **Error handling**: backend `BaseProblem` envelope mapped to `ApiError`; per-form `setError`, page-level inline, or global toast
- **Naming conventions**:
  | Type | Pattern | Example |
  |------|---------|---------|
  | Component file | `PascalCase.tsx` | `QuestionList.tsx` |
  | Hook | `use<Feature><Action>` | `useCreateQuestion` |
  | Zod schema | `camelCaseSchema` | `questionCreateSchema` |
  | Type from Zod | `<Feature><Variant>Input` | `QuestionCreateInput` |
  | Zustand store | `use<Concern>Store` | `useUiStore` |
  | Query key namespace | `<feature>Keys` | `questionKeys` |
- **Testing**: One test file per component/hook in `tests/frontend/<feature>/`; MSW handlers in `tests/frontend/handlers/`; factories in `tests/frontend/factories/`

## Common Commands

| Command | Description |
|---------|-------------|
| `devbox shell` | Enter the development environment |
| `poetry install` | Install Python dependencies |
| `make run_dev_env` | Start Docker dev stack (API + PostgreSQL + pgweb) |
| `make run_dev_frontend` | Start the Vite frontend dev server |
| `make test` | Run the backend test suite |
| `make test_frontend` | Run the frontend test suite (Vitest) |
| `make lint_frontend` | Run ESLint on the frontend |
| `make typecheck_frontend` | Run `tsc --noEmit` on the frontend |
| `make generate_frontend_api` | Regenerate the Orval client from `openapi.json` |
| `make run_precommit` | Run all code quality checks |
| `make clean_dev_env` | Stop and remove Docker containers |

## Documentation

All detailed documentation lives in the [`documentations/`](./documentations/) directory.

| Document | Purpose |
|---|---|
| `.opencode/agents/backend.md` | Backend agent deep-dive (conventions, patterns, architecture guidelines) |
| `.opencode/agents/frontend.md` | Frontend agent deep-dive (conventions, patterns, architecture guidelines) |
| `.opencode/agents/git-commit-pusher.md` | Git workflow conventions for committing and pushing |
| `.opencode/agents/code-reviewer.md` | Code review subagent for backend, frontend, and project conventions |
| `documentations/architecture/overview.md` | High-level system design |
| `documentations/architecture/backend-structure.md` | Feature directory pattern and file responsibilities |
| `documentations/architecture/data-flow.md` | Request lifecycle and layer boundaries |
| `documentations/architecture/schema-strategy.md` | Internal vs external schemas, context pattern |
| `documentations/architecture/database.md` | Database design rules, model naming, session management |
| `documentations/development/backend/conventions.md` | Backend coding conventions, naming, file organization |
| `documentations/development/backend/adding-a-feature.md` | Step-by-step TDD guide for adding a new backend feature |
| `documentations/development/tooling.md` | Makefile commands, ruff, mypy, bandit, pre-commit |
| `documentations/backend/testing.md` | pytest setup, fixtures, factories, running tests |
| `documentations/backend/error-handling.md` | Exception hierarchy, BaseProblem, adding new exceptions |
| `documentations/backend/features.md` | Backend features and internals |
| `documentations/backend/auth.md` | Backend authentication and authorization |
| `documentations/backend/user.md` | User management |
| `documentations/frontend/setup.md` | Frontend tech stack, project structure, dev server |
| `documentations/frontend/architecture/overview.md` | Frontend layered architecture |
| `documentations/frontend/architecture/folder-structure.md` | Feature-based folder layout |
| `documentations/frontend/architecture/data-flow.md` | Read/write paths, layer boundaries |
| `documentations/frontend/architecture/state-management.md` | Server state vs client state rules |
| `documentations/frontend/conventions/coding-style.md` | Frontend coding style and naming |
| `documentations/frontend/conventions/components.md` | React component conventions |
| `documentations/frontend/conventions/hooks.md` | Custom hook conventions |
| `documentations/frontend/conventions/services.md` | API client / fetch wrapper conventions |
| `documentations/frontend/conventions/schemas-and-types.md` | Generated types vs Zod schemas |
| `documentations/frontend/conventions/forms.md` | React Hook Form + Zod patterns |
| `documentations/frontend/conventions/styling.md` | Tailwind CSS conventions |
| `documentations/frontend/conventions/routing.md` | TanStack Router conventions |
| `documentations/frontend/features/auth.md` | Frontend auth flow + backend prerequisites |
| `documentations/frontend/features/question.md` | Frontend Question feature |
| `documentations/frontend/features/prediction.md` | Frontend Prediction feature |
| `documentations/frontend/features/resolution.md` | Frontend Resolution feature |
| `documentations/frontend/error-handling.md` | Mapping BaseProblem to UI |
| `documentations/frontend/testing.md` | Vitest + RTL + MSW setup, factories |
| `documentations/frontend/adding-a-feature.md` | Step-by-step guide for a new frontend feature |
| `documentations/getting-started/index.md` | Environment setup and first run |
| `documentations/deployment/docker.md` | Docker Compose development stack |
| `documentations/api/openapi.md` | SwaggerUI, endpoint prefixes, OpenAPI schema |
