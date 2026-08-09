# Lesson 11 — QuestLog's Agent Frontend, the MCP Tie-Back, and Going Live

## What you'll learn

- How QuestLog's own chat frontend (`AgentChatPanel.tsx`) turns Lesson
  10's backend SSE events into a real, usable conversation UI.
- The concrete, bounded decision this module makes about exposing
  QuestLog's own real data over MCP — what got built, what didn't, and
  why.
- The complete, honest path this feature takes from your own machine to
  production: what Module 10's containers, Module 11's CI/CD pipeline,
  and Module 11's own Sentry monitoring do and don't need to change for
  it — including one real, small gap this lesson found and fixed.

## Why this matters

This is the last lesson of the entire course. Every module since Module
04 has been building toward exactly this: one real feature, built end to
end — frontend, backend, database, AI, tests, containers, CI/CD,
monitoring — using nothing invented for this lesson alone, only what you
already built. If you can explain every piece of this lesson, you can
explain your entire portfolio piece to someone else, which is the whole
point.

## Prerequisites

- **Lesson 10, in full.**
- **Module 10 (Docker) and Module 11 (CI/CD, cloud, monitoring), in full**
  — this lesson's "going live" section assumes you remember what
  `render.yaml`, the GitHub Actions pipeline, and Sentry's own
  initialization already do, and adds nothing new to any of them beyond
  one real, honest fix.

## The concept, explained simply

The frontend half of this feature is the least novel part of the entire
module — it's the third time this exact frontend pattern (a hand-rolled
`fetch()` + `ReadableStream` SSE reader, feeding a small React state
machine) has appeared in this course, after Module 13's
`QuestBreakdownPanel` and Module 14's `QuestNotesPanel`. If those two
felt solid, this lesson should feel almost like copying a template you
already trust — because that's exactly what it is.

## The details

### `agentApi.ts`: the third copy of the same SSE-parsing loop

