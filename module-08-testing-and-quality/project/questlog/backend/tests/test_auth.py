"""Integration tests for /api/auth/* -- signup, login, and the protected
/me and /api/quests routes' authentication requirement.

"Integration" (not "unit," see tests/test_security.py) because every test
below goes through a real HTTP request/response cycle against the real
FastAPI app (via the `client` fixture in conftest.py), which in turn talks
to a real (if temporary, in-memory) database through the real
app/repository.py code -- several real layers integrated together, not one
function in isolation. See lessons/01-why-tests-and-the-testing-pyramid.md.
"""

import pytest


async def test_signup_creates_an_account(client):
    response = await client.post(
        "/api/auth/signup",
        json={"email": "hero@example.com", "password": "sword-and-shield"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "hero@example.com"
    assert "id" in body
    assert "createdAt" in body
    # UserPublic (app/models.py) deliberately has no password field at
    # all -- see that class's own docstring. This asserts that promise is
    # actually kept over the wire, not just true in the class definition.
    assert "password" not in body
    assert "hashedPassword" not in body
    assert "hashed_password" not in body


async def test_signup_rejects_a_duplicate_email(client):
    payload = {"email": "hero@example.com", "password": "sword-and-shield"}
    first = await client.post("/api/auth/signup", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/auth/signup", json=payload)
    assert second.status_code == 400


@pytest.mark.parametrize(
    "email, password",
    [
        ("not-an-email", "sword-and-shield"),  # EmailStr rejects this shape
        ("hero@example.com", "short"),  # shorter than min_length=8
    ],
)
async def test_signup_rejects_invalid_input(client, email, password):
    """One test function, run twice with two different bad inputs -- see
    lessons/03-parametrize-and-mocking.md for exactly how
    `@pytest.mark.parametrize` does this and why it beats copy-pasting
    this test body twice with one line changed."""
    response = await client.post("/api/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 422


async def test_login_with_correct_password_returns_a_token(client):
    await client.post(
        "/api/auth/signup",
        json={"email": "hero@example.com", "password": "sword-and-shield"},
    )

    response = await client.post(
        "/api/auth/login",
        data={"username": "hero@example.com", "password": "sword-and-shield"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 0


async def test_login_with_wrong_password_is_rejected(client):
    await client.post(
        "/api/auth/signup",
        json={"email": "hero@example.com", "password": "sword-and-shield"},
    )

    response = await client.post(
        "/api/auth/login",
        data={"username": "hero@example.com", "password": "the-wrong-password"},
    )

    assert response.status_code == 401
    # Same message whether the password is wrong or the account doesn't
    # exist at all -- see app/routers/auth.py's `login` docstring for why
    # that's deliberate, not an oversight.
    assert "Authorization" not in response.headers


async def test_login_with_unknown_email_is_rejected(client):
    response = await client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "whatever-1"},
    )
    assert response.status_code == 401


async def test_me_without_a_token_is_rejected(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


async def test_me_with_a_valid_token_returns_the_account(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "hero@example.com"


async def test_me_with_a_garbage_token_is_rejected(client):
    response = await client.get(
        "/api/auth/me", headers={"Authorization": "Bearer this-is-not-a-real-jwt"}
    )
    assert response.status_code == 401


async def test_quests_route_without_a_token_is_rejected(client):
    """The same "no token -> 401" rule protects every quest route too --
    see app/dependencies.py's `CurrentUser`, which every route in
    app/routers/quests.py depends on. tests/test_quests.py assumes this
    already holds and moves straight on to testing what happens once a
    caller *does* have a valid token."""
    response = await client.get("/api/quests")
    assert response.status_code == 401
