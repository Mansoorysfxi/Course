# Module 05 — Backend with Python (FastAPI)

**Phase:** 2 — Backend Engineering
**Estimated time:** 16–22 hours over one to two weeks (nine teaching lessons including setup, five exercises, and a capstone that wires a real backend to an existing frontend for the first time)
**Verified against (August 2026):** FastAPI **0.141.1** (confirmed via `https://pypi.org/pypi/fastapi/json`); Uvicorn **0.52.1** (confirmed via `https://pypi.org/pypi/uvicorn/json`); Pydantic **2.13.4** (confirmed via `https://pypi.org/pypi/pydantic/json` — installed automatically as a FastAPI dependency, pinned explicitly too since it's used directly). Every lesson's own header states exactly what was checked and when; see [`lessons/00-setup.md`](lessons/00-setup.md) for the full picture.

## What this module is

Modules 00–04 built a professional frontend (React + TypeScript + Tailwind + React Router) that, per `RUNNING_PROJECT.md`, has been holding QuestLog's data in local browser state, fetched through a mocked, fake `fetchQuests()` with no real server involved at all. This module builds QuestLog's first real backend: a Python web API, using **FastAPI**, that the frontend actually talks to over HTTP — the moment this course's running project stops being a convincing illusion of a client-server app and becomes a genuine one.

You'll learn what a backend framework actually does; routing, path/query parameters, and request bodies; **Pydantic** models and what validation really is, in real depth (the master plan calls this lesson out specifically); **dependency injection** and FastAPI's `Depends()`, fully explained rather than treated as magic; middleware; deliberate error handling and status codes (building directly on Module 02's vocabulary, not re-teaching it); and exactly what the automatically-generated `/docs` page and OpenAPI actually are. The capstone is a complete, in-memory CRUD API for quests — no database yet, that's Module 06 — tested with both `curl` (Module 02's own skill) and the interactive docs UI.

## What you'll be able to do after this module

- Explain precisely what a web framework does versus an ASGI server, and why FastAPI is built the way it is.
- Write routes using path parameters, query parameters, and request bodies, and explain exactly how FastAPI decides which is which.
- Design and validate Pydantic models with `Literal`, `Field`, `model_config`, `@field_validator`, and `Field(alias=...)` — and read a `422` validation error response fluently, field by field.
- Explain dependency injection as a general idea, then explain exactly what `Depends()` does mechanically, including sub-dependencies and per-request caching.
- Write your own middleware, and explain precisely how it differs from a dependency.
- Handle errors deliberately with `HTTPException`, custom exceptions and exception handlers, `response_model`, and correctly-chosen status codes.
- Explain what OpenAPI actually is (a specification, not a page), and use Swagger UI as a real, hands-on API-testing tool.
- Have built, from scratch, the **QuestLog API** — a real, working, in-memory CRUD backend — and connected Module 04's real frontend to it.

## Prerequisites

**Module 01, in full** — especially decorators/context managers (Lesson 10, since FastAPI's routing and dependency mechanisms are direct, working applications of exactly that mechanism), async/await (Lesson 11, since FastAPI route handlers are commonly `async def`), and type hints (Lesson 09, since this module is where type hints stop being purely advisory and start being the literal mechanism FastAPI uses to validate data). **Module 02, in full** — HTTP methods, status codes, headers, and `curl` are assumed throughout and never re-taught, only applied. **Module 04, in full**, especially its finished `project/questlog/` codebase — this module's capstone copies it forward and connects it to a real backend for the first time.

## Module structure

```
module-05-backend-fastapi/
├── README.md                                          ← you are here
├── lessons/
│   ├── 00-setup.md                                   ← new venv, install FastAPI + Uvicorn, run, verify, run frontend+backend together
│   ├── 01-what-a-backend-does-and-your-first-routes.md
│   ├── 02-path-and-query-parameters.md
│   ├── 03-request-bodies-and-pydantic-validation.md  ← the "big one" — validation explained deeply
│   ├── 04-dependency-injection-and-depends.md         ← Depends() fully opened up
│   ├── 05-middleware.md
│   ├── 06-error-handling-status-codes-and-responses.md
│   ├── 07-auto-docs-and-openapi.md
│   └── 08-building-the-questlog-api.md                ← puts every lesson together into one real API
├── exercises/
│   ├── 01-hello-world-and-path-params/                ← very easy
│   ├── 02-request-bodies-and-validation/              ← guided
│   ├── 03-dependency-injection/                       ← guided/independent
│   ├── 04-middleware-and-error-handling/              ← independent
│   └── 05-extend-the-quest-api/                       ← independent, a real routing gotcha included on purpose
├── project/
│   ├── BRIEF.md                                       ← the QuestLog API capstone brief
│   └── questlog/
│       ├── README.md                                  ← how frontend/ and backend/ relate
│       ├── frontend/                                  ← Module 04's app, copied forward, now calling the real API
│       └── backend/                                   ← the new FastAPI backend built in this module
└── CHECKLIST.md
```

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson fully, answer its self-check questions, do the matching exercise without peeking at the solution, then ask your AI session *"Review my solution for exercise 0N."* After all five exercises and the capstone are done, say *"Check my module"* for the full module-end review.

A note specific to this module: **you'll be running two servers at once from Lesson 00 onward** — this module's backend (port `8000` by default) and Module 04's frontend (port `5173` by default). Keep two terminal tabs/windows open throughout, per Lesson 00's own setup instructions.

## A note on the capstone

The Module 05 capstone (`project/BRIEF.md`) has you build the **QuestLog API**: a full CRUD backend for quests, in-memory only (a plain Python `dict` stands in for a database, deliberately, until Module 06), matching Module 04's existing `Quest` type field-for-field via Pydantic aliasing. Per `RUNNING_PROJECT.md`, `project/questlog/frontend/` is Module 04's exact finished codebase, copied forward, with its mocked data layer swapped for real HTTP calls — see `project/questlog/README.md` for precisely what changed and why, and `project/questlog/backend/README.md` for the new backend's own routes and how it was tested. Both halves were actually built and run while writing this module — see this module's own report/PROGRESS.md entry (once you've completed it) and `project/questlog/README.md`'s own "Verified while writing this module" section for exactly what was confirmed live versus by careful reading.
