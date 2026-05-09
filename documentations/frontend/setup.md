# Frontend Setup

The frontend is in early development. Technology choices are confirmed but the application is not yet feature-complete.

## Tech Stack

- **React 19**
- **TypeScript**
- **Vite** (build tool)
- **SWC** for fast compilation (via `@vitejs/plugin-react-swc`)

## Project Structure

```
sources/frontend/
├── app/
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Entry point
│   ├── App.css              # Component styles
│   ├── index.css            # Global styles
│   ├── vite-env.d.ts        # Vite type declarations
│   ├── services/
│   │   └── api.tsx          # API client (healthcheck only)
│   └── components/
│       └── StatusIndicator.tsx
├── index.html               # HTML entry
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript config
├── tsconfig.app.json        # App-specific TS config
├── tsconfig.node.json       # Node-specific TS config
├── eslint.config.js         # ESLint configuration
└── package.json             # Dependencies
```

## Dependencies

Runtime:
- `react` ^19.1.0
- `react-dom` ^19.1.0

Dev:
- `typescript` ~5.8.3
- `vite` ^6.3.5
- `@vitejs/plugin-react-swc` ^3.9.0
- `eslint` ^9.25.0, `typescript-eslint` ^8.30.1

## API Client

Currently minimal - only a healthcheck endpoint is implemented:

```typescript
// sources/frontend/app/services/api.tsx
export const getHealthStatus = async (): Promise<HealthResponse> => {
  const response = await fetch('http://localhost:8800/api/debug/healthcheck/status');
  return await response.json() as HealthResponse;
};
```

## Development Server

```bash
# From project root
make run_dev_frontend

# Or manually
cd sources/frontend && npm run dev
```

Server runs at `http://localhost:5173` with HMR and fast refresh.

## Build

```bash
cd sources/frontend && npm run build
```

Output goes to `sources/frontend/dist/`. Not yet integrated with backend serving.
