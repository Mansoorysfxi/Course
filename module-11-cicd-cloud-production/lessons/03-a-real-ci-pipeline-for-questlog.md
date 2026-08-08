# Lesson 03 — A Real CI Pipeline for QuestLog

## What you'll learn

- How to read and explain `project/questlog/.github/workflows/ci-cd.yml`'s
  first two jobs (`backend-tests`, `frontend-tests`) line by line, as a
  direct, real application of Lesson 02's syntax.
- Why these two jobs run in parallel, and exactly what each one proves.
- How to watch a real test failure happen in CI, on purpose, and read the
  resulting logs to find exactly what broke.
- The specific, real reason `SECRET_KEY` needs a fresh value in this
  workflow's own `env:`, distinct from any value in your own `.env` file.

## Why this matters

This is where Lesson 02's syntax stops being abstract. QuestLog's backend
and frontend each already have a real, passing test suite (Module 08).
This lesson makes that test suite run **automatically, on every single
push**, so a regression is caught within minutes, by a machine, instead
of being discovered by you (or worse, by nobody, until a real user hits
it) days later.

## Prerequisites

- **Lesson 02** — every syntax element used here (`on:`, `jobs:`,
  `uses:`, `working-directory:`, `env:`, `cache:`) was taught there
  first.
- **Module 08's testing lessons** — this lesson runs, unmodified, the
  exact `pytest`/`vitest` commands and test files that module wrote.
- **Module 10's `frontend/package.json` `optionalDependencies` fix** —
  this lesson's `npm ci` step depends on that exact fix still being in
  place; see that module's own `lessons/08` if this feels unfamiliar.

## The concept, explained simply

Think of these two jobs as two separate, automated QA testers, working
at the same time, each responsible for one half of QuestLog: one
compiles and runs every backend Python test, the other type-checks,
builds, and runs every frontend test. Neither depends on the other
finishing first (Lesson 02's "jobs run in parallel" — there's no reason
the backend tester should sit idle waiting for the frontend tester, or
vice versa), and — this is the load-bearing part — **nothing later in
the pipeline (image builds, deploys) is even attempted unless BOTH
testers give a genuine thumbs-up.**

## The details

Open `project/questlog/.github/workflows/ci-cd.yml` now, and find the
`backend-tests` job:

```yaml
  backend-tests:
    name: Backend tests (pytest)
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repo
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.14"
          cache: "pip"
          cache-dependency-path: |
            backend/requirements.txt
            backend/requirements-dev.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Run pytest
        working-directory: backend
        env:
          SECRET_KEY: ci-test-secret-key-do-not-use-in-production
        run: python -m pytest -v

      - name: ruff lint
        working-directory: backend
        run: ruff check app tests

      - name: ruff format check
        working-directory: backend
        run: ruff format --check app tests
```

Every piece here is Lesson 02's syntax, applied: `python-version: "3.14"`
matches `backend/Dockerfile`'s own `python:3.14-slim` exactly (Module
10) — a deliberate, necessary match, not a coincidence: if this workflow
tested against a different Python version than the one the real Docker
image actually runs, a passing CI run would prove nothing meaningful
about what actually ships.

**Why `SECRET_KEY` needs a value here at all:** recall
`tests/conftest.py`'s own `os.environ.setdefault("SECRET_KEY", ...)`
line from Module 08 — it already provides a fallback value if none
exists in the environment, specifically so `pytest` works locally with
zero setup. This workflow's own `env:` line is technically redundant with
that fallback for THIS specific test suite... except relying on that
silently is fragile: if `conftest.py` ever changed to require
`SECRET_KEY` to be set by the caller (a real, plausible future change),
a CI run with no explicit `env:` would suddenly, mysteriously start
failing with a `pydantic_core.ValidationError`. Setting it explicitly,
here, in the workflow that's specifically responsible for proving "this
code works in a clean environment," is the more honest, more robust
choice — it makes this workflow's own assumptions about what the app
needs to run fully explicit, rather than silently borrowed from a test
fixture's own convenience fallback.

**Why `ruff check`/`ruff format --check` run here too, not just
`pytest`:** Module 08's own pre-commit hooks already run these locally —
but a pre-commit hook only runs on YOUR machine, at the moment YOU
commit. It's entirely possible to accidentally skip a hook (`git commit
--no-verify`, or simply not having hooks installed on a second machine)
and push code that was never actually checked. Running the exact same
checks in CI closes that gap completely: no push to `main` can ever
bypass these checks, no matter what happened (or didn't) on whoever's
own machine.

Now the `frontend-tests` job:

```yaml
  frontend-tests:
    name: Frontend tests (vitest)
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repo
        uses: actions/checkout@v7

      - name: Set up Node.js
        uses: actions/setup-node@v6
        with:
          node-version: "24"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Run vitest
        working-directory: frontend
        run: npm run test

      - name: Type-check and build
        working-directory: frontend
        env:
          VITE_API_BASE_URL: ""
        run: npm run build
