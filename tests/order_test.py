import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, select

from dishes.models import Dish
from main import app

from session import get_session

client = TestClient(app)

# Создаем тестовую базу данных в памяти
test_engine = create_engine("sqlite:///test.db")


# Переопределяем зависимость get_session для использования тестовой базы данных
def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


def seed_dishes_table():
    with open(os.getcwd() + "/tests/dishes.json", "r") as file:
        data = json.load(file)
        session = next(override_get_session())
        for dish in data:
            obj = Dish(**dish)
            print(obj)
            session.add(obj)
            session.commit()

        print("test")


# Функция для подготовки базы данных перед тестами
@pytest.fixture(name="setup_db")
def setup_db_fixture():
    SQLModel.metadata.create_all(test_engine)
    seed_dishes_table()
    yield
    SQLModel.metadata.drop_all(test_engine)


def test_order(setup_db):
    response = client.post("/orders", json={"items": [{"dish_id": 1, "quantity": 1}], "client": "test client"})
    assert response.json()['status'] == 'OK'
