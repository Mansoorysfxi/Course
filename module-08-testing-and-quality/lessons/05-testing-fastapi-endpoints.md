# Lesson 05 — Testing FastAPI Endpoints

## What you'll learn

- What ASGI is, in enough depth to understand why it lets you test a
  FastAPI app without a real running server.
- How `httpx.AsyncClient` + `ASGITransport` sends a real HTTP request
  straight into your app's own code, in-process.
- Why FastAPI test functions need to be `async def`, and what
  `pytest-asyncio`'s `asyncio_mode = "auto"` (Lesson 00) does for you so
  you never have to think about that beyond writing `async def`.
- How to override a FastAPI dependency (`app.dependency_overrides`) so a
  test can substitute a fake for something the real app depends on —
  this module's own database session, specifically (fully covered in
  Lesson 06, but introduced here at the mechanism level).
- How to write real, working tests for QuestLog's actual signup, login,
  and protected-route behavior — reading and understanding this module's
  own `backend/tests/test_auth.py`, line by line.

## Why this matters

Module 07's own backend `README.md` says every route was tested "with
`curl` and FastAPI's `/docs`... while building this module" — real
verification, but entirely manual, and entirely undone the moment you
change one line of `app/routers/auth.py` and want to re-check nothing
broke. This lesson turns that same verification into code that runs in
milliseconds and re-checks itself forever, automatically, exactly the
value Lesson 01 argued for — now made concrete against the real app.

## Prerequisites

Lessons 02–03 (fixtures, mocking) — this lesson's `client` fixture is
built from exactly those tools. Module 05 (FastAPI routing, `Depends`,
Pydantic models) and Module 07 (auth, JWTs, protected routes) — this
lesson tests that exact, real code, so you need to already understand
what it does.

## The concept, explained simply

Every module through Module 07 tested QuestLog's API the same way: start
`uvicorn`, which opens a real network port, then send it real HTTP
requests (via `curl`, or a browser) over that real network connection,
even though both sides were running on the very same machine. That's a
genuinely real, complete round trip — but it's slow to set up (a whole
separate server process has to actually start) and awkward to automate
(something has to know when the server is "ready," manage starting and
stopping it around every test run, and so on).

**A FastAPI app is not "a server" by itself — it's a specific,
callable Python object.** `uvicorn` is the *separate* program whose job
is: open a real network port, and forward what arrives on it into that
callable object, then send its return value back out over the network.
The actual "did this request produce this response" logic all lives
inside the callable — `uvicorn` is just plumbing around it. This
matters because it means you can call that same object *directly*, with
no network, no separate process, no `uvicorn` at all — exactly what this
lesson's tools do.

## The details

### What ASGI actually is

