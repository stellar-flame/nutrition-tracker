# app/queue/local_queue.py
from app.ports.job_queue import JobQueue
from lambdas.nutrition_ai import lambda_function
import logging

class LocalJobQueue(JobQueue):

    def enqueue(self, prompt: dict) -> None:
        logging.info(f"Processing job locally with prompt: {prompt}")
        lambda_function.process_nutrition_event(prompt=prompt)
