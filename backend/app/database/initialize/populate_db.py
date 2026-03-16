from sqlmodel import Session, select
from app.database.database import get_engine
from app.models.db_models import User
from app.models.nutrition_schemas import Gender   


def create_user():
    engine = get_engine()
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.id == 1)).first()
        if existing_user:
            print("User with id=1 already exists. Skipping creation.")
            return
        
        user = User(id=1, 
                    first_name="Default User",
                    last_name="Default User",
                    height_in=70.0,
                    weight_lb=150.0,
                    date_of_birth="1990-01-01",
                    gender=Gender.FEMALE)
        
        session.add(user)
        session.commit()
        print("Created default user with id=1")


if __name__ == "__main__":
    create_user()