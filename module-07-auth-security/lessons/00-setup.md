# Lesson 00 — Setup: New Packages, a Fresh Database, and a Real Secret

**Verified against (August 2026):** `bcrypt` **5.0.0** (confirmed via
`https://pypi.org/pypi/bcrypt/json`); `PyJWT` **2.13.0** (confirmed via
`https://pypi.org/pypi/PyJWT/json`, released 2026-05-21); `pydantic-settings`
**2.14.2** (confirmed via `https://pypi.org/pypi/pydantic-settings/json`,
released 2026-06-19); `python-multipart` **0.0.32** (confirmed via
`https://pypi.org/pypi/python-multipart/json`); `email-validator` **2.3.0**
(confirmed via `https://pypi.org/pypi/email-validator/json`). FastAPI,
Uvicorn, Pydantic, PostgreSQL, SQLAlchemy, Alembic, and asyncpg are all
**unchanged** from Module 06 — see that module's `README.md` for their
pinned versions, re-verified here as still current.

This lesson's library **choices**, not just their version numbers, were
also verified through real research, not memory, because this is exactly
the kind of fast-moving, security-relevant area Rule 7 singles out:

- **Password hashing:** FastAPI's own official documentation has, in the
  last couple of years, moved *away* from recommending `passlib` — multiple
  FastAPI maintainer discussions (`github.com/fastapi/fastapi/discussions/9576`
  and `/11773`) confirm `passlib` is now effectively unmaintained (its last
  release predates this lesson by years, and it breaks outright on current
  Python because it depends on the standard library's `crypt` module,
  removed in Python 3.13). This course uses the `bcrypt` package
  **directly**, with no `passlib` layer in between, for exactly the reasons
  in Lesson 02.
- **JWTs:** FastAPI's docs recommended `python-jose` for years; the same
  kind of maintainer discussion
  (`github.com/fastapi/fastapi/discussions/11345`) confirms the project
  moved back to recommending **PyJWT** after concluding `python-jose` was
  abandoned (multi-year gaps between releases, incompatible with newer
  Python). This course uses PyJWT.
- **Settings:** `pydantic-settings` (a separate package from core
  Pydantic since Pydantic v2) is the current, officially documented way to
  read typed configuration from environment variables and `.env` files in
  a FastAPI project.
- **CORS:** FastAPI's own CORS documentation (`fastapi.tiangolo.com/tutorial/cors/`)
  and the underlying Starlette `CORSMiddleware` it wraps are unchanged in
  shape from what Module 05/06 already used — this lesson's setup doesn't
  change *how* CORS is configured, only *what values* it's configured
  with; Lesson 10 explains the whole thing properly.

## What you'll learn

- Why this module needs five new backend packages, and what job each one does.
- How to install them into the *same* venv Module 06 already created (not a new one).
- How to generate a real, random secret key, and why you generate your own instead of using one from this lesson.
- How to create a `.env` file — and why `.env` itself must never be committed to Git, while a `.env.example` template is.
- Why this module has you start from a **fresh** `questlog` database, and how to create one.
- How to verify all of this before Lesson 01 asks anything more of you.

## Why this matters

Module 06 left QuestLog's backend able to store quests permanently, but
with no real concept of a password, a login, or a session — every quest
was silently owned by one seeded "default" user, and anyone who could
reach the API at all could see and change every quest. This module makes
QuestLog **multi-user for real**, and that requires exactly one new piece
of infrastructure this lesson sets up: a **secret** the backend uses to
prove a JWT (Lesson 04) really came from it, plus a handful of small,
focused libraries that do the actual cryptographic work (hashing
passwords, signing/verifying tokens) so this course never has to hand-roll
cryptography — a categorically bad idea explained in Lesson 02.

## Prerequisites

**Module 06 in full**, especially its own `lessons/00-setup.md` — this
lesson assumes PostgreSQL is already installed and running, and that
`module-07-auth-security/project/questlog/backend` already has the
`.venv` Module 06's setup lesson had you create (this module's backend is
a **copy forward** of Module 06's, per `RUNNING_PROJECT.md` — same
project, same venv convention, not a new one). **Module 01's venv/pip
lesson** for what a virtual environment is and how `pip install` works.

## The concept, explained simply

Think of this module's new packages the way you'd think about adding a
save-encryption library to an Unreal project that previously just wrote
plain JSON save files to disk: the *save system itself* (loading/saving
game state) doesn't change, but you're adding a small, specialized,
heavily-scrutinized library to do one dangerous job correctly (encryption)
rather than writing that logic yourself. This lesson adds five such
specialized libraries — none of them touches quests, routing, or the
database directly; each does exactly one narrow job:

- **`bcrypt`** — turns a plain-text password into a secure hash, and
  checks a password attempt against a stored hash. (Lesson 02.)
- **`PyJWT`** — creates and verifies JSON Web Tokens. (Lesson 04.)
- **`pydantic-settings`** — reads typed configuration (including secrets)
  from environment variables and a `.env` file. (This lesson, and Lesson 11.)
