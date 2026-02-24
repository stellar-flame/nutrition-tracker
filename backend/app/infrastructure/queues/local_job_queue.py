# app/queue/local_queue.py
import asyncio
from app.ports.job_queue import JobQueue
from lambdas.nutrition_ai import lambda_function

class LocalJobQueue(JobQueue):

    async def enqueue(self, prompt: dict) -> None:
        asyncio.create_task(lambda_function.process_nutrition_event(prompt=prompt))
