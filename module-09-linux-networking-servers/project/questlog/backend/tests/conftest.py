"""Shared pytest fixtures for the whole backend test suite.

Every other file under tests/ receives these fixtures automatically just by
naming them as a parameter -- pytest discovers `conftest.py` on its own,
with no import needed in test_*.py files. See
lessons/02-pytest-fundamentals-and-fixtures.md for what a "fixture" is in
the first place, and lessons/06-testing-with-a-database.md for exactly why
this file is built the way it is (a fresh, empty SQLite database per test,
never Postgres, never a shared database across tests).

**Order matters at the top of this file.** `os.environ.setdefault(...)`
for `SECRET_KEY` runs *before* anything imports `app.main` (directly or
indirectly) -- app/config.py's `Settings.secret_key` has no default value
(Module 07's own deliberate choice, see that module's lessons/11), so the
very first `import app...` anywhere in this process would crash at
collection time with a `pydantic_core.ValidationError` if a real
`SECRET_KEY` weren't already sitting in the environment before that import
happens. This value is never used to sign a token any real user relies on
-- it exists purely so the app's own settings validation has something to
accept during a test run.
"""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-production")

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# A single, shared, **in-memory** SQLite database URL. See
# lessons/06-testing-with-a-database.md's "why SQLite, and why in-memory"
# section for the full, honest trade-off discussion (verified via real
# research, not memory) against the alternative this course seriously
# considered -- a dedicated `questlog_test` Postgres database -- and why
# this module picks the former for the exercises and this capstone.
#
# `poolclass=StaticPool` is the one non-obvious piece: an in-memory SQLite
# database normally lives and dies with a single connection -- open a
# second connection and you get a second, completely empty database, not
# the same one. `StaticPool` makes SQLAlchemy's engine hand out that exact
# same one connection every time something asks the pool for one, so every
# query in a single test, no matter how many times code calls
# `get_db()`, actually sees the same in-memory database.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Hands each test function its own, freshly created, completely empty
    database -- every table `app/db_models.py` defines, with zero rows in
    any of them, guaranteed. Nothing a previous test did (or failed to
    clean up) can ever leak into the next one, because there is no
    "previous" database at all -- this fixture builds a brand new one from
    scratch, every single time a test asks for it.

    `create_async_engine` -> `engine.begin()` -> `run_sync(...create_all)`
    is the async equivalent of Module 06's `Base.metadata.create_all(engine)`
    -- `run_sync` exists because `create_all` itself is a *synchronous*
    SQLAlchemy operation; wrapping it lets an async engine run it anyway.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """An `httpx.AsyncClient` wired directly to the FastAPI app, via
    `ASGITransport` -- no real network socket, no `uvicorn` process
    running anywhere, just this test process calling straight into the
    app's own ASGI callable. See lessons/05-testing-fastapi-endpoints.md
    for exactly what "ASGI" and "transport" mean here.

    `app.dependency_overrides[get_db] = override_get_db` is the one line
    that makes this whole file work: every route that normally depends on
    `Depends(get_db)` (app/dependencies.py's `DbSession`) receives this
    test's own `db_session` instead of a real connection to the app's
    configured Postgres database. Nothing in app/routers/ or
    app/repository.py needed to change, or even know, that it's talking to
    SQLite in a test instead of Postgres for real -- that's the entire
    point of depending on an abstract `get_db` dependency in the first
    place rather than importing a concrete session directly (Module 05,
    Lesson 04).
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def signup_and_login():
    """A small factory fixture -- a fixture whose value is itself a
    function, so each test can call it more than once with different
    arguments (e.g. to create two separate users). See
    lessons/02-pytest-fundamentals-and-fixtures.md's "fixtures that return
    a function" box.

    Returns an async function `(client, email, password) -> dict[str, str]`
    that signs a brand-new account up, logs it in, and hands back a ready-
    to-use `{"Authorization": "Bearer <token>"}` header dict -- the exact
    shape `httpx`'s `headers=` argument expects. Every quest test in
    tests/test_quests.py uses this to get a logged-in user with zero
    repeated boilerplate.
    """

    async def _signup_and_login(client: AsyncClient, email: str, password: str) -> dict[str, str]:
        signup_response = await client.post(
            "/api/auth/signup", json={"email": email, "password": password}
        )
        assert signup_response.status_code == 201, signup_response.text

        login_response = await client.post(
            "/api/auth/login",
            data={"username": email, "password": password},
        )
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _signup_and_login
