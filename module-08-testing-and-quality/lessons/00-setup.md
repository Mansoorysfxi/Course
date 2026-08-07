# Lesson 00 — Setup: Installing This Module's Testing and Quality Tools

**Verified against (August 2026), by actually installing each one and
reading back the resolved version — not from memory:**

**Backend (Python, installed into `backend/.venv`):**

| Tool | Version | Source |
|---|---|---|
| `pytest` | **9.1.1** | resolved via `pip install`, confirmed against `https://pypi.org/pypi/pytest/json` |
| `pytest-asyncio` | **1.4.0** | same, `https://pypi.org/pypi/pytest-asyncio/json` |
| `httpx` | **0.28.1** | same, `https://pypi.org/pypi/httpx/json` |
| `aiosqlite` | **0.22.1** | same, `https://pypi.org/pypi/aiosqlite/json` |
| `pytest-cov` | **7.1.0** | same, `https://pypi.org/pypi/pytest-cov/json` |
| `ruff` | **0.16.1** | same, `https://pypi.org/pypi/ruff/json` |
| `pre-commit` | **4.6.1** | same, `https://pypi.org/pypi/pre-commit/json` |

**Frontend (Node, installed into `frontend/node_modules`):**

| Tool | Version | Source |
|---|---|---|
| `vitest` | **4.1.10** | resolved via `npm install`, confirmed against `https://www.npmjs.com/package/vitest` |
| `@vitest/coverage-v8` | **4.1.10** | same |
| `jsdom` | **24.0.0** (deliberately *not* the newest 30.x — see "Common mistakes & gotchas" below) | same |
| `@testing-library/react` | **16.3.2** | same |
| `@testing-library/jest-dom` | **7.0.0** | same |
| `@testing-library/user-event` | **14.6.3** | same |
| `prettier` | **3.9.6** | same |

Everything else this module touches (FastAPI, SQLAlchemy, React, Vite,
Tailwind, oxlint...) is **unchanged from Module 07** — this lesson does
not re-verify those; see that module's own `lessons/00-setup.md` and
`README.md` if you need a refresher.

## What you'll learn

- How to install this module's backend testing tools (`pytest`,
  `pytest-asyncio`, `httpx`, `aiosqlite`, `pytest-cov`) into the *same*
  backend project Module 07 finished, without touching its runtime
  dependencies at all.
- How to install this module's frontend testing tools (`vitest` and
  React Testing Library's small family of packages) into the *same*
  frontend project.
