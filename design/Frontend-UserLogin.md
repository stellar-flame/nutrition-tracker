
## Plan: Frontend Cognito Authentication

Add self-registration, login, and protected routes to the React app. The frontend calls Cognito directly using `amazon-cognito-identity-js` to exchange credentials for an access token, which is then attached to every API request via the existing axios client.

**New dependencies to install**
- `react-router-dom` — routing (currently none — the app renders one component directly)
- `amazon-cognito-identity-js` — official lightweight AWS library to call Cognito sign-up/sign-in APIs

---

### Phase 1 — Foundation (blocks all other phases)

1. Install `react-router-dom` and `amazon-cognito-identity-js` (+ their `@types/`)
2. Add Cognito env vars to `frontend/.env.development`, .env.production, .env.example:
   - `VITE_COGNITO_USER_POOL_ID`
   - `VITE_COGNITO_CLIENT_ID`
   - `VITE_COGNITO_REGION`
3. Create `frontend/src/app/auth/AuthContext.tsx` — a React context that holds:
   - `accessToken: string | null` (in state + mirrored to `sessionStorage`)
   - `login(email, password)` — calls `CognitoUser.authenticateUser()`, stores token
   - `register(email, password)` — calls `CognitoUserPool.signUp()`
   - `logout()` — clears sessionStorage, resets state
   - On mount: restores token from `sessionStorage` (survives page refresh)
4. Wrap `main.tsx` with `<BrowserRouter>`, `<AuthProvider>`, and a `<Routes>` tree:
   - `"/"` → `<ProtectedRoute>` → existing `<Index>`
   - `"/login"` → `<LoginPage>`
   - `"/register"` → `<RegisterPage>`

### Phase 2 — API integration (*parallel with Phase 3*)

5. Update `frontend/src/lib/apiClient.ts` — add a **request interceptor** that reads the access token from `sessionStorage` and attaches `Authorization: Bearer <token>`
6. Update the **response interceptor** (already exists) — on `401` response, clear the token from `sessionStorage` and redirect to `/login`

### Phase 3 — UI screens (*parallel with Phase 2*)

7. Create `frontend/src/app/routes/Login.tsx` — form: email + password fields, submit calls `login()` from context, redirects to `/` on success, shows error message on failure
8. Create `frontend/src/app/routes/Register.tsx` — form: email + password + confirm password, calls `register()`, on success redirects to `/login` with a "Check your email to confirm" message (or auto-confirmed if disabled in Cognito pool for dev)
9. Create `frontend/src/app/components/ProtectedRoute.tsx` — reads `accessToken` from context, redirects to `/login` if null
10. Add a **Logout button** to the existing `Index` route (or a simple nav header component)

---

**Relevant files**
- `frontend/src/main.tsx` — add router + auth provider + routes
- `frontend/src/lib/apiClient.ts` — add request interceptor for Bearer token, update 401 handler
- `frontend/src/app/auth/AuthContext.tsx` — **new**, core auth state
- `frontend/src/app/routes/Login.tsx` — **new**
- `frontend/src/app/routes/Register.tsx` — **new**
- `frontend/src/app/components/ProtectedRoute.tsx` — **new**
- `frontend/.env.development` / .env.example — add three Cognito env vars

**Verification**
1. `npm run dev` — app should redirect to `/login` immediately (unauthenticated)
2. Register a user → check AWS Cognito Console that the user appeared
3. Log in → app loads nutrition tracker, network tab shows `Authorization: Bearer ...` on API requests
4. Refresh page → still logged in (sessionStorage restored)
5. Close tab, reopen → redirected to login (sessionStorage cleared)
6. Click logout → redirected to login, header gone from subsequent requests

**Decisions**
- Token stored in `sessionStorage` — survives refresh, clears on tab close, no XSS persistence risk
- Email verification screen deferred — works if you disable "email verification required" in Cognito user pool settings for dev. Can add `/confirm` route later
- No UI library — continue CSS modules pattern already in use
- `amazon-cognito-identity-js` chosen over full `aws-amplify` — lighter, no global config file required, just a `CognitoUserPool` instance

**Further considerations**
1. **Token refresh:** Cognito access tokens expire in 1 hour. `amazon-cognito-identity-js` can refresh transparently using the stored refresh token — this can be wired into the 401 interceptor as a follow-up
2. **User profile:** After login you may want to show the user's email/name in the header — the ID token (also returned on login) contains these claims and can be decoded client-side without a backend call