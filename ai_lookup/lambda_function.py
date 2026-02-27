import json
import logging

from jobs.openai_loookup_job import ai_lookup
from jobs.nutrition_result_update_job import update_nutrition_info, mark_as_failed

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

def handler(event, context=None):
    for record in event.get("Records", []):
        body = record.get("body")
        # body is a JSON string, so pare it
        data = json.loads(body)
        return process_nutrition_event(data)
    
def process_nutrition_event(prompt):
    meal_id = prompt.get("meal_id")
    meal_description = prompt.get("meal_description")
    
    try:
        logger.info(f"Processing nutrition event for meal_id {meal_id} with description: {meal_description}")
        data = ai_lookup(meal_description, meal_id) 
        update_nutrition_info(meal_id=meal_id, items=data["items"])
        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"result": data}),
        }
    except Exception as e:
        mark_as_failed(meal_id=meal_id, error_message=str(e))
        return {
            "statusCode": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
    