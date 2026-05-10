# Folder Structure

The frontend uses a **feature-based** organization that mirrors the backend layout. Each feature is a self-contained directory under `sources/frontend/app/features/<feature>/`.

## Top-level Layout

```
sources/frontend/app/
├── main.tsx                # Bootstraps providers (QueryClient, RouterProvider)
├── routes/                 # TanStack Router file-based routes
├── features/               # Domain features (auth, question, prediction, resolution)
├── components/             # Cross-feature reusable presentational components
├── hooks/                  # Cross-feature reusable hooks
├── stores/                 # Cross-feature Zustand stores
├── services/
│   ├── api/
│   │   ├── generated/      # Orval-generated, never edited
│   │   └── client.ts       # fetch wrapper
│   └── query-client.ts
├── lib/                    # Pure utility helpers (no React)
└── styles/
    └── index.css
```

## Feature Directory Pattern

Every feature follows the same internal structure (mirrors `sources/backend/<feature>/`):

```
app/features/<feature>/
├── components/             # Feature-specific React components
├── hooks/                  # Feature-specific hooks (wrap generated query/mutation hooks)
├── schemas.ts              # Zod schemas + derived TypeScript types (Form/Internal)
├── stores.ts               # Zustand store(s) scoped to this feature (optional)
├── types.ts                # Type aliases that are not derived from Zod schemas
└── index.ts                # Public re-exports of the feature's surface
```

| Backend file | Frontend equivalent | Notes |
|---|---|---|
| `models.py` | (none) | Models live on the backend |
| `schemas.py` | `schemas.ts` | Zod schemas mirror Pydantic schemas — Read/Create/Update variants |
| `stores.py` | `services/api/generated/` | DB writes are backend; the frontend's "store" of API calls is the generated client |
| `services.py` | `hooks/` | Wrappers around the generated hooks; expose feature semantics |
| `apis.py` | `routes/` + `components/` | UI entry points |
| `constants.py` | `constants.ts` (when needed) | Enums mirroring backend StrEnums |

## File Responsibilities

### `routes/`

TanStack Router file-based routes. A route file is a thin shell:
- Declares the route (path, params, validators)
- Calls a feature hook to fetch / mutate
- Renders a component from `features/<feature>/components/`

Routes never contain business logic.

### `features/<feature>/components/`

React components specific to the feature. Component files use `PascalCase.tsx`. One component per file. Co-locate small subcomponents only if private to the parent.

### `features/<feature>/hooks/`

Custom hooks named `use<Feature><Action>`. Examples: `useQuestionList`, `useCreateQuestion`. Hooks:
- Wrap an Orval-generated hook
- Inject default options (staleTime, optimistic updates)
- Return a stable, feature-shaped API to the components
- Map errors to user-meaningful codes when needed

### `features/<feature>/schemas.ts`

Zod schemas that serve dual roles:
- **Form schemas** for React Hook Form validation (input shape)
- **Read/parse schemas** for runtime validation when needed (rare — Orval already provides types)

Naming mirrors the backend:
- `<feature>BaseSchema`
- `<feature>CreateSchema` / `<feature>CreateInput` (TS type)
- `<feature>UpdateSchema` / `<feature>UpdateInput`
- `<feature>FilterSchema`

### `features/<feature>/stores.ts`

Zustand stores scoped to UI concerns of this feature only. Forbidden: caching server data here. See `architecture/state-management.md`.

### `features/<feature>/index.ts`

Public surface of the feature. Other features and routes import from `@/features/<feature>` only. This enforces the boundary.

```ts
// app/features/question/index.ts
export { QuestionList } from "./components/QuestionList";
export { useQuestionList } from "./hooks/useQuestionList";
export type { QuestionCreateInput } from "./schemas";
```

## Cross-feature Code

| Type | Location | When to put it here |
|---|---|---|
| Reusable component (e.g., `Button`, `Modal`) | `app/components/` | Used by ≥ 2 features and contains no domain logic |
| Reusable hook (e.g., `useDebounce`) | `app/hooks/` | Used by ≥ 2 features, no domain logic |
| Cross-feature store (e.g., auth status flag) | `app/stores/` | Read by ≥ 2 features |
| Pure helper | `app/lib/` | No React, no IO, no DOM |

## Path Aliases

The TS path alias `@/` points to `./app`. Always import via the alias rather than long relative paths:

```ts
import { Button } from "@/components/Button";
import { useQuestionList } from "@/features/question";
```

## Boundary Rules

These mirror the backend's layer rules:

1. **Components** never call `fetch` or generated client functions directly — only feature hooks.
2. **Feature hooks** never import from another feature's internals — only from another feature's `index.ts`.
3. **Stores (Zustand)** never store server data; that lives in TanStack Query.
4. **Routes** are thin; they delegate to components and feature hooks.
5. **Generated client** (`services/api/generated/`) is read-only — regenerate via `npm run generate:api`.
