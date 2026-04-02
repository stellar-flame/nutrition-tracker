
from fastapi import HTTPException, Header
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from sqlmodel import Session
from app.database.database import get_session
from app.infrastructure.auth.cognito import get_current_user_sub
from app.models.db_models import User
from app.models.nutrition_schemas import UserBase, UserRead
from app.repositories import user_repo


router = APIRouter(prefix="/users", tags=["users"])   


@router.get("/me", response_model=UserRead)
def get_user(user = Depends(get_current_user)) -> UserRead | None:
    return UserRead.model_validate(user)

@router.post("/create", response_model=UserRead, status_code=201)
def create_user(payload: UserBase,db: Session = Depends(get_session), authorization: str | None = Header(default=None)) -> UserRead:
    cognito_sub = get_current_user_sub(authorization)  # verified from JWT
    existing = user_repo.get_user_by_cognito_sub(db, cognito_sub)
    if existing:
        raise HTTPException(status_code=409, detail="User already registered.")
    user = User(**payload.model_dump(), cognito_sub=cognito_sub)
    saved = user_repo.create_user(db, user)
    return UserRead.model_validate(saved)