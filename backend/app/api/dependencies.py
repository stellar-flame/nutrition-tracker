from fastapi import Header, HTTPException, Depends
import os
from app.ports.job_queue import JobQueue
from app.infrastructure.queues.sqs_job_queue import SQSQueue
from app.infrastructure.auth.cognito import get_current_user_sub
from app.database.database import get_session
from app.repositories import user_repo
from app.models.db_models import User
from sqlmodel import Session

def get_queue() -> JobQueue:
    if os.environ.get("SQS_QUEUE_URL"):
        return SQSQueue()
    raise Exception("No job queue configured. Please set SQS_QUEUE_URL environment variable or implement another JobQueue.")    

def verify_internal_token(x_internal_token: str = Header(...)) -> str:
    if x_internal_token != os.environ.get("INTERNAL_TOKEN"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_internal_token


def get_current_user(authorization: str | None = Header(default=None),db: Session = Depends(get_session)) -> User:
    cognito_sub = get_current_user_sub(authorization)
    user = user_repo.get_user_by_cognito_sub(db, cognito_sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please complete registration.")
    return user
