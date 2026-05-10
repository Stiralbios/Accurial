# Auth (Frontend)

Frontend handling of authentication. The transport convention is **httpOnly cookies set by the backend**.

## ⚠ Backend Prerequisites

This convention requires the following backend changes, which are **not yet implemented**:

1. `POST /api/auth/jwt/login` must set the JWT in a cookie:
   - `HttpOnly`
   - `Secure` (production)
   - `SameSite=Lax`
   - Path `/`
   - Max-Age aligned with `JWT_ACCESS_TOKEN_EXPIRATION_MINUTES`
2. A new `POST /api/auth/jwt/logout` endpoint that clears the cookie.
3. `get_current_user` (`sources/backend/auth/dependencies.py`) must read the JWT from the cookie. The current `OAuth2PasswordBearer` flow can remain as a fallback for SwaggerUI but cookie auth becomes the production path.
4. `CORSMiddleware` already uses `allow_credentials=True`. Ensure `ALLOWED_CORS_ORIGINS` lists the frontend origin explicitly (no `*`).
5. CSRF posture: with `SameSite=Lax`, CSRF risk on state-changing requests is mitigated for same-site contexts. Cross-site state-changing requests should add a CSRF double-submit token if the deployment topology requires it.

Until these land, the frontend must temporarily fall back to sending `Authorization: Bearer <token>` from a memory-only token. The fallback is documented at the bottom of this page and is removable once the backend prerequisites are met.

## Authentication Flow (Target — cookie-based)

```
1. User submits the login form.
2. Frontend POSTs username + password to /api/auth/jwt/login (form-encoded).
3. Backend validates, sets the auth cookie, returns 204 (or minimal body).
4. Frontend triggers a TanStack Query refetch of /api/user/me.
5. The me query succeeds -> the user is authenticated.
6. Frontend updates `useAuthStore.setIsAuthenticated(true)`.
7. Router redirects to the originally requested page.
```

```
Logout:
1. POST /api/auth/jwt/logout — backend clears the cookie.
2. queryClient.clear() — flush all server caches.
3. useAuthStore.setIsAuthenticated(false).
4. Navigate to /login.
```

## Frontend Pieces

### `app/features/auth/`

```
features/auth/
├── components/
│   ├── LoginForm.tsx
│   └── LogoutButton.tsx
├── hooks/
│   ├── useLogin.ts            # mutation: POST /api/auth/jwt/login
│   ├── useLogout.ts           # mutation: POST /api/auth/jwt/logout
│   └── useCurrentUser.ts      # query:    GET  /api/user/me
├── stores.ts                  # useAuthStore (Zustand) — mirrors `isAuthenticated`
├── schemas.ts                 # loginSchema (email + password)
└── index.ts
```

### `useCurrentUser` is the source of truth

```ts
import { useRetrieveUserMe } from "@/services/api/generated/user/user";

export function useCurrentUser() {
  return useRetrieveUserMe({
    query: {
      retry: false,
      staleTime: 5 * 60_000,
    },
  });
}
```

If the query succeeds, the user is authenticated. If it 401s, they are not. The auth store is a small mirror used by the router guard for synchronous checks.

### `useAuthStore` (Zustand)

```ts
interface AuthState {
  isAuthenticated: boolean;
  setAuthenticated: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools((set) => ({
    isAuthenticated: false,
    setAuthenticated: (value) => set({ isAuthenticated: value }),
  })),
);
```

The store is updated in `useCurrentUser`'s `onSuccess` / `onError` (or via a wrapping effect) and on login/logout mutations. It is **never** the source of truth for user data — only the boolean flag.

## Login Form

`LoginForm.tsx` is a standard RHF + Zod form (see `conventions/forms.md`). The mutation:

```ts
import { useLoginForAccessToken } from "@/services/api/generated/auth/auth";

export function useLogin() {
  const queryClient = useQueryClient();
  const setAuthenticated = useAuthStore((s) => s.setAuthenticated);
  return useLoginForAccessToken({
    mutation: {
      onSuccess: async () => {
        setAuthenticated(true);
        await queryClient.invalidateQueries({ queryKey: ["user", "me"] });
      },
    },
  });
}
```

The login endpoint accepts `application/x-www-form-urlencoded` per the OAuth2 password flow. Orval generates the correct content-type; if the codegen does not, the mutation function in `app/services/api/auth.ts` overrides it.

## Route Guard

Authenticated pages are nested under the `_authed` layout route (see `conventions/routing.md`). The guard reads `useAuthStore.getState().isAuthenticated` synchronously in `beforeLoad`.

On first load (cookie present, store initialized to `false`), the root route triggers `useCurrentUser`. The auth store flips to `true` once the me query succeeds. Routes that require auth wait on a small splash component while the bootstrap runs.

## Bootstrap on Page Load

`__root.tsx` (or `main.tsx` before `RouterProvider` mounts) prefetches `/api/user/me`:

```tsx
queryClient.prefetchQuery(getUserMeQueryOptions()).then(() => {
  // Sync isAuthenticated based on whether the query has data or errored.
});
```

## Security Notes

- The token is **never** accessible from JavaScript — XSS cannot read it.
- The token is **never** logged or sent to telemetry.
- `localStorage` is **not** used for auth.
- `useCurrentUser` is the only way the UI knows about the logged-in user.

## Transitional Fallback (until backend cookie support lands)

If the backend still returns `{ access_token, token_type }` in the body:

1. Store the token in `useAuthStore` **in memory only** (no `persist` middleware).
2. The fetch wrapper (`apiFetch`) reads the token via `useAuthStore.getState().token` and adds the `Authorization: Bearer ...` header.
3. On reload, the user must log in again. This is acceptable for development and for the early-stage MVP.
4. When the backend prerequisites land, delete the token state and the header injection — `credentials: 'include'` does the rest.

This fallback is the **only** time JS-side token storage is allowed. Mark the code with a `// TODO(auth-cookie): remove when backend cookies land` comment.

## Testing

- Unit-test `useLogin`, `useLogout`, `useCurrentUser` with MSW handlers.
- Integration-test the login → protected-route flow: `LoginForm` → me query → guard allows navigation.
- See `testing.md` for the MSW pattern.