Read `frontend/src/api/agentApi.ts`'s own module docstring now. It states
plainly that this is the *third* appearance of the exact same
`fetch()` + `ReadableStream` reader loop this course has written, and
raises an honest question worth actually thinking about: at what point
does a third copy of the same code stop being "keeping each feature
simple and independent" and start being genuine duplication worth
extracting into a shared helper? This module's own answer, stated in that
docstring, is that a fourth copy would likely be one too many — but three
small, independent, well-tested files, each easy to read start to finish
without indirection, is a defensible place to stop for this course's own
scope. This is a real, honest engineering trade-off, not an oversight —
you're free to disagree and extract the shared helper yourself as extra
practice (see this module's own exercises for a related idea).

### `AgentChatPanel.tsx`: the state machine

Read the whole component now — it's a genuine chat UI, not a single
in-flight status like `QuestBreakdownPanel`. Trace these pieces
specifically:

- **`messages`** is the *entire* memory this feature has (Lesson 04,
  made concrete on the frontend this time) — a plain array in this one
  component's own React state, gone the instant the tab closes.
- **`applyEvent`** is where every SSE event type from Lesson 10's backend
  gets turned into a state update — `tool_call` sets `activeTool` (so the
  UI can show "Creating a quest..." live, per `TOOL_LABELS`), `sources`
  populates the notes-consulted list, `usage` populates the small
  turn/tool-call footer, and `result` is the one event that actually
  appends to `messages` — every other event only affects *transient*,
  in-progress display state, never the persisted conversation itself.
- **The `sources` display bug this module's own first draft had, and the
  actual fix.** An honest story, the frontend's own parallel to Lesson
  10's backend one: the first version only rendered the "Notes
  consulted" list while `status === "streaming"`, which meant it
  vanished the instant a turn finished — exactly the moment a player
  would actually want to double-check what the answer was based on.
  `AgentChatPanel.tsx`'s own comment above that block states the fix:
  render `sources` whenever it's non-empty, independent of streaming
  status, clearing it only when the *next* turn starts. This was caught
  by this module's own test suite, not a design review — go read
  `AgentChatPanel.test.tsx`'s own `"shows sources when the agent searches
  quest notes"` test, which is exactly what failed before the fix.

**Live-verified in this course's own environment, August 9, 2026:**
`npx vitest run`, from `project/questlog/frontend`, passes **34 tests**
across 7 files, including every test in this module's own new
`AgentChatPanel.test.tsx`. `npx tsc -b --noEmit` reports no type errors.
`npm run build` succeeds. `npm run lint` (this project's own `oxlint`)
reports zero new warnings — the two pre-existing warnings it does report
are in `AuthContext.tsx`/`QuestsContext.tsx`, files this module never
touched.

### The MCP tie-back, and why it stays this small

Lesson 05 built a standalone MCP server over a toy, in-memory dataset.
This module's own capstone adds one more piece: `app/mcp_server.py`, a
small, **read-only** MCP server exposing two of QuestLog's own *real*
capabilities — listing a demo account's quests, and searching that
account's own notes — reusing `app/repository.py`'s real, tested
functions directly, never duplicating their logic.

**Read that file's own module docstring now.** It states two real,
bounded scope decisions plainly, worth understanding rather than just
accepting:

1. **Read-only, on purpose.** `app/agent.py`'s own tools already handle
   write access correctly, with a real JWT-authenticated caller behind
   every request. An MCP server exposing *write* access to a real,
   multi-user account needs a genuine answer to "which MCP client, acting
   on whose behalf" — a real, harder authentication problem this file's
   own teaching scope doesn't need to solve, since the feature that
   actually needs write access (`app/agent.py`) already solves it
   correctly, the ordinary way, over HTTP.
2. **One hard-coded demo user.** A local, `stdio`-transported MCP server
   has no `Authorization` header and no natural per-connection identity
   the way an HTTP route does — this file resolves QuestLog's own seeded
   demo account instead, stated honestly as a real simplification, not a
   pattern to copy for a production, multi-user MCP integration.

**What this course actually verified, and what it didn't, stated
honestly:** `list_quests()` was run live in this course's own environment
on August 9, 2026, against a real (SQLite-backed, for this test only)
QuestLog database, and returned the seeded demo account's five real
quests correctly. `search_quest_notes()` follows the exact same
`app/repository.py`'s `find_similar_chunks` query every other retrieval
feature in this course already uses — and, for the exact same reason
Module 14's own `tests/test_notes_pgvector_integration.py` is separately
gated behind a real Postgres+pgvector instance (`.cosine_distance()`
compiles to Postgres's own `<=>` operator, which doesn't exist on
SQLite), this course's own environment could not verify it live. This
isn't a gap unique to this file — it's the exact same, already-documented
limitation of `find_similar_chunks` itself, showing up again here for the
same honest reason.

**Try it yourself:** With this backend's own Module 15 setup running
(a real `pgvector`-enabled Postgres, per Lesson 00), run
`python -m app.mcp_server` from `backend/`, and separately run
`mcp dev app/mcp_server.py` (Lesson 05's own inspector) to call
`search_quest_notes` for real, against a note you've actually added to
the seeded demo account through QuestLog's own UI. Confirm it returns a
real excerpt.

### Going live: what actually needs to change, checked honestly

This section is the "does this feature need anything new in
production" audit the master plan asks every capstone lesson to do —
performed for real, not assumed.

- **Containers (Module 10).** Nothing changes. `backend/Dockerfile` and
  `frontend/Dockerfile` package this app's own source code — this
  module's new files (`app/agent.py`, `app/routers/agent.py`, the
  frontend's `agentApi.ts`/`AgentChatPanel.tsx`/`AgentPage.tsx`) are
  ordinary application source, already covered by the exact same `COPY`
  instructions every earlier module's code was. `app/mcp_server.py` and
  `requirements-mcp.txt` are **not** copied into the production image at
  all, on purpose — see that file's own docstring: it's a standalone
  teaching artifact, never started by `uvicorn`, never a runtime
  dependency of the deployed app.
- **CI/CD (Module 11).** The pipeline's own test jobs need nothing new —
  `tests/test_agent.py` runs under the exact same `pytest -v` step every
  earlier module's tests already ran under, with the same
  `SECRET_KEY`-only environment (Module 08's own conftest.py reasoning),
  and no `ANTHROPIC_API_KEY` at all — because, exactly like every AI
  feature since Module 13, this one is fully mockable, never requiring a
  real key to test. The build/push/deploy jobs need no changes either —
  they build whatever's in `backend/`/`frontend/`, unconditionally.
- **Deploy configuration (Module 11's `render.yaml`) — a real, honest
  finding.** Checking this file for this lesson surfaced something
  genuinely missing, not hypothetical: `render.yaml` declared
  `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ENVIRONMENT`, `SENTRY_DSN`,
  and `CORS_ORIGINS` for `questlog-backend` — but never
  `ANTHROPIC_API_KEY`, despite every one of QuestLog's AI features,
  starting with Module 13's own quest-breakdown assistant, requiring it.
  A deploy from this file alone would have every AI feature (including
  this module's own agent) silently return `503 Service Unavailable`
  forever, with no loud failure at deploy time to point you at why. This
  module's own `render.yaml` fixes that gap, adding
  `- key: ANTHROPIC_API_KEY` / `sync: false` alongside the other secrets
  — go read that entry's own comment now for the full, stated reasoning.
  This is exactly the kind of check this lesson's own job is: not
  assuming past modules got everything right, actually looking.
- **Monitoring (Module 11's Sentry).** Nothing to add. `app/main.py`'s
  Sentry initialization (`sentry_sdk.init(...)`, gated on a real
  `SENTRY_DSN` being configured) instruments the whole FastAPI
  application generically, at the framework level — it has no per-route
  allowlist to update. An unhandled exception inside
  `app/routers/agent.py`'s own route, or anywhere in `app/agent.py`'s own
  loop, is captured automatically, exactly the same way an exception in
  any earlier module's route already was, with zero new configuration.

## Common mistakes & gotchas

- **Assuming a third copy of the same frontend SSE-parsing pattern is
  automatically wrong.** It's a real trade-off (see `agentApi.ts`'s own
  docstring) — worth naming and thinking about deliberately, not
  worth reflexively "fixing" by extracting an abstraction you haven't
  actually confirmed pays for itself yet.
- **Confusing `app/mcp_server.py`'s scope decisions with production
  readiness.** It's read-only and single-user *on purpose*, for a stated,
  honest reason — not a rough draft of a "real" multi-user MCP server you
  should assume is coming later in this course. If you build on this
  file for a real product, you'd need to solve per-connection
  authentication for real, which this file explicitly does not attempt.
- **Shipping a Blueprint/deploy config change without re-reading it
  end to end.** This lesson's own `render.yaml` fix was found by actually
  checking every existing `envVars` entry against what the running app
  requires, not by assuming Module 11 already got it right — the same
  "verify, don't assume" discipline this whole capstone lesson practices.

## How this connects

This is the last lesson of the course. Every concept from Modules 00
through 15 — HTTP, React, FastAPI, Postgres, auth, testing, Docker,
CI/CD, LLM APIs, RAG, and now agents — converges in this one feature.
`CHECKLIST.md` is your own final self-assessment before calling this
course complete; `project/BRIEF.md` is the capstone assignment that asks
you to extend and explain this feature in your own words, the way every
earlier module's own capstone already has.

## Quick self-check

1. Trace one SSE event type (your choice) from `app/agent.py`'s own
   `yield` statement, through `app/routers/agent.py`'s own SSE
   formatting, to the exact line in `AgentChatPanel.tsx` that reacts to
   it.
2. What real bug did this module's own first-draft frontend have around
   showing `sources`, and what test caught it?
3. State, precisely, `app/mcp_server.py`'s own two scope decisions
   (read-only; one hard-coded user) and the real reason behind each one.
4. What real gap did this lesson's own audit of `render.yaml` find, and
   why would a deploy from the *un-fixed* file have failed silently
   rather than loudly?
5. Name one thing about this feature's path to production that needed
   **zero** new configuration at all, and explain why — what about
   Module 10's or Module 11's own earlier design already covered it?
