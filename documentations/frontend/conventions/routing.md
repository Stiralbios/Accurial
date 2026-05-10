# Routing

Routing is handled by **TanStack Router** with the **file-based** convention. Routes live in `sources/frontend/app/routes/`.

## Why TanStack Router

- Fully type-safe params, search params, and links
- First-class loader integration with TanStack Query (`queryClient.ensureQueryData`)
- File-based discovery via `@tanstack/router-vite-plugin`
- Search-param-as-state model fits forecasting filters naturally

## File Layout

```
app/routes/
├── __root.tsx              # Root layout (providers consumed here as well)
├── index.tsx               # /
├── login.tsx               # /login
├── question/
│   ├── index.tsx           # /question
│   ├── $id.tsx             # /question/:id
│   └── $id.edit.tsx        # /question/:id/edit
├── prediction/
│   └── ...
└── _authed.tsx             # Layout route enforcing authentication
```

The Vite plugin auto-generates `routeTree.gen.ts` from this tree. Do not edit it.

## Route File Anatomy

```tsx
// app/routes/question/index.tsx
import { createFileRoute } from "@tanstack/react-router";

import { QuestionList } from "@/features/question";

export const Route = createFileRoute("/question/")({
  component: QuestionListRoute,
});

function QuestionListRoute() {
  return <QuestionList />;
}
```

Rules visible:
- The `Route` named export is required by TanStack Router.
- The component is named `<Path>Route` to mark it as a route shell.
- Route shells are **thin** — they delegate to feature components.

## Loaders

Use loaders to prefetch via TanStack Query so the UI never starts in a loading state if data was already cached:

```tsx
export const Route = createFileRoute("/question/$id")({
  loader: ({ context: { queryClient }, params }) =>
    queryClient.ensureQueryData(getQuestionQueryOptions(params.id)),
  component: QuestionDetailRoute,
});
```

The `queryClient` is provided via the router's context, set up in `main.tsx`:

```tsx
const router = createRouter({ routeTree, context: { queryClient } });
```

## Search Params

Validate search params with Zod via the `validateSearch` option. Search params replace UI state for filters, so they survive reloads and bookmarks.

```ts
const questionListSearchSchema = z.object({
  status: z.enum(["DRAFT", "OPEN", "CLOSED", "ARCHIVED"]).optional(),
});

export const Route = createFileRoute("/question/")({
  validateSearch: questionListSearchSchema,
  component: QuestionListRoute,
});
```

Read at the call site:

```ts
const { status } = Route.useSearch();
```

## Authentication Guards

Use a layout route (`_authed.tsx`) that performs the check `beforeLoad` and redirects to `/login` when unauthenticated:

```tsx
// app/routes/_authed.tsx
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/_authed")({
  beforeLoad: async ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: "/login", search: { redirect: location.href } });
    }
  },
  component: () => <Outlet />,
});
```

All authenticated routes nest under this layout (`question/index.tsx` becomes effectively `/_authed/question/`). The `auth` context is wired in `main.tsx` from the auth store.

See `features/auth.md` for the auth bootstrap flow.

## Links

Always use `<Link>` from `@tanstack/react-router` — never `<a href>` for in-app navigation. Type-safe params are checked at compile time:

```tsx
<Link to="/question/$id" params={{ id: question.id }}>
  {question.title}
</Link>
```

## Programmatic Navigation

```ts
const navigate = Route.useNavigate();
await navigate({ to: "/question/$id", params: { id: created.id } });
```

## What's Forbidden

- `window.location.assign` for navigation
- Manual route strings (`'/question/' + id`) — use `<Link>` or `navigate({ to, params })`
- Putting business logic in route files — keep them as shells
- Calling feature hooks directly in `loader` — call the underlying query options helper so the loader and the component share the same cache key