```

`node-version: "24"` matches `frontend/Dockerfile`'s own `node:24-alpine`
exactly, for the same "CI should prove something true about what actually
ships" reason as the backend job's Python version. `npm ci`, never `npm
install` — Module 10's own explanation of this exact distinction applies
identically here: a CI run should fail loudly if `package.json` and
`package-lock.json` have drifted apart, never silently "fix" it by
rewriting the lockfile mid-run.

**Why `npm run build` runs here, in a job whose whole job is "run
tests":** `npm run build` is `tsc -b && vite build` (Module 10's own
observation) — running it here catches a REAL category of bug `npm run
test` alone would miss entirely: a TypeScript type error, or a build-time
failure, in code that happens to have zero test coverage. `vitest`
checks *behavior* for the code it actually tests; `tsc -b` checks that
the *entire* codebase still type-checks, tested or not. Both matter; this
job runs both. `VITE_API_BASE_URL: ""` matches the exact value Module
09's own manual deploy and Module 10's own Dockerfile both use, for the
exact same same-origin-relative-request reason — this build's output is
thrown away immediately after (this job's only job is to *prove* it
builds, not to ship the result — Lesson 08's `build-and-push-images` job
produces the real, shipped build, inside a container, separately).

### Watching this actually catch a real failure

**Try it yourself:** on a throwaway branch (never `main` directly — see
this lesson's own "Common mistakes" section for why), deliberately break
one backend test — open `backend/tests/test_auth.py` and change one
`assert response.status_code == 201` to `assert response.status_code ==
999`. Commit, push that branch, and open a pull request against `main`
(Lesson 02's `on: pull_request:` trigger). **Predict, before pushing,**
exactly which job will show a red X, and which will still show green.
Confirm, then read that failing job's own expanded log output — pytest's
own failure output (`assert 201 == 999`) should be visible directly in
GitHub's own UI, with zero need to reproduce the failure locally first to
know exactly what broke. Revert your change before merging anything.

## Common mistakes & gotchas

- **Testing a "break something" experiment directly on `main`.** Always
  use a separate branch and a pull request for this kind of intentional
  experiment — pushing straight to `main` (this pipeline's own deploy
  trigger, Lesson 08) means a deliberately broken test could, depending
  on exactly which check fails, still attempt later pipeline steps.
  Working on a branch and opening a PR is also simply the normal,
  professional way real teams use this exact CI setup day to day: tests
  run on the PR, a human (or, in a stricter setup, a required-check rule)
  reviews the green checkmark before merging.
- **A local `pytest`/`npm run test` passes, but the identical command
  fails in CI.** The single most common real cause: something present on
  your own machine (a locally installed system library, a cached file,
  an environment variable you set once months ago and forgot about) that
  the clean CI runner simply doesn't have — this is, precisely, CI doing
  its job correctly by exposing a "works on my machine" problem before it
  reaches anyone else.
- **Forgetting that `working-directory:` doesn't persist between steps**
  the way `cd` inside one long multi-line `run:` block would — each
  step's `working-directory:` (or lack of one) is independent; a step
  with no `working-directory:` runs from the repository's own root,
  regardless of what an earlier step's `working-directory:` was.

## How this connects

This lesson's two jobs are exactly the `needs: [backend-tests,
frontend-tests]` this module's Lesson 02 already showed —
`build-and-push-images` (Lesson 08) can't even start unless both of
these succeed. Lesson 04 shifts focus to *where* a passing build
actually gets shipped to.

## Quick self-check

1. Why do `backend-tests` and `frontend-tests` run as two SEPARATE jobs
   instead of one job with all the steps combined?
2. Why does this workflow set `SECRET_KEY` explicitly in its own `env:`,
   given that `tests/conftest.py` already has a fallback?
3. What real category of bug does the `frontend-tests` job's `npm run
   build` step catch that `npm run test` alone would miss?
4. Why does `python-version: "3.14"` in this workflow need to match
   `backend/Dockerfile`'s base image version, specifically — what would a
   mismatch actually risk?
5. If you deliberately broke a test on a feature branch and opened a pull
   request, which trigger in `on:` is responsible for this workflow even
   running at all for that PR?
