import uuid
from decimal import Decimal
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from app.models.nutrition_schemas import MealItemBase


def _floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_floats_to_decimal(i) for i in obj]
    return obj


def _decimals_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _decimals_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimals_to_float(i) for i in obj]
    return obj


def create_pending_meal(table, user_id: int, description: str, date: str, time: str) -> dict:
    meal_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    ttl = int(datetime.now(timezone.utc).timestamp()) + 86400
    item = {
        "meal_id": meal_id,
        "user_id": user_id,
        "date": date,
        "time": time,
        "description": description,
        "created_at": created_at,
        "status": "pending_ai",
        "items": [],
        "ttl": ttl,
    }
    table.put_item(Item=item)
    return item


def get_pending_meal(table, meal_id: str) -> dict | None:
    response = table.get_item(Key={"meal_id": meal_id})
    item = response.get("Item")
    return _decimals_to_float(item) if item else None


def attach_ai_items(table, meal_id: str, items: list[MealItemBase]) -> None:
    """Update pending meal with AI-estimated items and advance to pending_approval status.
    Raises ClientError with ConditionalCheckFailedException if the meal no longer exists."""
    table.update_item(
        Key={"meal_id": meal_id},
        UpdateExpression="SET #s = :status, #i = :items",
        ConditionExpression="attribute_exists(meal_id)",
        ExpressionAttributeNames={"#s": "status", "#i": "items"},
        ExpressionAttributeValues={
            ":status": "pending_approval",
            ":items": _floats_to_decimal([i.model_dump() for i in items]),
        },
    )


def get_pending_meals_by_date(table, user_id: int, date: str) -> list[dict]:
    response = table.query(
        IndexName="UserDateIndex",
        KeyConditionExpression=Key("user_id").eq(user_id) & Key("date").eq(date),
    )
    return [_decimals_to_float(item) for item in response.get("Items", [])]


def set_failed_status(table, meal_id: str, error: str) -> None:
    """Mark a pending meal as failed. Silently no-ops if the record no longer exists."""
    try:
        table.update_item(
            Key={"meal_id": meal_id},
            UpdateExpression="SET #s = :status, error_message = :error",
            ConditionExpression="attribute_exists(meal_id)",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": "failed", ":error": error},
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise


def delete_pending_meal(table, meal_id: str) -> None:
    table.delete_item(Key={"meal_id": meal_id})
