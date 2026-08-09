"""Tests for POST /api/agent/chat -- NEW in Module 15, the capstone
feature.

Every test runs against a **fake** Anthropic client, reusing
`tests/test_ai_assistant.py`'s own `FakeMessageStream`/`_text_block`/
`_tool_use_block`/`_final_message` helpers for the streamed main loop, and
this file's own small `FakeCreateResponse`/extended fake client for the
one place `app/agent.py` makes a *non*-streaming call
(`suggest_quest_breakdown`'s own single call to `ai_client.messages.create`
-- see that function's own docstring in app/agent.py for why it doesn't
stream). Never a real `ANTHROPIC_API_KEY`, a real embedding model, or a
real Postgres+pgvector instance -- the same principle every earlier
AI-feature test file in this backend already established.
"""

import json

import app.routers.notes as notes_router
from app import repository
from app.agent import AGENT_TOOLS
from app.dependencies import get_ai_client
from app.main import app
from app.rag import RetrievedChunk
from tests.test_ai_assistant import FakeMessageStream, _final_message, _text_block, _tool_use_block
from tests.test_quests import _create_quest


def _fake_embed_text(text: str) -> list[float]:
    """Same tiny, fixed, deterministic fake embedding
    tests/test_notes.py already uses -- see that file's own docstring for
    why a fake vector (not the real model) is the right thing to test
    against here."""
    seed = (len(text) % 5) + 1
    first = ord(text[0]) % 7 if text else 0
    return [float(seed), float(first), 1.0, 0.5]


async def _async_result(value):
    return value


class FakeAgentMessages:
    """Stands in for the real SDK's `client.messages`, but -- unlike
    `tests/test_ai_assistant.py`'s `FakeMessages` -- supports **both**
    `.stream(...)` (this agent's own main loop, one call per iteration)
    and `.create(...)` (the one non-streaming call
    `app/agent.py`'s `_tool_suggest_quest_breakdown` makes). The two are
    tracked as two completely independent queues -- a test that never
    exercises `suggest_quest_breakdown` can simply never pass any
    `create_responses` at all.
    """

    def __init__(
        self, stream_turns: list[tuple[list[str], object]], create_responses: list[object]
    ):
        self._stream_turns = iter(stream_turns)
        self._create_responses = iter(create_responses)

    def stream(self, **kwargs: object) -> FakeMessageStream:
        text_chunks, final_message = next(self._stream_turns)
        return FakeMessageStream(text_chunks, final_message)

    async def create(self, **kwargs: object):
        return next(self._create_responses)


class FakeAgentAnthropicClient:
    def __init__(
        self,
        stream_turns: list[tuple[list[str], object]],
        create_responses: list[object] | None = None,
    ):
        self.messages = FakeAgentMessages(stream_turns, create_responses or [])


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


def test_agent_has_no_delete_tool_and_has_the_six_documented_tools():
    """A direct, unit-level proof of app/agent.py's own stated guardrail 2
    ("no destructive tool at all") -- not something that needs a live
    conversation to demonstrate, since it's a fact about the tool
    definitions themselves."""
    names = {tool["name"] for tool in AGENT_TOOLS}
    assert names == {
        "list_quests",
        "create_quest",
        "update_quest",
        "complete_quest",
        "search_quest_notes",
        "suggest_quest_breakdown",
    }
    assert "delete_quest" not in names


async def test_missing_api_key_returns_503(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    response = await client.post(
        "/api/agent/chat", json={"messages": [{"role": "user", "content": "hi"}]}, headers=headers
    )

    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]


async def test_agent_answers_directly_without_a_tool_call(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    answer = "I can help you manage your quests -- what would you like to do?"
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[([answer], _final_message([_text_block(answer)], stop_reason="end_turn"))]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, "/api/agent/chat", {"messages": [{"role": "user", "content": "hello"}]}, headers
    )

    event_names = [name for name, _ in events]
    assert "tool_call" not in event_names
    assert event_names[-1] == "result"
    assert events[-1][1]["answer"] == answer
    usage = dict(events)["usage"]
    assert usage == {"iterations": 1, "tool_calls": 0}


async def test_agent_lists_quests_via_tool_round_trip(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, headers, title="Slay the Dragon")

    final_answer = "You have one quest: Slay the Dragon."
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[
            (
                [],
                _final_message(
                    [_tool_use_block("toolu_1", "list_quests", {})], stop_reason="tool_use"
                ),
            ),
            ([final_answer], _final_message([_text_block(final_answer)], stop_reason="end_turn")),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": "what are my quests?"}]},
        headers,
    )

    event_names = [name for name, _ in events]
    assert event_names.count("tool_call") == 1
    tool_call_event = dict(events)
    assert events[event_names.index("tool_call")][1] == {"tool": "list_quests", "input": {}}
    assert events[-1] == ("result", {"answer": final_answer})
    assert tool_call_event["usage"] == {"iterations": 2, "tool_calls": 1}


