# Lesson 07 — Building QuestLog's AI Assistant: The Backend

This lesson has no external facts to re-verify — everything in it
describes this module's own `project/questlog/` code, which was written,
run, and tested for real while generating this module (exact commands and
real output are shown throughout, and repeated in this module's
`CHECKLIST.md`).

## What you'll learn

- The exact, real feature this module adds to QuestLog: `POST
  /api/quests/{quest_id}/suggest-breakdown`, and precisely why it's
  shaped the way it is.
- How Lessons 01-06's separate pieces — a real API call, streaming,
  structured output, tool use, error handling, and the idea of evaluating
  the result — combine into one real, working FastAPI endpoint.
- Exactly what changed in QuestLog's backend code, file by file, and why
  each change lives where it does.
- How to test an AI feature without ever needing a real API key in the
  test suite — and see that principle actually working, with real
  `pytest` output.

## Why this matters

Every module since Module 05 grew QuestLog's backend by adding one real,
necessary thing at a time: a database, auth, a Redis cache, a health
check, a CI/CD pipeline. This module's AI-assistant endpoint follows that
exact same discipline — a small, real, well-justified feature added
*around* the existing code, not a rewrite. If you've kept up with the
running project, this lesson should read like "one more, very
recognizable, growth step," not a new codebase.

## Prerequisites

- **Lessons 01-06 of this module, in full.** This lesson assumes you can
  read a manual tool-use loop, recognize `output_config.format`, and know
  what `stream.text_stream` does, without those being re-explained.
- **Module 07's `CurrentUser`/`get_quest_or_404` dependency pattern** and
  **Module 10's `RedisClient` dependency pattern** — this lesson's new
  `AiClient` dependency is built from the exact same shape as both.
- **Your own copy of `project/questlog/`, copied forward from Module 11**
  — every file this lesson discusses is a real file in this module's own
  `project/questlog/backend/`.

## The concept, explained simply

Think of this feature the way you'd think about adding one new, focused
system to an already-shipped game — not a rewrite of the save system, the
combat system, and the UI all at once, just one new, self-contained
feature (say, a hint system) that reads from data the game already has
and writes back through the exact same save-game pipeline everything else
already uses. QuestLog's AI assistant reads an existing quest (through the
exact same auth-scoped lookup every other quest route already uses) and,
when the player accepts a suggestion, creates a new quest through the
exact same `addQuest` path every other "add a quest" action already goes
through. Nothing about how QuestLog stores or serves quests changes; one
new, real capability is added on top.

## The details

### The feature, precisely

**Endpoint:** `POST /api/quests/{quest_id}/suggest-breakdown`

Given one of the player's own quests, streams back Claude's suggestion of
2-4 concrete sub-quests, checking the player's other quest titles first
to avoid suggesting a duplicate. Chosen (per the master plan's own
suggested feature) because it's small, genuinely useful, and exercises
every one of this module's real techniques without forcing any of them:

- **Structured output** (Lesson 03) — the final list of sub-quest titles
  is schema-constrained JSON, validated again with Pydantic, never
  parsed from free-form prose.
- **Tool use** (Lesson 04) — a real `check_existing_quest_titles` tool,
  giving Claude live access to information it has no other way to know.
- **Streaming** (Lesson 02) — every turn, including the tool-use turn,
  streams to the frontend so the player sees progress immediately rather
  than waiting for the whole feature to finish silently.

### Why a REST-ish shape, and why streaming via a POST, not a GET

