
from app.ports.job_queue import JobQueue
import boto3
import json
import os
import logging

class SQSQueue(JobQueue):
    def enqueue(self, prompt: dict) -> None:
        try:    
            logging.info(f"Processing with SQS Queue job with prompt: {prompt}")

            queue_url = os.getenv("SQS_QUEUE_URL")
            endpoint_url = os.environ.get("SQS_ENDPOINT_URL")
            sqs = boto3.client(
                "sqs",
                endpoint_url=endpoint_url,
                region_name="us-east-1",
            )
            message = {
                "meal_description": prompt["meal_description"],
                "meal_id": prompt["meal_id"]
            }
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message)
            )
        except Exception as e:
            raise Exception(f"Failed to enqueue job to SQS: {e}")