async def test_agent_creates_a_quest_via_tool(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    tool_input = {
        "title": "Gather Healing Herbs",
        "description": "Five bundles of silverleaf.",
        "priority": "low",
        "quest_line": "Village Errands",
    }
    final_answer = "Created 'Gather Healing Herbs' for you."
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[
            (
                [],
                _final_message(
                    [_tool_use_block("toolu_1", "create_quest", tool_input)], stop_reason="tool_use"
                ),
            ),
            ([final_answer], _final_message([_text_block(final_answer)], stop_reason="end_turn")),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": "add a quest to gather healing herbs"}]},
        headers,
    )

    assert events[-1] == ("result", {"answer": final_answer})
    listed = await client.get("/api/quests", headers=headers)
    titles = [q["title"] for q in listed.json()]
    assert "Gather Healing Herbs" in titles


async def test_agent_create_quest_with_invalid_input_does_not_create_anything(
    client, signup_and_login
):
    """Proves app/agent.py's own guardrail 5 (Pydantic-validated tool
    inputs) is real: `priority` here is not one of `low`/`medium`/`high`,
    so `QuestCreate.model_validate` must reject it -- and the tool result
    that produces should be an error the agent can recover from, not a
    500 that crashes the whole streamed turn."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    bad_input = {
        "title": "Bad Quest",
        "description": "...",
        "priority": "urgent",  # not a valid Priority
        "quest_line": "Side Quests",
    }
    final_answer = "I couldn't create that quest -- priority must be low, medium, or high."
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[
            (
                [],
                _final_message(
                    [_tool_use_block("toolu_1", "create_quest", bad_input)], stop_reason="tool_use"
                ),
            ),
            ([final_answer], _final_message([_text_block(final_answer)], stop_reason="end_turn")),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": "add a bad quest"}]},
        headers,
    )

    assert events[-1] == ("result", {"answer": final_answer})
    listed = await client.get("/api/quests", headers=headers)
    assert "Bad Quest" not in [q["title"] for q in listed.json()]


async def test_agent_completes_a_quest_via_tool(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers, title="Clear the Old Mine")

    final_answer = "Marked 'Clear the Old Mine' as done."
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[
            (
                [],
                _final_message(
                    [_tool_use_block("toolu_1", "complete_quest", {"quest_id": created["id"]})],
                    stop_reason="tool_use",
                ),
            ),
            ([final_answer], _final_message([_text_block(final_answer)], stop_reason="end_turn")),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": "I finished the mine quest"}]},
        headers,
    )

    fetched = await client.get(f"/api/quests/{created['id']}", headers=headers)
    assert fetched.json()["done"] is True


async def test_agent_update_for_someone_elses_quest_is_a_recoverable_tool_error(
    client, signup_and_login
):
    """Proves app/agent.py's own guardrail 3 (ownership scoping, with no
    exceptions) end to end: the fake model is instructed to update a
    quest_id belonging to a *different* account, and this test proves
    that quest is genuinely untouched afterward -- not merely that the
    HTTP response looked fine."""
    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    villains_quest = await _create_quest(client, villain_headers, title="Villain's Secret Plan")

    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    final_answer = "I couldn't find that quest on your account."
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[
            (
                [],
                _final_message(
                    [
                        _tool_use_block(
                            "toolu_1",
                            "update_quest",
                            {"quest_id": villains_quest["id"], "title": "Hacked"},
                        )
                    ],
                    stop_reason="tool_use",
                ),
            ),
            ([final_answer], _final_message([_text_block(final_answer)], stop_reason="end_turn")),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": f"update quest {villains_quest['id']}"}]},
        hero_headers,
    )

    still_theirs = await client.get(f"/api/quests/{villains_quest['id']}", headers=villain_headers)
    assert still_theirs.json()["title"] == "Villain's Secret Plan"


async def test_agent_search_quest_notes_emits_sources_then_a_cited_answer(
    client, signup_and_login, monkeypatch
):
    monkeypatch.setattr(notes_router, "embed_text", _fake_embed_text)
    monkeypatch.setattr(
        notes_router, "embed_texts", lambda texts: [_fake_embed_text(t) for t in texts]
    )
    # See tests/test_notes.py's own module docstring for why the real
    # pgvector query is mocked here rather than run for real against this
    # suite's SQLite database.
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
    # app/agent.py imports `embed_text` directly (`from app.embeddings
    # import embed_text`), so it must be patched on app.agent itself --
    # patching app.embeddings.embed_text would not affect the name already
    # bound into app.agent's own namespace.
    import app.agent as agent_module

    monkeypatch.setattr(agent_module, "embed_text", _fake_embed_text)

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    quest = await _create_quest(client, headers, title="Defeat the dragon")
    await client.post(
        f"/api/quests/{quest['id']}/notes",
        json={"title": "Boss Fight Prep", "content": "Bring fire resistant armor."},
        headers=headers,
    )

    final_answer = "According to your note 'Boss Fight Prep': bring fire resistant armor."
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[
            (
                [],
                _final_message(
                    [
                        _tool_use_block(
                            "toolu_1",
                            "search_quest_notes",
                            {"quest_id": quest["id"], "question": "What armor?"},
                        )
                    ],
                    stop_reason="tool_use",
                ),
            ),
            (
                [final_answer],
                _final_message([_text_block(final_answer)], stop_reason="end_turn"),
            ),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": "what armor should I bring for the dragon?"}]},
        headers,
    )

    event_names = [name for name, _ in events]
    assert "sources" in event_names
    sources = dict(events)["sources"]["sources"]
    assert sources[0]["note_title"] == "Boss Fight Prep"
    assert events[-1] == ("result", {"answer": final_answer})


async def test_agent_suggest_quest_breakdown_uses_a_non_streaming_call(client, signup_and_login):
    """`suggest_quest_breakdown` doesn't `.stream(...)` -- it calls
    `ai_client.messages.create(...)` once (see app/agent.py's own
    docstring for why). This test proves that path works end to end by
    supplying a `create_responses` entry, never a `stream_turns` entry,
    for that inner call."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers, title="Defeat the dragon")

    breakdown_json = json.dumps(
        {"sub_quests": [{"title": "Scout the lair"}, {"title": "Buy fire-resistant armor"}]}
    )
    final_answer = "I suggest: Scout the lair, and Buy fire-resistant armor. Want me to add them?"
    fake_client = FakeAgentAnthropicClient(
        stream_turns=[
            (
                [],
                _final_message(
                    [
                        _tool_use_block(
                            "toolu_1", "suggest_quest_breakdown", {"quest_id": created["id"]}
                        )
                    ],
                    stop_reason="tool_use",
                ),
            ),
            ([final_answer], _final_message([_text_block(final_answer)], stop_reason="end_turn")),
        ],
        create_responses=[_final_message([_text_block(breakdown_json)], stop_reason="end_turn")],
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": "break down the dragon quest"}]},
        headers,
    )

    assert events[-1] == ("result", {"answer": final_answer})
    # The suggestion alone must never create a quest -- only a later,
    # explicit create_quest tool call would (see app/agent.py's own
    # SYSTEM_PROMPT, which instructs exactly that).
    listed = await client.get("/api/quests", headers=headers)
    assert "Scout the lair" not in [q["title"] for q in listed.json()]