`POST /api/quests/{quest_id}/suggest-breakdown` is a `POST`, not a `GET`,
even though it doesn't strictly create or replace a stored resource the
way `POST /api/quests` does — this course's own judgment call, and worth
stating honestly: a `GET` is supposed to be safe and idempotent (Module
02's own REST material), and triggering a real, billed AI call with real,
observable side effects (checking other quests) each time doesn't fit
that contract as cleanly as a `POST` does, even though nothing is written
to the database by this route itself. The `/{quest_id}/suggest-breakdown`
path shape (a sub-resource-like action under an existing quest) mirrors
how a REST API commonly expresses "do a specific action to this specific
resource" when that action isn't a plain CRUD verb.

**Why a POST body can still stream:** streaming isn't tied to `GET` or to
`EventSource` specifically — it's a property of the *response*, not the
request method. FastAPI's `StreamingResponse` (below) works identically
regardless of which HTTP method triggered it; Lesson 08 explains exactly
why the frontend uses `fetch()` rather than a native `EventSource` for
this reason (`EventSource` can only issue `GET` requests and cannot set
custom headers, and this route needs both a `POST` and an `Authorization`
header).

### File by file: exactly what changed

**`app/config.py`** — two new `Settings` fields, following the exact
pattern `sentry_dsn` already established in Module 11:

```python
anthropic_api_key: str | None = None
ai_model: str = "claude-haiku-4-5"
```

`anthropic_api_key` defaults to `None` — the same "this app must run
correctly with no key at all" principle every optional external
dependency in this codebase already follows (Redis, Sentry, and now
this). `ai_model` is a **fixed technology decision**, recorded in
`RUNNING_PROJECT.md`: Claude Haiku 4.5, chosen because suggesting 2-4
short sub-quest titles doesn't need a larger model's deeper reasoning,
and Lesson 05's cost-management principle ("pick the cheapest model that
does the job") applies directly.

**`app/dependencies.py`** — a new `get_ai_client` dependency and
`AiClient` alias, shaped exactly like `RedisClient`:

```python
def get_ai_client() -> anthropic.AsyncAnthropic | None:
    if not settings.anthropic_api_key:
        return None
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

AiClient = Annotated[anthropic.AsyncAnthropic | None, Depends(get_ai_client)]
```

Two deliberate choices worth pausing on: it returns `None`, not a client
that would fail confusingly on its first real call, when no key is
configured — the route (below) turns that `None` into a clean, specific
`503`. And it uses `anthropic.AsyncAnthropic`, not the plain
`anthropic.Anthropic` this module's standalone exercises use — Lesson
02's own explanation of why a synchronous, blocking call inside an
`async def` FastAPI route would freeze the whole server applies directly
here.

**`app/ai_assistant.py`** — an entirely new file, and the real heart of
this feature. Its central function, `stream_quest_breakdown`, is Lesson
04's manual tool-use loop, with Lesson 02's streaming and Lesson 03's
structured output layered on top of every turn:

```python
async def stream_quest_breakdown(client, quest, existing_titles):
    messages = [{"role": "user", "content": _build_user_prompt(quest)}]

    for _ in range(MAX_TOOL_ITERATIONS):
        collected_text = ""
        async with client.messages.stream(
            model=settings.ai_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[CHECK_EXISTING_TITLES_TOOL],
            output_config={"format": {"type": "json_schema", "schema": BREAKDOWN_SCHEMA}},
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                collected_text += text
                yield {"event": "token", "data": {"text": text}}
            final_message = await stream.get_final_message()

        if final_message.stop_reason == "tool_use":
            # ... echo the assistant turn, execute the tool, append the
            # tool_result, loop again -- exactly Lesson 04's round-trip.
            ...
            continue

        if final_message.stop_reason == "refusal":
            yield {"event": "error", "data": {"message": "..."}}
            return

        if final_message.stop_reason == "max_tokens":
            yield {"event": "error", "data": {"message": "..."}}
            return

        # A genuine final answer -- parse and validate before trusting it.
        try:
            parsed = json.loads(collected_text)
            result = QuestBreakdownResult.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError):
            yield {"event": "error", "data": {"message": "..."}}
            return

        yield {"event": "result", "data": {"sub_quests": [s.title for s in result.sub_quests]}}
        return
```

(The full file, with every line explained, is in this module's own
`project/questlog/backend/app/ai_assistant.py` — its module docstring
alone is worth reading in full; it's written as this lesson's own
supplementary material.)

**Every parameter on `client.messages.stream(...)` here is included on
*every* turn of the loop, tool-use turns included** — `tools` and
`output_config.format` together, exactly as Lesson 03's own header table
confirmed is supported. This is a deliberate, load-bearing design
decision, not an accident: since a manual loop can't know in advance
whether the *next* response will be another tool call or the final
answer, opening every turn with `.stream()` (rather than trying to guess
which turn should be streamed and which shouldn't) means the frontend
sees Claude's text the instant it's generated on *every* turn — including
a short "Let me check your other quests" preamble, if Claude produces
one — rather than only on whichever turn happens to be last.

**Streaming and structured output, reconciled honestly.** This is the
real tension the master plan calls out, and here's exactly how this code
resolves it: `output_config.format` guarantees the *complete* response
text is valid, schema-conformant JSON — but only once it's complete. A
partially-streamed JSON string (`{"sub_quests": [{"tit`) is not valid
JSON and can't be safely parsed mid-stream. So this code streams the
**raw text** as it arrives (`event: "token"`, forwarded live to the
frontend for a genuinely responsive feel) and only calls `json.loads()` +
`QuestBreakdownResult.model_validate(...)` on `collected_text` once
`stream.get_final_message()` confirms the turn is actually done. This is
a real, common pattern for reconciling the two features — not a
compromise on correctness, since the schema guarantee is still fully
honored on the complete text, only a decision about *when* the frontend
gets to see characters arrive versus when it gets the final, structured,
trustworthy result.

**`app/routers/quests.py`** — one new route, reusing everything this
router already has:

```python
@router.post("/{quest_id}/suggest-breakdown")
async def suggest_quest_breakdown(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
    current_user: CurrentUser,
    ai_client: AiClient,
):
    if ai_client is None:
        raise HTTPException(status_code=503, detail="...")

    existing = await repository.list_quests(session, owner_id=current_user.id)
    existing_titles = [q.title for q in existing if q.id != quest.id]

    async def event_stream():
        async for event in stream_quest_breakdown(ai_client, quest, existing_titles):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

Notice what's **not** new here: `quest: Annotated[Quest, Depends(get_quest_or_404)]`
is the exact same auth-scoped lookup `get_quest`, `update_quest`, and
`delete_quest` already use — a request for a quest that doesn't exist, or
belongs to someone else, is rejected before this function's own body ever
runs, with zero new authorization logic written for this feature.
`repository.list_quests` is the exact same query `list_quests` (the plain
`GET /api/quests` route) already calls — no new database query was
written at all; this feature just reuses existing data access to compute
`existing_titles`. This is the whole point of building on an established
codebase: the *only* genuinely new logic is the AI round-trip itself.

`event_stream()` is where the raw SSE wire format (Lesson 02) is actually
written — two lines per event, a blank line between them — and it's the
*only* place in this backend that knows that format; `stream_quest_breakdown`
itself yields plain dicts and knows nothing about SSE, the same "one
seam" separation `app/repository.py`'s own module docstring already
established between "how data is stored" and "how it's served."

**`requirements.txt`** — one new line: `anthropic==0.121.0`, this
lesson's own verified SDK version (Lesson 00).

### Testing an AI feature without ever needing a real key

`tests/test_ai_assistant.py` is a new file with **seven tests**, none of
which touch a real Anthropic API, following the exact same principle
Module 08 established for the database (in-memory SQLite) and Module 10
established for Redis (`FakeRedis`): a small fake standing in for the
real external dependency, exercising this backend's own logic.

```python
class FakeMessageStream:
    """Stands in for the real SDK's stream object -- implements exactly
    the two things app/ai_assistant.py actually calls: iterating
    `text_stream`, and awaiting `get_final_message()`."""

    def __init__(self, text_chunks, final_message):
        self._text_chunks = text_chunks
        self._final_message = final_message

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    @property
    def text_stream(self):
        async def _iter():
            for chunk in self._text_chunks:
                yield chunk
        return _iter()

    async def get_final_message(self):
        return self._final_message
```

A `FakeAnthropicClient` wraps this and is installed via
`app.dependency_overrides[get_ai_client] = lambda: fake_client` — the
exact same override mechanism `tests/conftest.py`'s own `client` fixture
already uses for `get_db` and `get_redis_client`. One test needs **no
override and no fake client at all**:

```python
async def test_missing_api_key_returns_503(client, signup_and_login):
    headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    created = await _create_quest(client, headers)

    response = await client.post(f"/api/quests/{created['id']}/suggest-breakdown", headers=headers)

    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]
```

This test relies on a plain fact about the test environment: no test in
this suite ever sets `ANTHROPIC_API_KEY`, so `get_ai_client`'s real,
un-overridden implementation genuinely returns `None` — this is the
proof, not just the claim, that the whole suite needs no real key. The
other six tests cover: a direct answer with no tool call; the full
tool-use round-trip (asserting the actual event sequence — `token`, then
`tool_call`, then `result`); a refusal; malformed/under-length JSON
failing the second, defense-in-depth Pydantic check (Lesson 03); a
pathological fake client that never stops asking for the tool (proving
`MAX_TOOL_ITERATIONS` actually bounds the loop); and ownership — a
request for someone else's quest returns 404, proving this new route
inherited the existing auth-scoping correctly rather than needing its own.

**Actual output**, running the whole backend suite (this exact command
was run for real while writing this lesson, from
`module-13-building-with-llm-apis/project/questlog/backend/`, with `ANTHROPIC_API_KEY`
unset the entire time):

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

```
..............................................                           [100%]
46 passed in 17.20s
```

46 tests — the 39 already passing at the end of Module 11, plus this
lesson's 7 new ones — all passing, with `ruff check .` and `ruff format
--check .` both clean, and no real API key anywhere in the process.

**Try it yourself:** Open `app/ai_assistant.py`, temporarily change
`MAX_TOOL_ITERATIONS` from `3` to `1`, and re-run
`pytest tests/test_ai_assistant.py -v`. Predict, before running it, which
specific test will fail (hint: re-read
`test_breakdown_with_a_tool_call_round_trip`'s own fake client — how many
turns does it need to reach a final answer?) — then confirm your
prediction against the real failure, and change the value back.

## Common mistakes & gotchas

- **Putting `model`/`system`/`tools`/`output_config` only on the *first*
  turn of the loop, assuming later turns don't need them.** Every field
  the API needs to interpret a request correctly must be present on
  *every* call — the Messages API has no memory between requests (Lesson
  01), tool-use turns included.
- **Forgetting the second, application-level Pydantic validation "because
  the schema already guarantees it."** Lesson 03 already covered why this
  is wrong in general; this feature's own `test_breakdown_handles_malformed_json`
  test exists specifically to prove that check is real, not decorative.
- **Building a new authorization check for this route** instead of
  reusing `get_quest_or_404`. If you find yourself writing a new
  `if quest.owner_id != current_user.id:` check anywhere in this feature,
  that's a sign you've duplicated logic that already exists and is
  already tested.
- **Testing this feature by actually calling the real API.** Slow,
  costs real money on every CI run, and non-deterministic — exactly the
  reasons Module 08 and Module 10 already established for mocking the
  database and Redis, applying here to a third external dependency.
- **Forgetting `ai_client is None` is a real, expected case to test**,
  not just a defensive `if` statement that happens to exist. It's the
  *default* state of this entire test suite (no key configured) — if it
  weren't handled and tested, every single other test in this file would
  need to remember to override it, and a bug here would go unnoticed.

## How this connects

This lesson is where every earlier lesson in this module stops being
separate, standalone material and becomes one real, shipped feature.
Lesson 08 is next — and it's the other half of this same feature: the
React frontend that actually calls this endpoint, consumes its streamed
events, and lets the player see and accept the suggestions this backend
produces.

## Quick self-check

1. Why does `stream_quest_breakdown` open *every* turn of its loop with
   `.stream()`, including tool-use turns, rather than only streaming the
   final answer?
2. What specific tension exists between streaming and structured output,
   and how does this feature's own code resolve it?
3. Name three pieces of this feature that reuse existing QuestLog code
   with zero new logic, and say what each one is.
4. Which single test in `tests/test_ai_assistant.py` needs no fake client
   and no dependency override at all, and why does that particular test
   prove this feature's tests genuinely don't need a real API key?
5. Why does `get_ai_client` return `None` for a missing key instead of
   constructing an `AsyncAnthropic` client anyway and letting the first
   real call fail?
