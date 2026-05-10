# Forms

All forms use **React Hook Form** (RHF) for state and **Zod** for validation, connected via `@hookform/resolvers/zod`.

## Anatomy of a Form

```tsx
// app/features/question/components/QuestionCreateForm.tsx
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { ErrorMessage } from "@/components/ErrorMessage";

import { useCreateQuestion } from "../hooks/useCreateQuestion";
import { questionCreateSchema, type QuestionCreateInput } from "../schemas";

export function QuestionCreateForm({ onCreated }: { onCreated: (id: string) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<QuestionCreateInput>({
    resolver: zodResolver(questionCreateSchema),
    defaultValues: { title: "", description: "", prediction_type: "BINARY" },
  });
  const createQuestion = useCreateQuestion();

  const onSubmit = handleSubmit(async (input) => {
    try {
      const created = await createQuestion.mutateAsync({ data: input });
      onCreated(created.id);
    } catch (error) {
      // Map field-specific server errors into form errors. See error-handling.md.
      if (isFieldError(error, "title")) {
        setError("title", { message: error.detail });
        return;
      }
      throw error; // bubble to global error boundary
    }
  });

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-3">
      <label className="flex flex-col gap-1">
        <span>Title</span>
        <input {...register("title")} className="rounded border p-2" />
        {errors.title && <ErrorMessage message={errors.title.message} />}
      </label>
      {/* ...other fields... */}
      <button type="submit" disabled={isSubmitting}>Create</button>
    </form>
  );
}
```

## Rules

1. **Always use `zodResolver`.** No native `required`-only validation in production code.
2. **Schema lives in `features/<feature>/schemas.ts`.** Components import it.
3. **Default values** are explicit. Avoid uncontrolled forms with `undefined` defaults — they break SSR-style hydration if added later.
4. **`handleSubmit` wraps the submit handler.** Never read `formState` from outside RHF.
5. **`mutateAsync` for awaitable submissions** (so you can navigate / show toast on success). Use `mutate` only for fire-and-forget.
6. **`isSubmitting`** controls submit button disabled state (not a separate `useState`).
7. **Server-side field errors** are surfaced via `setError`. Generic errors bubble to the global error boundary.
8. **Reset on success** with `reset()` for forms that stay mounted (e.g., a "create another" pattern).

## Field-level Components

When a field is reused (date picker, multi-select), wrap with RHF's `Controller`:

```tsx
import { Controller } from "react-hook-form";

<Controller
  control={control}
  name="resolved_at"
  render={({ field, fieldState }) => (
    <DatePicker value={field.value} onChange={field.onChange} error={fieldState.error?.message} />
  )}
/>
```

Place reusable controlled fields in `app/components/forms/`.

## Validation Strategy

- **Sync** for shape, length, format — done by Zod.
- **Async** (e.g., "is this email available") — done in the mutation, surfaced via `setError`. Avoid async Zod refinements; they slow down typing.
- **Cross-field** rules (`refine`) live in the schema, not in the component.

## Submit-on-Enter / Submit-Disabled

- Forms must submit on Enter inside any text input — this is RHF's default.
- The submit button is `type="submit"`.
- Disable submit while `isSubmitting` is true.
- Re-enable after the mutation settles.

## Accessibility

- Every `input`, `select`, `textarea` has an associated `<label>` (via `htmlFor` or by wrapping).
- Field errors are linked via `aria-describedby` when rendered separately.
- The form sets `aria-busy` while submitting if the form is the page's primary content.

## Testing

Form tests use `userEvent` from RTL. See `testing.md` for examples. Always test:
- Validation errors render
- Successful submit calls the mutation with the right payload
- Server-side field error renders inline
