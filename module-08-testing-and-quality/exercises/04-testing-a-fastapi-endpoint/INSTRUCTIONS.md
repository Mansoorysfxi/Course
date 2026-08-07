# Exercise 04 — Testing a FastAPI Endpoint

**Difficulty:** Guided, leaning independent — you're given a working app
and told what to cover, but you write the whole test file and its
`client` fixture yourself, from scratch.

## Concepts this exercise uses (all taught in the lessons named)

- `httpx.AsyncClient` + `ASGITransport`, and why FastAPI test functions
  are `async def` — `lessons/05-testing-fastapi-endpoints.md`.
- Writing your own `client` fixture in `conftest.py` — same lesson, plus
  `lessons/02-pytest-fundamentals-and-fixtures.md` for fixture mechanics
  generally.
- `@pytest.mark.parametrize` for testing several kinds of invalid input
  with one test function — `lessons/03-parametrize-and-mocking.md`.

This exercise deliberately does **not** use a real database — that's
Lesson 06's separate topic, exercised for real in Exercise 05.

## What you're given

`starter/main.py` — "The Guild Board API," a small, complete, in-memory
FastAPI app with no tests at all:
- `GET /announcements` — list every announcement.
- `POST /announcements` — create one (`title`, `body`); `422` if either
  is missing or `title` is empty.
- `GET /announcements/{id}` — `404` if the id doesn't exist.
- `DELETE /announcements/{id}` — `204`; `404` if the id doesn't exist.

## What to do

1. Create `starter/conftest.py` with a `client` fixture that:
   - Wraps `main.app` in an `httpx.AsyncClient` via `ASGITransport`,
     exactly as `lessons/05-testing-fastapi-endpoints.md` demonstrated.
   - Clears `main._announcements` (the app's one in-memory dict) *before*
     yielding the client, so every test starts from a genuinely empty
     board — this app has no real database to recreate, so clearing its
     one piece of stored state is the direct equivalent of what Lesson
     06's `db_session` fixture does for QuestLog's real database.
2. Create `starter/test_main.py` covering:
   - Listing announcements on an empty board returns `[]`.
   - Creating an announcement returns `201` with the right fields, and a
     real `id`.
   - A created announcement actually shows up in a subsequent `GET
     /announcements` call.
   - Getting a real announcement by its id works; getting a
     made-up id returns `404`.
   - Deleting a real announcement returns `204`, and a subsequent `GET`
     for that same id then returns `404`.
   - Deleting a made-up id returns `404`.
   - Using `@pytest.mark.parametrize`, confirm at least **three**
     different kinds of invalid `POST` body (missing `title`, empty
     `title`, missing `body`) all correctly return `422`, as one
     parametrized test function.

## Acceptance criteria

- [ ] `python -m pytest -v` from `starter/` shows every test passing.
- [ ] `starter/pyproject.toml` (already given) sets `asyncio_mode =
      "auto"` — confirm your test functions are all plain `async def`
      with no `@pytest.mark.asyncio` decorator anywhere, and that they
      still run correctly.
- [ ] Every test genuinely starts from an empty board (no test depends
      on another test having run first, or on ordering at all) — try
      running `pytest -v` twice in a row and confirm the results are
      identical both times.
- [ ] The parametrized invalid-input test reports as **three** separate
      test cases in `pytest -v`'s output, not one.

## What to submit

`starter/conftest.py` and `starter/test_main.py`.

## Hints

**Level 1:** Your `client` fixture's shape should look almost identical
to the one shown in `lessons/05-testing-fastapi-endpoints.md` — the only
genuinely new line for this exercise is clearing `_announcements` first.

**Level 2:** To get an announcement's real `id` for a later `GET`/`DELETE`
test, first `POST` one and read `.json()["id"]` off the response —
exactly the same "create it first, then use what came back" pattern
Lesson 05's own `test_signup_creates_an_account` doesn't need (nothing
there needs a follow-up request), but this module's real
`backend/tests/test_quests.py::_create_quest` helper uses constantly.

**Level 3 (closer to the answer):** For the parametrize case, your list
of bad payloads is a list of dictionaries, one dictionary per case —
`@pytest.mark.parametrize("bad_payload", [{"body": "..."}, {"title": "",
"body": "..."}, {"title": "..."}])` — and your test function takes
`bad_payload` as its second parameter (after `client`), sending it
directly as the request's `json=`.