- How to install `ruff` (Python) and `prettier` (JS/TS) — this module's
  two new **linter**/**formatter** tools — and `pre-commit`, the tool that
  runs both automatically.
- How to verify every piece actually works, and what to do about two real,
  current environment gotchas this course's own author hit while writing
  this exact lesson (a broken native-binding install on some Windows
  setups, and an incompatibility between very recent `jsdom` releases and
  older Node.js versions) — included here because you may hit them too.

## Why this matters

Every tool in this lesson exists to answer one question this whole module
is about: **"how do I know my code actually works, without checking by
hand every single time?"** None of these tools change what QuestLog
*does* — a learner who skipped this entire module would still have a
working app. What changes is confidence, and the *speed* of confidence:
once these tools are installed, checking "did I just break anything?"
takes seconds (`pytest`, `npm run test`) instead of manually clicking
through every page and typing every `curl` command again, the way Modules
05–07 verified things.

## Prerequisites

- **Module 07 in full**, especially its own `lessons/00-setup.md` — this
  lesson assumes `module-08-testing-and-quality/project/questlog/backend`
  already has a working Python virtual environment the way Module 07's
  did, and that PostgreSQL is installed (Module 06). You will **not**
  need PostgreSQL running for this module's actual tests to pass — see
  `lessons/06-testing-with-a-database.md` for why — but it should still
  be installed, because the app itself (outside of tests) still uses it.
- **Module 01's venv/pip lesson** for what a virtual environment is and
  what `pip install` actually does.
- **Module 04's `npm install` experience** for the Node/npm side.

## The concept, explained simply

Think of this the way you'd think about adding a **unit-testing framework
and a static-analysis pass to an Unreal Engine project**: the game itself
doesn't need Google Test or a linter to run, but no serious studio ships
without them, because both catch entire categories of mistake — a
regression in gameplay logic, a mismatched brace, an inconsistent
indentation style across a team — *before* a human has to notice them by
playing the game or reading a diff by eye. Every tool this lesson installs
falls into exactly one of two buckets:

1. **Tools that run your code and check the answer** — `pytest` (Python),
   `vitest` (JavaScript/TypeScript). These are **test runners**: programs
   whose entire job is finding every function you've written that's
   *labeled* as a test, running it, and reporting which ones behaved as
   expected and which didn't.
2. **Tools that read your code without running it, looking for problems**
   — `ruff` and `prettier`. These are a **linter** and a **formatter**
   (defined properly in `lessons/08-linters-and-formatters.md`) — think of
   them as an extremely fast, extremely literal-minded code reviewer that
   never gets tired of pointing out the same fifty small things.

`pre-commit` is the glue: a small framework that runs *all* of the above,
automatically, every time you try to `git commit` — so none of this ever
depends on a human remembering to run it by hand.

## The details

### Step 1 — Re-verify Module 07's setup still works

Rule 8: never assume a tool from an earlier module is still configured.

```bash
cd module-08-testing-and-quality/project/questlog/backend
python -m venv .venv
```

Wait — Module 07's `lessons/00-setup.md` already had you create a
`.venv` inside `module-07-auth-security/project/questlog/backend`. This
module's `backend/` folder is a **fresh copy forward** (per
`RUNNING_PROJECT.md`'s "each module's starter code is a copy of the
previous module's finished solution" convention) — copies of files, but
**not** a copy of that `.venv` folder itself (a virtual environment is
never copied between folders; it's regenerated fresh every time, exactly
like Module 01 and every setup lesson since have had you do). So yes,
run the command above for real, here, in *this* module's `backend/`
folder.

```bash
source .venv/Scripts/activate
```

**Expected:** `(.venv)` appears at the start of your prompt.

### Step 2 — Install the app's own runtime dependencies (unchanged)

```bash
pip install -r requirements.txt
```

**Expected:** the same `fastapi`, `sqlalchemy`, `bcrypt`, `pyjwt`, and so
on that Module 07 already pinned, with no version changes at all.

### Step 3 — Install this module's new backend dev/test tools

This module adds a **second** requirements file,
`requirements-dev.txt`, deliberately separate from `requirements.txt`:

```bash
pip install -r requirements-dev.txt
```

**Line by line, `requirements-dev.txt`:**
```
pytest==9.1.1
pytest-asyncio==1.4.0
pytest-cov==7.1.0
httpx==0.28.1
aiosqlite==0.22.1
ruff==0.16.1
```
- `pytest` — the test runner itself. See `lessons/02-pytest-fundamentals-and-fixtures.md`.
- `pytest-asyncio` — teaches `pytest` how to run `async def test_...`
  functions at all. Without it, `pytest` would try to call an `async def`
  test function as if it were a normal one, get back a coroutine object
  instead of a real pass/fail result, and silently report the test as
  passing without ever actually running its body — a genuinely nasty trap
  this lesson's "Common mistakes & gotchas" section covers.
- `pytest-cov` — measures **coverage**: which lines of your actual
  application code ran at all while the test suite executed. See
  `lessons/02-pytest-fundamentals-and-fixtures.md`'s coverage box.
- `httpx` — the HTTP client this module's tests use to make real requests
  into the FastAPI app, without a real network socket. See
  `lessons/05-testing-fastapi-endpoints.md`.
- `aiosqlite` — lets SQLAlchemy's *async* engine talk to SQLite. See
  `lessons/06-testing-with-a-database.md` for why this module's tests use
  SQLite at all, instead of the real Postgres Module 06/07 use.
- `ruff` — the linter/formatter. See `lessons/08-linters-and-formatters.md`.

**Why a second file, instead of just adding these to `requirements.txt`?**
Because a real, deployed copy of this API (which is exactly what happens
starting Module 09) never needs `pytest` installed at all — it's a
development-only tool. Keeping the two files separate means a production
install (`pip install -r requirements.txt`) stays small and never
installs test tooling it will never use, while a developer's machine
installs both.

**Expected output (abbreviated):** lines ending in `Successfully installed
pytest-9.1.1 pytest-asyncio-1.4.0 pytest-cov-7.1.0 httpx-0.28.1
aiosqlite-0.22.1 ruff-0.16.1` alongside whatever their own dependencies
pull in (e.g. `iniconfig`, `pluggy`, `coverage`).

### Step 4 — Confirm pytest runs (even with zero tests written yet)

```bash
python -m pytest --version
```
**Expected:** a line like `pytest 9.1.1`.

### Step 5 — Install this module's new frontend dev/test tools

```bash
cd ../frontend
npm install
npm install --save-dev vitest @vitest/coverage-v8 jsdom@24.0.0 \
  @testing-library/react @testing-library/jest-dom @testing-library/user-event \
  prettier
```

**Line by line:**
- `npm install` (no arguments) first — installs everything Module 07's
  `package.json` already listed (React, Vite, Tailwind, React Router,
  TypeScript, oxlint), exactly like re-verifying Step 1 did for the
  backend.
- `vitest` — the test runner. See `lessons/07-frontend-testing-with-vitest-and-rtl.md`.
- `@vitest/coverage-v8` — Vitest's own coverage measurement, using the
  same underlying engine (V8, the JavaScript engine inside Chrome and
  Node.js itself) your code already runs on — no separate instrumentation
  step needed.
- `jsdom` — a full, plain-JavaScript **implementation** of a browser's
  DOM (Document Object Model — Module 03's term for the tree of objects a
  real browser builds out of your HTML) that runs inside plain Node.js,
  with no actual browser window at all. This is what lets a component
  that calls `document.getElementById(...)` or renders a real `<button>`
  run inside a test at all. **Pinned to exactly `24.0.0`** here — see
  "Common mistakes & gotchas" below for why this course pins an *older*
  version on purpose.
- `@testing-library/react` — utilities for rendering a React component
  into that fake DOM and finding things inside it the way a real user
  would (by visible text, by label, by role) — not by reaching into React
  internals. See `lessons/07-frontend-testing-with-vitest-and-rtl.md`.
- `@testing-library/jest-dom` — adds extra, readable assertions
  (`toBeInTheDocument()`, `toHaveValue()`, `toBeChecked()`) on top of
  Vitest's own `expect`.
- `@testing-library/user-event` — simulates real user interactions
  (typing, clicking, selecting a dropdown option) far more realistically
  than firing raw DOM events by hand.
- `prettier` — the formatter. See `lessons/08-linters-and-formatters.md`.

**Expected output (abbreviated):** `added N packages` for each command,
with no `npm error` lines.

### Step 6 — Wire up npm scripts for the new tools

Module 07's `frontend/package.json` only had `dev`/`build`/`lint`/
`preview`. This module adds:

```json
"test": "vitest run",
"test:watch": "vitest",
"test:coverage": "vitest run --coverage",
"format": "prettier --write .",
"format:check": "prettier --check ."
```

**Line by line:** `vitest run` runs every test file once and exits — the
right mode for CI, and for this lesson's "verify your setup" section
below. Plain `vitest` (no `run`) starts **watch mode**: it stays open,
re-running only the tests affected by whatever file you just saved — the
mode you'll actually use while working through the exercises. `--coverage`
adds a coverage report on top of a normal run. `format`/`format:check`
mirror Python's `ruff format`/`ruff format --check` pairing exactly — one
command changes files, the other only reports what *would* change,
useful in `pre-commit` (`lessons/09-pre-commit-hooks.md`) where you never
want a hook to silently rewrite a file you haven't reviewed yet without
telling you.

### Step 7 — Install `pre-commit` and generate its own config

`pre-commit` is a Python tool, so it lives in the backend's venv:

```bash
cd ../backend
pip install pre-commit
```

This module's `project/questlog/.pre-commit-config.yaml` is already
written for you (see `lessons/09-pre-commit-hooks.md` for what every line
of it does) — from the `project/questlog/` folder (one level above both
`backend/` and `frontend/`):

```bash
cd ..
pre-commit install
```

**Expected:** `pre-commit installed at .git/hooks/pre-commit`.

**A note if this errors with "not a git repository":** `pre-commit
install` writes a hook file *inside* a `.git` folder, so it only works
inside a real Git repository. If you're working through this module
inside a clone of the whole course repository, you likely already have
one at the repository's root — run `pre-commit install` from there
instead, or skip this one step and use `pre-commit run --all-files`
directly (below) any time you want to check everything by hand without
installing the automatic Git hook at all.

## Verify your setup

**Backend:**
```bash
cd module-08-testing-and-quality/project/questlog/backend
python -m pytest --version
python -m ruff --version
```
**Expected:** `pytest 9.1.1` and `ruff 0.16.1` (or later patch versions —
see this lesson's header for exactly what was verified and when).

**Frontend:**
```bash
cd ../frontend
npx vitest --version
npx prettier --version
```
**Expected:** version numbers, no errors.

**Both, together — run this module's actual, already-written test
suites** (you haven't written any tests yourself yet; this just proves
the *tools* work against the ones this module ships in
`project/questlog/`):
```bash
cd ../backend && python -m pytest -q
```
**Expected:** a line ending in `31 passed in <a few> seconds`.
```bash
cd ../frontend && npm run test
```
**Expected:** `Test Files  4 passed (4)` and `Tests  17 passed (17)`.

If both of those match, every tool in this lesson is installed correctly
and working against real code — you're ready for Lesson 01.

## Common mistakes & gotchas

- **`ModuleNotFoundError: No module named 'pytest'`.** The venv isn't
  active — same root cause as every prior module's version of this
  error. Check for `(.venv)` at the start of your prompt.
- **An `async def test_...` function silently "passes" even though its
  body clearly does something wrong.** `pytest-asyncio` isn't installed,
  or this backend's `pyproject.toml` is missing its `asyncio_mode =
  "auto"` setting (already present in this module's `backend/pyproject.toml`
  — check it's actually there if you copied this project by hand instead
  of using the one already in `project/questlog/`). Without either,
  plain `pytest` treats an `async def` test as a *synchronous* function
  that happens to return a coroutine object — calling it "succeeds" (no
  exception was raised creating the object), so the test is marked
  passed, and the actual test body — the part with your real
  assertions — never executed at all. `lessons/02-pytest-fundamentals-and-fixtures.md`
  revisits this specific trap.
- **`Error: Cannot find native binding` when running `npx vitest` on
  Windows**, mentioning `rolldown` and a bug about npm's optional
  dependencies (`github.com/npm/cli/issues/4828`). This is a real,
  current npm bug (hit and fixed while writing this exact lesson, August
  2026): npm sometimes fails to install the correct **platform-specific
  native binary** a package needs (here, Vite 8's Rust-based bundler,
  `rolldown`, ships a separate compiled binary per operating
  system/architecture combination). Fix: delete `node_modules` *and*
  `package-lock.json`, then `npm install` again. If it still fails,
  install the missing platform package directly and explicitly — for a
  64-bit Windows machine:
  ```bash
  npm install --save-dev @rolldown/binding-win32-x64-msvc
  ```
  The same underlying bug can also affect `oxlint` (Module 04's linter)
  on some setups — the fix is the same shape: `npm install --save-dev
  @oxlint/binding-win32-x64-msvc`.
- **`Error: require() of ES Module ... not supported` mentioning
  `html-encoding-sniffer` or `@csstools/css-calc`, when running Vitest
  tests for the first time.** This is *not* a mistake in your code at
  all — it's a real, current incompatibility (also hit while writing this
  lesson) between the newest `jsdom` releases (30.x) and Node.js versions
  older than 20.19/22.12. Recent `jsdom` versions pulled in a couple of
  their own dependencies that are **ESM-only** (ECMAScript Modules — the
  modern, `import`/`export`-based module system, as opposed to the older
  CommonJS `require()`/`module.exports` this course's own backend and
  frontend tooling still uses in plain `.js` config files) — and Node
  only learned how to `require()` an ESM file *synchronously* starting
  with those specific versions. Two real fixes: (1) upgrade Node.js past
  20.19/22.12 (`node --version` to check yours), or (2) if you can't
  upgrade Node right now, pin `jsdom` to an older version whose own
  dependencies are still plain CommonJS — this course's own
  `package.json` deliberately pins `jsdom` to exactly `24.0.0` (not the
  newest `30.x`) for exactly this reason. If you ever bump this pin
  yourself, re-run the full test suite immediately afterward.
- **`npx oxlint` (or any oxlint-based script) reports the same "Cannot
  find native binding" error as the `rolldown` gotcha above.** Same root
  cause, same fix — see that bullet.
- **`pre-commit install` fails with "not a git repository".** See Step 7's
  note above.

## How this connects

Every lesson from here on assumes these tools are installed and working.
Lesson 01 starts with no code at all (the conceptual "why tests, and the
testing pyramid" material) — Lesson 02 is the first lesson to actually
run `pytest` against a test you write yourself.

## Quick self-check

1. Why does this module use a separate `requirements-dev.txt` instead of adding `pytest` etc. directly to `requirements.txt`?
2. What specifically goes wrong if you write an `async def test_...` function but `pytest-asyncio` isn't installed (or `asyncio_mode` isn't configured)? Why does it fail silently instead of with an obvious error?
3. What is `jsdom`, in one sentence, and why does a React Testing Library test need it at all?
4. Why does this course's `package.json` pin `jsdom` to exactly `24.0.0` instead of letting `npm install` pick the newest version?
5. What are the two broad "buckets" of tool this lesson installs, and which bucket does `pre-commit` itself fall into — or does it fall into neither?
