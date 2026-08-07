# Exercise 04 — Wire Up Full Auth on a Starter Copy of QuestLog's Backend

**Difficulty:** Independent. This is the least guided exercise in this
module, deliberately — it asks you to combine everything Lessons 01–07
taught into one working system, on your own, the way the real capstone
already did. There are no `# TODO` markers inside the starter's code this
time; you decide which files to add and change.

## Concepts this exercise uses (and where they're taught)

- Authentication vs. authorization — [Lesson 01](../../lessons/01-authentication-vs-authorization.md).
- Hashing and verifying a password with `bcrypt` — [Lesson 02](../../lessons/02-password-hashing.md) (and Exercise 01, which you should have already completed).
- Why a JWT, what claims to put in one, and how to create/verify one with PyJWT — [Lesson 03](../../lessons/03-sessions-vs-jwts.md) and [Lesson 04](../../lessons/04-jwt-structure-in-depth.md) (and Exercise 02).
- Building real `signup`/`login` routes, including why `login` uses `OAuth2PasswordRequestForm` (form data, not JSON) — [Lesson 06](../../lessons/06-building-signup-login.md).
- `OAuth2PasswordBearer`, a `get_current_user` dependency, and the `CurrentUser` pattern that makes a route "protected" — [Lesson 07](../../lessons/07-protecting-routes-with-dependencies.md) (and Exercise 03).
- Scoping a database query by the authenticated user's id, and why a quest that exists but belongs to someone else should 404, not 403 — Lesson 07's "404, not 403" box, and `app/repository.py`'s own docstrings in Module 06's version of this backend.

If any of those feel shaky, re-read the lesson before starting — this
exercise assumes all of it, combined, with no new teaching of its own.

## What this is

`starter/backend/` is **Module 06's finished QuestLog backend, copied
here unchanged** — same three tables, same routes, same silent
`DEFAULT_USER_EMAIL`-owned quests, zero passwords, zero JWTs, zero
protected routes. Your job is to turn it into exactly what
`module-07-auth-security/project/questlog/backend/` (the real capstone)
already is: a genuinely multi-user backend with signup, login, and every
quest route requiring a valid token and scoped to its owner.

This is deliberately the same transformation the real capstone already
demonstrates working — the difference is you do it yourself, first,
before comparing against `solution/backend/` (which is a full working
copy of the real `project/questlog/backend/`, provided so you have
something concrete to check against once you're done or well and truly
stuck).

