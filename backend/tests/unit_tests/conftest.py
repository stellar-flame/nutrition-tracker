import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_session
from app.models.db_models import Meal, MealItem


@pytest.fixture(scope="session")
def engine():
    """Shared in-memory database for all tests."""
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    return eng


@pytest.fixture
def session(engine):
    """Fresh session for each test, with rollback cleanup."""
    with Session(engine) as s:
        yield s
        s.rollback()
        for table in reversed(SQLModel.metadata.sorted_tables):
            s.exec(table.delete())
        s.commit()


@pytest.fixture
def client(session):
    """TestClient with DB session override."""
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Default test environment variables."""
    monkeypatch.setenv("INTERNAL_TOKEN", "testtoken")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")