async def test_agent_handles_a_refusal(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    fake_client = FakeAgentAnthropicClient(
        stream_turns=[([], _final_message([], stop_reason="refusal"))]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, "/api/agent/chat", {"messages": [{"role": "user", "content": "hi"}]}, headers
    )

    assert events[-1] == ("error", {"message": "Claude declined to answer that."})


async def test_agent_gives_up_after_too_many_iterations(client, signup_and_login):
    """Proves app/agent.py's own guardrail 1 (`MAX_AGENT_ITERATIONS`) is a
    real, enforced cap -- a deliberately pathological fake client that
    calls a tool on every single turn, forever."""
    from app.agent import MAX_AGENT_ITERATIONS

    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")

    def _tool_use_turn(n: int):
        return (
            [],
            _final_message(
                [_tool_use_block(f"toolu_{n}", "list_quests", {})], stop_reason="tool_use"
            ),
        )

    fake_client = FakeAgentAnthropicClient(
        stream_turns=[_tool_use_turn(i) for i in range(MAX_AGENT_ITERATIONS + 2)]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client,
        "/api/agent/chat",
        {"messages": [{"role": "user", "content": "keep listing"}]},
        headers,
    )

    assert events[-1] == (
        "error",
        {
            "message": (
                f"Stopped after {MAX_AGENT_ITERATIONS} steps without a final answer. "
                "Try asking again, more specifically."
            )
        },
    )
    usage = dict(events)["usage"]
    assert usage == {"iterations": MAX_AGENT_ITERATIONS, "tool_calls": MAX_AGENT_ITERATIONS}


async def test_agent_chat_rejects_more_than_forty_messages(client, signup_and_login):
    """A direct proof of app/models.py's own `AgentChatRequest` guardrail
    -- a request this oversized is rejected by Pydantic validation (a 422)
    before app/agent.py's own loop, or any Claude call, is ever reached."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    too_many = [{"role": "user", "content": "hi"} for _ in range(41)]

    response = await client.post("/api/agent/chat", json={"messages": too_many}, headers=headers)

    assert response.status_code == 422
