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


def test_health_ok_when_greeting_configured(monkeypatch):
    monkeypatch.setenv("GREETING", "hello")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "greeting_configured": True}


def test_health_unhealthy_when_greeting_missing(monkeypatch):
    # `raising=False` -- delenv would otherwise raise KeyError if
    # GREETING happened not to be set at all when this test runs; this
    # test only cares that it's ABSENT afterward, not whether it started
    # out present.
    monkeypatch.delenv("GREETING", raising=False)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "greeting_configured": False}


def test_health_unhealthy_when_greeting_empty(monkeypatch):
    monkeypatch.setenv("GREETING", "")

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "greeting_configured": False}
