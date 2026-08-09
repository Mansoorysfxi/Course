"""Integration tests for /api/quests/{quest_id}/notes/* -- NEW in Module 14.

Every test monkeypatches `app.routers.notes.embed_text`/`embed_texts`
(never the real `sentence-transformers` model, and never a real
`ANTHROPIC_API_KEY`) -- see app/embeddings.py's own module docstring for
why the real model is never even imported unless one of those two
functions is actually called for real, and lessons/00-setup.md's testing
note for why this backend's test suite deliberately never installs
`sentence-transformers`/`torch` at all. The fake embeddings below are
small, fixed, and deterministic -- exactly the "mocking... the actual free
local model deterministically" approach this module's own scope
explicitly allows.

Claude itself is mocked the exact same way tests/test_ai_assistant.py
already established (`FakeAnthropicClient`, reused directly from that
file) -- these two test files together prove this backend's own logic
(chunking, embedding calls, SSE formatting, auth scoping, the
503-when-unconfigured path) without ever needing a real key, a real
model, or a real Postgres+pgvector instance.

**`POST .../ask` tests also monkeypatch `app.repository.find_similar_chunks`
itself**, never letting the real query run -- and this is a real,
load-bearing detail, not just tidiness. `NoteChunk.embedding` compiles to a
plain SQLite `JSON` column in this test suite (app/db_models.py's own
docstring), and `pgvector-python`'s `.cosine_distance()` comparator always
emits Postgres's real `<=>` operator, no matter what column type it's
attached to -- so calling the real `find_similar_chunks` against this
suite's SQLite database doesn't quietly do the wrong thing, it fails
outright with a SQL syntax error. That failure is exactly why
tests/test_notes_pgvector_integration.py exists as its own, separately
gated file (see that file's own module docstring) -- these tests here
mock the repository call precisely at that boundary, so `/ask`'s own
routing/orchestration logic (talking to app/rag.py, formatting SSE) stays
covered without ever touching the one query this test database genuinely
cannot run.
"""

import json

import app.routers.notes as notes_router
from app import repository
from app.dependencies import get_ai_client
from app.main import app
from app.rag import RetrievedChunk
from tests.test_ai_assistant import FakeAnthropicClient, _final_message, _text_block
from tests.test_quests import _create_quest


def _fake_embed_text(text: str) -> list[float]:
    """A tiny, fixed, 4-dimensional fake embedding -- deterministic and
    dependency-free. Its actual direction encodes nothing about `text`'s
    real meaning (unlike the genuine model) -- these tests are verifying
    this backend's own plumbing (does an embedding get computed and
    stored/retrieved correctly?), not embedding *quality*, which
    lessons/03-embeddings-for-search.md and Module 12 Lesson 04 already
    cover with the real model."""
    # A short, readable, deterministic function of the text's own length
    # and first character, so different notes/questions get different (but
    # always reproducible) fake vectors across a single test run.
    seed = (len(text) % 5) + 1
    first = ord(text[0]) % 7 if text else 0
    return [float(seed), float(first), 1.0, 0.5]


def _fake_embed_texts(texts: list[str]) -> list[list[float]]:
    return [_fake_embed_text(text) for text in texts]


async def _create_note(client, headers, quest_id, **overrides):
    payload = {
        "title": "Boss Fight Prep",
        "content": "Bring fire resistant armor.\n\nApproach from the east ridge.",
    }
    payload.update(overrides)
    response = await client.post(f"/api/quests/{quest_id}/notes", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_note_chunks_and_embeds_content(client, signup_and_login, monkeypatch):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers)

    note = await _create_note(client, headers, quest["id"])

    assert note["title"] == "Boss Fight Prep"
    # Two paragraphs, separated by a blank line -> two chunks (see
    # app/chunking.py's own paragraph-splitting tests for the chunking
    # logic itself; this test only checks the route wires it up correctly).
    assert note["chunkCount"] == 2
    assert "id" in note
    assert "content" not in note  # QuestNote response model has no content field


async def test_list_notes_returns_chunk_counts(client, signup_and_login, monkeypatch):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers)
    await _create_note(client, headers, quest["id"], title="Note A", content="Single paragraph.")
    await _create_note(
        client, headers, quest["id"], title="Note B", content="Para one.\n\nPara two."
    )

    response = await client.get(f"/api/quests/{quest['id']}/notes", headers=headers)

    assert response.status_code == 200
    notes = response.json()
    assert {note["title"]: note["chunkCount"] for note in notes} == {"Note A": 1, "Note B": 2}


