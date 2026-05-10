import type { HttpHandler } from "msw";

// Per-feature handlers will be added as features land. Until then, an empty
// list is fine — vitest.setup.ts uses `onUnhandledRequest: 'error'` so any test
// that hits the network must add its own handler via server.use(...).

export const handlers: HttpHandler[] = [];
