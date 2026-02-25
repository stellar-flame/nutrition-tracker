import httpx
import os
import logging

logger = logging.getLogger(__name__)


def update_nutrition_info(meal_id: int, items: list[dict]):
        # Add before the post call
        logger.info(f"Posting to {os.getenv('INTERNAL_API_URL')}/nutrition_result with token {os.getenv('INTERNAL_TOKEN')}")
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                os.getenv("INTERNAL_API_URL") + "/nutrition_result",
                headers={"X-Internal-Token": os.getenv("INTERNAL_TOKEN")},
                json={
                    "meal_id": meal_id,
                    "items": items
                }
            )
            response.raise_for_status()
            logger.info(f"Updated nutrition info for meal_id {meal_id}")
            
        
       
def mark_as_failed(meal_id: int, error_message: str):
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                os.getenv("INTERNAL_API_URL") + "/nutrition_failed",
                headers={"X-Internal-Token": os.getenv("INTERNAL_TOKEN")},
                json={
                    "meal_id": meal_id,
                    "error": error_message
                }
            )
            response.raise_for_status()
            logger.info(f"Marked meal {meal_id} as FAILED")
    except Exception as e:
        # Last resort - log but don't raise, nothing more we can do
        logger.error(f"Failed to mark meal {meal_id} as FAILED: {e}")