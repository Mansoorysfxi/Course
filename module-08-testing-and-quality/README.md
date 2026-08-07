# Module 08 — Testing & Software Quality

**Phase:** 2 — Backend Engineering (closing phase)
**Estimated time:** 16–20 hours
**Verified against:** `pytest` 9.1.1, `pytest-asyncio` 1.4.0, `httpx` 0.28.1,
`aiosqlite` 0.22.1, `pytest-cov` 7.1.0, `ruff` 0.16.1, `pre-commit` 4.6.1
(all confirmed via `pip install` + `pip freeze`, August 2026); `vitest`
4.1.10, `@testing-library/react` 16.3.2, `@testing-library/jest-dom`
7.0.0, `@testing-library/user-event` 14.6.3, `jsdom` 24.0.0 (deliberately
pinned below the newest 30.x — see `lessons/00-setup.md`), `prettier`
3.9.6 (all confirmed via `npm install` + reading `package.json`, August
2026). FastAPI, SQLAlchemy, React, Vite, Tailwind, and every other tool
from Modules 04–07 are unchanged.

## This module is a milestone — the "Review Project"

The master plan for this course flags Module 08 explicitly: **"Full
stack app combining Modules 3–8 ... first major milestone."** Every
module through Module 07 added a genuinely new piece of QuestLog
(HTML/CSS/JS fundamentals, React, FastAPI, Postgres, auth). This module
adds no new user-facing feature at all — instead, it's where you step
back, install real testing and code-quality tooling, and prove, with
your own hands, that the entire application built across those five
modules actually works, correctly, and keeps working as it changes.
Treat this module with the same care you'd give a real checkpoint at
work: this is exactly the moment a real team would stop, write tests for
what exists, and set up the automated guardrails that make everything
built afterward safer to change.

## What this module is

Through Module 07, QuestLog was verified entirely by hand — `curl`
commands, the FastAPI `/docs` UI, clicking through the real React app.
That works, but it's slow, it's easy to forget a case, and it has to be
redone by a human every single time. This module teaches **why**
automated tests exist and where they fit (the testing pyramid), **how**
to write them properly in Python with `pytest` (fixtures, parametrize,
mocking — explained completely from scratch, including what a mock
actually *is*), how to test a real FastAPI application (including
against a real, if temporary, database), how to test a React frontend
with Vitest and React Testing Library, general debugging technique, and
finally the tooling (`ruff`, `prettier`, `pre-commit`) that keeps code
correct and consistent automatically, on every single commit.

## What you'll be able to do after this module

- Explain the testing pyramid (unit/integration/end-to-end) and place
  any given test correctly within it, with real reasoning, not just a
  label.
- Write real `pytest` tests using fixtures, `pytest.raises`, and
  `@pytest.mark.parametrize` — and explain exactly how `pytest`'s
  dependency-injection-by-parameter-name mechanism works, with no
  hand-waving.
- Explain what a mock is, from scratch, and use `unittest.mock.patch`
  and `pytest`'s `monkeypatch` correctly — including recognizing the
  single most common mocking mistake (patching the wrong path).
- Test a real FastAPI application's endpoints with `httpx.AsyncClient` +
  `ASGITransport`, with no real network socket involved, and override a
  FastAPI dependency to substitute a test database for a real one.
- Justify, with real research and an honest cost/benefit accounting, a
  specific test-database strategy (this module: in-memory SQLite) for a
  real async FastAPI + SQLAlchemy application.
- Test React components and pages with Vitest and React Testing
  Library, following RTL's "test behavior, not implementation"
  philosophy, including `vi.mock`, `userEvent`, and the `getBy`/`queryBy`/
  `findBy` query distinction.
- Use a systematic debugging loop (`pytest -k`/`--lf`/`--pdb`,
  `breakpoint()`, VS Code's debugger, `console.log`/`debugger`/
  `screen.debug()`) instead of only rereading code and guessing.
- Configure and run `ruff` (Python) and `prettier` (JS/TS) deliberately,
  with a narrow, explicit rule set rather than an unexamined "enable
  everything."
- Read, understand, and extend a real `.pre-commit-config.yaml`,
  including the trade-off between managed and `local`/`system` hooks and
  the trade-off of running a full test suite inside a hook at all.

## Prerequisites

Modules 04–07 in full — this module's tests and exercises are written
directly against QuestLog's real, current React frontend and FastAPI/
Postgres/JWT backend, exactly as Module 07 left them. Module 01's
functions, exceptions, and `async`/`await` fundamentals; Module 00's
"reading errors and stack traces" lesson, directly built on by Lesson 04.

## Module structure

```
module-08-testing-and-quality/
├── README.md                                    ← you are here
├── lessons/
│   ├── 00-setup.md                              ← install pytest/httpx/vitest/RTL/ruff/prettier/pre-commit
│   ├── 01-why-tests-and-the-testing-pyramid.md
│   ├── 02-pytest-fundamentals-and-fixtures.md
│   ├── 03-parametrize-and-mocking.md
│   ├── 04-debugging-techniques.md
│   ├── 05-testing-fastapi-endpoints.md
│   ├── 06-testing-with-a-database.md
│   ├── 07-frontend-testing-with-vitest-and-rtl.md
│   ├── 08-linters-and-formatters.md
│   └── 09-pre-commit-hooks.md
├── exercises/
│   ├── 01-first-pytest-tests/                    ← easy — pure functions, almost impossible to fail if the lesson was read
│   ├── 02-fixtures-and-parametrize/               ← guided
│   ├── 03-mocking/                                 ← guided, more independent
│   ├── 04-testing-a-fastapi-endpoint/               ← guided, leaning independent
│   └── 05-independent-coverage/                      ← independent — find and close a real gap in this exact capstone
├── project/
│   ├── BRIEF.md                                       ← capstone: run, verify, and understand QuestLog's real test suite
│   └── questlog/                                       ← QuestLog, copied forward from Module 07, now with a real test suite + tooling
│       ├── frontend/                                     ← + Vitest, RTL, jsdom, prettier, 4 real test files (17 tests)
│       ├── backend/                                       ← + pytest, pytest-asyncio, httpx, ruff, 3 real test files (31 tests)
│       └── .pre-commit-config.yaml                         ← wires ruff, prettier, oxlint, and both test suites together
└── CHECKLIST.md
```

Read the lessons in order. Lesson 00's setup is not optional — every
later lesson assumes the tools it installs are already working. Lessons
01–04 build the general testing/debugging foundation, mostly with small,
standalone examples; Lessons 05–07 apply that foundation to QuestLog's
own real backend and frontend; Lessons 08–09 close with the code-quality
tooling that ties everything together automatically.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without
looking at its solution, ask for a review, revise if needed, then move
on. This module's exercises go from very easy (Exercise 01, testing pure
functions with no setup at all) to fully independent (Exercise 05,
finding and closing a real, verified gap in this exact capstone's own
test suite) — do them in order.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's `project/questlog/`
is Module 07's finished, authenticated QuestLog, copied forward and
given a real, genuinely passing backend test suite (31 tests), a real,
genuinely passing frontend test suite (17 tests), `ruff`/`prettier`
configured and clean, and a working `.pre-commit-config.yaml` — every
one of these was actually installed and actually run while this module
was written, not just described; see `project/questlog/README.md` and
this module's own `project/BRIEF.md` for the honest, complete account of
what was verified. This exact, now-tested codebase is what Module 09
begins deploying.