- **`python-multipart`** — lets FastAPI parse form-encoded request bodies,
  needed specifically because this app's login endpoint uses FastAPI's
  `OAuth2PasswordRequestForm` (Lesson 06), which reads form fields, not JSON.
- **`email-validator`** — backs Pydantic's `EmailStr` type, used to reject
  a signup request whose `email` field isn't even shaped like an email
  address, before any of this app's own code runs.

## The details

### Step 1 — Re-verify Module 06's setup still works

Rule 8: never assume a tool from an earlier module is still configured.
Confirm PostgreSQL is running and Module 06's venv still works:

```bash
psql -U questlog -d questlog -h localhost -c "SELECT 1;"
```
**Expected:** a one-row table containing `1`. If this fails, revisit
Module 06's `lessons/00-setup.md` troubleshooting section before continuing.

### Step 2 — Get this module's copy of the backend, and its own venv

This module's backend lives at
`module-07-auth-security/project/questlog/backend` — a copy of Module
06's finished backend (per `RUNNING_PROJECT.md`'s "each module's starter
code is a copy of the previous module's finished solution" convention),
already extended with this module's auth code. Give it its own fresh
venv (never reuse a venv folder across module folders — each project
folder is a separate Python project, exactly Module 01's isolation
lesson):

```bash
cd module-07-auth-security/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
```

**Expected:** `(.venv)` appears at the start of your prompt.

### Step 3 — Install every dependency, including the five new ones

```bash
pip install -r requirements.txt
```

**Expected output (abbreviated):** lines ending in
`Successfully installed fastapi-0.141.1 ... bcrypt-5.0.0 ... pyjwt-2.13.0 ...
pydantic_settings-2.14.2 ... python_multipart-0.0.32 ... email_validator-2.3.0 ...`
alongside every package Module 06 already needed (`sqlalchemy`,
`alembic`, `asyncpg`, and so on — all pinned in `requirements.txt`).

**Line by line, the five new entries in `requirements.txt`:**
```
bcrypt==5.0.0
pyjwt==2.13.0
pydantic-settings==2.14.2
python-multipart==0.0.32
email-validator==2.3.0
```
None of these are extras of an existing package (unlike `uvicorn[standard]`
back in Module 05) — each is installed on its own, because each does a
genuinely separate job, per the "one narrow job each" framing above.

### Step 4 — Drop and recreate the `questlog` database

This module's `db_models.py` adds a new, `NOT NULL` column
(`hashed_password`) to the `users` table Module 06 created. Adding a
`NOT NULL` column to a table that might already have rows in it is
genuinely awkward — every existing row would need a real value *before*
the constraint could apply — and handling that properly (a multi-step
"add nullable → backfill → make non-null" migration) is a real technique,
but not this lesson's topic (see this module's Alembic migration file,
`alembic/versions/..._add_hashed_password_to_users.py`, for a full
explanation and a pointer back to Module 06's own Alembic lesson for how
the general technique works). To keep this module focused on auth, not
migrations, start from a genuinely empty database:

```bash
psql -U postgres -h localhost -c "DROP DATABASE IF EXISTS questlog;"
psql -U postgres -h localhost -c "CREATE DATABASE questlog OWNER questlog;"
```

**Line by line:** connecting as the `postgres` superuser (Module 06's
Lesson 00 created this account) is required to drop a database — the
`questlog` user owns the database but Postgres still requires elevated
privileges to destroy one outright. `DROP DATABASE IF EXISTS` deletes the
old database (and everything in it — this is exactly as destructive as it
sounds; this is fine here because this is disposable local practice data)
without erroring if it somehow didn't exist. `CREATE DATABASE ... OWNER
questlog` recreates it empty, owned by the same `questlog` user Module 06
already set up — nothing about that user or its password changes.

### Step 5 — Apply migrations to the fresh database

```bash
alembic upgrade head
```

**Expected output:** two lines mentioning `Running upgrade ... -> ...`,
one for Module 06's original migration (creates `users`, `quest_lines`,
`quests`) and one for this module's new migration (adds
`users.hashed_password`) — both apply, in order, to your now-empty
database. Confirm with:

```bash
psql -U questlog -d questlog -h localhost -c "\d users"
```
**Expected:** a table listing `id`, `email`, `hashed_password`, and
`created_at` as columns.

### Step 6 — Generate a real secret key, and create `.env`

Every JWT this backend issues (Lesson 04) is **signed** with a secret key
only this server knows — anyone who obtained that key could forge a
token claiming to be any user at all, so it must be long, random, and
never committed to Git. Generate one:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Expected output:** a 64-character string of random hex digits, e.g.
`a94c...` (yours will be different — that's the entire point). **Line by
line:** `secrets` is Python's standard-library module specifically for
generating cryptographically strong random values (unlike the plain
`random` module, which is not safe for anything security-related —
Lesson 02 revisits this distinction for bcrypt's own salt generation).
`token_hex(32)` returns 32 random bytes, rendered as 64 hex characters.

Now create your own `.env` from the committed template:

```bash
cp .env.example .env
```

Open `.env` in your editor and replace the placeholder `SECRET_KEY` line
with your own generated value from above, so it reads something like:

```
SECRET_KEY=a94c1e2b7f...   (your own 64-character value, not this one)
```

**Do not commit `.env`.** Check that it's ignored:

```bash
git check-ignore -v .env
```
**Expected:** a line of output naming this backend's `.gitignore` and the
`.env` pattern in it — confirming Git will never track this file. If
nothing prints, `.env` is *not* ignored — stop and fix `.gitignore` before
continuing (Lesson 11 explains exactly why this matters and what happens
when a real secret leaks into a Git history by accident).

### Step 7 — Run the API and confirm it starts

```bash
uvicorn app.main:app --reload
```

**Expected output:** the same startup lines Module 05/06 produced, ending
in `Application startup complete.` — with no `pydantic_core.ValidationError`
mentioning `secret_key`. (If you see that error, `.env` is missing, in the
wrong folder, or still has the placeholder value uncommented incorrectly —
see Troubleshooting below.)

## Verify your setup

```bash
curl http://127.0.0.1:8000/
```
**Expected:** `{"message":"QuestLog API. See /docs for interactive documentation."}`

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -d "username=player@questlog.local&password=dragon-slayer-1"
```
**Expected:** a JSON object shaped like
`{"access_token":"eyJ...","token_type":"bearer"}` — a real JWT, issued
for the demo account this module's `seed_if_empty()` created on first
startup. If you see this, every new package installed correctly, your
`.env`/`SECRET_KEY` is being read, the fresh database has the seeded demo
user, and password verification (Lesson 02) and token creation (Lesson 04)
both genuinely worked end to end. Copy the `access_token` value and try:

