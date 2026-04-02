from app.models.nutrition_schemas import UserBase

def test_create_user(client, session):
    user = UserBase(
        first_name="John",
        last_name="Doe",
        height_in=70.0,
        weight_lb=150.0,
        date_of_birth="1990-01-01",
        gender="male",
    )

    resp = client.post("/users/create", json=user.model_dump(mode='json'))
    assert resp.status_code == 201
    data = resp.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["height_in"] == 70.0
    assert data["weight_lb"] == 150.0
    assert data["date_of_birth"] == "1990-01-01"
    assert data["gender"] == "male"
