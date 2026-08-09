"""Tests for `GET /health` -- NEW in Module 11. See app/main.py's own
`health()` docstring for exactly what this endpoint checks and why, and
lessons/08-deploying-questlog-with-ci-cd.md for why Render itself depends
on this exact endpoint before routing real traffic to a deploy.

Both tests reuse the `client` fixture (tests/conftest.py), which already
overrides `get_db` and `get_redis_client` app-wide -- so `session.execute`
and `redis.ping()` inside `health()` transparently hit the test's own
in-memory SQLite database and `FakeRedis`, never a real Postgres or Redis
server. This is exactly why `health()` was written to depend on
`DbSession`/`RedisClient` instead of reaching for `app.database.engine`
directly -- see that function's own docstring.
"""


async def test_health_reports_ok_when_dependencies_are_reachable(client):
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "database": "ok", "cache": "ok"}


async def test_health_requires_no_authentication(client):
    # Deliberately no `headers=` at all -- unlike every /api/quests route,
    # a health check has to be reachable by an unauthenticated caller
    # (Render's own deploy process has no QuestLog account or JWT), so
    # this is really a test that /health was never accidentally wired up
    # behind CurrentUser/get_current_user.
    response = await client.get("/health")

    assert response.status_code != 401
