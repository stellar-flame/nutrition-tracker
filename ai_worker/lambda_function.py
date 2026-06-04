import json
import logging

from jobs.nutrition_estimator import estimate
from jobs.nutrition_result_updater import update_nutrition_info, mark_as_failed

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

def handler(event, context=None):
    for record in event.get("Records", []):
        data = json.loads(record["body"])
        process_nutrition_event(data)

def process_nutrition_event(prompt):
    meal_id = prompt.get("meal_id")
    meal_description = prompt.get("meal_description")
    try:
        logger.info(f"Processing nutrition event for meal_id {meal_id} with description: {meal_description}")
        data = estimate(meal_description, meal_id)
        update_nutrition_info(meal_id=meal_id, items=data["items"])
    except Exception as e:
        mark_as_failed(meal_id=meal_id, error_message=str(e))
        raise
