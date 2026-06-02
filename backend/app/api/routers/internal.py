from fastapi import APIRouter, Depends, HTTPException
from botocore.exceptions import ClientError
from app.api.dependencies import verify_internal_token, get_dynamo
from app.repositories import pending_meal_repo
from app.models.nutrition_schemas import NutritionResultPayload, NutritionFailedPayload
import logging

router = APIRouter(prefix="/internal", tags=["internal"])
logger = logging.getLogger(__name__)


@router.post("/nutrition_result")
def nutrition_result(
    payload: NutritionResultPayload,
    dynamo=Depends(get_dynamo),
    _: str = Depends(verify_internal_token),
):
    logger.info(f"Received internal nutrition result: {payload}")

    try:
        pending_meal_repo.attach_ai_items(dynamo, payload.meal_id, payload.items)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise HTTPException(status_code=404, detail="Pending meal not found or already expired")
        raise

    logger.info(f"Updated pending meal {payload.meal_id} with AI nutrition info.")
    return {"status": "ok"}


@router.post("/nutrition_failed")
def mark_nutrition_failed(
    payload: NutritionFailedPayload,
    dynamo=Depends(get_dynamo),
    _: str = Depends(verify_internal_token),
):
    pending_meal_repo.set_failed_status(dynamo, payload.meal_id, payload.error)
    logger.warning(f"Pending meal {payload.meal_id} marked failed: {payload.error}")
    return {"status": "ok"}