```bash
curl http://127.0.0.1:8000/api/quests \
  -H "Authorization: Bearer PASTE_YOUR_TOKEN_HERE"
```
**Expected:** a JSON array of five seeded quests. Then try the same
request with no `Authorization` header at all:

```bash
curl -i http://127.0.0.1:8000/api/quests
```
**Expected:** `HTTP/1.1 401 Unauthorized` and a body mentioning `"Not
authenticated"` — proof this route is now genuinely protected (Lesson 07
explains exactly which piece of code produces this specific message).

Stop the server (`Ctrl+C`) once everything above matches.

## Common mistakes & gotchas

- **`pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings / secret_key / Field required`** on startup. `.env` doesn't exist, isn't in the same folder as where you ran `uvicorn` (it must be `backend/.env`, since `SettingsConfigDict(env_file=".env")` in `app/config.py` resolves relative to your current working directory, not this file's own location), or `SECRET_KEY=` is missing/still commented out. Run `cat .env` and confirm the line is there, uncommented, with a real value.
- **`ModuleNotFoundError: No module named 'bcrypt'` (or `jwt`, or `pydantic_settings`)** even after `pip install -r requirements.txt`. Same root cause as every prior module's version of this error: the venv isn't actually active. Check for `(.venv)` in your prompt.
- **`alembic upgrade head` fails with `duplicate column name` or similar.** You likely skipped Step 4 and ran this module's migrations against a database that still has Module 06's old schema *plus* something already resembling this module's change. Drop and recreate the database (Step 4) and try again.
- **`curl`'s login request returns `422 Unprocessable Entity`.** Almost always a missing or malformed `-d` body — this endpoint expects form-encoded data (`username=...&password=...`), not JSON, unlike every other endpoint in this API (Lesson 06 explains exactly why). Double-check there's no stray `Content-Type: application/json` header being sent (some HTTP clients default to it) — `curl -d` sets `application/x-www-form-urlencoded` automatically as long as you don't override it.
- **Login succeeds, but every quest request returns `401` even with the token pasted in.** Check for a stray space, missing `Bearer ` prefix, or a token you copied with surrounding quote characters accidentally included. Lesson 04's self-check has you inspect a token's own structure, which makes spotting this kind of copy-paste error much easier.

## How this connects

Every lesson from here on assumes: the five packages above are installed,
a real `SECRET_KEY` exists in `.env`, and the database is the fresh one
this lesson created. Lesson 01 starts the actual conceptual material
(authentication vs. authorization) with no code yet; Lesson 02 is the
first lesson to use `bcrypt` directly, and Lesson 04 the first to use
`PyJWT` directly — both already installed and ready, thanks to this
lesson.

## Quick self-check

1. Why does this course use `bcrypt` directly instead of `passlib`, and PyJWT instead of `python-jose`? What specifically went wrong with each of those older choices?
2. Why does `SECRET_KEY` have no default value in `app/config.py`, unlike `DATABASE_URL` or `ALGORITHM`?
3. Why does `.env` need to be in `.gitignore`, while `.env.example` is committed?
4. Why did this lesson have you drop and recreate the `questlog` database rather than just running a new migration against the existing one from Module 06?
5. If `uvicorn app.main:app --reload` immediately crashes with a `pydantic_core.ValidationError` mentioning `secret_key`, what are the first two things you should check?
