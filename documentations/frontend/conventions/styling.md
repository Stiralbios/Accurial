# Styling

Tailwind CSS is the styling system. There is no global CSS architecture (no BEM, no SCSS partials, no CSS-in-JS) outside Tailwind utilities and the design tokens declared in `tailwind.config.ts`.

## Why Tailwind

- Co-located with markup, no naming overhead
- Strong design-token discipline via `theme.extend`
- Excellent purge / build size
- Compatible with Radix-based primitives if a component library is later adopted (e.g., shadcn/ui)

## File Layout

```
app/
├── styles/
│   └── index.css            # @tailwind directives + minimal globals + tokens via @layer
tailwind.config.ts           # design tokens, content paths
postcss.config.js            # tailwindcss + autoprefixer
```

`index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    color-scheme: light dark;
  }
}
```

## Design Tokens

Tokens live in `tailwind.config.ts` under `theme.extend`. Examples:
- Colors (primary, accent, danger, neutral scale)
- Spacing scale (4, 8, 12, 16, 24, 32, 48, 64)
- Border radius (sm, md, lg)
- Typography (font-sans, font-display, font sizes)

Use semantic names (`primary`, `danger`) rather than hue names (`blue`, `red`) so re-theming doesn't require rewriting components.

## Class Composition

- Inline classes are fine — readable, with `prettier-plugin-tailwindcss` ordering them automatically.
- For variants, use [`clsx`](https://github.com/lukeed/clsx) (or `cn` helper) and the `cva` (class-variance-authority) pattern when a component has more than two variants.

```tsx
// app/components/Button.tsx
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded font-medium transition-colors disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary text-white hover:bg-primary/90",
        ghost: "bg-transparent text-primary hover:bg-primary/10",
        danger: "bg-danger text-white hover:bg-danger/90",
      },
      size: {
        sm: "px-3 py-1 text-sm",
        md: "px-4 py-2",
        lg: "px-6 py-3 text-lg",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={buttonVariants({ variant, size, className })} {...props} />;
}
```

## Dark Mode

Use Tailwind's `class` strategy (`darkMode: 'class'`). Toggle by adding `dark` to the `<html>` element. The toggle UI lives in a Zustand store (`useUiStore.theme`).

## When NOT to Use a Tailwind Utility

- Long, repeated class strings (≥ 6 classes in 3+ places) → extract a component, not a CSS class.
- Animations / keyframes that don't fit `transition-` and `animate-` utilities → declare in the Tailwind config, not in a stray CSS file.
- CSS-only effects beyond Tailwind's reach → add a CSS module **co-located** with the component, scoped by file name.

## What's Forbidden

- Inline `style={...}` props for static styling — only allowed for dynamic values (e.g., `transform: translateX(${x}px)`).
- Global CSS rules outside `@layer base`.
- `!important` — break the cascade by ordering Tailwind classes correctly or restructuring the component.
- BEM, OOCSS, or any other naming method — Tailwind utilities are the only abstraction.

## Plugins

Useful plugins enabled in `tailwind.config.ts`:
- `@tailwindcss/forms` — sane form defaults
- `@tailwindcss/typography` — for prose / markdown rendering when needed (added on first use)

## Testing

Snapshot tests of class strings are forbidden — they're brittle and don't catch real bugs. Test the **behavior** (interactive states, disabled, focused) and use visual regression testing if the project later adds it.
