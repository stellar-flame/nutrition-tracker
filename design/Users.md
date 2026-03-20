
## Plan: Add Amazon Cognito Authentication

**TL;DR:** Cognito acts as the identity provider — it handles user registration, login, and token issuance. Your backend only needs to **verify the JWT**, not manage passwords. Your frontend uses the Amplify/Cognito SDK to log in and attach the token to every API call.

---

### Phase 1 — AWS Setup (no code yet)

1. Create a **Cognito User Pool** in AWS Console (or CloudFormation)
   - Enable email/password sign-in
   - Note the **User Pool ID** and **region**
2. Create an **App Client** within the pool (no client secret — SPA client)
   - Note the **Client ID**
3. Optionally configure a **Cognito domain** for the hosted UI (simplest login page, zero frontend work)

### Phase 2 — Backend JWT Verification

4. Add `python-jose` (JWT decode) and `httpx` to backend/requirements.txt
5. Add a `get_current_user` dependency to backend/app/api/dependencies.py that:
   - Extracts the `Authorization: Bearer <token>` header
   - Fetches Cognito's JWKS (public keys) from `https://cognito-idp.<region>.amazonaws.com/<user-pool-id>/.well-known/jwks.json`
   - Verifies the token signature + expiry using `python-jose`
   - Extracts the `sub` claim (Cognito's unique user UUID)
6. Add a `get_or_create_user` step that looks up `User` by `cognito_sub` and creates if not found — this bridges Cognito identity to your DB row
7. Add `cognito_sub: str` column to the `User` DB model + migration
8. Wire `get_current_user` into `nutrition.py` routes, replacing `user_id=1`

### Phase 3 — Frontend

9. Install `aws-amplify` or `amazon-cognito-identity-js` in the frontend
10. Add a `Login` component that calls Cognito's hosted UI or uses Amplify's `Auth.signIn()`
11. On successful login, store the **ID token** (JWT) in memory or `sessionStorage`
12. Add a request interceptor to frontend/src/lib/apiClient.ts that attaches `Authorization: Bearer <token>` to every request
13. Add a protected route wrapper — redirect to login if no token present
14. Add a logout button that clears the token

### Phase 4 — Infrastructure

15. Add Cognito User Pool + App Client to the deployment/aws/CFN-templates/ CloudFormation stack

---

**Relevant files to modify:**
- backend/requirements.txt — add `python-jose[cryptography]`
- backend/app/api/dependencies.py — add `get_current_user`
- backend/app/models/db_models.py — add `cognito_sub` to `User`
- backend/app/api/routers/nutrition.py — use `get_current_user`
- frontend/src/lib/apiClient.ts — add auth interceptor
- New: `frontend/src/app/components/Login.tsx`
- New: `backend/alembic/versions/<rev>_add_cognito_sub_to_users.py`

**Key decision:** The Cognito `sub` is a UUID that is stable per user and per user pool. Store it as `cognito_sub` on your `User` table rather than putting the DB `id` in the token — Cognito controls the token contents, not you. Your backend maps `cognito_sub → User.id` on every request.