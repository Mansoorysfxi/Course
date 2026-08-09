"""Tests for POST /api/quests/{quest_id}/suggest-breakdown -- NEW in
Module 13.

Every test in this file runs against a **fake** Anthropic client -- never
a real one, and never a real `ANTHROPIC_API_KEY` -- exactly the same
principle Module 08 established for the database (in-memory SQLite, not a
real Postgres) and Module 10 established for Redis (`FakeRedis`, not a
real Redis server). See lessons/07-building-questlogs-ai-assistant-backend.md's
own "testing an AI feature without an API key" section for the full
reasoning: this backend's own logic (the tool round-trip, the SSE
formatting, the auth scoping, the 503-when-unconfigured behavior) is what
these tests verify, and none of that logic requires ever actually talking
to Claude.

`test_missing_api_key_returns_503` is the one test that needs **no fake
client and no override at all** -- it relies on the plain fact that this
test environment's `.env`/`conftest.py` never sets `ANTHROPIC_API_KEY`, so
`app.dependencies.get_ai_client`'s real, un-overridden implementation
already returns `None`. That is itself the proof this feature's tests
don't require a real key: the *default* test environment already exercises
the "not configured" path correctly.
"""

import json
from types import SimpleNamespace

from app.dependencies import get_ai_client
from app.main import app
from tests.test_quests import _create_quest


def _text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def _tool_use_block(block_id: str, name: str, tool_input: dict) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=tool_input)


def _final_message(content: list, stop_reason: str) -> SimpleNamespace:
    return SimpleNamespace(content=content, stop_reason=stop_reason)


class FakeMessageStream:
    """Stands in for the real SDK's `AsyncMessageStreamManager` -- see
    app/ai_assistant.py's own use of `async with client.messages.stream(...)
    as stream:`. Implements exactly the two things that file actually
    calls on a real stream: iterating `stream.text_stream`, and awaiting
    `stream.get_final_message()` afterward. Nothing else about the real
    SDK's stream object is faked, because nothing else is used.
    """

    def __init__(self, text_chunks: list[str], final_message: SimpleNamespace):
        self._text_chunks = text_chunks
        self._final_message = final_message

    async def __aenter__(self) -> "FakeMessageStream":
        return self

    async def __aexit__(self, *exc_info: object) -> bool:
        return False

    async def _iter_text(self):
        for chunk in self._text_chunks:
            yield chunk

    @property
    def text_stream(self):
        return self._iter_text()

    async def get_final_message(self) -> SimpleNamespace:
        return self._final_message


class FakeMessages:
    """Stands in for the real SDK's `client.messages`. `turns` is a list
    of `(text_chunks, final_message)` pairs, consumed one per call to
    `.stream(...)` -- turn 0 for the first request this test's code makes,
    turn 1 for the second (e.g. after a tool result goes back), and so
    on. A test with only one turn is asserting Claude answers directly, no
    tool call at all."""

    def __init__(self, turns: list[tuple[list[str], SimpleNamespace]]):
        self._turns = iter(turns)

    def stream(self, **kwargs: object) -> FakeMessageStream:
        text_chunks, final_message = next(self._turns)
        return FakeMessageStream(text_chunks, final_message)


class FakeAnthropicClient:
    """Stands in for `anthropic.AsyncAnthropic` in its entirety -- this
    test suite's only touchpoint with "the Anthropic API" is this class's
    `.messages` attribute. Installed via `app.dependency_overrides`,
    exactly the same mechanism tests/conftest.py's `client` fixture
    already uses for `get_db` and `get_redis_client`."""

    def __init__(self, turns: list[tuple[list[str], SimpleNamespace]]):
        self.messages = FakeMessages(turns)


async def _collect_sse_events(client, url: str, headers: dict) -> list[tuple[str, dict]]:
    """Reads a streamed `text/event-stream` response body and returns it
    as a list of `(event_name, data_dict)` pairs, in arrival order. httpx's
    `AsyncClient.stream(...)` works the same way over `ASGITransport`
    (this test suite's transport -- see conftest.py) as it does over a
    real socket, so this reads the *actual* streamed response the way a
    real browser's `EventSource`/`fetch` would, not a pre-buffered one."""
    events: list[tuple[str, dict]] = []
    async with client.stream("POST", url, headers=headers) as response:
        assert response.status_code == 200, await response.aread()
        event_name = None
        async for line in response.aiter_lines():
            if line.startswith("event: "):
                event_name = line.removeprefix("event: ")
            elif line.startswith("data: "):
                assert event_name is not None
                events.append((event_name, json.loads(line.removeprefix("data: "))))
    return events


