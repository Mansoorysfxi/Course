"""Exercise 05 -- covers a real gap this module's own capstone test suite
(tests/test_quests.py) left: `GET /api/quests`'s three query-parameter
filters (`done`, `priority`, `quest_line`), and `GET /api/quests/stats`
with more than one quest per quest line and a mix of done/not-done
quests. See exercises/05-independent-coverage/INSTRUCTIONS.md.
"""


async def test_filter_by_done_true(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    first = await client.post(
        "/api/quests",
        json={
            "title": "Slay the Dragon",
            "description": "Big lizard.",
            "priority": "high",
            "questLine": "Main Story",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Gather Herbs",
            "description": "Small errand.",
            "priority": "low",
            "questLine": "Village Errands",
        },
        headers=headers,
    )
    await client.patch(f"/api/quests/{first.json()['id']}", json={"done": True}, headers=headers)

    response = await client.get("/api/quests", params={"done": "true"}, headers=headers)

    assert response.status_code == 200
    titles = {quest["title"] for quest in response.json()}
    assert titles == {"Slay the Dragon"}


async def test_filter_by_done_false(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    first = await client.post(
        "/api/quests",
        json={
            "title": "Slay the Dragon",
            "description": "Big lizard.",
            "priority": "high",
            "questLine": "Main Story",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Gather Herbs",
            "description": "Small errand.",
            "priority": "low",
            "questLine": "Village Errands",
        },
        headers=headers,
    )
    await client.patch(f"/api/quests/{first.json()['id']}", json={"done": True}, headers=headers)

    response = await client.get("/api/quests", params={"done": "false"}, headers=headers)

    assert response.status_code == 200
    titles = {quest["title"] for quest in response.json()}
    assert titles == {"Gather Herbs"}


async def test_filter_by_priority(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await client.post(
        "/api/quests",
        json={
            "title": "Slay the Dragon",
            "description": "Big lizard.",
            "priority": "high",
            "questLine": "Main Story",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Gather Herbs",
            "description": "Small errand.",
            "priority": "low",
            "questLine": "Village Errands",
        },
        headers=headers,
    )

    response = await client.get("/api/quests", params={"priority": "low"}, headers=headers)

    assert response.status_code == 200
    titles = {quest["title"] for quest in response.json()}
    assert titles == {"Gather Herbs"}


async def test_filter_by_quest_line(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await client.post(
        "/api/quests",
        json={
            "title": "Slay the Dragon",
            "description": "Big lizard.",
            "priority": "high",
            "questLine": "Main Story",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Gather Herbs",
            "description": "Small errand.",
            "priority": "low",
            "questLine": "Village Errands",
        },
        headers=headers,
    )

    response = await client.get(
        "/api/quests", params={"quest_line": "Village Errands"}, headers=headers
    )

    assert response.status_code == 200
    titles = {quest["title"] for quest in response.json()}
    assert titles == {"Gather Herbs"}


async def test_filters_can_combine(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await client.post(
        "/api/quests",
        json={
            "title": "Slay the Dragon",
            "description": "Big lizard.",
            "priority": "high",
            "questLine": "Main Story",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Defend the Castle",
            "description": "Also Main Story, but low priority.",
            "priority": "low",
            "questLine": "Main Story",
        },
        headers=headers,
    )

    response = await client.get(
        "/api/quests",
        params={"quest_line": "Main Story", "priority": "high"},
        headers=headers,
    )

    assert response.status_code == 200
    titles = {quest["title"] for quest in response.json()}
    assert titles == {"Slay the Dragon"}


async def test_stats_aggregates_multiple_quests_in_the_same_quest_line(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    first = await client.post(
        "/api/quests",
        json={
            "title": "Gather Herbs",
            "description": "One.",
            "priority": "low",
            "questLine": "Village Errands",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Deliver the Letter",
            "description": "Two.",
            "priority": "medium",
            "questLine": "Village Errands",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Repair the Fence",
            "description": "Three.",
            "priority": "low",
            "questLine": "Village Errands",
        },
        headers=headers,
    )
    await client.patch(f"/api/quests/{first.json()['id']}", json={"done": True}, headers=headers)

    response = await client.get("/api/quests/stats", headers=headers)

    assert response.status_code == 200
    stats = response.json()
    assert len(stats) == 1
    assert stats[0]["questLine"] == "Village Errands"
    assert stats[0]["total"] == 3
    assert stats[0]["done"] == 1


async def test_stats_reports_one_row_per_quest_line(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await client.post(
        "/api/quests",
        json={
            "title": "Slay the Dragon",
            "description": "Main.",
            "priority": "high",
            "questLine": "Main Story",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Gather Herbs",
            "description": "Side.",
            "priority": "low",
            "questLine": "Village Errands",
        },
        headers=headers,
    )
    await client.post(
        "/api/quests",
        json={
            "title": "Clear the Mine",
            "description": "Side.",
            "priority": "medium",
            "questLine": "Village Errands",
        },
        headers=headers,
    )

    response = await client.get("/api/quests/stats", headers=headers)

    assert response.status_code == 200
    by_line = {row["questLine"]: row for row in response.json()}
    assert by_line.keys() == {"Main Story", "Village Errands"}
    assert by_line["Main Story"]["total"] == 1
    assert by_line["Village Errands"]["total"] == 2
    assert by_line["Village Errands"]["done"] == 0
