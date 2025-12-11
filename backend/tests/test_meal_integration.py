# tests/test_meals_integration.py
import datetime
import pytest

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

from app.main import app
from app.database.database import get_session
from app.models.db_models import Meal, MealItem

@pytest.fixture(scope="session")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return eng

@pytest.fixture(autouse=True)
def session(engine):
    with Session(engine) as s:
        # seed one meal
        meal = Meal(
            date=datetime.date(2024, 7, 1),
            time="10:30",
            description="Apple and Peanut Butter",
            serving_size=1.0,
            items=[
                MealItem(
                    description="Apple",
                    caloriesKcal=90,
                    proteinG=1,
                    carbsG=25,
                    fatG=0,
                    fiberG=4,
                    sugarG=19,
                    sodiumMg=2,
                )
            ],
        )
        s.add(meal)
        s.commit()
        s.refresh(meal)
        yield s
        # clean tables between tests
        s.rollback()
        for table in reversed(SQLModel.metadata.sorted_tables):
            s.exec(table.delete())
        s.commit()

@pytest.fixture(autouse=True)
def override_db(session):
    app.dependency_overrides[get_session] = lambda: session
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

def test_get_meals_by_date_returns_seed():
    resp = client.get("/nutrition/meals", params={"date": "2024-07-01"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["description"] == "Apple and Peanut Butter"
    assert data[0]["items"][0]["caloriesKcal"] == 90

def test_get_summary_aggregates_items():
    resp = client.get("/nutrition/summary", params={"date": "2024-07-01"})
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["caloriesKcal"] == 90
    assert summary["proteinG"] == 1
