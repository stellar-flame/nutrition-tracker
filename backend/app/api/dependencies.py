from app.infrastructure.queues.local_job_queue import LocalJobQueue
from fastapi import Header, HTTPException
import os
from app.ports.job_queue import JobQueue
from app.infrastructure.queues.sqs_job_queue import SQSQueue
        

def get_queue() -> JobQueue:
    if os.environ.get("SQS_QUEUE_URL"):
        return SQSQueue()
    return LocalJobQueue()

def verify_internal_token(x_internal_token: str = Header(...)) -> str:
    if x_internal_token != os.environ.get("INTERNAL_TOKEN"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_internal_token