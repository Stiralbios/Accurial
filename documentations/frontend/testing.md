# Frontend Testing

The frontend test stack mirrors the backend's pytest discipline: every feature has tests, every PR adds tests for new behavior.

## Stack

| Tool | Purpose |
|---|---|
| **Vitest** | Test runner (Vite-native, fast, ESM-friendly) |
| **React Testing Library (RTL)** | Component rendering and queries |
| **`@testing-library/user-event`** | User interaction simulation |
| **`@testing-library/jest-dom`** | DOM matchers (`toBeInTheDocument`, etc.) |
| **MSW** | API mocking via service worker / Node interceptors |
| **jsdom** | Browser-like environment for Node-based test runs |

## Layout

Tests live under `tests/frontend/`, mirroring `sources/frontend/app/features/`:

```
tests/frontend/
├── setup/
│   ├── server.ts                # MSW server lifecycle
│   ├── render.tsx               # custom render with providers
│   └── vitest.setup.ts          # global jest-dom + MSW hooks
├── handlers/
│   ├── question.ts
│   ├── prediction.ts
│   ├── resolution.ts
│   ├── user.ts
│   └── auth.ts
├── factories/
│   ├── question.ts
│   └── ...
├── auth/
│   └── LoginForm.test.tsx
├── question/
│   ├── QuestionList.test.tsx
│   ├── QuestionCreateForm.test.tsx
│   └── useCreateQuestion.test.ts
├── prediction/
│   └── ...
└── resolution/
    └── ...
```

## Running Tests

| Command | Purpose |
|---|---|
| `npm run test` | One-shot run (CI mode) |
| `npm run test:watch` | Watch mode |
| `npm run test:ui` | Vitest UI |
| `npm run coverage` | Coverage report |
| `make test_frontend` | Same as `npm run test` |

## Custom Render

`tests/frontend/setup/render.tsx` wraps RTL's `render` with the providers a real route would have:

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderOptions } from "@testing-library/react";
import type { ReactElement } from "react";

export function renderWithProviders(ui: ReactElement, options?: RenderOptions) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return {
    queryClient,
    ...render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>, options),
  };
}
```

For tests that need routing, a `renderWithRouter` variant builds a memory router with the provided routes.

## MSW

`tests/frontend/setup/server.ts`:

```ts
import { setupServer } from "msw/node";
import { handlers } from "../handlers";

export const server = setupServer(...handlers);
```

Vitest setup wires the lifecycle:

```ts
// tests/frontend/setup/vitest.setup.ts
import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

`onUnhandledRequest: 'error'` enforces that every test mocks every request it makes.

### Handler example

```ts
// tests/frontend/handlers/question.ts
import { http, HttpResponse } from "msw";

import type { QuestionRead } from "@/services/api/generated";

import { questionFactory } from "../factories/question";

export const questionHandlers = [
  http.get("http://localhost:8800/api/question/", () => {
    return HttpResponse.json<QuestionRead[]>([questionFactory.build()]);
  }),
  http.post("http://localhost:8800/api/question", async ({ request }) => {
    const body = (await request.json()) as Partial<QuestionRead>;
    return HttpResponse.json<QuestionRead>(questionFactory.build(body));
  }),
];
```

Orval can also generate handlers (`mock: true` in `orval.config.ts`). Prefer generated handlers as the baseline; override per-test for failure scenarios.

## Factories

`tests/frontend/factories/question.ts`:

```ts
import type { QuestionRead } from "@/services/api/generated";

let counter = 0;
export const questionFactory = {
  build(overrides: Partial<QuestionRead> = {}): QuestionRead {
    counter += 1;
    return {
      id: `00000000-0000-0000-0000-${String(counter).padStart(12, "0")}`,
      title: `Question ${counter}`,
      description: `Description ${counter}`,
      prediction_type: "BINARY",
      status: "DRAFT",
      owner_id: "00000000-0000-0000-0000-000000000001",
      ...overrides,
    };
  },
};
```

The pattern intentionally mirrors `factory_boy` factories on the backend. A library is unnecessary at this size; introduce one only if factories get complex.

## What to Test

| Layer | What to test |
|---|---|
| **Component** | What the user sees and does. Renders, click outcomes, error states. |
| **Form** | Validation messages, submit payload, server-error mapping. |
| **Hook** | Query keys, mutation invalidation, optimistic update rollback. |
| **Route guard** | Redirects when unauthenticated. |
| **Error boundary** | Renders fallback on thrown error. |

## What NOT to Test

- Third-party library internals (RHF, TanStack Query)
- Tailwind class strings
- Implementation details of generated client (only the contract via MSW)
- Snapshot of entire DOM trees (brittle)

## Hook Testing Example

```ts
import { renderHook, waitFor } from "@testing-library/react";

import { useQuestionList } from "@/features/question";

import { renderWithProviders } from "../setup/render";

it("returns the list of questions", async () => {
  const { result } = renderHook(() => useQuestionList({}), {
    wrapper: renderWithProviders.Wrapper,
  });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toHaveLength(1);
});
```

## Component Testing Example

```tsx
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { QuestionCreateForm } from "@/features/question";

import { renderWithProviders } from "../setup/render";

it("submits a valid form", async () => {
  const onCreated = vi.fn();
  renderWithProviders(<QuestionCreateForm onCreated={onCreated} />);

  await userEvent.type(screen.getByLabelText(/title/i), "My question");
  await userEvent.type(screen.getByLabelText(/description/i), "Will it rain?");
  await userEvent.click(screen.getByRole("button", { name: /create/i }));

  await waitFor(() => expect(onCreated).toHaveBeenCalledOnce());
});
```

## Coverage

Targets (advisory, not enforced as CI gate yet):
- 70%+ line coverage on `app/features/`
- 0% on `app/services/api/generated/` (excluded from coverage)
- 100% on `app/services/api/client.ts` and `app/services/api/errors.ts` — tiny critical surface

## Pre-commit

`.pre-commit-config.yaml` runs `npm run lint`, `npm run typecheck`, and `npx vitest related --run` on staged files.
