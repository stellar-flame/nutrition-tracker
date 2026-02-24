import boto3
import time
import os
from lambdas.nutrition_ai import lambda_function  # adjust import as needed
import logging
logging.basicConfig(level=logging.INFO)

endpoint_url = os.environ.get("SQS_ENDPOINT_URL")
queue_url = os.environ.get("SQS_QUEUE_URL")

sqs = boto3.client(
    "sqs",
    endpoint_url=endpoint_url,
    region_name="us-east-1",
    aws_access_key_id="x",
    aws_secret_access_key="x"
)


while True:
    try:
        resp = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5
        )
        for msg in resp.get("Messages", []):
            event = {
                "Records": [
                    {
                        "body": msg["Body"]
                    }
                ]
            }
            try:
                lambda_function.handler(event)
                logging.info(f"Processed message: {msg['MessageId']}")
            except Exception as e:
                logging.error(f"Error processing message {msg['MessageId']}: {e}")
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg["ReceiptHandle"]
            )
            logging.info(f"Deleted message: {msg['MessageId']}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Polling error: {e}")
        time.sleep(5)