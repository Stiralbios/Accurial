# Data Flow

How data flows through the Accurial frontend, from user interaction to API call and back to UI.

## Read Path (Query)

```
User navigates / component mounts
    |
    v
Route loader (TanStack Router)         [optional: prefetch]
    |
    v
Component renders, calls feature hook (use<Feature>List, useQuestion)
    |
    v
Feature hook -> generated TanStack Query hook (useListQuestion)
    |
    | cache miss / stale
    v
Orval typed function -> fetch wrapper (credentials: 'include')
    |
    v
Backend HTTP API (FastAPI)
    |
    v
JSON response
    |
    v
Cached by TanStack Query under [feature, params] key
    |
    v
Component receives `{ data, isLoading, error }` and renders
```

## Write Path (Mutation)

```
User submits a form (RHF + Zod)
    |
    v
Component calls feature mutation hook (useCreateQuestion)
    |
    v
Feature hook -> generated mutation hook
    |
    v
Orval typed function -> fetch wrapper (POST/PATCH/DELETE)
    |
    v
Backend processes request
    |
    v
On success: hook invalidates / sets relevant query keys
    |
    v
Component reads the refreshed data via its query hook
```

## Layer Boundaries

### Component Layer

- May call hooks (feature, RHF, Router) only
- Must not call `fetch`, axios, or generated client functions directly
- Must not read from or write to TanStack Query cache directly (use feature hooks)
- Receives `BaseProblem`-shaped errors via the hook's `error` field (see `error-handling.md`)

### Feature Hook Layer

- Wraps a generated TanStack Query / mutation hook
- Sets sensible defaults (`staleTime`, `gcTime`, `retry`)
- Returns a feature-shaped object: `{ questions, isLoading, error, refetch }` rather than the raw query result if it improves call-site clarity
- Performs query invalidation on mutations (`queryClient.invalidateQueries({ queryKey: ['question'] })`)
- May compose multiple generated hooks for derived views, but **does not call other feature hooks** — symmetric to backend's "services don't call services" rule

### Generated Client Layer

- Output of Orval — fully typed
- Re-generated via `npm run generate:api`
- Committed in source control under `app/services/api/generated/`
- Never edited by hand

### Fetch Wrapper

- Sets `credentials: 'include'` (cookie auth)
- Sets `VITE_API_BASE_URL` from env
- Adds `Accept: application/json`
- Parses JSON, normalizes errors into `ApiError` (see `error-handling.md`)
- Single source of truth for HTTP-level concerns

## Query Keys

Stable, hierarchical query keys per feature:

```ts
// app/features/question/hooks/keys.ts
export const questionKeys = {
  all: ['question'] as const,
  lists: () => [...questionKeys.all, 'list'] as const,
  list: (filter: QuestionFilterInput) => [...questionKeys.lists(), filter] as const,
  details: () => [...questionKeys.all, 'detail'] as const,
  detail: (id: string) => [...questionKeys.details(), id] as const,
};
```

Orval can be configured to emit these. Treat the emitted helpers as the source of truth and re-export them through the feature module.

## Invalidation Rules

| Mutation | Invalidates |
|---|---|
| `createQuestion` | `questionKeys.lists()` |
| `updateQuestion(id)` | `questionKeys.detail(id)` and `questionKeys.lists()` |
| `deleteQuestion(id)` | `questionKeys.detail(id)` and `questionKeys.lists()` |

Do **not** call `queryClient.invalidateQueries()` without a key — that flushes everything.

## Optimistic Updates

Optimistic updates live in the feature hook layer. Use `onMutate` / `onError` / `onSettled` of the mutation. Never mirror the in-flight value in a Zustand store: TanStack Query already handles this via the cache snapshot pattern.

## SSR / Hydration

Not applicable — this is a CSR-only Vite SPA. Adding SSR would require revisiting the data-flow doc.

## Comparison to Backend Data Flow

| Backend layer | Frontend equivalent | Same rule |
|---|---|---|
| API → Service → Store | Component → Feature hook → Generated client | Yes |
| Service may call multiple stores | Feature hook may compose multiple generated hooks | Yes |
| Service must not call other services | Feature hook must not call other feature hooks | Yes |
| API converts external↔internal schemas | Component converts form input↔Create schema | Yes |
| `context` carried in internal schemas | Feature hook injects auth/user-aware bits where needed | Yes |
