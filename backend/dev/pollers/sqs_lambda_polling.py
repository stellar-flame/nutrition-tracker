import sys

import boto3
import time
import os
from lambdas.nutrition_ai import lambda_function  # adjust import as needed
import logging
import signal
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(level=logging.INFO)

endpoint_url = os.environ.get("SQS_ENDPOINT_URL")
queue_url = os.environ.get("SQS_QUEUE_URL")
queue_name = os.environ.get("SQS_QUEUE_NAME")


class SQSQueuePoller:
    def __init__(self, queue_url=queue_url, endpoint_url=endpoint_url):
        self.queue_url = queue_url
        self.endpoint_url = endpoint_url

        self.sqs = boto3.client(
            "sqs",
            endpoint_url=self.endpoint_url,
            region_name="us-east-1",
            aws_access_key_id="x",
            aws_secret_access_key="x"
        )

        self.sqs.create_queue(QueueName=queue_name)
        

    def poll(self):
        logging.info(f"Starting SQS poller for queue: {queue_name} at {self.queue_url} with endpoint {self.endpoint_url}")
        while True:
            try:
                resp = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
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
                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=msg["ReceiptHandle"]
                    )
                    logging.info(f"Deleted message: {msg['MessageId']}")
                time.sleep(1)
            except Exception as e:
                logging.error(f"Polling error: {e}")
                time.sleep(5)

    def delete_queue(self, queue_name=queue_name):
        try:
            self.sqs.delete_queue(QueueUrl=self.queue_url)
            logging.info(f"Deleted SQS queue: {queue_name}")
        except Exception as e:
            logging.error(f"Error deleting SQS queue {queue_name}: {e}")

if __name__ == "__main__":
    poller = SQSQueuePoller()

    def cleanup(signum, frame):
        print("Terminating poller and deleting queue...")
        poller.delete_queue()
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    poller.poll()