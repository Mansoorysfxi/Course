"""Tests for the Redis-backed quest-list cache -- NEW in Module 10.

Every test here runs against `fake_redis` (tests/conftest.py's in-memory
stand-in), never a real Redis server -- see that fixture's own docstring,
and lessons/07-containerizing-questlogs-backend.md's "testing code that
talks to Redis" section, for why that's the right call for this suite.
These tests care about **behavior** (does a second identical request come
back as a cache hit; does a write actually clear the cache), not about
Redis's own internals, which is exactly what a fake in place of a real
external dependency should let you test.
"""

from tests.test_quests import _create_quest


async def test_second_identical_list_request_is_a_cache_hit(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, headers)

    first = await client.get("/api/quests", headers=headers)
    assert first.status_code == 200
    assert first.headers["x-cache"] == "MISS"

    second = await client.get("/api/quests", headers=headers)
    assert second.status_code == 200
    assert second.headers["x-cache"] == "HIT"
    # Same data either way -- caching must never change *what* the caller
    # sees, only how fast/expensively the answer was produced.
    assert second.json() == first.json()


async def test_filtered_list_request_bypasses_the_cache(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, headers, priority="high")

    response = await client.get("/api/quests?priority=high", headers=headers)

    assert response.status_code == 200
    assert response.headers["x-cache"] == "BYPASS"


async def test_creating_a_quest_invalidates_the_cached_list(client, signup_and_login, fake_redis):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, headers, title="First Quest")

    # Warm the cache.
    warm = await client.get("/api/quests", headers=headers)
    assert warm.headers["x-cache"] == "MISS"
    assert len(fake_redis._store) == 1

    # Creating a second quest must clear the cached entry...
    await _create_quest(client, headers, title="Second Quest")
    assert len(fake_redis._store) == 0

    # ...so the very next list call is a fresh MISS, not a stale HIT that
    # would be missing "Second Quest."
    refreshed = await client.get("/api/quests", headers=headers)
    assert refreshed.headers["x-cache"] == "MISS"
    titles = {quest["title"] for quest in refreshed.json()}
    assert titles == {"First Quest", "Second Quest"}


async def test_updating_a_quest_invalidates_the_cached_list(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)
    await client.get("/api/quests", headers=headers)  # warm the cache

    await client.patch(f"/api/quests/{created['id']}", json={"done": True}, headers=headers)

    response = await client.get("/api/quests", headers=headers)
    assert response.headers["x-cache"] == "MISS"
    assert response.json()[0]["done"] is True


async def test_deleting_a_quest_invalidates_the_cached_list(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)
    await client.get("/api/quests", headers=headers)  # warm the cache

    await client.delete(f"/api/quests/{created['id']}", headers=headers)

    response = await client.get("/api/quests", headers=headers)
    assert response.headers["x-cache"] == "MISS"
    assert response.json() == []


async def test_two_users_never_share_a_cached_list(client, signup_and_login):
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, hero_headers, title="Hero's Quest")

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")

    # The villain's own first request is still a MISS -- a cache keyed
    # only by "the unfiltered quest list" with no owner in the key at all
    # would leak the hero's quests to the villain as a false HIT. This
    # test is the one that would catch that specific, serious bug.
    response = await client.get("/api/quests", headers=villain_headers)
    assert response.headers["x-cache"] == "MISS"
    assert response.json() == []
