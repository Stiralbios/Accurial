# Components

Conventions for writing React components in the Accurial frontend.

## File Layout

- One component per file.
- File name matches component name in `PascalCase.tsx`.
- Co-located test: `Component.test.tsx` lives under `tests/frontend/<feature>/Component.test.tsx`.
- Component-specific styles go in Tailwind classNames; only extract a CSS module when a non-utility concern (keyframes, scoped overrides) requires it.

## Component Anatomy

```tsx
// app/features/question/components/QuestionListItem.tsx
import { Link } from "@tanstack/react-router";

import { StatusBadge } from "@/components/StatusBadge";

import type { QuestionRead } from "@/services/api/generated";

interface QuestionListItemProps {
  question: QuestionRead;
}

export function QuestionListItem({ question }: QuestionListItemProps) {
  return (
    <li className="flex items-center gap-2 rounded border p-3">
      <Link to="/question/$id" params={{ id: question.id }} className="font-medium">
        {question.title}
      </Link>
      <StatusBadge status={question.status} />
    </li>
  );
}
```

Rules visible in this example:
- Named export, no default export.
- Props are typed with an `interface` named `<Component>Props`.
- Imports use the `@/` alias and follow the import-order rules.
- Tailwind utility classes for styling; no CSS file.

## Container vs Presentational

Avoid the strict "container vs presentational" dichotomy. Instead:
- Components consume **feature hooks** for data.
- Components remain dumb about HTTP / cache shape.
- If a component needs more than one feature hook, consider whether a **route shell** should compose them and pass plain props down.

## Composition over Configuration

- Prefer accepting `children` and small focused props over a long `options` object.
- Avoid prop explosion via "boolean trap" — multiple booleans signal a need for variants.

```tsx
// PREFER
<Button variant="primary" size="md">Save</Button>

// AVOID
<Button isPrimary isLarge isLoading isFullWidth>Save</Button>
```

## State

- Keep state as local as possible.
- Lift only when two siblings genuinely share it.
- Prefer derived values during render over `useState` + `useEffect` mirrors.

## Effects

- `useEffect` is for syncing with **outside-of-React** systems (subscriptions, document title, focus management).
- Never use `useEffect` to:
  - Transform props into state (compute during render or via `useMemo`)
  - Trigger data fetching for the component itself (use TanStack Query)
  - Call mutations on mount (use route loaders)

## Forms

- All forms use React Hook Form + Zod resolver. See `forms.md`.

## Error & Loading UI

- Each component reading from a feature hook handles `isLoading` and `error`.
- Spinner / skeleton component lives in `app/components/`.
- Errors are rendered via `<ErrorMessage error={error} />` from `app/components/`. See `error-handling.md`.

## Accessibility Checklist

- Interactive element is a real `<button>`, `<a>`, or `<input>`.
- Image: `alt` text.
- Icon-only button: `aria-label`.
- Form input: associated `<label htmlFor>`.
- Modal / dialog: focus trap and Escape close (use a primitive like Radix when needed).

## Performance

- Memoize only after measuring.
- For long lists (≥ 200 items), use a virtualization library (TanStack Virtual is the default if/when needed).
- Avoid passing inline objects/functions to memoized children.

## Public Surface

A feature component is exported from `features/<feature>/index.ts` only if it is consumed by a route or another feature. Internal helpers stay unexported.