**ASGI** (Asynchronous Server Gateway Interface) is the specific,
standardized shape that "callable object" has to have — a formal
agreement between a web framework (FastAPI) and whatever runs it
(`uvicorn` for real traffic; this lesson's test tools for tests) about
exactly how a request comes in and a response goes out, so any
ASGI-compatible framework works with any ASGI-compatible server, and (the
part that matters for testing) with any ASGI-compatible *test tool* too.
You don't need to know ASGI's exact technical shape to use it — the
practical takeaway is just this: **because FastAPI's `app` object speaks
ASGI, any tool that also speaks ASGI can hand it a fake request and read
its response, entirely in-process, with zero real networking involved.**

### `httpx.AsyncClient` + `ASGITransport`: the tool that does this

`httpx` is a Python HTTP client library — the same general idea as
`requests` (if you've used that before) or the browser's own `fetch`, but
built with async support from the start. Its **transport** is the layer
that actually decides how a request physically travels — normally, over
a real network socket. `ASGITransport` swaps that out for "call the ASGI
app object directly instead":

```python
from httpx import ASGITransport, AsyncClient
from app.main import app

transport = ASGITransport(app=app)
async with AsyncClient(transport=transport, base_url="http://testserver") as client:
    response = await client.get("/")
```

**Line by line:** `ASGITransport(app=app)` wraps your actual, real
FastAPI `app` object (the exact same one `uvicorn app.main:app` would
run) as a transport `AsyncClient` can use. `base_url="http://testserver"`
is required by `httpx` (every request needs *some* base URL to resolve
relative paths like `/api/quests` against) but is otherwise meaningless
here — no real network request to any real "testserver" host ever
happens; ASGITransport intercepts it before it would ever leave the
process. `await client.get("/")` then runs, genuinely, through FastAPI's
real routing, real dependency injection, real Pydantic validation — every
piece of real app logic runs exactly as it would for a real user, just
without an actual network socket in the middle.

This module's real `backend/tests/conftest.py` wraps exactly this pattern
in a fixture named `client` — open that file now and find it; every line
should already make sense.

### Why test functions must be `async def`

`client.get(...)` above is awaited — `httpx.AsyncClient`'s methods are
all coroutines (Module 01's async lesson). A test function that calls
`await` anywhere in its body must itself be declared `async def`, the
same rule that applies to any Python code using `await`. Lesson 00
already covered what makes this work with `pytest` at all: this backend's
`pyproject.toml` sets `asyncio_mode = "auto"`, so `pytest-asyncio`
automatically treats every `async def test_...` function correctly — you
never write `@pytest.mark.asyncio` yourself anywhere in this module's
real test files; check `backend/tests/test_auth.py` to confirm this for
yourself.

### Reading this module's real `test_auth.py`, together

Open `backend/tests/test_auth.py` now. Walk through
`test_signup_creates_an_account` with this lesson's concepts in hand:

```python
async def test_signup_creates_an_account(client):
    response = await client.post(
        "/api/auth/signup",
        json={"email": "hero@example.com", "password": "sword-and-shield"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "hero@example.com"
    assert "id" in body
    assert "createdAt" in body
    assert "password" not in body
    assert "hashedPassword" not in body
    assert "hashed_password" not in body
```

- `async def test_signup_creates_an_account(client):` — `client` is a
  fixture parameter (Lesson 02) — `pytest` resolves it automatically from
  `conftest.py`, handing this test a fully working `AsyncClient` wired to
  the real app, with zero setup code written in this function at all.
- `await client.post("/api/auth/signup", json={...})` — a real `POST`
  request, with a real JSON body, into the real `signup` route
  (`app/routers/auth.py`, Module 07) — every line of that real route runs:
  Pydantic validates the body against `UserCreate` (rejecting a malformed
  request before the route's own code even executes, exactly as it would
  for a real caller), `app.security.hash_password` genuinely hashes the
  password with real `bcrypt`, and `app.repository.create_user` genuinely
  inserts a row (into the test database — Lesson 06).
- `assert response.status_code == 201` — matches the real route's
  `status_code=status.HTTP_201_CREATED` (Module 05).
- The final three assertions are a direct, executable check of something
  Module 07's own `UserPublic` docstring only *claims* in a comment: that
  a password (in any of its three plausible field-name spellings) never
  appears in a signup response. If a future change accidentally added a
  `password` field back onto that response model, this exact test would
  fail immediately, catching a real security regression the moment it
  happened — not months later, by chance, when someone happened to notice.

Now read `test_login_with_wrong_password_is_rejected` and
`test_me_without_a_token_is_rejected` yourself, matching each line against
Module 07's real `app/routers/auth.py` and `app/dependencies.py` — every
assertion in this module's real test files traces back to a specific,
real piece of application behavior; there is no test in this module that
checks something the app doesn't actually, genuinely do.

### `app.dependency_overrides`: substituting a fake dependency

One line in `backend/tests/conftest.py`'s `client` fixture hasn't been
explained yet:

```python
app.dependency_overrides[get_db] = override_get_db
```

Recall Module 05's `Depends` mechanism: a route parameter like `session:
DbSession` (an alias for `Annotated[AsyncSession, Depends(get_db)]`,
`app/dependencies.py`) means "before running this route, call `get_db`
and hand me whatever it produces." **`app.dependency_overrides` is a
dictionary FastAPI itself checks first, before ever calling the real
dependency function** — `{get_db: override_get_db}` tells the app "any
route that asks for `get_db` should get `override_get_db`'s result
instead, for as long as this override is in place." This is *how* this
module's tests run against a temporary test database instead of the real
Postgres database `app/config.py` defaults to, with **zero changes to any
route or repository function** — they still just write `Depends(get_db)`,
exactly as Module 05/06/07 already did; only *which* function actually
runs behind that name changes, and only inside a test. Lesson 06 covers
exactly what `override_get_db` itself does and why.

## Common mistakes & gotchas

- **`RuntimeWarning: coroutine '...' was never awaited`, and the test
  reports as passed anyway.** Almost always a forgotten `await` before an
  `async` call — e.g. `client.get(...)` instead of `await client.get(...)`.
  Without `await`, you get back a coroutine *object*, not the real
  response — no exception is raised just from that, so the test can
  appear to "pass" while never having actually made the request or
  checked anything meaningful at all (the same "silently checks nothing"
  trap Lesson 00's async gotcha and Lesson 01's coverage warning both
  named from a different angle).
- **`TypeError: object dict can't be used in 'await' expression`, or
  similar.** Usually means an `async def` function was called without
  `await` somewhere earlier, and the resulting coroutine object got
  passed around and used as if it were the real value.
- **A test passes locally but the same route clearly requires
  authentication when you try it by hand.** Check whether the test is
  actually sending the `Authorization` header it needs — a passing test
  that accidentally tests the *wrong* thing (e.g. hitting a route that
  doesn't require a token at all, by a typo in the URL) is worse than no
  test, because it creates false confidence. This module's real
  `test_quests_route_without_a_token_is_rejected` exists specifically to
  pin down the *other* half of this: confirming a route genuinely does
  reject an unauthenticated request, not just that it accepts an
  authenticated one.
- **Forgetting `app.dependency_overrides.clear()` after a test.** This
  module's `client` fixture does this in the line after its `yield` —
  without it, an override set up by one test could leak into a later,
  unrelated one (the exact fixture-isolation problem Lesson 02's
  "Common mistakes" section warned about generally, now shown in a real,
  specific place it actually matters).

## How this connects

This lesson explained the *mechanism* (`ASGITransport`, dependency
overrides) behind this module's real `client` fixture; Lesson 06
explains the other half — exactly what `db_session` and `override_get_db`
do, and why this module's tests use SQLite instead of the real Postgres
database, a decision backed by real research, not assumption. Together,
Lessons 05–06 are what makes `backend/tests/test_auth.py` and
`test_quests.py` — this module's capstone-level integration tests — work
at all.

## Quick self-check

1. What is ASGI, in your own words, and why does FastAPI's `app` object speaking it let you test the app with no real network connection at all?
2. Why must a test function that calls `await client.get(...)` be declared `async def`? What normally makes `pytest` handle that correctly with zero extra decorator in this module's own tests?
3. Walk through `test_signup_creates_an_account` (`backend/tests/test_auth.py`) line by line and name, for each assertion, the exact real application code it's checking.
4. What does `app.dependency_overrides[get_db] = override_get_db` actually do, mechanically, and why does it let this module's tests run without a real Postgres database, with zero changes to any route function?
5. What specific, real security property does this lesson's `test_signup_creates_an_account` check that a casual read of `app/models.py`'s `UserPublic` class would only *claim*, not actually verify?