async def test_missing_api_key_returns_503(client, signup_and_login):
    """No override at all -- the un-overridden `get_ai_client` dependency
    is exercised exactly as it runs for real when `ANTHROPIC_API_KEY`
    isn't set, which is the case for this entire test run (see this
    file's own module docstring). This is the test that proves the whole
    suite genuinely needs no real key: it isn't skipped or mocked around,
    it's directly exercising -- and asserting on -- the "not configured"
    behavior."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    response = await client.post(f"/api/quests/{created['id']}/suggest-breakdown", headers=headers)

    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]


async def test_breakdown_without_a_tool_call(client, signup_and_login):
    """Claude answers directly, first turn, no tool use at all -- the
    simplest possible successful path."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers, title="Defeat the dragon")

    final_json = json.dumps(
        {"sub_quests": [{"title": "Scout the lair"}, {"title": "Gather fire-resistant gear"}]}
    )
    fake_client = FakeAnthropicClient(
        turns=[
            (
                # Split into two chunks purely to prove `collected_text` is
                # correctly *accumulated* across multiple `text_stream`
                # pieces (a real streamed response arrives in many small
                # chunks, not one) -- concatenated, they equal `final_json`
                # exactly, which is what app/ai_assistant.py actually
                # parses (never the final_message's own content blocks).
                [final_json[:20], final_json[20:]],
                _final_message([_text_block(final_json)], stop_reason="end_turn"),
            ),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, f"/api/quests/{created['id']}/suggest-breakdown", headers
    )

    event_names = [name for name, _ in events]
    assert "tool_call" not in event_names
    assert event_names[-1] == "result"
    result_data = events[-1][1]
    assert result_data["sub_quests"] == ["Scout the lair", "Gather fire-resistant gear"]


async def test_breakdown_with_a_tool_call_round_trip(client, signup_and_login):
    """The full round-trip: Claude calls `check_existing_quest_titles` on
    its first turn, gets a tool_result back, and answers on its second
    turn. Asserts the actual sequence of events the frontend would see,
    not just the final result."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    await _create_quest(client, headers, title="Gather Healing Herbs")
    created = await _create_quest(client, headers, title="Defeat the dragon")

    final_json = json.dumps({"sub_quests": [{"title": "Scout the lair"}, {"title": "Buy a sword"}]})
    fake_client = FakeAnthropicClient(
        turns=[
            (
                ["Let me check your other quests first."],
                _final_message(
                    [
                        _text_block("Let me check your other quests first."),
                        _tool_use_block("toolu_1", "check_existing_quest_titles", {}),
                    ],
                    stop_reason="tool_use",
                ),
            ),
            (
                [final_json],
                _final_message([_text_block(final_json)], stop_reason="end_turn"),
            ),
        ]
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, f"/api/quests/{created['id']}/suggest-breakdown", headers
    )

    event_names = [name for name, _ in events]
    assert event_names.count("token") >= 2  # one preamble chunk + the final JSON chunk
    assert "tool_call" in event_names
    assert events[event_names.index("tool_call")][1] == {"tool": "check_existing_quest_titles"}
    assert event_names[-1] == "result"
    assert events[-1][1]["sub_quests"] == ["Scout the lair", "Buy a sword"]


async def test_breakdown_handles_a_refusal(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    fake_client = FakeAnthropicClient(
        turns=[([], _final_message([], stop_reason="refusal"))],
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, f"/api/quests/{created['id']}/suggest-breakdown", headers
    )

    assert events == [
        ("error", {"message": "Claude declined to suggest a breakdown for this quest."})
    ]


async def test_breakdown_handles_malformed_json(client, signup_and_login):
    """Even though `output_config.format` is documented to guarantee
    schema-conformant JSON on a normal `end_turn`, app/ai_assistant.py
    still validates the parsed result with Pydantic (this module's own
    "defense in depth" reasoning) -- this test proves that check is real,
    not decorative, by feeding it text that fails validation (only one
    sub-quest, below `QuestBreakdownResult`'s `min_length=2`)."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    bad_json = json.dumps({"sub_quests": [{"title": "Only one, which is invalid"}]})
    fake_client = FakeAnthropicClient(
        turns=[([bad_json], _final_message([_text_block(bad_json)], stop_reason="end_turn"))],
    )
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, f"/api/quests/{created['id']}/suggest-breakdown", headers
    )

    assert events[-1][0] == "error"
    assert "Could not parse" in events[-1][1]["message"]


async def test_breakdown_gives_up_after_too_many_tool_iterations(client, signup_and_login):
    """A deliberately pathological fake client that calls the tool every
    single turn, forever -- proves MAX_TOOL_ITERATIONS actually bounds the
    loop instead of it hanging (or billing) indefinitely."""
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    def _tool_use_turn(n: int):
        return (
            [],
            _final_message(
                [_tool_use_block(f"toolu_{n}", "check_existing_quest_titles", {})],
                stop_reason="tool_use",
            ),
        )

    fake_client = FakeAnthropicClient(turns=[_tool_use_turn(i) for i in range(10)])
    app.dependency_overrides[get_ai_client] = lambda: fake_client

    events = await _collect_sse_events(
        client, f"/api/quests/{created['id']}/suggest-breakdown", headers
    )

    assert events[-1] == (
        "error",
        {"message": "Gave up after checking too many times without a final answer."},
    )


async def test_breakdown_for_someone_elses_quest_is_404(client, signup_and_login):
    """The same ownership check every other single-quest route already
    enforces (app/dependencies.py's `get_quest_or_404`) -- this route adds
    no new authorization logic, so this test exists to prove that's
    actually true for this specific new route too, not just by
    inspection."""
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, hero_headers)

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")

    response = await client.post(
        f"/api/quests/{created['id']}/suggest-breakdown", headers=villain_headers
    )

    assert response.status_code == 404
