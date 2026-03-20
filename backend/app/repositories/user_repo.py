from sqlmodel import Session, select
from app.models.db_models import User

def get_user_by_cognito_sub(db: Session, cognito_sub: str) -> User | None:
    return db.exec(select(User).where(User.cognito_sub == cognito_sub)).first()
