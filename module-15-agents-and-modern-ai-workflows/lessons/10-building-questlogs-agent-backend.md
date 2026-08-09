# Lesson 10 — Building QuestLog's Agent: The Backend

## What you'll learn

- How every concept from Lessons 01–08 (the loop, tool design, memory
  scope, guardrails) comes together in one real feature:
  `POST /api/agent/chat`, QuestLog's own autonomous agent.
- The exact six tools this agent has, and the real design reasoning
  behind each one — including the one tool this feature deliberately
  does **not** have.
- A genuine mistake this module's own agent's first draft made, and the
  actual fix — a real story about why a design decision that looks fine
  on paper can still be wrong, and how you'd catch it.

## Why this matters

This is the payoff lesson for the entire module. Nothing here introduces
a new concept — every single piece is something Lessons 01–08 already
taught you, applied to a real, running, tested feature inside an app
you've been building since Module 04. Reading this lesson should feel
like recognizing old friends in new places, not learning anything new.

## Prerequisites

- **Every lesson in this module so far.** This lesson doesn't re-explain
  the loop, tool design, memory, or guardrails — it shows you exactly
  where each one lives in real code.
- **Module 13 and Module 14, in full** — this agent reuses both modules'
  own features as tools, unmodified.

## The concept, explained simply

QuestLog's agent is nothing more than Lesson 02's loop, with six real
tools instead of two toy ones, wired to QuestLog's own database instead
of a calculator, and streamed over Server-Sent Events the same way
Module 13's and Module 14's own AI features already were. If you can
explain Lesson 02's `run_agent` function from memory, you already
understand the shape of `app/agent.py`'s `run_agent_turn` — the rest of
this lesson is just naming which real QuestLog capability sits behind
each tool, and why.

## The details

### The six tools, and the one QuestLog doesn't have

`app/agent.py`'s `AGENT_TOOLS` defines exactly these, each a thin wrapper
around code you've already read in an earlier module:

| Tool | Wraps | New code needed? |
|---|---|---|
| `list_quests` | `app/repository.py`'s `list_quests` | None |
| `create_quest` | `app/repository.py`'s `create_quest`, validated via `QuestCreate` | None |
| `update_quest` | `app/repository.py`'s `update_quest`, validated via `QuestUpdate` | None |
| `complete_quest` | The same `update_quest`, called with `QuestUpdate(done=True)` | None |
| `search_quest_notes` | Module 14's `embed_text` + `find_similar_chunks` | None (retrieval only — see below) |
| `suggest_quest_breakdown` | Module 13's `BREAKDOWN_SCHEMA`/`QuestBreakdownResult` | One new, direct Claude call (see below) |

**There is no `delete_quest` tool.** Lesson 08 already gave you the full
reasoning — QuestLog's own `delete_quest` is a real, permanent operation
with no undo, and the cheapest honest guardrail is simply not exposing
that capability to the agent at all, ever. `tests/test_agent.py`'s own
`test_agent_has_no_delete_tool_and_has_the_six_documented_tools` asserts
this directly, as a fact about the tool list itself — go read that test
now if you haven't; it's a one-line proof of a real safety decision, not
decoration.

### `complete_quest` vs. `update_quest`: Lesson 03's tool-design principle, applied

You met the general principle in Lesson 03: promote a common, easily
misused action to its own tool. `complete_quest(quest_id)` exists
specifically so the model never has to remember that "mark it done"
means `{"done": true}` on `update_quest` — one argument, one job, harder
to get subtly wrong than a general-purpose update call.

### `search_quest_notes`: composing Module 14 without duplicating it

