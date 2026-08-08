from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from the CI/CD toy app!"}


def test_add():
    response = client.get("/add/2/3")
    assert response.status_code == 200
    assert response.json() == {"result": 5}


def test_add_negative():
    response = client.get("/add/-1/1")
    assert response.status_code == 200
    assert response.json() == {"result": 0}
