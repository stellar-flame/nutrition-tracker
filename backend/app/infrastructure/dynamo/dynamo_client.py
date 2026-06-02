import boto3
import os


def get_dynamo_table():
    kwargs = {"region_name": os.getenv("AWS_DEFAULT_REGION", "us-east-1")}
    endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL")
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(os.getenv("DYNAMODB_PENDING_MEALS_TABLE", "PendingMeals"))
