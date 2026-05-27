# Codebase Review — Nutrition Tracker

## Overview

A well-structured full-stack application: React 19 frontend → FastAPI backend → SQS → Lambda (GPT-4o-mini) → webhook back to backend. Clean separation of concerns, good use of async job queue pattern, and a sensible local dev setup with Docker Compose + LocalStack. The core architecture is sound; the issues below are specific and fixable.

---

## 1. Bugs (High Priority)

### Lambda processes only the first SQS record

`ai_worker/lambda_function.py:15`

```python
for record in event.get("Records", []):
    body = record.get("body")
    data = json.loads(body)
    return process_nutrition_event(data)  # ← returns inside loop
```

`return` inside the `for` exits after the first record. SQS can batch multiple records per Lambda invocation, so all records after the first are silently dropped. Fix:

```python
def handler(event, context=None):
    results = []
    for record in event.get("Records", []):
        data = json.loads(record["body"])
        results.append(process_nutrition_event(data))
    return results
```

### Internal webhook raises `ValueError` → 500, not 404

`backend/app/repositories/meal_repo.py:24` + `backend/app/api/routers/internal.py:20-22`

`attach_meal_items` raises `ValueError` if the meal isn't found. The router then does:

```python
updated = meal_repo.attach_meal_items(db, meal_id, items)
if not updated:   # Never reached — ValueError already escaped
    raise HTTPException(status_code=404, ...)
```

The `ValueError` propagates as a 500. Either have the repo return `None` and check it in the router, or catch `ValueError` in the router.

### Internal webhook has no schema validation → `KeyError` → 500

`backend/app/api/routers/internal.py:18-19`

```python
meal_id = payload["meal_id"]   # KeyError if missing
items = payload["items"]       # KeyError if missing
```

`payload: dict` with no Pydantic model means any malformed call crashes with a 500 instead of 422. Define a proper request body:

```python
class NutritionResultPayload(BaseModel):
    meal_id: int
    items: list[MealItemData]
```

---

## 2. Security

### Secrets in `.env` files

The `.env` files exist locally with real values (OpenAI key, internal token, Cognito credentials). They're gitignored, but check `git log --all -- backend/.env ai_worker/.env` to confirm they were never accidentally staged. The `INTERNAL_TOKEN=supersecretinternaltoken12345` is a placeholder — make sure production uses a properly random value (e.g. `openssl rand -hex 32`).

### `AUTH_DISABLED` flag risk

`backend/app/infrastructure/auth/cognito.py:39-40`

```python
if os.environ.get("AUTH_DISABLED") == "true":
    return "default-user-sub"
```

Fine for dev, but there's no guard preventing this env var from being set in production. Consider asserting it's not set when `ENV=production`, or remove it and use dependency injection overrides in tests instead.

### No audience validation on JWT

`backend/app/infrastructure/auth/cognito.py:32-35`

```python
options={"verify_aud": False},  # access tokens have no aud
```

Cognito access tokens don't carry an `aud` claim, so `verify_aud: False` is correct. The `client_id` check on line 58 compensates. This is fine — worth documenting clearly since it looks like a security shortcut at a glance.

### `sessionStorage` for tokens

Access tokens in `sessionStorage` survive refreshes but are accessible via JS (XSS risk). For this app's threat model it's acceptable, but `httpOnly` cookies would be more secure. If third-party scripts are ever added, revisit this.

---

## 3. Code Quality

### `print()` instead of `logger` in routers

`backend/app/api/routers/nutrition.py:19,43`

```python
print(f"Fetching meals for user {user.id} on date {date}")
```

The module has `import logging` and other routers use `logger.info()`. Replace these `print()` calls with `logger.debug()`.

### Debug `console.log` left in production

`frontend/src/app/hooks/useMeals.ts:33-34`

```typescript
console.log(`Checking meal ${meal.created_at} with status ${meal.status}`);
console.log(`Current time: ${Date.now()}, Created at: ${meal.created_at}, ...`);
```

These fire on every render cycle with active pending meals. Remove them.

