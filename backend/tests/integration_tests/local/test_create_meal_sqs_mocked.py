import subprocess
import threading
import time
import pytest
import httpx

from dev_tools.sqs_lambda_polling import SQSQueuePoller

#Start LocalStack SQS with SQS_QUEUE_URL for testing
#   docker run -d -p 4566:4566 -p 4571:4571 --name localstack localstack/localstack


BASE_URL = "http://localhost:8000"  # Assuming FastAPI is running here

@pytest.fixture(scope="session", autouse=True)
def start_poller():
    # Start your polling script with output visible in terminal
    proc = subprocess.Popen(
        ["python", "-m", "dev_tools.sqs_lambda_polling"],
    )
    time.sleep(2)  # Give poller time to start
    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="session", autouse=True)
def start_uvicorn():
    # Start Uvicorn server with output visible in terminal and mocked SQS_QUEUE_URL
    proc = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    )
    time.sleep(2)  # Give server time to start
    yield
    proc.terminate()
    proc.wait()


@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=60.0)  # Long timeout for OpenAI

 
class TestFullMealFlow:
    """End-to-end test with real OpenAI, real DB, real HTTP."""

    def test_create_meal_and_get_nutrition(self, client):
        # 1. Create a meal
        response = client.post("/nutrition/meals", json={
            "description": "1 banana and 2 tablespoons peanut butter",
            "date": "2024-07-01",
            "time": "12:00"

        })
        assert response.status_code == 201
        meal = response.json()
        meal_id = meal["id"]
        
        assert meal["description"] == "1 banana and 2 tablespoons peanut butter"
        assert meal["status"] == "pending"  # Async processing

        # 2. Poll until complete (or timeout)
        for _ in range(20):  # Max 20 attempts
            time.sleep(2)
            response = client.get("/nutrition/meals", params={"date": "2024-07-01"})
            meals = response.json()
            meal = next((m for m in meals if m["id"] == meal_id), None)
            
            if meal and meal["status"] == "complete":
                break
        
        assert meal["status"] == "complete", f"Meal stuck in {meal['status']}"
        
    
        # 3. Verify nutrition data exists
        assert len(meal["items"]) > 0
        
        # Check reasonable values (AI-generated, so rough bounds)
        total_calories = sum(item["caloriesKcal"] for item in meal["items"])
        assert 200 < total_calories < 500, f"Unexpected calories: {total_calories}"
