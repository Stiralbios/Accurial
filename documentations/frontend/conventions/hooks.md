# Hooks

Custom hook conventions. Hooks are the bridge between components and the generated API client.

## Naming

- Always begin with `use`.
- Pattern: `use<Feature><Action>` for feature hooks: `useQuestionList`, `useCreateQuestion`, `useDeleteQuestion`.
- Pattern: `use<Concern>` for cross-feature hooks: `useDebounce`, `useClickOutside`.

## File Layout

- One hook per file (unless a private helper is trivially related).
- Feature hooks in `app/features/<feature>/hooks/<hookName>.ts`.
- Cross-feature hooks in `app/hooks/<hookName>.ts`.
- Test in `tests/frontend/<feature>/<hookName>.test.ts`.

## Feature Hook Anatomy

A feature hook wraps one or more Orval-generated TanStack Query hooks and adapts them to the feature's needs.

```ts
// app/features/question/hooks/useQuestionList.ts
import { useListQuestion } from "@/services/api/generated/question/question";

import type { QuestionFilterInput } from "../schemas";

export function useQuestionList(filter: QuestionFilterInput) {
  return useListQuestion(filter, {
    query: {
      staleTime: 30_000,
    },
  });
}
```

Mutation example:

```ts
// app/features/question/hooks/useCreateQuestion.ts
import { useQueryClient } from "@tanstack/react-query";
import { useCreateQuestion as useCreateQuestionGenerated } from "@/services/api/generated/question/question";

import { questionKeys } from "./keys";

export function useCreateQuestion() {
  const queryClient = useQueryClient();
  return useCreateQuestionGenerated({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: questionKeys.lists() });
      },
    },
  });
}
```

## Rules

1. **Hooks call hooks; hooks don't call hooks of other features.** Symmetric to backend's "service must not call service". A hook may compose multiple **generated** hooks. If shared logic is needed across features, extract a pure helper in `app/lib/`.
2. **Side effects belong in `useEffect`** or in mutation callbacks (`onSuccess`, `onError`).
3. **No conditional hook calls.** React's rules of hooks.
4. **Stable return shape.** A hook's return type does not change between calls. Prefer always returning the same keys.
5. **Type the return** explicitly when the inferred type leaks generated internals (`UseQueryResult<...>`). Return a feature-shaped object instead.

## Query Keys

A `keys.ts` file per feature centralizes query keys:

```ts
// app/features/question/hooks/keys.ts
import type { QuestionFilterInput } from "../schemas";

export const questionKeys = {
  all: ["question"] as const,
  lists: () => [...questionKeys.all, "list"] as const,
  list: (filter: QuestionFilterInput) => [...questionKeys.lists(), filter] as const,
  details: () => [...questionKeys.all, "detail"] as const,
  detail: (id: string) => [...questionKeys.details(), id] as const,
};
```

If Orval emits keys that match this structure, prefer those.

## Optimistic Updates

```ts
return useUpdateQuestionGenerated({
  mutation: {
    onMutate: async (variables) => {
      await queryClient.cancelQueries({ queryKey: questionKeys.detail(variables.id) });
      const previous = queryClient.getQueryData(questionKeys.detail(variables.id));
      queryClient.setQueryData(questionKeys.detail(variables.id), (old) => ({ ...old, ...variables.data }));
      return { previous };
    },
    onError: (_error, variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(questionKeys.detail(variables.id), context.previous);
      }
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: questionKeys.detail(variables.id) });
    },
  },
});
```

## Testing

Hooks are tested with `renderHook` from RTL plus an MSW server for API responses. See `testing.md`.
