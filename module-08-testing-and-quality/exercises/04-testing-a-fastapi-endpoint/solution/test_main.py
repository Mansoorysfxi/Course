import pytest


async def test_list_announcements_starts_empty(client):
    response = await client.get("/announcements")
    assert response.status_code == 200
    assert response.json() == []


async def test_create_announcement(client):
    response = await client.post(
        "/announcements", json={"title": "Guild Meeting", "body": "Tonight at 8pm."}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Guild Meeting"
    assert body["body"] == "Tonight at 8pm."
    assert "id" in body


async def test_created_announcement_appears_in_the_list(client):
    await client.post("/announcements", json={"title": "Guild Meeting", "body": "Tonight."})

    response = await client.get("/announcements")

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_announcement_by_id(client):
    created = await client.post(
        "/announcements", json={"title": "Guild Meeting", "body": "Tonight."}
    )
    announcement_id = created.json()["id"]

    response = await client.get(f"/announcements/{announcement_id}")

    assert response.status_code == 200
    assert response.json()["id"] == announcement_id


async def test_get_nonexistent_announcement_is_404(client):
    response = await client.get("/announcements/no-such-id")
    assert response.status_code == 404


async def test_delete_announcement(client):
    created = await client.post(
        "/announcements", json={"title": "Guild Meeting", "body": "Tonight."}
    )
    announcement_id = created.json()["id"]

    delete_response = await client.delete(f"/announcements/{announcement_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/announcements/{announcement_id}")
    assert get_response.status_code == 404


async def test_delete_nonexistent_announcement_is_404(client):
    response = await client.delete("/announcements/no-such-id")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"body": "No title at all."},
        {"title": "", "body": "Empty title."},
        {"title": "A Title With No Body"},
    ],
)
async def test_create_announcement_rejects_invalid_input(client, bad_payload):
    response = await client.post("/announcements", json=bad_payload)
    assert response.status_code == 422
