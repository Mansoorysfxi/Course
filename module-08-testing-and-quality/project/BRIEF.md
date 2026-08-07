# Module 08 Capstone — QuestLog Gets a Real Test Suite (Review Project Milestone)

## What this is

**This is the course's first major milestone** — the master plan calls
Module 08's capstone the "Review Project": the point where everything
built across Modules 3–8 (HTML/CSS/JS, React, FastAPI, databases, auth,
and now testing) comes together in one, already-working, now genuinely
**verified** full-stack application. QuestLog's actual features do not
change in this module at all — Module 07's signup/login/quest CRUD is
exactly what's still here. What changes is that this exact application
now has a real, automated backend test suite (31 tests), a real
automated frontend test suite (17 tests), a linter and formatter for
each side of the stack, and a `pre-commit` configuration that runs all
of it automatically, every time anyone tries to commit.

Your job for this capstone is **not** to write QuestLog's test suite
from scratch — that's already done for you at `project/questlog/`
(copied forward from Module 07, with this module's tests/tooling added).
Your job is to **get everything running yourself, verify every piece
actually works, and be able to explain what each test checks and why**.
The hands-on *writing* practice for this module's concepts is
concentrated in Exercises 01–05, which have you write real tests
yourself, on progressively larger and more realistic code, ending with
Exercise 05's genuinely independent task: finding and closing a real gap
in this exact capstone's own test suite.

## Concepts this capstone uses

Every lesson in this module: the testing pyramid and why tests exist (01),
pytest fundamentals and fixtures (02), parametrize and mocking (03),
debugging technique (04), testing FastAPI endpoints with `httpx` +
`ASGITransport` (05), testing against a real (if temporary) database (06),
frontend testing with Vitest and React Testing Library (07), linters and
formatters — `ruff` and `prettier` (08), and pre-commit hooks tying all
of it together automatically (09).

## What to do

1. **Follow [`lessons/00-setup.md`](../lessons/00-setup.md)** if you
   haven't already — install this module's backend and frontend test
   tooling, `ruff`, `prettier`, and `pre-commit`.
2. **Get the backend's real test suite running, and read its output
   closely:**
   ```bash
   cd project/questlog/backend
   python -m venv .venv
   source .venv/Scripts/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   python -m pytest -v
   ```
   **Expected:** `31 passed`. Open `tests/test_auth.py` and
   `tests/test_quests.py` and, for at least five tests total, trace each
   one back to the exact real application code (in `app/routers/` or
   `app/repository.py`) it's checking — this is the same "read together"
   exercise Lessons 05–06 already walked you through; now do a few more
   on your own.
3. **Measure real coverage:**
   ```bash
   python -m pytest --cov=app --cov-report=term-missing
   ```
   Identify which files/functions have the lowest coverage, and — using
   Lesson 01's own warning in mind — decide, in your own written
   judgment (a sentence or two is enough), whether each low-coverage
   spot is a real gap worth closing or reasonably out of scope (e.g.
   `seed_if_empty`, which only ever runs once, at real startup, and is
   not reachable through this module's test setup at all — see
   Exercise 05's own note on exactly this).
4. **Get the frontend's real test suite running:**
   ```bash
   cd ../frontend
   npm install
   npm run test
   ```
   **Expected:** `Test Files  4 passed (4)` and `Tests  17 passed (17)`.
   Open `src/components/QuestForm.test.tsx` and
   `src/pages/QuestListPage.test.tsx` and, for at least three tests,
   explain in your own words what real component behavior each one
   checks, and whether it renders behavior a real user could actually
   observe (Lesson 07's central RTL philosophy) or reaches into
   something a real user never sees.
5. **Run the linters and formatters, by hand, against this exact
   codebase:**
   ```bash
   cd ../backend && ruff check app tests && ruff format --check app tests
   cd ../frontend && npx prettier --check . && npm run lint
   ```
   **Expected:** all four report clean (`All checks passed!`, `N files
   already formatted`, no prettier warnings, and oxlint reporting at
   most its two known, pre-existing "Fast refresh" warnings — see
   Lesson 08's own honest account of what `ruff` actually found in this
   codebase the first time it was ever run, and confirm none of those
   specific issues have reappeared).
6. **Install and run `pre-commit` for real:**
   ```bash
   cd ../.. # to project/questlog/
   pip install pre-commit    # into the backend's venv, or any Python environment on PATH
   pre-commit run --all-files
   ```
   **Expected:** every hook listed in `.pre-commit-config.yaml` reports
   `Passed`. If you're working inside a real Git repository, also run
   `pre-commit install` and make one small, harmless change (e.g. add a
   blank line somewhere) to confirm `git commit` genuinely triggers
   every hook automatically, without you running anything by hand.
7. **Break something on purpose, then watch a test catch it.** Pick one
   real behavior this test suite checks — for example,
   `app/repository.py`'s `get_quest` combining the id and owner-id check
   in one `WHERE` clause (Lesson 06) — and temporarily "break" it (e.g.
   change `get_quest` to look up a quest by id alone, ignoring
   `owner_id` entirely). Re-run `pytest -v` and confirm
   `test_one_user_cannot_get_another_users_quest_by_id` now **fails**,
   with a clear, readable message pointing at the actual wrong
   assertion. This is the single most concrete proof this module's whole
   subject actually delivers what Lesson 01 promised: a regression that
   would otherwise ship silently, caught immediately, automatically,
   with zero manual re-testing. **Revert your change** before continuing
   — `git diff`/`git checkout` (Module 00) if you're in a real repo, or
   just undo it by hand.
8. **Complete Exercises 01–05** if you haven't already — they're the
   hands-on component this capstone assumes is done, ending with
   Exercise 05's genuinely independent task against this exact codebase.

## Acceptance criteria

- [ ] The backend's real test suite passes in full (`31 passed`), run
      by you, on your own machine.
- [ ] The frontend's real test suite passes in full (`Tests 17 passed
      (17)`), run by you, on your own machine.
- [ ] `ruff check`, `ruff format --check`, `prettier --check`, and
      `oxlint` all report clean against this exact codebase.
- [ ] `pre-commit run --all-files` reports every hook `Passed`.
- [ ] You performed the "break something on purpose" step (step 7) for
      real, watched a specific real test fail with a specific real
      message, and reverted the change afterward — describe, in your own
      words, exactly which test caught it and why.
- [ ] For at least five backend tests and three frontend tests, you can
      explain, from memory or by re-reading the actual application code
      (not by re-reading the test's own comments), exactly what real
      behavior each one is checking.
- [ ] All 5 exercises are complete, including Exercise 05's own coverage
      verification.

## What to submit for review

When you say "check my module," point the AI at: your written judgment
from step 3 (which low-coverage areas are real gaps vs. reasonably out
of scope, and why), a short description of the "break something on
purpose" test you ran in step 7 and exactly what failed, and your
completed exercises' `solution/` files — Exercise 05's especially, since
it's this module's only fully independent one.

## Why this capstone is "run and verify" rather than "build from scratch"

The same reasoning every prior module's capstone has given, still true
here, and arguably more important for a testing-focused module
specifically: the actual hands-on test-*writing* practice for this
module's concepts (plain pytest fundamentals, fixtures, parametrize,
mocking, testing a real FastAPI endpoint, and finally an independent
gap-finding exercise) is concentrated in Exercises 01–05, each with a
real, runnable solution to check your own work against. This capstone's
job is different, and just as real: prove, with your own hands, that
this module's central promise — automated, repeatable, trustworthy
verification, replacing "click through it and hope" — genuinely holds
for the entire, real, full-stack application this course has been
building since Module 04, not just for small, isolated exercise code.
