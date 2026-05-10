# State Management

The frontend separates state into two strict categories. Mixing them is a bug.

## The Two Buckets

### 1. Server State — TanStack Query

Anything that originates from the backend or is a function of backend data.

- Lists of questions, predictions, resolutions
- The current user (`/api/user/me`)
- Computed views over server data

Owned exclusively by TanStack Query. Never mirror it into Zustand.

### 2. Client State — Zustand

UI / transient state that has no server origin.

- Auth status flag (`isAuthenticated: boolean`) — derived from "do we have a current user?" but kept as a UI concern for routing
- Theme preference (light/dark)
- Open/closed state of global modals
- In-progress form drafts that need to survive navigation
- Filter values for a list view (until applied)

## Decision Matrix

| Question | Lives in |
|---|---|
| Does it come from the API? | TanStack Query |
| Will the UI need it after a page reload without re-fetch? | TanStack Query (with `staleTime`) |
| Is it pure UI / transient? | Zustand |
| Is it shared between two unrelated components? | Zustand if client-only, Query if server-derived |
| Is it form state? | React Hook Form |
| Is it route state? | TanStack Router (search params, route params) |

## Rules

1. **Never duplicate server state into Zustand.** If you find yourself doing it, you need a derived TanStack Query selector.
2. **Never store React state in module globals.** Use Zustand if it must be shared.
3. **Never persist auth tokens in JS.** Tokens live in httpOnly cookies (see `features/auth.md`).
4. **One Zustand store per concern.** Avoid a single global store. Co-locate feature-specific stores in `features/<feature>/stores.ts`.
5. **Stores must be small and flat.** No deeply nested objects. Use multiple atomic stores instead.

## Zustand Conventions

### Store creation

```ts
// app/stores/uiStore.ts
import { create } from "zustand";

interface UiState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  isSidebarOpen: false,
  toggleSidebar: () => set((s) => ({ isSidebarOpen: !s.isSidebarOpen })),
}));
```

- Hook export name: `use<Concern>Store`
- Selector usage at call site to avoid unnecessary renders:

```tsx
const isOpen = useUiStore((s) => s.isSidebarOpen);
```

- Never destructure the whole store in a component:

```tsx
// BAD - re-renders on any state change
const { isSidebarOpen, toggleSidebar } = useUiStore();
```

### Persist middleware

Use `zustand/middleware`'s `persist` only for non-sensitive UI preferences (theme, sidebar). Never persist auth or PII.

### Devtools middleware

Wrap stores with `devtools` in development:

```ts
import { devtools } from "zustand/middleware";

export const useUiStore = create<UiState>()(
  devtools((set) => ({ /* ... */ }), { name: "ui" }),
);
```

## TanStack Query Conventions

### QueryClient defaults

```ts
// app/services/query-client.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      gcTime: 5 * 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});
```

Override per-hook when a stronger or weaker policy is justified — document the reason in the hook.

### Suspense

The codebase does **not** use TanStack Query's Suspense mode by default. Components handle `isLoading` / `error` explicitly via the feature hook return.

### Selectors

Prefer the `select` option to derive values without leaking the raw query shape:

```ts
useQuestionList({ status: "OPEN" }, { select: (data) => data.length });
```

## Authentication State

Auth is a hybrid concern:
- **Token transport** — httpOnly cookie, invisible to JS
- **"Am I logged in?" flag** — derived from a TanStack Query for `/api/user/me`. If the query succeeds, the user is authenticated.
- **Routing-level guard** — a tiny Zustand mirror (`isAuthenticated`) updated by the auth hook so route guards can read it synchronously without subscribing to the query

See `features/auth.md` for the full pattern.
