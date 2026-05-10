# Adding a Frontend Feature

Step-by-step guide for adding a new frontend feature, mirroring the backend's TDD-style guide.

This assumes the backend feature already exists (or is being built in parallel). The frontend follows the API.

## TDD Workflow

```
1. Generate / refresh the API client from the backend's OpenAPI schema
2. Write failing tests (component + hook + MSW handlers)
3. Implement schemas, hooks, components
4. Add the route(s)
5. Refactor
6. Run lint, typecheck, tests, build
```

## Checklist

### 1. Refresh the generated API client

If the backend changed:

```bash
make run_dev_env                  # backend must be running on :8800
cd sources/frontend
npm run generate:api
git add app/services/api/generated
```

Commit the generated diff with the change.

### 2. Create the feature directory

```bash
mkdir -p sources/frontend/app/features/<feature>/{components,hooks}
touch sources/frontend/app/features/<feature>/{schemas.ts,index.ts}
```

### 3. Write failing tests

```bash
mkdir -p tests/frontend/<feature>
mkdir -p tests/frontend/handlers
mkdir -p tests/frontend/factories
```

Start from a UI assertion:

```tsx
// tests/frontend/<feature>/<Component>.test.tsx
import { renderWithProviders } from "../setup/render";

it("renders the list", async () => {
  renderWithProviders(<FeatureList />);
  expect(await screen.findByText("My item")).toBeInTheDocument();
});
```

Add an MSW handler returning the canned response. Run:

```bash
npm run test -- <feature>
```

Confirm the test fails for the right reason (component or hook does not exist yet).

### 4. Define Zod schemas (`features/<feature>/schemas.ts`)

```ts
import { z } from "zod";

export const featureCreateSchema = z.object({
  name: z.string().min(1).max(255),
});

export type FeatureCreateInput = z.infer<typeof featureCreateSchema>;
```

Add the structural-equivalence assertion against the generated `FeatureCreate` type (see `conventions/schemas-and-types.md`).

### 5. Define query keys (`features/<feature>/hooks/keys.ts`)

```ts
export const featureKeys = {
  all: ["feature"] as const,
  lists: () => [...featureKeys.all, "list"] as const,
  list: (filter: FeatureFilterInput) => [...featureKeys.lists(), filter] as const,
  details: () => [...featureKeys.all, "detail"] as const,
  detail: (id: string) => [...featureKeys.details(), id] as const,
};
```

### 6. Write feature hooks

One file per hook. Wrap the generated hook, set defaults, handle invalidation.

See `conventions/hooks.md` for examples.

### 7. Build components

One file per component. Co-located test in `tests/frontend/<feature>/`.

See `conventions/components.md` and `conventions/forms.md`.

### 8. Add routes

Create files under `app/routes/<feature>/`:

```
app/routes/<feature>/
├── index.tsx               # /<feature>
├── new.tsx                 # /<feature>/new
└── $id.tsx                 # /<feature>/:id
```

Routes are thin shells; they read params, call feature hooks, render components.

### 9. Wire the public surface

```ts
// app/features/<feature>/index.ts
export { FeatureList } from "./components/FeatureList";
export { FeatureDetail } from "./components/FeatureDetail";
export { useFeatureList } from "./hooks/useFeatureList";
export type { FeatureCreateInput } from "./schemas";
```

### 10. Run quality gates

```bash
npm run typecheck
npm run lint
npm run test
npm run build
```

All must pass before opening a PR.

### 11. Update docs

If the feature introduces new patterns or screens, add a short note to `documentations/frontend/features/<feature>.md`.

## Don't

- Don't import from another feature's internals — only its `index.ts`.
- Don't put `fetch` in components.
- Don't bypass the generated client unless explicitly justified (binary download).
- Don't skip MSW handlers — every API call in a test must be mocked.