async def test_delete_note_removes_it(client, signup_and_login, monkeypatch):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers)
    note = await _create_note(client, headers, quest["id"])

    delete_response = await client.delete(
        f"/api/quests/{quest['id']}/notes/{note['id']}", headers=headers
    )
    assert delete_response.status_code == 204

    list_response = await client.get(f"/api/quests/{quest['id']}/notes", headers=headers)
    assert list_response.json() == []


async def test_delete_nonexistent_note_is_404(client, signup_and_login, monkeypatch):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers)

    response = await client.delete(
        f"/api/quests/{quest['id']}/notes/does-not-exist", headers=headers
    )

    assert response.status_code == 404


async def test_notes_for_someone_elses_quest_are_404(client, signup_and_login, monkeypatch):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)

    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, hero_headers)

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    response = await client.get(f"/api/quests/{quest['id']}/notes", headers=villain_headers)

    assert response.status_code == 404


async def test_ask_without_api_key_returns_503(client, signup_and_login, monkeypatch):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers)
    await _create_note(client, headers, quest["id"])

    response = await client.post(
        f"/api/quests/{quest['id']}/notes/ask", json={"question": "What armor?"}, headers=headers
    )

    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]


async def test_ask_with_no_notes_returns_error_event_without_calling_claude(
    client, signup_and_login, monkeypatch
):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)
    # See this file's own module docstring: the real `find_similar_chunks`
    # cannot run against this suite's SQLite test database at all (its
    # `.cosine_distance()` SQL is Postgres-only), so it's mocked here to
    # return the same "nothing retrieved" result a genuinely empty quest
    # would produce, letting this test verify /ask's own routing logic
    # (does it correctly turn zero retrieved chunks into the right error
    # event, without ever calling Claude?) in isolation from that query.
    monkeypatch.setattr(repository, "find_similar_chunks", lambda *a, **k: _async_result([]))

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers)

    fake_client = FakeAnthropicClient(turns=[])  # zero turns -- must never be called
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, f"/api/quests/{quest['id']}/notes/ask", {"question": "Anything?"}, headers
    )

    assert events == [
        (
            "error",
            {"message": "This quest has no notes yet. Add one before asking a question."},
        )
    ]


async def test_ask_streams_sources_then_answer(client, signup_and_login, monkeypatch):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(notes_router, "embed_texts", _fake_embed_texts)

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers)
    await _create_note(client, headers, quest["id"], title="Boss Fight Prep")

    # Same reasoning as the test above: `find_similar_chunks` itself is
    # mocked here (returning one hand-built `RetrievedChunk`, standing in
    # for whatever the real pgvector query would have found) so this test
    # can verify /ask's SSE orchestration -- sources first, then streamed
    # tokens, then a final result -- without depending on the one query
    # this test database cannot run.
    retrieved = RetrievedChunk(
        note_id="note-1",
        note_title="Boss Fight Prep",
        chunk_index=0,
        content="Bring fire resistant armor.",
        embedding=[1.0, 0.0, 0.0, 0.0],
    )
    monkeypatch.setattr(
        repository, "find_similar_chunks", lambda *a, **k: _async_result([retrieved])
    )

    answer = "According to your note 'Boss Fight Prep': bring fire resistant armor."
    fake_client = FakeAnthropicClient(
        turns=[([answer], _final_message([_text_block(answer)], stop_reason="end_turn"))]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, f"/api/quests/{quest['id']}/notes/ask", {"question": "What armor?"}, headers
    )

    event_names = [name for name, _ in events]
    assert event_names[0] == "sources"
    assert event_names[-1] == "result"
    assert events[-1][1]["answer"] == answer
    sources = events[0][1]["sources"]
    assert sources[0]["note_title"] == "Boss Fight Prep"


async def _async_result(value):
    """A tiny helper so `monkeypatch.setattr(repository, "find_similar_chunks", ...)`
    can install a plain `lambda` that still satisfies `await
    repository.find_similar_chunks(...)` at the call site in
    app/routers/notes.py -- `lambda *a, **k: _async_result([...])` returns
    this coroutine, which resolves to `value` when awaited."""
    return value


async def _collect_sse_events(client, url: str, json_body: dict, headers: dict):
    events: list[tuple[str, dict]] = []
    async with client.stream("POST", url, json=json_body, headers=headers) as response:
        assert response.status_code == 200, await response.aread()
        event_name = None
        async for line in response.aiter_lines():
            if line.startswith("event: "):
                event_name = line.removeprefix("event: ")
            elif line.startswith("data: "):
                assert event_name is not None
                events.append((event_name, json.loads(line.removeprefix("data: "))))
    return events