**One deliberate scope reduction versus the real capstone**, so this
exercise stays focused on auth wiring rather than repeating Lesson 00/11's
settings-management material: this exercise's `app/config.py` keeps
Module 06's plain `os.environ.get(...)` style rather than
`pydantic-settings`, and you should put your `SECRET_KEY` as a plain
Python constant in whatever new file you create for password/JWT
functions (exactly Exercise 03's pattern), rather than wiring up a `.env`
file. Real settings management is already fully exercised by the real
capstone; this exercise's job is specifically signup, login, protection,
and ownership.

## What to build

Starting from `starter/backend/`, without looking at
`project/questlog/backend/` first:

1. **Add a `hashed_password` column to `User`** (`app/db_models.py`), and
   write a real Alembic migration for it (`alembic revision --autogenerate
   -m "..."`, then read the generated file before applying it — Module 06's
   own Alembic lesson already taught you never to apply a migration you
   haven't read).
2. **Write password hashing and JWT functions** (a new file,
   `app/security.py` is the obvious name, matching the real capstone's
   convention, but the exact filename is your call): `hash_password`,
   `verify_password`, `create_access_token`, `decode_access_token`.
3. **Add `UserCreate`/`UserPublic`/`Token` Pydantic models** (`app/models.py`).
4. **Add `get_user_by_email`, `get_user_by_id`, `create_user` to `app/repository.py`**, and **change every quest function in that file to take and filter by `owner_id`** — `list_quests`, `get_quest`, `create_quest`, `update_quest`, `delete_quest`, `quest_line_stats`. Delete `_get_default_owner_id` entirely; nothing should call it once you're done.
5. **Add `oauth2_scheme`, `get_current_user`, and a `CurrentUser` alias** to `app/dependencies.py`, and update `get_quest_or_404` to require and use one.
6. **Add a new `app/routers/auth.py`** with `POST /signup` and `POST /login` (mount it in `app/main.py` alongside the existing `quests` router).
7. **Add `current_user: CurrentUser` to every route in `app/routers/quests.py`**, passing `current_user.id` through to `repository` as `owner_id`.
8. **Decide what `seed_if_empty` should do now.** Module 06's version silently created one default user with no password. Once real accounts exist, does it still make sense to auto-create quests owned by an account nobody can ever log into? Make a decision, write one sentence in a comment explaining it, and implement it. (There is a defensible answer either way — what matters is that you made the decision on purpose, not by accident. Compare your reasoning against the real capstone's `seed_if_empty` and its own comment once you're done.)

## Setup

This exercise needs its own, separate Postgres database — **do not**
point it at the same `questlog` database the real capstone
(`project/questlog/backend/`) uses; `starter/backend/app/config.py`
already defaults to a different name (`questlog_exercise04`) for exactly
this reason.

```bash
psql -U postgres -h localhost -c "CREATE DATABASE questlog_exercise04 OWNER questlog;"
cd exercises/04-wire-up-questlog-auth/starter/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt   # already includes bcrypt, PyJWT, python-multipart
alembic upgrade head               # Module 06's original schema only, for now
uvicorn app.main:app --reload      # confirm it still runs, unmodified, before changing anything
```

Confirm the unmodified starter works first:

```bash
curl http://127.0.0.1:8000/api/quests
```
**Expected:** a JSON array of five quests, all silently owned by
`player@questlog.local` — Module 06's exact behavior. Only once you've
seen this should you start changing code.

## Acceptance criteria

- [ ] `POST /signup` with a new email+password creates an account and returns it (never a token) — a second signup with the same email fails cleanly (400 or 409, your choice, but not a raw, unhandled database error).
- [ ] `POST /login` with correct credentials returns `{"access_token", "token_type"}`; with wrong credentials, returns `401`.
- [ ] Every `/api/quests` route returns `401` with no `Authorization` header at all.
- [ ] A freshly signed-up account sees **zero** quests until it creates its own.
- [ ] Two different accounts each create a quest; each account's `GET /api/quests` shows only its own quest, never the other's.
- [ ] Requesting a quest by id that exists but belongs to the *other* account returns `404`, not `403` — verify this specifically with `curl`, don't just reason about it.
- [ ] Your migration file was generated with `--autogenerate`, then actually read before running `alembic upgrade head` — describe, in one sentence in your submission, what it added.

## What to submit for review

Your completed `starter/backend/` (every changed/new file), plus a
transcript of `curl` commands demonstrating each acceptance criterion
above actually happening against your own running server — specifically
including the cross-account `404` test, since that one is easy to get
subtly wrong (e.g. accidentally returning `403`, or accidentally letting
the second account see the first account's quest at all).

## Hints

**Level 1:** You've already built every individual piece of this in
Exercises 01–03. This exercise's actual new skill is *integration* —
making all four pieces (hashing, JWTs, a protecting dependency, and
owner-scoped queries) work together inside one real, multi-file FastAPI
app, not any single new technique. If you're stuck on what a function
should do, its near-exact twin already exists in `app/security.py`,
`app/dependencies.py`, or `app/repository.py` inside
`module-07-auth-security/project/questlog/backend/` — the real, running
capstone. Looking at ONE function there to unblock yourself, after a real
attempt, is a reasonable use of a hint; copying the whole file without
attempting it first defeats the exercise.

**Level 2:** The single most common mistake here is scoping ownership in
the *route* instead of the *query* — e.g. fetching a quest by id first,
then checking `if quest.owner_id != current_user.id: raise 403` as a
separate step afterward. This works, but it's the wrong shape for two
reasons Lesson 07 explains: it leaks *which* quests exist to unauthorized
callers via timing/behavior differences, and it's easy to forget to add
to a future route. Put `owner_id` directly in the `WHERE` clause instead
(`WHERE id = :quest_id AND owner_id = :owner_id`), so a quest belonging to
someone else is genuinely indistinguishable, at the database level, from
a quest that doesn't exist at all.

**Level 3:** If your migration fails with something like `column
"hashed_password" of relation "users" contains null values`, you ran
`alembic upgrade head` against a database that already had a seeded
`player@questlog.local` row with no password — exactly the scenario
Lesson 00's own migration file docstring warns about. Either drop and
recreate `questlog_exercise04` (cheap — it's disposable practice data) and
migrate from empty, or decide `hashed_password` should be nullable at the
database level (matching a real production migration's "add nullable,
backfill, then constrain" pattern) — either is a defensible choice; pick
one and be able to explain why.
