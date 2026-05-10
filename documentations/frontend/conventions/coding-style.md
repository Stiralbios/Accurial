# Coding Style

Style and formatting rules for the Accurial frontend. Enforced by ESLint, Prettier, and `tsc --strict`.

## General

- **Line length**: 120 characters (matches backend convention)
- **Indentation**: 2 spaces
- **Quotes**: double quotes for TS/TSX, single quotes inside JSX attributes only when escaping
- **Semicolons**: required
- **Trailing commas**: always (`all` in Prettier)
- **No `any`**: forbidden. Use `unknown` when type is genuinely unknown. ESLint rule `@typescript-eslint/no-explicit-any: error`.
- **No `as` casts** unless narrowing a `unknown` after runtime validation.
- **No default exports** for regular code. Only allowed for: route files (TanStack Router requires it) and Vite config files. ESLint rule `import/no-default-export: error` with overrides for these paths.
- **Type-only imports**: required where applicable — `import type { Foo } from "bar"`. The TS compiler option `verbatimModuleSyntax: true` enforces this.

## File and Identifier Naming

| Kind | Pattern | Example |
|---|---|---|
| React component file | `PascalCase.tsx` | `QuestionList.tsx` |
| Hook file | `useCamelCase.ts` | `useQuestionList.ts` |
| Zustand store file | `camelCaseStore.ts` | `uiStore.ts` |
| Schema file | `schemas.ts` | `app/features/question/schemas.ts` |
| Test file | `<source>.test.ts(x)` | `QuestionList.test.tsx` |
| Route file | TanStack Router convention | `routes/question/index.tsx` |
| Component | `PascalCase` | `QuestionList` |
| Hook | `camelCase`, `use*` prefix | `useCreateQuestion` |
| Type / Interface | `PascalCase`, no `I` prefix | `Question`, `QuestionFormState` |
| Zod schema | `camelCase` ending in `Schema` | `questionCreateSchema` |
| Constant | `SCREAMING_SNAKE_CASE` | `MAX_TITLE_LENGTH` |
| Enum-like object | `PascalCase` keys, `as const` | `QuestionStatus` |

Never use the `I` prefix for interfaces. Never use Hungarian notation.

## Imports

Order, enforced by `eslint-plugin-import`:

1. Node built-ins
2. External packages
3. Internal aliases (`@/...`)
4. Parent / sibling / index relative imports
5. Type-only imports (suffix grouping handled by typescript-eslint)
6. CSS imports last

Always use the `@/` alias rather than long relative paths. `../../` chains beyond one level are forbidden.

```ts
import { useEffect } from "react";

import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/Button";
import { useQuestionList } from "@/features/question";

import type { QuestionRead } from "@/services/api/generated";

import "./QuestionList.css";
```

## React Conventions

- **Functional components only.** No class components.
- **Hooks rules** are enforced by `eslint-plugin-react-hooks`.
- **Props typed via `interface`**, named `<Component>Props`.

```tsx
interface QuestionListProps {
  filter: QuestionFilterInput;
}

export function QuestionList({ filter }: QuestionListProps) {
  const { data, isLoading } = useQuestionList(filter);
  if (isLoading) return <Spinner />;
  return <ul>{data?.map((q) => <li key={q.id}>{q.title}</li>)}</ul>;
}
```

- `key` props are required on lists; never use array indices as keys for non-static lists.
- Avoid `useEffect` for derivations — compute during render.
- Avoid `useMemo` / `useCallback` unless the profiler shows a real cost.
- Refs only for imperative DOM access.

## TypeScript

- `strict: true` always.
- Prefer `interface` for object types meant to be extended; `type` for unions, intersections, mapped types.
- Prefer `readonly` for arrays and props that aren't mutated.
- Use `satisfies` rather than type assertions when checking literal shapes.

```ts
const config = {
  staleTime: 30_000,
  retry: 1,
} satisfies QueryClientConfig;
```

## Comments

- **No inline "what" comments.** Code should explain itself.
- **JSDoc allowed** on exported public functions when the contract isn't obvious from types — keep it short, skip `@param` lists when types make them redundant.
- **TODO / FIXME / XXX** comments must include an issue or owner: `// TODO(astyan): ...`. ESLint rule warns on lone `TODO`.

## Async

- `async` / `await` only — no raw `.then()` chains except in one-line `.catch()` for fire-and-forget telemetry.
- Top-level `await` is forbidden in module scope.
- Always handle errors at the boundary (form submit handler, mutation `onError`). Never swallow with empty `catch`.

## Logging

- No `console.log` in committed code. ESLint rule `no-console: ['error', { allow: ['warn', 'error'] }]`.
- Use a `logger` helper from `app/lib/logger.ts` if richer logging is needed (added when first required).

## Accessibility

- `eslint-plugin-jsx-a11y` rules are warnings on `recommended`, errors on `strict`.
- All interactive elements must be reachable by keyboard.
- Buttons over divs: never put `onClick` on a `div` for a button-like action.
- All images need `alt`.
- Form inputs need an associated `<label>`.

## Files: One Responsibility Each

- One component per file.
- One hook per file (unless trivially related, e.g., a hook and its `select` helper).
- One Zustand store per file.
- A schemas file may export multiple related schemas for a feature.
