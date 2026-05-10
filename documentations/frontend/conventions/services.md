# Services / API Client

How the frontend talks to the backend.

## Pipeline

```
Feature hook
    |
    v
Generated TanStack Query hook  (Orval)
    |
    v
Generated typed function  (Orval)
    |
    v
Custom fetch wrapper  (app/services/api/client.ts)
    |
    v
fetch()  with credentials: 'include'
    |
    v
FastAPI backend
```

## Fetch Wrapper

`app/services/api/client.ts` is the single HTTP entry point.

Responsibilities:
- Set base URL from `import.meta.env.VITE_API_BASE_URL`
- Set `credentials: 'include'` so the browser attaches the auth cookie
- Set `Accept: application/json`, `Content-Type: application/json` for JSON bodies
- Parse JSON
- Normalize errors into `ApiError` from `app/services/api/errors.ts`

Sketch:

```ts
import { ApiError } from "./errors";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8800";

export async function apiFetch<T>(input: RequestInfo, init: RequestInit = {}): Promise<T> {
  const url = typeof input === "string" && input.startsWith("/") ? `${BASE_URL}${input}` : input;
  const response = await fetch(url, {
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
    ...init,
  });

  if (!response.ok) {
    throw await ApiError.fromResponse(response);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}
```

Orval is configured with `mutator: { path: './client.ts', name: 'apiFetch' }` so all generated requests route through this wrapper.

## Generated Client

`app/services/api/generated/` is the Orval output. Treat as read-only:
- Re-generate via `npm run generate:api`
- Commit the diff with the change that triggered it
- Never edit by hand
- Do not import generated symbols outside of feature hooks (`features/<feature>/hooks/`) — feature hooks are the only sanctioned consumers

## Why Orval + TanStack Query

- **Type safety** — request and response types come from the OpenAPI schema; manual drift is impossible
- **Hook ergonomics** — each endpoint becomes a `useXxx` hook with caching, retries, and dedup
- **MSW handlers** — Orval can emit MSW handlers for testing, see `testing.md`
- **Single source of truth** — the backend's Pydantic schemas drive frontend types

## When to Bypass the Generated Client

Almost never. The only legitimate cases:
- An endpoint that returns a binary stream (file download)
- An out-of-band call during error recovery (e.g., probing health)

In both cases, use `apiFetch` directly from a feature hook — never from a component.

## CORS and Credentials

Both must be aligned with backend settings:

| Side | Required setting |
|---|---|
| Backend `CORSMiddleware` | `allow_credentials=True` and a non-`*` `allow_origins` list |
| Frontend `apiFetch` | `credentials: 'include'` |

If `allow_origins=['*']` is used, the browser will refuse to send cookies — the backend's `ALLOWED_CORS_ORIGINS` setting must list the frontend origin explicitly.

## Errors

The fetch wrapper throws `ApiError`. Components and hooks see them through TanStack Query's `error` field. See `error-handling.md` for the full mapping from `BaseProblem` to UI.
