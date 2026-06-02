from fastapi import APIRouter, Depends, HTTPException
from botocore.exceptions import ClientError
from app.api.dependencies import verify_internal_token, get_dynamo
from app.repositories import pending_meal_repo
import logging

router = APIRouter(prefix="/internal", tags=["internal"])
logger = logging.getLogger(__name__)


@router.post("/nutrition_result")
def nutrition_result(
    payload: dict,
    dynamo=Depends(get_dynamo),
    _: str = Depends(verify_internal_token),
):
    logger.info(f"Received internal nutrition result: {payload}")
    meal_id = payload["meal_id"]
    items = payload["items"]

    try:
        pending_meal_repo.attach_ai_items(dynamo, meal_id, items)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise HTTPException(status_code=404, detail="Pending meal not found or already expired")
        raise

    logger.info(f"Updated pending meal {meal_id} with AI nutrition info.")
    return {"status": "ok"}


@router.post("/nutrition_failed")
def mark_nutrition_failed(
    payload: dict,
    dynamo=Depends(get_dynamo),
    _: str = Depends(verify_internal_token),
):
    meal_id = payload["meal_id"]
    error = payload.get("error", "Unknown error")
    pending_meal_repo.set_failed_status(dynamo, meal_id, error)
    logger.warning(f"Pending meal {meal_id} marked failed: {error}")
    return {"status": "ok"}
