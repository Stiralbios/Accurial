# Prediction (Frontend)

UI mapping of the backend `prediction` feature.

Backend reference: `documentations/backend/features.md` and `sources/backend/prediction/`.

## Domain Recap

A Prediction is a user forecast on a question.

- `id`, `user_id`, `question_id`
- `value` (JSONB) — for `BINARY` questions, an object like `{ probability: number }`
- `status`: `DRAFT → PUBLISHED → CLOSED`
- `published_at` set on transition to `PUBLISHED`

## Screens

| Route | Purpose | Auth |
|---|---|---|
| `/question/$id` (section) | The user's predictions on the question, plus a "new prediction" form when no `PUBLISHED` exists | required |
| `/me/predictions` | All of the current user's predictions across questions | required |

The prediction UI is mostly a sub-section of the question detail screen.

## File Layout

```
app/features/prediction/
├── components/
│   ├── PredictionList.tsx
│   ├── PredictionForm.tsx          # input depends on prediction_type
│   ├── BinaryPredictionInput.tsx   # probability slider 0..1
│   └── PredictionStatusBadge.tsx
├── hooks/
│   ├── keys.ts
│   ├── usePredictionList.ts
│   ├── useCreatePrediction.ts
│   ├── useUpdatePrediction.ts
│   └── usePublishPrediction.ts
├── schemas.ts
└── index.ts
```

## Schemas

```ts
// app/features/prediction/schemas.ts
import { z } from "zod";

export const binaryPredictionValueSchema = z.object({
  probability: z.number().min(0).max(1),
});

export const predictionCreateSchema = z.object({
  question_id: z.string().uuid(),
  value: binaryPredictionValueSchema, // expand when more types are added
});

export type PredictionCreateInput = z.infer<typeof predictionCreateSchema>;
```

When new `prediction_type` values are added on the backend (e.g., numeric range, multiple-choice), the Zod schema becomes a discriminated union keyed on `prediction_type`.

## UI Considerations

- **Probability input** is a slider with a numeric input next to it. Display is in percentage (`50%`), stored as `0.5`.
- **Calibration cues**: show the user's previous predictions on the same question to encourage Bayesian updating.
- **Status transitions** mirror the backend FSM. Publishing is a deliberate action behind a confirm.

## Permissions

A prediction belongs to the user who created it. The UI only ever shows `useCurrentUser`'s own predictions. The backend enforces this — the UI is not a security boundary.
