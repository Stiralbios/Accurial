# Question (Frontend)

UI mapping of the backend `question` feature.

Backend reference: `documentations/backend/features.md` and `sources/backend/question/`.

## Domain Recap

A Question has:
- `id` (UUID)
- `title`, `description`
- `prediction_type` (currently only `BINARY`)
- `status`: `DRAFT → OPEN → CLOSED → ARCHIVED` (or `OPEN → ARCHIVED`)
- `owner_id`

Only the owner may update or delete. Delete is allowed only in `DRAFT`.

## Screens

| Route | Purpose | Auth |
|---|---|---|
| `/question` | Paginated/filterable list of the user's questions | required |
| `/question/new` | Create form | required |
| `/question/$id` | Detail view + status transitions + linked predictions | required |
| `/question/$id/edit` | Edit form | required |

## File Layout

```
app/features/question/
├── components/
│   ├── QuestionList.tsx
│   ├── QuestionListItem.tsx
│   ├── QuestionDetail.tsx
│   ├── QuestionCreateForm.tsx
│   ├── QuestionEditForm.tsx
│   └── QuestionStatusBadge.tsx
├── hooks/
│   ├── keys.ts
│   ├── useQuestionList.ts
│   ├── useQuestion.ts
│   ├── useCreateQuestion.ts
│   ├── useUpdateQuestion.ts
│   └── useDeleteQuestion.ts
├── schemas.ts
├── constants.ts
└── index.ts
```

## Schemas

```ts
// app/features/question/schemas.ts
import { z } from "zod";

export const questionCreateSchema = z.object({
  title: z.string().min(1).max(255),
  description: z.string().min(1),
  prediction_type: z.enum(["BINARY"]),
});

export const questionUpdateSchema = z.object({
  title: z.string().min(1).max(255).optional(),
  description: z.string().min(1).optional(),
  prediction_type: z.enum(["BINARY"]).optional(),
  status: z.enum(["DRAFT", "OPEN", "CLOSED", "ARCHIVED"]).optional(),
});

export const questionFilterSchema = z.object({
  status: z.enum(["DRAFT", "OPEN", "CLOSED", "ARCHIVED"]).optional(),
  prediction_type: z.enum(["BINARY"]).optional(),
});

export type QuestionCreateInput = z.infer<typeof questionCreateSchema>;
export type QuestionUpdateInput = z.infer<typeof questionUpdateSchema>;
export type QuestionFilterInput = z.infer<typeof questionFilterSchema>;
```

The structural-equivalence assertion (see `conventions/schemas-and-types.md`) ensures these stay in sync with the generated API types.

## Status Transition UI

The list of allowed transitions mirrors the backend FSM:

```ts
// app/features/question/constants.ts
import type { QuestionStatus } from "@/services/api/generated";

export const QUESTION_STATUS_TRANSITIONS: Record<QuestionStatus, QuestionStatus[]> = {
  DRAFT: ["OPEN"],
  OPEN: ["CLOSED", "ARCHIVED"],
  CLOSED: ["ARCHIVED"],
  ARCHIVED: [],
};

export const QUESTION_STATUS_LABEL: Record<QuestionStatus, string> = {
  DRAFT: "Draft",
  OPEN: "Open",
  CLOSED: "Closed",
  ARCHIVED: "Archived",
};
```

The detail screen renders only the buttons for transitions allowed from the current status. The backend FSM remains the source of truth — failed transitions surface as `QuestionNotAllowedProblem` (403) and are mapped via `error-handling.md`.

## Permissions in UI

The frontend hides edit/delete affordances when `question.owner_id !== currentUser.id`. The backend enforces ownership; the UI hide is purely a UX optimization. Always treat the API as the authority.

## Delete

Delete is allowed in `DRAFT` only. The button is hidden otherwise. On click:

1. Confirmation modal.
2. `useDeleteQuestion` mutation.
3. On success, navigate to `/question` and invalidate `questionKeys.lists()`.

## Filters as Search Params

The list route's filter state lives in URL search params, validated by `questionFilterSchema`. See `conventions/routing.md`.