Read `app/agent.py`'s `_tool_search_quest_notes` now. It calls
`embed_text` (Module 14) and `repository.find_similar_chunks` (Module 14)
directly — the *exact* retrieval primitives that module already built and
tested — but it deliberately does **not** call `app/rag.py`'s
`stream_note_answer`. Why not? `stream_note_answer` both retrieves *and*
asks Claude to write a cited answer. Nesting that entire second
conversation inside one tool call of *this* agent's own loop would mean
one player message could trigger two, entirely separate, unrelated
Claude conversations — real, avoidable complexity, since this agent's own
outer loop is *already* about to make another Claude call right after
the tool result comes back, and that outer call can write the cited
answer itself (see `SYSTEM_PROMPT`'s own citation instruction) once it
has the excerpts in hand. The tool's job stays narrow: retrieval, and
nothing else — the same "one tool, one job" discipline from Lesson 03.

### `suggest_quest_breakdown`: reusing a schema without reusing a whole round trip

Read `_tool_suggest_quest_breakdown` now. It imports `BREAKDOWN_SCHEMA`
and `QuestBreakdownResult` directly from `app.ai_assistant` — Module 13's
own, already-tested JSON Schema and Pydantic validation model — but makes
its **own**, single, non-streaming `ai_client.messages.create(...)` call,
rather than reusing `stream_quest_breakdown`'s whole tool-use round trip.
Two real reasons: this call's own text never reaches the player directly
(only the parsed `sub_quests` titles do, folded into the agent's own next
turn), so there's nothing for token-by-token streaming to make more
responsive; and reusing the *schema and validation* (pure data) without
reusing the *behavior* (a whole nested tool-calling loop) keeps this
agent's own iteration budget honest — one tool call here costs exactly
one Claude call, not a whole second, hidden loop with its own iteration
count.

### The real mistake this module's own first draft made — and the actual fix

Here's an honest story, not a hypothetical: the first version of
`app/agent.py`'s `_execute_tool` opened a **fresh** database session per
tool call, directly via `AsyncSessionLocal()`, reasoning that a streamed
agent turn could run for several seconds across several tool calls, and
holding one long-lived session open for that whole time seemed like bad
practice. That reasoning wasn't wrong in the abstract — but it broke this
backend's own test suite outright: every test that exercised a real tool
call (`test_agent_lists_quests_via_tool_round_trip`, and six others)
failed with a `ConnectionRefusedError`, because `AsyncSessionLocal`
always connects to the app's own *configured* Postgres URL — it has no
way to know that `tests/conftest.py`'s own `client` fixture had already
substituted an in-memory SQLite session via
`app.dependency_overrides[get_db]`, the exact mechanism every other route
in this app relies on for testing (Module 08, then Module 10 for Redis,
now here). Opening a session directly, instead of accepting the one
FastAPI's own dependency injection already resolved, silently bypassed
that entire test infrastructure.

**The fix:** `app/routers/agent.py`'s route takes `session: DbSession` —
the same request-scoped session dependency every other route in this app
already uses — and passes it straight through to `run_agent_turn`, which
threads it into every tool call for the whole turn. Read
`_execute_tool`'s own docstring now for the fix stated in the code itself.
This is a real, worked example of exactly the kind of mistake Lesson 08
warned you an eval or a test suite exists to catch: a design that looks
reasonable on paper, caught immediately and concretely by running the
real test suite, not by re-reading the code and hoping it was right.

**Try it yourself:** Explain, in your own words, why a design that opens
its own database connection *inside* a function is fundamentally harder
to test than one that receives its connection as a parameter — this is
the exact same "dependency injection makes testing possible" lesson
Module 05 first taught you, now showing up again in a completely
different feature.

### Memory scope, made concrete in code

`app/models.py`'s `AgentChatMessage`/`AgentChatRequest` are the entire
memory story for this feature: a plain `role` and `content` string, and
nothing else, resent in full on every request. Read their own docstrings
now — they state, in the code itself, exactly what Lesson 04 taught you
to say honestly: short-term only, held on the frontend, gone the moment
the tab closes, and — the one subtler point — a turn's own tool-calling
scratch work is never part of what gets resent; only the finished answer
is.

### Guardrails, all six, located in one place

Read `app/agent.py`'s own module docstring in full now — it states every
guardrail from Lesson 08 explicitly, with the exact reasoning, and points
at exactly where each one lives in the code below it (`MAX_AGENT_ITERATIONS`,
the missing `delete_quest` tool, `_get_owned_quest`'s ownership check,
the `usage` event, and the reused `QuestCreate`/`QuestUpdate` validation).
There is nothing left for this lesson to add here — go read it.

### The tests: proving every one of these decisions is real

`tests/test_agent.py` is not decoration — it's the same trajectory-level
and tool-call-correctness evaluation style Lesson 08 taught you, applied
for real. A few worth reading closely right now:

- `test_agent_update_for_someone_elses_quest_is_a_recoverable_tool_error`
  — proves the ownership guardrail by actually checking the *other*
  user's quest is untouched afterward, not just that the HTTP response
  looked fine.
- `test_agent_create_quest_with_invalid_input_does_not_create_anything`
  — proves the Pydantic-validation guardrail the same way: by checking
  the database's own real state, not the response shape.
- `test_agent_gives_up_after_too_many_iterations` — a deliberately
  pathological fake client that never stops asking for tools, proving
  `MAX_AGENT_ITERATIONS` is a real, enforced cap, not just a constant
  sitting unused in the file.

**Live-verified in this course's own environment, August 9, 2026:**
`pytest -q`, run from `project/questlog/backend` with this module's own
`requirements.txt`/`requirements-dev.txt` installed, passes **85 tests**,
with 2 skipped (the pgvector-only integration tests, exactly as
established since Module 14) — including every test in this module's own
new `tests/test_agent.py`. `ruff check app tests` reports zero issues.
No real `ANTHROPIC_API_KEY`, no real Postgres, no real embedding model
was used for any of it — the same principle every AI feature's test
suite in this course has followed since Module 13.

## Common mistakes & gotchas

- **Assuming a tool needs its own database session "for safety."** As
  this lesson's own real story shows, the *safer*-looking choice
  (open your own session) was actually the *wrong* one here, because it
  broke testability — always prefer the dependency your framework already
  gives you over rolling your own, unless you have a specific, concrete
  reason not to.
- **Forgetting that reusing a schema and reusing a whole feature's
  behavior are different things.** `suggest_quest_breakdown`'s own
  design (reuse `BREAKDOWN_SCHEMA`, don't reuse
  `stream_quest_breakdown`'s whole round trip) is the general pattern:
  ask specifically what you need from an existing module, not "the whole
  thing or nothing."
- **Reading `AGENT_TOOLS` without also reading `_execute_tool` and the
  individual `_tool_*` functions.** The tool *definitions* only tell the
  model what's possible — the real guardrails (ownership checks,
  validation) live in the *implementations*, not the schemas.

## How this connects

Lessons 01–08 gave you every concept this lesson just pointed at inside
real code. Lesson 11 finishes the story — the frontend that talks to this
backend, and the honest walkthrough of how this feature actually reaches
production using Module 10's containers, Module 11's CI/CD pipeline, and
Module 11's own Sentry monitoring, with nothing new to build on the
deployment side at all.

## Quick self-check

1. Name QuestLog's own six agent tools from memory, and for each one,
   which earlier module's own code it reuses.
2. Explain, precisely, why `search_quest_notes` doesn't call
   `app/rag.py`'s `stream_note_answer`.
3. Walk through the real mistake this lesson describes (the first draft's
   own session-handling choice) and the actual fix — why did the original
   choice fail, specifically, and what concept from Module 05 explains
   why the fix works?
4. What is the complete memory story for this feature, stated the way
   `app/models.py`'s own `AgentChatMessage` docstring states it?
5. Pick one guardrail from `app/agent.py`'s own module docstring and
   explain, in your own words, which specific line(s) of code enforce it.
