from fastapi import HTTPException
import os
import time
import httpx
from jose import jwt, JWTError

_JWKS_TTL = 86_400  # 24 hours
_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0.0


def _fetch_jwks() -> dict:
    region = os.environ["COGNITO_REGION"]
    pool_id = os.environ["COGNITO_USER_POOL_ID"]
    url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def _get_jwks(force_refresh: bool = False) -> dict:
    global _jwks_cache, _jwks_fetched_at
    if force_refresh or _jwks_cache is None or (time.monotonic() - _jwks_fetched_at) > _JWKS_TTL:
        _jwks_cache = _fetch_jwks()
        _jwks_fetched_at = time.monotonic()
    return _jwks_cache


def _decode(token: str, force_refresh: bool = False) -> dict:
    return jwt.decode(
        token,
        _get_jwks(force_refresh=force_refresh),
        algorithms=["RS256"],
        options={"verify_aud": False},  # access tokens have no aud
    )


def get_current_user_sub(authorization: str | None) -> str:
    if os.environ.get("AUTH_DISABLED") == "true":
        return "default-user-sub" 

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.removeprefix("Bearer ")

    try:
        try:
            claims = _decode(token)
        except JWTError:
            # JWKS may have rotated — retry once with a fresh fetch
            claims = _decode(token, force_refresh=True)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    if claims.get("token_use") != "access":
        raise HTTPException(status_code=401, detail="Expected an access token")

    if claims.get("client_id") != os.environ["COGNITO_APP_CLIENT_ID"]:
        raise HTTPException(status_code=401, detail="Invalid token audience")

    return claims["sub"]  # Cognito UUID, e.g. "a1b2c3d4-1234-..."