### OpenAI client instantiated per call

`ai_worker/jobs/nutrition_estimator.py:9`

```python
def estimate(description: str, meal_id: int):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60.0)
```

A new `OpenAI` client is created for every meal. Lambda reuses the execution environment between warm invocations — move the client to module level:

```python
_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=60.0)

def estimate(description: str, meal_id: int):
    response = _client.chat.completions.create(...)
```

### Unused import

`backend/app/api/routers/internal.py:1`

```python
from asyncio import sleep  # never used
```

### Stray comment mid-file

`backend/app/repositories/meal_repo.py:13`

```python
# meal_repo.py
def create_meal(db: Session, meal: Meal) -> Meal:
```

### Typo in comment

`ai_worker/lambda_function.py:13`

```python
# body is a JSON string, so pare it
```

Should be "parse".

---

## 4. Performance

### Missing database indices

The schema has no explicit indices on the most-queried columns:
- `users.cognito_sub` (unique lookup on every authenticated request)
- `meals.user_id` + `meals.date` (compound filter on every meal fetch)

Add to a new Alembic migration:

```python
Index("ix_users_cognito_sub", User.cognito_sub, unique=True)
Index("ix_meals_user_date", Meal.user_id, Meal.date)
```

### `created_at` stored as string

`backend/app/api/routers/nutrition.py:46`

```python
created_at = datetime.now(timezone.utc).isoformat()  # str
```

`Meal.created_at` is a `str` column. The query sorts by it with `desc(Meal.created_at)` — this works with ISO8601 strings but is semantically fragile and won't benefit from a proper index. Make it a `DateTime` column with timezone and let the DB handle sorting.

### 10-second client-side failure timeout is too short

`frontend/src/app/hooks/useMeals.ts:35`

```typescript
if (now - createdAt > 10_000) {
    return { ...meal, status: 'failed' as const };
}
```

This is a UI-only pessimistic timeout. If OpenAI responds in 11 seconds (common), the meal shows as failed on screen even though the backend completes it successfully. The next 3-second poll will then show a successful meal that was already marked failed. Consider raising this to 60–90 seconds to match the OpenAI timeout, or base the "failed" display solely on the backend `status: 'failed'` response.

---

## 5. Test Coverage Gaps

| Area | Current | Gap |
|---|---|---|
| `POST /nutrition/meals` | None | Happy path, queue failure path |
| `GET /nutrition/summary` | None | No meals, multiple meals |
| `GET /users/me` | Indirect | Direct test with mocked `get_current_user` |
| `attach_meal_items` | None | Missing meal → ValueError propagation |
| Cognito JWT verification | None | Expired token, wrong `token_use`, wrong `client_id` |
| Lambda multi-record batching | None | Two records in one SQS event |
| Internal webhook schema | None | Missing `meal_id` key |

---

## 6. Minor / Nice-to-Have

- **No rate limiting** on any endpoints — `POST /nutrition/meals` and `POST /users/create` are open to abuse by authenticated users.
- **No correlation ID** — adding `X-Request-ID` logging makes tracing Lambda → backend calls much easier.
- **`/users/create`** should be `POST /users` (REST convention for resource creation).
- **`CompleteProfile.tsx`** — email is lost if the user refreshes the confirm-email page. Persist email in `sessionStorage` during the registration flow.
- **Token expiry** — `AuthContext` stores the token but doesn't check the `exp` claim. A user with an expired token gets a 401 and is silently logged out rather than having the session refreshed.

---

## Summary

The architecture is solid and the async meal-processing flow works well end-to-end. The most impactful fixes in priority order:

1. **Lambda `return` inside loop** — silent data loss in production under batch SQS delivery
2. **`attach_meal_items` ValueError** — internal failures return 500 instead of 404
3. **Missing DB indices** — will hurt at any meaningful scale
4. **Client-side 10s timeout** — causes misleading UX on slow-but-successful OpenAI responses
5. **Remove `console.log` / `print` debug statements** — noise in production logs
