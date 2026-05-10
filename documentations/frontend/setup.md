# Frontend Setup

The frontend is a single-page React application that consumes the Accurial FastAPI backend.

## Tech Stack

| Layer | Choice |
|---|---|
| UI library | React 19 |
| Language | TypeScript (strict) |
| Build tool | Vite 6 (SWC plugin) |
| API client | [Orval](https://orval.dev/) generates a typed [TanStack Query](https://tanstack.com/query) client from the backend OpenAPI schema |
| Server state | TanStack Query v5 |
| Client state | [Zustand](https://zustand-demo.pmnd.rs/) |
| Routing | [TanStack Router](https://tanstack.com/router) (file-based) |
| Forms & validation | React Hook Form + Zod |
| Styling | Tailwind CSS |
| Testing | Vitest + React Testing Library + MSW |
| Lint / format | ESLint (typescript-eslint, jsx-a11y, import) + Prettier |
| Auth transport | httpOnly cookie (target convention — see `features/auth.md`) |

## Project Layout

```
sources/frontend/
├── app/
│   ├── main.tsx                      # Entry point, providers (QueryClient, Router)
│   ├── routes/                       # File-based TanStack Router routes
│   │   ├── __root.tsx
│   │   ├── index.tsx
│   │   └── ...
│   ├── features/                     # Feature-based modules (mirrors backend)
│   │   ├── auth/
│   │   ├── question/
│   │   ├── prediction/
│   │   └── resolution/
│   ├── components/                   # Cross-feature reusable components
│   ├── hooks/                        # Cross-feature reusable hooks
│   ├── stores/                       # Zustand stores (client state)
│   ├── services/
│   │   ├── api/
│   │   │   ├── generated/            # Orval-generated client (committed, not edited)
│   │   │   └── client.ts             # fetch wrapper (credentials, error mapping)
│   │   └── query-client.ts           # TanStack QueryClient instance
│   ├── lib/                          # Pure helpers (no React)
│   ├── styles/
│   │   └── index.css                 # Tailwind directives + design tokens
│   └── vite-env.d.ts
├── public/
├── index.html
├── package.json
├── vite.config.ts
├── vitest.config.ts
├── vitest.setup.ts
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── eslint.config.js
├── .prettierrc
├── tailwind.config.ts
├── postcss.config.js
└── orval.config.ts
```

Tests live under `tests/frontend/<feature>/` mirroring the backend.

## Prerequisites

- Node.js 20+ (devbox-managed)
- npm 10+
- A running backend on `http://localhost:8800` for API codegen

## Install

```bash
cd sources/frontend
npm install
```

## Scripts

| Script | Purpose |
|---|---|
| `npm run dev` | Start Vite dev server with HMR on `http://localhost:5173` |
| `npm run build` | Type-check + production build to `dist/` |
| `npm run preview` | Preview the production build |
| `npm run lint` | Run ESLint on the whole project |
| `npm run lint:fix` | Run ESLint with `--fix` |
| `npm run format` | Format the project with Prettier |
| `npm run format:check` | Check formatting without writing |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run test` | Run Vitest once (CI mode) |
| `npm run test:watch` | Run Vitest in watch mode |
| `npm run test:ui` | Open Vitest UI |
| `npm run coverage` | Run Vitest with coverage |
| `npm run generate:api` | Run Orval to regenerate `app/services/api/generated/` |

## Makefile shortcuts

| Command | Purpose |
|---|---|
| `make run_dev_frontend` | Same as `npm run dev` |
| `make lint_frontend` | `npm run lint` |
| `make test_frontend` | `npm run test` |
| `make typecheck_frontend` | `npm run typecheck` |
| `make generate_frontend_api` | `npm run generate:api` (requires running backend) |

## Environment Variables

Vite reads `.env`, `.env.development`, `.env.local` from `sources/frontend/`.

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8800` | Backend base URL used by the fetch wrapper and Orval codegen |

Never expose secrets in `VITE_*` variables — they are bundled into the client.

## API Codegen Flow

1. Start the backend: `make run_dev_env`
2. Generate the client: `npm run generate:api`
3. Commit `app/services/api/generated/` along with the change
4. Use the generated hooks (e.g., `useListQuestion`, `useCreateQuestion`) in feature code

See `conventions/services.md` for usage rules and `api/openapi.md` for the OpenAPI exposure on the backend.

## Build & Deploy

```bash
npm run build
```

Output goes to `sources/frontend/dist/`. Production deployment integration with the backend is not yet defined and will be documented in `documentations/deployment/` when established.
