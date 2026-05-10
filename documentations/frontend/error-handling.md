# Error Handling

How frontend code surfaces backend errors and other failures to the user.

## The `BaseProblem` Envelope

The backend serializes every domain exception as:

```json
{
  "type": "NOT_FOUND",
  "on": "QUESTION",
  "title": "Question Not Found",
  "detail": "Question abc-123 not found",
  "status": 404
}
```

The frontend mirrors this in a single `ApiError` class:

```ts
// app/services/api/errors.ts
export type ProblemKind = "NOT_FOUND" | "ALREADY_EXIST" | "NOT_ALLOWED" | "VALIDATION" | "UNKNOWN";
export type Entity = "USER" | "QUESTION" | "PREDICTION" | "RESOLUTION" | "AUTH" | "UNKNOWN";

export interface ApiErrorPayload {
  type: ProblemKind;
  on: Entity;
  title: string;
  detail: string;
  status: number;
}

export class ApiError extends Error {
  readonly status: number;
  readonly kind: ProblemKind;
  readonly entity: Entity;
  readonly title: string;
  readonly detail: string;

  constructor(payload: ApiErrorPayload) {
    super(payload.detail);
    this.name = "ApiError";
    this.status = payload.status;
    this.kind = payload.type;
    this.entity = payload.on;
    this.title = payload.title;
    this.detail = payload.detail;
  }

  static async fromResponse(response: Response): Promise<ApiError> {
    let payload: ApiErrorPayload;
    try {
      const body = await response.json();
      payload = {
        type: body.type ?? "UNKNOWN",
        on: body.on ?? "UNKNOWN",
        title: body.title ?? response.statusText,
        detail: body.detail ?? `${response.status} ${response.statusText}`,
        status: body.status ?? response.status,
      };
    } catch {
      payload = {
        type: "UNKNOWN",
        on: "UNKNOWN",
        title: response.statusText,
        detail: `${response.status} ${response.statusText}`,
        status: response.status,
      };
    }
    return new ApiError(payload);
  }
}
```

## Where Errors Surface

```
fetch wrapper throws ApiError
    -> generated client returns rejected promise
        -> TanStack Query stores it in `error`
            -> feature hook returns it
                -> component handles it
```

## Three UI Patterns

### 1. Form-field error

Server-validation errors that map to a specific field. Use RHF `setError` in the submit handler:

```ts
try {
  await mutation.mutateAsync(input);
} catch (error) {
  if (error instanceof ApiError && error.kind === "ALREADY_EXIST" && error.entity === "USER") {
    setError("email", { message: error.detail });
    return;
  }
  throw error;
}
```

### 2. Inline page-level error

Errors that affect a whole page (e.g., `NOT_FOUND` on a detail page). Render inline:

```tsx
if (questionQuery.error instanceof ApiError && questionQuery.error.status === 404) {
  return <NotFound entity="Question" />;
}
```

### 3. Global toast / error boundary

Unhandled errors bubble to a top-level error boundary that displays a toast and logs the error.

```tsx
<QueryErrorResetBoundary>
  {({ reset }) => (
    <ErrorBoundary onReset={reset} fallbackRender={({ error, resetErrorBoundary }) => (
      <ErrorScreen error={error} onRetry={resetErrorBoundary} />
    )}>
      <RouterProvider router={router} />
    </ErrorBoundary>
  )}
</QueryErrorResetBoundary>
```

## Mapping Table

| `kind` | HTTP | UI strategy |
|---|---|---|
| `NOT_FOUND` | 404 | Inline page-level error or hide affordance |
| `ALREADY_EXIST` | 409 | Form-field error |
| `NOT_ALLOWED` | 403 | Toast + redirect to a safe page |
| `VALIDATION` | 422 (FastAPI default) | Form-field error if mappable, otherwise toast |
| `UNKNOWN` | 5xx / network | Toast: "Something went wrong" + retry option |

## 401 Unauthorized

A 401 response triggers:
1. `useAuthStore.setAuthenticated(false)`
2. `queryClient.clear()`
3. Redirect to `/login` with the current location stored as a `redirect` search param

This logic lives in the fetch wrapper or a TanStack Query global error handler — never duplicated in components.

## Network Errors

`fetch` rejects with `TypeError` on network failure. The wrapper converts:

```ts
try {
  response = await fetch(url, init);
} catch {
  throw new ApiError({ type: "UNKNOWN", on: "UNKNOWN", title: "Network error", detail: "Check your connection.", status: 0 });
}
```

## Helper

A small helper `isApiError(error, { kind?, entity?, status? })` lives in `app/lib/errors.ts`:

```ts
export function isApiError(
  error: unknown,
  match?: { kind?: ProblemKind; entity?: Entity; status?: number },
): error is ApiError {
  if (!(error instanceof ApiError)) return false;
  if (match?.kind && error.kind !== match.kind) return false;
  if (match?.entity && error.entity !== match.entity) return false;
  if (match?.status && error.status !== match.status) return false;
  return true;
}
```

## Logging

- `console.error` is allowed for unexpected errors caught at boundaries (lint rule `no-console: ['error', { allow: ['warn', 'error'] }]`).
- A future telemetry hook (Sentry, etc.) plugs in at the global error boundary and `apiFetch`.

## Testing

For each feature, write an MSW handler that returns each `ProblemKind` variant and assert the UI renders the appropriate pattern. See `testing.md`.
