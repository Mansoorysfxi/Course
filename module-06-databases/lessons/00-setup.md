# Lesson 00 — Setup: PostgreSQL and the Backend's New Dependencies

## What you'll learn

- How to install PostgreSQL on Windows and confirm it's actually running.
- How to create the specific database and user QuestLog's backend expects.
- How to install SQLAlchemy, Alembic, and an async PostgreSQL driver into the backend's existing venv.
- How to verify all of this actually works before touching any lesson content that depends on it.

## Why this matters

Module 05's QuestLog API worked entirely in memory — a Python `dict` that
Uvicorn kept in RAM and threw away every time the process stopped. That was
fine for learning FastAPI, but it's not how any real application works: a
real product cannot lose every user's data every time the server restarts,
redeploys, or crashes. This lesson installs the one new piece of
infrastructure — a real database server — that this entire module depends
on, before a single lesson explains *how* to talk to it.

## Prerequisites

Module 05 (the QuestLog API backend, and its venv/`pip` workflow from
Module 01) and Module 00 (Git Bash as this course's shell).

## The concept, explained simply

PostgreSQL ("Postgres") is a **database server** — a separate, standalone
program that runs continuously in the background, listens on a network
port (by default `5432`), and manages data stored permanently on disk. This
is a different shape of program than anything you've installed so far:
VS Code and Node are tools you run *on demand*; Postgres is a *service* —
something meant to always be running, the way a multiplayer game's
dedicated server process stays up between matches rather than starting
fresh for every request. Your FastAPI backend will be a *client* of this
server, exactly the client/server relationship Module 02 taught from
first principles — just now with Postgres as the "server" instead of a
website.

## The details

### Step 1 — Install PostgreSQL on Windows

Go to `https://www.postgresql.org/download/windows/` and download the
official installer (via EDB, the maintainer of the Windows build). At the
time this lesson was verified (August 2026), the current stable major
version is **PostgreSQL 18** (18.4) — PostgreSQL 19 exists only as a beta
and should not be used for this course. Run the installer:

1. Accept the default install location.
2. **Components:** keep "PostgreSQL Server," "pgAdmin 4" (a graphical tool
   for browsing your database — optional but useful), and "Command Line
   Tools" all checked.
3. **Data directory:** keep the default.
4. **Password:** you'll be asked to set a password for the default
   `postgres` superuser account. Pick something you'll remember — this is
   a local development password, not a production secret.
5. **Port:** keep the default, `5432`.
6. **Locale:** keep the default.
7. Finish the install. The installer registers PostgreSQL as a **Windows
   service** — meaning it starts automatically on boot and runs in the
   background with no window open, exactly like the "always running"
   framing above.

### Step 2 — Create QuestLog's database and user

Real applications never connect as the all-powerful `postgres` superuser —
they use a dedicated, narrowly-scoped user. Open Git Bash and connect using
`psql` (Postgres's command-line client, installed in Step 1):

```bash
psql -U postgres -h localhost
```

Enter the password from Step 1 when prompted. Your prompt changes to
`postgres=#` — you're now inside an interactive SQL session. Run:

```sql
CREATE USER questlog WITH PASSWORD 'questlog_dev_password';
CREATE DATABASE questlog OWNER questlog;
\q
```

**Line by line:** `CREATE USER` makes a new login role named `questlog`
with the given password (matching exactly what `app/config.py`'s
`DEFAULT_DATABASE_URL` already expects — see that file). `CREATE DATABASE
... OWNER questlog` creates an empty database named `questlog`, owned by
that user, so it has full permissions on it without being a superuser.
`\q` quits `psql` back to your regular shell prompt — commands starting
with a backslash are `psql`'s own client commands, not SQL.

### Step 3 — Install the new Python packages into the backend's venv

```bash
cd module-06-databases/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

This installs `fastapi`, `uvicorn`, and the three packages new to this
module: `sqlalchemy[asyncio]` (the ORM, with the extra needed for async
support), `alembic` (migrations), and `asyncpg` (the actual network driver
that speaks Postgres's wire protocol — SQLAlchemy itself never talks to
Postgres directly, it delegates to a driver like this one).

## Verify your setup

```bash
psql -U questlog -d questlog -h localhost -c "SELECT 1;"
```
Enter `questlog_dev_password` when prompted. **Expected output:** a small
table showing a single row with `1` in it — proof the `questlog` user can
authenticate and query the `questlog` database.

```bash
python -c "import sqlalchemy, alembic, asyncpg; print(sqlalchemy.__version__)"
```
**Expected output:** a version string starting with `2.0` (e.g. `2.0.51`)
and no import errors — confirming all three new packages installed
correctly into the active venv.

## Common mistakes & gotchas

- **`psql: error: connection to server ... failed`** — the PostgreSQL
  service isn't running. Open Windows' Services app (`services.msc`),
  find "postgresql-x64-18," and confirm its status is "Running." Start it
  if not.
- **`FATAL: password authentication failed for user "questlog"`** — a typo
  in the password either when you created the user or in
  `app/config.py`'s `DEFAULT_DATABASE_URL`. They must match exactly, or you
  must set the `DATABASE_URL` environment variable yourself to override it.
- **Port `5432` already in use.** Something else (an old Postgres install,
  Docker container, etc.) is already listening there. Either stop it or
  reconfigure this install to a different port and update `DATABASE_URL`
  to match.
- **`ModuleNotFoundError: No module named 'sqlalchemy'`** after `pip
  install`. Almost always means the venv wasn't actually activated before
  running `pip install` — check your prompt shows `(.venv)` at the start,
  per Module 01's venv lesson.

## How this connects

Every lesson from here on assumes PostgreSQL is running and the `questlog`
database/user exist. Lesson 01 starts explaining *why* this exists and what
a relational database actually is; Lesson 05 onward is where your Python
code actually starts talking to the server you just installed.

## Quick self-check

1. What's the difference between installing a program you run on demand (like `tsc`) and installing a service (like PostgreSQL)?
2. Why did you create a dedicated `questlog` user instead of just using `postgres` for everything?
3. What does `asyncpg` do that SQLAlchemy itself doesn't?
4. If `psql -U questlog -d questlog` fails with a password error, what's the first thing to check?
