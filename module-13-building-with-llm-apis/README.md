# Module 13 — Building with LLM APIs

**Phase:** 4 — AI Engineering & Agents
**Estimated time:** 14-18 hours (mostly reading and hands-on scripting,
plus a genuinely small amount of real API spend — see `lessons/00-setup.md`)
**Verified against (August 2026):** `anthropic` Python SDK `0.121.0`
(PyPI, released August 7, 2026); Claude Haiku 4.5 pricing ($1.00/million
input tokens, $5.00/million output tokens) and structured-output model
support (confirmed current for `claude-haiku-4-5`); the SDK's built-in
automatic retry behavior (connection errors, 408/409/429/5xx, up to
`max_retries=2` by default). Every fact above was checked with a live web
fetch of Anthropic's own current documentation or PyPI while writing this
module, on August 9, 2026 — see each lesson's own header table for the
specific source and date.

## What this module is

Module 12 taught the *concepts* underneath every LLM — tokens,
embeddings, context windows, sampling, prompt engineering — entirely with
free, local, offline tools. This module is where those concepts become
**API mechanics**: real requests, real streaming, real structured output,
real tool-use round-trips, real error handling, and a real, live-tested
feature added to QuestLog itself. This is the first module since Module
04 to add a genuinely new *kind* of capability to the running project,
not just change how it's built, run, or deployed.

**QuestLog gains its first real AI feature in this module:** given one of
the player's own quests, an assistant proposes 2-4 concrete sub-quests,
checking the player's other quest titles first so it doesn't suggest a
duplicate — streamed live to the React frontend. See
`lessons/07-building-questlogs-ai-assistant-backend.md` and
`lessons/08-building-questlogs-ai-assistant-frontend.md` for the complete
walkthrough, and `project/questlog/`'s own code for the real,
already-tested implementation (46 backend tests, 22 frontend tests, all
passing with no real API key required).

## What you'll be able to do after this module

- Make a real Anthropic API call from scratch, explain every parameter in
  the request, and read every field in the response — including real
  token-usage accounting.
- Stream a response token by token, in both a plain script and inside an
  async FastAPI route, and explain exactly what Server-Sent Events are
  underneath the SDK's convenience helpers.
- Constrain a model's response to a JSON Schema you define, validate it
  again with Pydantic, and explain honestly why both steps matter.
- Explain and implement the full tool-use round-trip from memory: how a
  model asks for a tool, what your code does with that request, and how
  the result gets back to the model — including handling more than one
  tool call in the same turn.
- Handle real API failures correctly: which ones the SDK already retries
  for you, which ones you should never retry, and how a "refusal" is a
  fundamentally different situation from an exception.
- Reason concretely about what a real AI feature costs, and control it.
- Build a small, honest eval harness for an AI feature, using a golden
  set and plain, deterministic checks — no framework required.
- Explain, end to end, exactly how QuestLog's own AI assistant feature
  works, because you can read (and did read) every line of its real,
  tested implementation.

## Prerequisites

- **Module 12 in full** — this module assumes fluency with tokens,
  context windows, sampling/temperature, and prompt-engineering technique
  (system prompts, few-shot, chain-of-thought, asking for structured
  output). None of that is re-taught here.
- **Module 11's finished QuestLog codebase** — this module's capstone
  (Lessons 07-08) extends that exact backend/frontend.
- **Module 01's async/await lesson** — this module's streaming and
  FastAPI-integration material uses `async`/`await` throughout.
- **Module 05's Pydantic material** and **Module 08's pytest/mocking
  material** — structured outputs and this module's whole approach to
  testing an AI feature both build directly on these.

## A real API key is genuinely needed this time

Unlike Module 12, this module's core material — every exercise, and the
capstone — needs a real, live Anthropic API key to run for real; there is
no free, local substitute for calling a real hosted model. Read
`lessons/00-setup.md` first: it states plainly, with a real, worked
calculation, that running every exercise in this module several times
over realistically costs well under a quarter, total, and frames getting
a key now as groundwork you'll reuse in Modules 14-15, not a one-off
expense. If you'd rather not spend anything yet, every lesson's live-call
examples are honestly labeled "a response along these lines" so you can
still read, understand, and predict behavior without running anything —
exactly the dry-run path Module 12's own Lesson 07 already established.

## Module structure

```
module-13-building-with-llm-apis/
├── README.md                                                    ← you are here
├── lessons/
│   ├── 00-setup.md                                                ← the API key, the SDK, real cost
│   ├── 01-calling-the-anthropic-api.md                              ← messages, roles, token counting
│   ├── 02-streaming-responses.md                                      ← SSE, .stream(), sync and async
│   ├── 03-structured-outputs-with-pydantic.md                          ← output_config.format + Pydantic
│   ├── 04-tool-use-and-function-calling.md                                ← the full round-trip, minutely
│   ├── 05-error-handling-retries-and-cost-management.md                     ← failures, retries, real cost
│   ├── 06-evaluating-ai-features.md                                           ← golden sets, simple eval harnesses
│   ├── 07-building-questlogs-ai-assistant-backend.md                            ← the capstone backend, explained
│   └── 08-building-questlogs-ai-assistant-frontend.md                             ← the capstone frontend, explained
├── exercises/
│   ├── 01-first-api-call/                                         ← easy
│   ├── 02-streaming-story-generator/                                ← guided
│   ├── 03-structured-quest-extractor/                                 ← guided
│   ├── 04-tool-use-quest-line-lookup/                                   ← independent
│   └── 05-eval-harness-for-breakdown/                                     ← independent
├── project/
│   ├── BRIEF.md                                                    ← capstone: verify & extend the AI assistant
│   └── questlog/                                                     ← QuestLog, copied forward from Module 11,
│       ├── backend/app/ai_assistant.py                                 ← NEW: the whole feature's real logic
│       ├── backend/app/routers/quests.py                                 ← NEW: one route, reusing everything else
│       ├── backend/tests/test_ai_assistant.py                              ← NEW: 7 tests, no real key required
│       ├── frontend/src/api/aiApi.ts                                         ← NEW: SSE consumption from the browser
│       ├── frontend/src/components/QuestBreakdownPanel.tsx                     ← NEW: the streaming UI
│       └── frontend/src/components/QuestBreakdownPanel.test.tsx                  ← NEW: 5 tests, fully mocked
└── CHECKLIST.md
```

Read the lessons in order — each one is a real prerequisite for the next,
and Lessons 07-08 assume every technique in Lessons 01-06 without
re-explaining any of them. Exercises 01-05 go from "almost impossible to
fail if you read Lesson 01" to "given a scenario and a fake dataset,
build the whole thing yourself" — see each exercise's own
`INSTRUCTIONS.md` for its specific difficulty and hints.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without looking
at its solution, ask for a review, revise if needed, then move on. Once
all five exercises are done, work through `project/BRIEF.md`.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's `project/questlog/` is
Module 11's finished, deployed QuestLog, copied forward, with
`backend/app/` and `frontend/src/` each changed only for this module's
own new, documented AI-assistant feature — see Lessons 07-08 for the
complete, file-by-file account of exactly what changed and why.
