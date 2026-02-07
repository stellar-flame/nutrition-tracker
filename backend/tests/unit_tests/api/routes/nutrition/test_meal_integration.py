
import datetime
import pytest
from app.models.db_models import Meal, MealItem


@pytest.fixture
def sample_meal(session):
    """A basic meal for tests that need one."""
    meal = Meal(
        date=datetime.date(2024, 7, 1),
        time="10:30",
        description="Apple and Peanut Butter",
        serving_size=1.0,
        status="complete",  # ← Start as pending to test the flow
        items=[  # ← Also check: is it "items" or "meal_items" in your model?
            MealItem(
                description="Apple",
                caloriesKcal=50,
                proteinG=0.3,
                carbsG=14,
                fatG=0.2,
                fiberG=2.4,
                sugarG=10,
                sodiumMg=1,
            ),
            MealItem(
                description="Peanut Butter",
                caloriesKcal=190,
                proteinG=8,
                carbsG=6,
                fatG=16,
                fiberG=2,
                sugarG=3,
                sodiumMg=150,
            ),
        ],
    )
    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


def test_get_meals_by_date_returns_seed(client, sample_meal):
    resp = client.get("/nutrition/meals", params={"date": "2024-07-01"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1

def test_get_summary_aggregates_items(client, sample_meal):
    resp = client.get("/nutrition/summary", params={"date": "2024-07-01"})
    assert resp.status_code == 200
    summary = resp.json()
    print(summary)
    assert summary["caloriesKcal"] == 240
    assert summary["proteinG"] == 8.3
    assert summary["carbsG"] == 20
    assert summary["fatG"] == 16.2
    assert summary["fiberG"] == 4.4
    assert summary["sugarG"] == 13
    assert summary["sodiumMg"] == 151