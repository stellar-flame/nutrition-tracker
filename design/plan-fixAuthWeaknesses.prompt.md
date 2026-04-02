# Fix Auth Weaknesses

## 🔴 Real issues

### 1. `POST /users/create` — duplicate registration returns 500
**File:** `backend/app/api/routers/users.py`
Add a duplicate check before creating the user:
```python
existing = user_repo.get_user_by_cognito_sub(db, cognito_sub)
if existing:
    raise HTTPException(status_code=409, detail="User already registered.")
```

### 2. `apiClient.ts` — 401 redirect loop on `/login`
**File:** `frontend/src/lib/apiClient.ts`
Only redirect if not already on `/login`:
```ts
if (axios.isAxiosError(error) && error.response?.status === 401) {
  sessionStorage.removeItem('accessToken');
  if (window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
}
```

### 3. `Login.tsx` — default import mismatch
**File:** `frontend/src/app/routes/Login.tsx`
Change:
```ts
import api from '@/lib/apiClient';
```
To:
```ts
import { api } from '@/lib/apiClient';
```

---

## 🟡 Worth fixing soon

### 4. `AuthContext` — no token expiry handling
**File:** `frontend/src/app/auth/AuthContext.tsx`
- Cognito access tokens expire after 1 hour
- On page refresh, a stale token is restored from sessionStorage without checking `exp`
- Fix: decode the token on rehydration and clear if expired, or use the refresh token returned by `authenticateUser` to silently renew

### 5. `ConfirmEmail.tsx` — email lost on page refresh
**File:** `frontend/src/app/routes/ConfirmEmail.tsx`
- Email comes from `location.state` which is cleared on refresh
- Fix: add a fallback input field shown when `email` is empty so user can re-enter it

### 6. `cognito.py` — JWKS cached forever
**File:** `backend/app/infrastructure/auth/cognito.py`
- `@lru_cache(maxsize=None)` never expires — AWS rotates keys periodically
- Fix: add a TTL (e.g. cache for 24h) or re-fetch on `JWTError` before giving up

---

## 🔵 Minor

### 7. `users.py` — unused imports and missing status code
**File:** `backend/app/api/routers/users.py`
- Remove unused `from app.api.dependencies import get_current_user` (only used on `GET /me` which does use it — check if actually unused)
- Add `status_code=201` to `POST /create`:
```python
@router.post("/create", response_model=UserRead, status_code=201)
```
