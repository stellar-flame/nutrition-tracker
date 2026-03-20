from fastapi import HTTPException
from functools import lru_cache
import os
import httpx
from jose import jwt, JWTError


@lru_cache(maxsize=None)
def _get_jwks() -> dict:
    region = os.environ["COGNITO_REGION"]
    pool_id = os.environ["COGNITO_USER_POOL_ID"]
    url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_current_user_sub(authorization: str | None) -> str:
    if os.environ.get("AUTH_DISABLED") == "true":
        return "default-user-sub" 

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.removeprefix("Bearer ")

    try:
        jwks = _get_jwks()
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},  # access tokens have no aud
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    if claims.get("token_use") != "access":
        raise HTTPException(status_code=401, detail="Expected an access token")

    if claims.get("client_id") != os.environ["COGNITO_APP_CLIENT_ID"]:
        raise HTTPException(status_code=401, detail="Invalid token audience")

    return claims["sub"]  # Cognito UUID, e.g. "a1b2c3d4-1234-..."
