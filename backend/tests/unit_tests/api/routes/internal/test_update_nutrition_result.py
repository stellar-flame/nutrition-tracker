import datetime
import pytest

from app.models.db_models import Meal

@pytest.fixture
def sample_meal(session):
    """A basic meal for tests that need one."""
    meal = Meal(
        date=datetime.date(2024, 7, 1),
        time="10:30",
        description="Apple and Peanut Butter",
        serving_size=1.0,
        status="pending",
    )
    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


def test_update_nutrition_result_updates_meal_and_items(client, sample_meal):
    #                                                   ↑ Must be a parameter
    resp = client.post(
        "/internal/nutrition_result",
        headers={"X-Internal-Token": "testtoken"},
        json={
            "meal_id": sample_meal.id,
            "items": [
                {
                    "description": "Banana",
                    "caloriesKcal": 105,
                    "proteinG": 1.3,
                    "carbsG": 27,
                    "fatG": 0.3,
                    "fiberG": 3.1,
                    "sugarG": 14,
                    "sodiumMg": 1,
                }
            ],
        },
    )
    assert resp.status_code == 200
    # Verify meal status updated
    meal_resp = client.get("/nutrition/meals", params={"date": "2024-07-01"})
    meal_data = meal_resp.json()[0]
    assert meal_data["status"] == "completed"
    # Verify meal item updated
    assert len(meal_data["items"]) == 1
    item = meal_data["items"][0]
    assert item["description"] == "Banana"
    assert item["caloriesKcal"] == 105
    assert item["proteinG"] == 1.3
    assert item["carbsG"] == 27
    assert item["fatG"] == 0.3
    assert item["fiberG"] == 3.1
    assert item["sugarG"] == 14
    assert item["sodiumMg"] == 1    
