# Exercise 05 — Independent: Test a Real, Untested Piece of QuestLog

**Difficulty:** Independent — the fullest exercise in this module, and
the last one before the capstone. No fixture or test file is given to
you beyond what this module's own capstone already had; you're finding
and closing a real gap yourself.

## Concepts this exercise uses (all taught in the lessons named)

Everything from this module's earlier lessons and exercises, applied
together: fixtures (`lessons/02-pytest-fundamentals-and-fixtures.md`),
parametrize if you choose to use it (`lessons/03-parametrize-and-mocking.md`),
testing a real FastAPI endpoint with `httpx.AsyncClient` + `ASGITransport`
(`lessons/05-testing-fastapi-endpoints.md`), and this module's own
`db_session`/SQLite test-database setup (`lessons/06-testing-with-a-database.md`)
— all of it already wired up for you in `starter/backend/tests/conftest.py`,
copied straight from this module's real capstone.

## The real gap this exercise asks you to close

`starter/backend/` is a full, working copy of this module's own real,
finished QuestLog backend — including its existing test suite
(`tests/test_auth.py`, `tests/test_quests.py`, `tests/test_security.py`),
all already passing. **Run them first, before changing anything, to
confirm this for yourself:**

```bash
cd starter/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest -v
```
**Expected:** `31 passed`.

Now look closely at `app/repository.py`'s `list_quests` function — it
accepts `done`, `priority`, and `quest_line` query-parameter filters
(wired up in `app/routers/quests.py`'s `GET /api/quests` route) — and at
`quest_line_stats`, which groups quests by quest line and counts totals
and done-counts per line. **Neither of these is actually tested at all**
in this module's existing `tests/test_quests.py` — check for yourself:
search that file for `params=` or `"/stats"` and confirm how little (if
anything) it actually exercises either piece. Confirm this with real
coverage numbers:

```bash
python -m pytest --cov=app.repository --cov-report=term-missing
```
**Expected (verified while writing this exercise):** `app/repository.py`
at **45% coverage**, with the `Missing` column explicitly listing lines
`121, 123, 125` — the exact three `if done is not None: / if priority is
not None: / if quest_line is not None:` branches inside `list_quests`
that filtering, by definition, needs to exercise, and that no existing
test currently reaches at all.

## What to do

Create a new test file, `starter/backend/tests/test_quest_filters_and_stats.py`,
and write tests covering:

1. **Filtering by `done`** — create quests in both states, filter by
   `done=true`, then `done=false`, and confirm each response contains
   exactly the quests you expect.
2. **Filtering by `priority`** — same idea, for at least one specific
   priority value.
3. **Filtering by `quest_line`** — same idea, for one specific quest
   line name.
4. **Combining two filters at once** (e.g. `quest_line` *and* `priority`
   together) — confirm the result is the intersection, not either filter
   alone.
5. **`quest_line_stats` with more than one quest in the same quest
   line, with a mix of done and not-done** — confirm `total` and `done`
   are both correct, not just "greater than zero." This module's own
   existing `test_quest_stats_are_scoped_to_the_current_user` only ever
   creates **one** quest per line — read it and notice this yourself
   before writing your own test.
6. **`quest_line_stats` with quests spread across *two different* quest
   lines** — confirm the response has one correctly-aggregated row per
   line, not one merged row.

## Acceptance criteria

- [ ] `python -m pytest -v` from `starter/backend/` shows every test
      passing (the original 31, plus your new ones).
- [ ] Re-running `python -m pytest --cov=app.repository --cov-report=term-missing`
      no longer lists lines `121`, `123`, or `125` in the `Missing`
      column — this is the concrete, verifiable proof your filter tests
      genuinely exercise all three filter branches. (`app/repository.py`'s
      overall percentage will only move from 45% to about **48%** — most
      of the file's remaining "Miss" lines are `seed_if_empty`, which
      only ever runs once, at real app startup, and is never reachable
      through this test setup at all; a much higher percentage on this
      *specific* file was never a realistic target, and chasing one
      would be exactly the wrong lesson to take from
      `lessons/01-why-tests-and-the-testing-pyramid.md`'s "100% coverage
      is not the goal" section.)
- [ ] Your two `quest_line_stats` tests genuinely add new *behavioral*
      confidence even though they may not move the coverage percentage
      at all beyond the filter fix above — the existing, single-quest-
      per-line stats test already runs every line of `quest_line_stats`
      at least once, but never actually proves the `GROUP BY`/counting
      logic aggregates *correctly* across more than one row. This is
      worth sitting with for a moment: it's a direct, concrete example of
      coverage measuring "did this line run" while saying nothing about
      "was the result actually checked thoroughly" — exactly Lesson 01's
      point, now something you've verified with your own hands instead
      of just read about.

## What to submit

`starter/backend/tests/test_quest_filters_and_stats.py`.

## Hints

**Level 1:** Reuse the `client` and `signup_and_login` fixtures already
defined in `starter/backend/tests/conftest.py` — you don't need to write
any new fixtures for this exercise at all.

**Level 2:** `httpx`'s `AsyncClient.get(...)` takes a `params=` keyword
argument — a plain dict — for query parameters, e.g. `await
client.get("/api/quests", params={"priority": "high"}, headers=headers)`
— don't hand-build the query string yourself.

**Level 3 (closer to the answer):** For the multi-quest-per-line stats
test, create three quests with the *same* `questLine` value, mark exactly
one of them done via `PATCH .../{id}` with `{"done": true}`, then assert
the one row `GET /api/quests/stats` returns for that quest line has
`"total": 3` and `"done": 1`.
