# Resolution (Frontend)

UI mapping of the backend `resolution` feature.

Backend reference: `documentations/backend/features.md` and `sources/backend/resolution/`.

## Domain Recap

A Resolution is the actual outcome of a question, used for scoring and calibration. One question has at most one resolution (unique FK constraint).

- `id`, `question_id`
- `value` (JSONB)
- `date` (the day the question was resolved)
- `description`

## Screens

| Route | Purpose | Auth |
|---|---|---|
| `/question/$id` (section) | Show the resolution if any; "Resolve" button if owner and question is `CLOSED` | required |
| `/question/$id/resolve` | Resolve form | required |

## File Layout

```
app/features/resolution/
├── components/
│   ├── ResolutionPanel.tsx
│   ├── ResolutionForm.tsx
│   └── BinaryResolutionInput.tsx   # outcome: true / false
├── hooks/
│   ├── keys.ts
│   ├── useResolution.ts
│   ├── useCreateResolution.ts
│   └── useUpdateResolution.ts
├── schemas.ts
└── index.ts
```

## Schemas

```ts
// app/features/resolution/schemas.ts
import { z } from "zod";

export const binaryResolutionValueSchema = z.object({
  outcome: z.boolean(),
});

export const resolutionCreateSchema = z.object({
  question_id: z.string().uuid(),
  value: binaryResolutionValueSchema,
  date: z.string(), // ISO date — yyyy-MM-dd
  description: z.string().min(1),
});

export type ResolutionCreateInput = z.infer<typeof resolutionCreateSchema>;
```

## Workflow

1. Question owner moves the question to `CLOSED`.
2. Owner navigates to `/question/$id/resolve`.
3. Submits the resolution.
4. Frontend invalidates `questionKeys.detail(id)` and `resolutionKeys.detail(question_id)`.
5. The detail screen now displays the resolution panel and Brier score per prediction (computed client-side or via a future backend endpoint — out of scope until the data is available).

## Calibration View (future)

A `/me/calibration` route will aggregate the user's predictions vs resolutions over time. This is documented when the backend exposes the necessary aggregation endpoint.
