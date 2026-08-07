# Exercise 03 — Protect a Route with a Dependency

**Difficulty:** Guided.

## Concepts this exercise uses (and where they're taught)

- What a FastAPI security scheme is, and specifically what `OAuth2PasswordBearer` does and doesn't do — [Lesson 07](../../lessons/07-protecting-routes-with-dependencies.md), "`OAuth2PasswordBearer` — reading the header, nothing more."
- How `get_current_user` turns a raw token into a verified user, and the "one error, three failure reasons" pattern — Lesson 07, "`get_current_user` — the real verification."
- How one dependency parameter makes an entire route "protected" — Lesson 07, "`CurrentUser` — the parameter that makes a route protected."
- `decode_access_token` and what exceptions it can raise — [Lesson 04](../../lessons/04-jwt-structure-in-depth.md).
- FastAPI's `Depends()` mechanism itself — Module 05, Lesson 04 (this exercise assumes you already know how `Depends()` calls a function and injects its return value; it does not re-teach that).

## What this is

A small, standalone FastAPI app — a toy "vault" API, **not** QuestLog —
with its own tiny in-memory (no database) set of users. `POST /login` is
already fully implemented for you (it's exactly Lesson 06's pattern,
already practiced). Your job is the part this exercise is actually
about: **protecting a route with a dependency**, from scratch, on a
codebase that isn't QuestLog — this is deliberately a different, smaller
app than the lesson's own examples, so you have to apply the pattern
yourself rather than recognize it from having already seen it.

## What to build

In `starter/main.py`, three things are marked `# TODO`:

1. `oauth2_scheme` — create an `OAuth2PasswordBearer` instance pointed at this app's own `/login` route.
2. `get_current_user(...)` — a dependency function that: reads the token via `oauth2_scheme`, calls `decode_access_token` (already provided), looks up the `sub` claim in `USERS`, and raises a `401` (with a `WWW-Authenticate: Bearer` header) if the token is invalid/expired OR if the user it names doesn't exist. One `except` clause should cover every JWT failure case — re-read Lesson 07's "one error, three failure reasons" box before writing this.
3. `GET /secret` — add whatever parameter is needed to make this route require a valid token, and return `{"message": f"Hello, {username}! The secret number is 42."}` using the authenticated username.

## Setup

```bash
cd exercises/03-protect-a-route-with-a-dependency/starter
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Verifying it yourself

```bash
# Should work with no token at all -- this route stays public on purpose.
curl http://127.0.0.1:8000/public

# Should fail with 401 -- no token supplied.
curl -i http://127.0.0.1:8000/secret

# Log in as the seeded user (username: alice, password: wonderland).
curl -X POST http://127.0.0.1:8000/login -d "username=alice&password=wonderland"
# Copy the access_token from the response, then:
curl http://127.0.0.1:8000/secret -H "Authorization: Bearer PASTE_TOKEN_HERE"
```

## Acceptance criteria

- [ ] `GET /public` works with no `Authorization` header at all.
- [ ] `GET /secret` with **no** `Authorization` header returns `401`.
- [ ] `GET /secret` with a **valid** token for `alice` returns `200` and a message containing `"alice"`.
- [ ] `GET /secret` with a token that has one character changed anywhere in it returns `401` (test this — it should fail the same way an entirely missing token does, per Lesson 07's "one error" design).
- [ ] `POST /login` with the wrong password for `alice` returns `401`, not `200`.

## What to submit for review

The completed `starter/main.py`, plus a short transcript (copy-pasted
terminal output) showing all five `curl` checks above actually run
against your own running server.

## Hints

**Level 1:** `get_current_user` in this exercise should look extremely
close to `app/dependencies.py`'s own `get_current_user` in QuestLog's
real backend (Lesson 07 walks through that exact function line by line)
— the difference here is *where* the user gets looked up (a plain Python
dict, `USERS`, instead of a database query).

**Level 2:** `decode_access_token` (already given in the starter) raises
`jwt.InvalidTokenError` for a bad signature, malformed token, or expired
token — catch that specific exception type, not a bare `except:`.

**Level 3:** For "make `/secret` require a token," the fix is exactly one
new parameter in that route function's signature — nothing about the
function's body needs a manual `if` check for "is there a valid token."
If you find yourself writing that kind of manual check inside the route
body, you're missing the actual FastAPI mechanism this exercise is
teaching.
