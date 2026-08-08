"""Integration tests for /api/quests/* -- CRUD, ownership isolation, 404s,
and validation errors.

Every test needs a logged-in user (every quest route is protected -- see
tests/test_auth.py's `test_quests_route_without_a_token_is_rejected`,
which already covers the "no token at all" case so it isn't repeated
here) via the `signup_and_login` fixture from conftest.py.
"""

import pytest


async def _create_quest(client, headers, **overrides):
    """A small local helper (not a fixture -- see
    lessons/02-pytest-fundamentals-and-fixtures.md's "helper function vs.
    fixture" box for when each is the right tool) that creates one quest
    with sensible defaults, overridable per call, and returns the parsed
    response body."""
    payload = {
        "title": "Slay the Dragon",
        "description": "The dragon has been terrorizing the northern villages.",
        "priority": "high",
        "questLine": "Main Story",
    }
    payload.update(overrides)
    response = await client.post("/api/quests", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_quest(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    quest = await _create_quest(client, headers)

    assert quest["title"] == "Slay the Dragon"
    assert quest["priority"] == "high"
    assert quest["questLine"] == "Main Story"
    assert quest["done"] is False
    assert "id" in quest
    assert "createdAt" in quest


async def test_list_quests_returns_only_created_quests(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, headers, title="Slay the Dragon")
    await _create_quest(client, headers, title="Gather Herbs", priority="low")

    response = await client.get("/api/quests", headers=headers)

    assert response.status_code == 200
    titles = {quest["title"] for quest in response.json()}
    assert titles == {"Slay the Dragon", "Gather Herbs"}


async def test_get_quest_by_id(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    response = await client.get(f"/api/quests/{created['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_nonexistent_quest_is_404(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    response = await client.get("/api/quests/no-such-id", headers=headers)

    assert response.status_code == 404


async def test_update_quest(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    response = await client.patch(
        f"/api/quests/{created['id']}", json={"done": True}, headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["done"] is True
    # Everything not sent in the PATCH body is unchanged -- see
    # app/models.py's QuestUpdate and app/repository.py's use of
    # `exclude_unset=True`, exactly what this assertion pins down.
    assert body["title"] == "Slay the Dragon"


async def test_delete_quest(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    delete_response = await client.delete(f"/api/quests/{created['id']}", headers=headers)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/quests/{created['id']}", headers=headers)
    assert get_response.status_code == 404


@pytest.mark.parametrize(
    "bad_payload",
    [
        {  # missing "title" entirely
            "description": "No title at all.",
            "priority": "high",
            "questLine": "Main Story",
        },
        {  # "urgent" is not one of the three allowed Priority values
            "title": "Slay the Dragon",
            "description": "The dragon has been terrorizing the northern villages.",
            "priority": "urgent",
            "questLine": "Main Story",
        },
    ],
)
async def test_create_quest_rejects_invalid_input(client, signup_and_login, bad_payload):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    response = await client.post("/api/quests", json=bad_payload, headers=headers)

    assert response.status_code == 422


# --- Ownership isolation -- the heart of what Module 07 added ------------


async def test_one_user_cannot_list_another_users_quests(client, signup_and_login):
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, hero_headers, title="Hero's Secret Quest")

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    response = await client.get("/api/quests", headers=villain_headers)

    assert response.status_code == 200
    assert response.json() == []


async def test_one_user_cannot_get_another_users_quest_by_id(client, signup_and_login):
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    hero_quest = await _create_quest(client, hero_headers, title="Hero's Secret Quest")

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    response = await client.get(f"/api/quests/{hero_quest['id']}", headers=villain_headers)

    # 404, never 403 -- see app/repository.py's `get_quest` docstring
    # (Module 07) for exactly why revealing "this exists, but isn't yours"
    # would itself be a small information leak (an IDOR).
    assert response.status_code == 404


async def test_one_user_cannot_update_another_users_quest(client, signup_and_login):
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    hero_quest = await _create_quest(client, hero_headers, title="Hero's Secret Quest")

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    response = await client.patch(
        f"/api/quests/{hero_quest['id']}", json={"done": True}, headers=villain_headers
    )

    assert response.status_code == 404

    # Confirm it truly is unchanged, using the rightful owner's own token.
    unchanged = await client.get(f"/api/quests/{hero_quest['id']}", headers=hero_headers)
    assert unchanged.json()["done"] is False


async def test_one_user_cannot_delete_another_users_quest(client, signup_and_login):
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    hero_quest = await _create_quest(client, hero_headers, title="Hero's Secret Quest")

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    response = await client.delete(f"/api/quests/{hero_quest['id']}", headers=villain_headers)

    assert response.status_code == 404

    # Still there, for its rightful owner.
    still_there = await client.get(f"/api/quests/{hero_quest['id']}", headers=hero_headers)
    assert still_there.status_code == 200


async def test_quest_stats_are_scoped_to_the_current_user(client, signup_and_login):
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, hero_headers, title="Hero Quest", questLine="Main Story")

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    await _create_quest(client, villain_headers, title="Villain Quest", questLine="Main Story")

    hero_stats = await client.get("/api/quests/stats", headers=hero_headers)

    assert hero_stats.status_code == 200
    stats = hero_stats.json()
    assert len(stats) == 1
    assert stats[0]["total"] == 1
