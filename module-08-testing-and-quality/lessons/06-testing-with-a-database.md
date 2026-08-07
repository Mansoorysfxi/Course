# Lesson 06 — Testing With a Database

**A note on this lesson's central decision, verified through real
research (August 2026), not memory:** current guidance for testing an
async FastAPI + SQLAlchemy app converges on three broadly workable
strategies, each with genuine trade-offs: (1) an in-memory SQLite database
via `aiosqlite`, recreated fresh per test; (2) a dedicated, real Postgres
database used only for tests, with either full schema recreation or a
transaction-rollback-per-test pattern; (3) `pytest-async-sqlalchemy` or
similar plugins standardizing either of the above. FastAPI's own
historical testing tutorial has used SQLite directly; more recent
community guidance increasingly favors a dedicated Postgres test database
specifically to avoid SQLite/Postgres **dialect** (Lesson 06's own term,
defined below) differences producing a false "it passed" result. This
module picks **option 1 (in-memory SQLite)** for its own capstone and
exercises — the reasoning, and the honest cost of that choice, is this
lesson's main subject, not a footnote.

## What you'll learn

- What a **test database** is, and the real trade-off between using a
  fast, fake one (SQLite) versus a slower, more realistic one (a real,
  separate Postgres instance).
- Exactly how this module's `db_session` fixture builds a completely
  fresh, empty database for every single test, and what `StaticPool`
  is for.
- What a database **dialect** is, and specifically which QuestLog schema
  features would (and would not) actually be affected by testing against
  SQLite instead of the real Postgres.
- Why this module's tests use `Base.metadata.create_all` directly instead
  of running Alembic migrations (Module 06) against the test database.
- How to actually write ownership-isolation and validation tests against
  a real (if temporary) database — reading this module's own
  `backend/tests/test_quests.py`.

## Why this matters

Every backend integration test in this module (Lesson 05) needs *some*
real database behind it — `app/repository.py`'s functions execute real
SQL (via SQLAlchemy), and there is no meaningful way to test "does
`create_quest` actually insert a row that `list_quests` can then find"
without a database that can actually store and retrieve a row. The
question this lesson answers isn't *whether* to use a database in tests
— it's *which kind*, and what you give up either way.

## Prerequisites

Module 06 (databases, SQLAlchemy, Alembic) — this lesson assumes you
understand what a table, a schema, and a migration are, and specifically
what `Base.metadata` (Module 06's own term) represents. Lesson 05
(testing FastAPI endpoints, `app.dependency_overrides`) — this lesson
completes that lesson's `client`/`db_session` fixture pair.

## The concept, explained simply

Think of QuestLog's real Postgres database the way you'd think about a
real multiplayer game server during development: heavyweight, genuinely
realistic, but slow and inconvenient to spin up fresh, from scratch, for
every single automated check you want to run. A **test database** is the
equivalent of a lightweight, disposable, local-only practice arena you
spin up (and tear down) for one specific test, instead of connecting to
the real, shared server every time — same fundamental rules, same
gameplay logic being exercised, but disposable and fast, precisely
because nothing about it needs to persist or be "real" beyond the single
test currently running.

The genuine trade-off, stated honestly: a disposable practice arena is
faster and needs no setup, but if the *real* server has a physics quirk
the practice arena doesn't reproduce, testing only in the practice arena
could let a bug through that only shows up on the real server. That's
exactly the SQLite-vs-Postgres trade-off this lesson is about.

## The details

### What a "dialect" is, and why it's the crux of this decision

**SQL dialect** — every real database (Postgres, SQLite, MySQL...)
implements the *core* of SQL similarly, but each has its own specific
extensions, data types, and edge-case behaviors that don't perfectly
match the others. SQLAlchemy's whole job (Module 06) is translating your
Python-level `select(...)`/`insert(...)` calls into the *correct* SQL for
whichever real database you've connected it to — which is exactly what
makes swapping SQLite in for Postgres in tests possible at all: the same
Python code (`app/repository.py`, completely unmodified) produces
SQLite-flavored SQL when connected to a SQLite engine, and
Postgres-flavored SQL when connected to a real Postgres engine.

**The honest risk:** if your actual application code depended on a
Postgres-*specific* feature (a `JSONB` column, a Postgres-specific
function, certain very particular constraint-violation behaviors),
testing only against SQLite could report "all green" while that
Postgres-specific behavior is silently broken or entirely untested — a
real, documented category of false confidence, and the strongest
argument for a dedicated Postgres test database instead.

**Why this module accepts that risk anyway, for QuestLog specifically:**
look at `backend/app/db_models.py` (Module 06/07's real schema) —
`String`, `Boolean`, `DateTime(timezone=True)`, a `ForeignKey`, a
`UniqueConstraint`. Every one of these is a genuinely standard SQL
concept with a direct, faithful SQLite equivalent — nothing in this exact
schema uses a Postgres-specific column type or feature. For *this*
app's actual schema, SQLite and Postgres behave identically for
everything this module's tests check. That is a real, specific
justification — not "SQLite is generally fine" as an unexamined rule —
and it is also why this lesson tells you, explicitly, to re-examine this
decision yourself the moment QuestLog's schema ever grows a genuinely
Postgres-specific feature (Module 14's `pgvector` columns, for a real
future example, would **not** have a faithful SQLite equivalent at all —
if you're following this course that far, that module's own tests will
need to revisit this exact trade-off).

**The other reason this module picks SQLite: zero extra infrastructure.**
A dedicated Postgres test database needs a real, running Postgres
instance the test suite can reach — one more thing that has to be
installed, configured, and kept running correctly on every machine (and
in CI, Module 11) that ever runs this test suite. An in-memory SQLite
database needs nothing beyond the `aiosqlite` Python package already
installed in Lesson 00 — it exists purely inside the test process's own
memory and disappears completely the instant that process ends.

### The fixture, explained completely

Open `backend/tests/conftest.py` — you've already read the `client`
fixture (Lesson 05); here is `db_session`, in full:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSessionLocal() as session:
        yield session

    await engine.dispose()
```

- **`"sqlite+aiosqlite:///:memory:"`** — a SQLAlchemy connection URL
  (Module 06's format: `dialect+driver://...`), where `:memory:` is
  SQLite's own special filename meaning "don't write to a real file on
  disk at all — keep this database entirely in RAM." The moment nothing
  refers to it anymore, it's gone, with zero cleanup needed.
- **`connect_args={"check_same_thread": False}`** — a SQLite-specific
  safety check, normally on by default, that forbids using one
  connection from more than one thread. This app's async code can
  genuinely hand control between different points without necessarily
  staying on one OS thread the whole time (Module 01's async/event-loop
  lesson), so this specific SQLite guard needs to be disabled for async
  use — a narrow, well-documented exception, not a general "turn off
  safety checks" habit.
- **`poolclass=StaticPool`** — this is the one genuinely subtle piece.
  Every SQLAlchemy engine keeps a **connection pool** (Module 06) — by
  default, a pool willingly opens a *new* real connection whenever one is
  needed and none is idle. For a real Postgres database, that's exactly
  right: many real, independent connections to the same real, persistent
  database, all seeing the same data. But an **in-memory** SQLite
  database lives and dies with the *single connection* that created it —
  a second connection would get a second, completely separate, empty
  database, not the same one. `StaticPool` overrides the pool's usual
  behavior to always hand back the exact same one connection, no matter
  how many separate times something asks the pool for one — which is
  precisely what makes a single in-memory database stay the *same*
  database throughout one whole test.
- **`engine.begin()` → `connection.run_sync(Base.metadata.create_all)`**
  — `Base.metadata` (Module 06) is SQLAlchemy's own live record of every
  table every ORM class (`User`, `QuestLine`, `Quest`,
  `app/db_models.py`) defines. `create_all` is a *synchronous* SQLAlchemy
  operation (it predates async SQLAlchemy entirely) — `run_sync` is the
  bridge that lets an async connection run it anyway, the same kind of
  sync/async bridge Module 06's own Alembic `env.py` uses for exactly the
  same reason.
- **`async_sessionmaker(engine, ...)` → `yield session`** — builds one
  real session bound to this fresh, empty, in-memory database, and hands
  it to the test — everything after `yield` (`engine.dispose()`) is
  teardown, run once the test finishes, exactly as Lesson 02 taught.

**The net effect:** every single test that asks for `db_session` (or,
transitively, `client`) gets its own brand-new SQLite database, with
every table already created and completely empty, guaranteed. No test
can ever see another test's leftover data, because there is no shared
database at all — the strongest, simplest possible form of test
isolation, at the cost of recreating the schema fresh, every single
time (Lesson 02's `scope="function"` trade-off, made concrete).

### Why `create_all`, not Alembic migrations, in tests

Module 06 taught Alembic migrations as the *only* correct way to change a
real, persistent database's schema over time, specifically because a
real database already has real rows that a raw `create_all` would never
touch or protect. A brand-new, empty, in-memory test database has no such
history to protect — there's nothing to migrate *from*. `create_all`
simply builds every table `Base.metadata` currently describes, once,
directly from the current models — the right, simpler tool for a
database that starts empty and is thrown away moments later, every
single time.

### Reading this module's real ownership-isolation tests

Open `backend/tests/test_quests.py`'s
`test_one_user_cannot_get_another_users_quest_by_id`:

```python
async def test_one_user_cannot_get_another_users_quest_by_id(client, signup_and_login):
    hero_headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
    hero_quest = await _create_quest(client, hero_headers, title="Hero's Secret Quest")

    villain_headers = await signup_and_login(client, "villain@example.com", "evil-plan-123")
    response = await client.get(f"/api/quests/{hero_quest['id']}", headers=villain_headers)

    assert response.status_code == 404
```

Every piece here is now fully explained across Lessons 02, 05, and this
lesson: `signup_and_login` (a factory fixture, Lesson 02) creates two
genuinely separate accounts, in the *same* fresh test database
`db_session` created for this one test; `_create_quest` (a plain helper
function, not a fixture — Lesson 02's "helper vs. fixture" distinction)
creates a real quest, owned by the hero account, via a real `POST`
request through the real app; the villain's own, separately issued token
is then used to try to read that exact quest by its real id. The `404`
this test asserts is not a guess about what *should* happen — it's a
direct, executable check of Module 07's own deliberate design decision
(`app/repository.py`'s `get_quest` docstring: combine the id and
owner-id check in one `WHERE` clause, so a quest belonging to someone
else looks, from the outside, identical to a quest that doesn't exist at
all).

## Common mistakes & gotchas

- **`sqlite3.OperationalError: no such table: quests`.** The
  `Base.metadata.create_all` step never ran, or ran against a
  *different* connection than the one the test's queries later used — a
  symptom, specifically, of forgetting `poolclass=StaticPool` on an
  in-memory SQLite engine (Step "`poolclass=StaticPool`" above): without
  it, `create_all` and your test's later queries can silently end up
  talking to two different, both otherwise-empty, in-memory databases.
- **Tests that pass individually but fail when run all together (or vice
  versa).** A strong sign that a fixture isn't actually giving fresh
  isolation the way this lesson's `db_session` does — check for any
  fixture scoped wider than the default `function` scope (Lesson 02)
  that's quietly sharing state across tests that assume they don't.
- **Forgetting that SQLite and Postgres really can disagree, for a
  feature this app doesn't currently use.** If you ever add a
  Postgres-specific column type or feature to `db_models.py`, this
  lesson's entire justification for SQLite needs re-examining for that
  specific feature — don't assume "our tests still pass" automatically
  means "this new Postgres-specific thing works," if the tests never ran
  against real Postgres at all.
- **Confusing "the test database is fresh" with "the real, running dev
  database is fresh."** This module's tests never touch the real
  Postgres database `app/config.py` defaults to at all — running the
  test suite has zero effect on whatever quests you've created by hand
  while using the actual running app.

## How this connects

Lessons 05–06 together are the complete story behind this module's real
integration tests. Lesson 07 shifts to the frontend, where an analogous
question comes up in a different shape: should a component test render
against a *real* backend, or a faked one? — answered there with mocking
(Lesson 03) rather than a database at all, since a frontend component
never talks to a database directly in this app's architecture.

## Quick self-check

1. What is a SQL "dialect," and specifically why is it safe for QuestLog's *current* schema to be tested against SQLite instead of real Postgres — what would make that unsafe for some *other* schema?
2. What does `poolclass=StaticPool` actually fix, and what specifically would go wrong for an in-memory SQLite test database without it?
3. Why does this module's test setup use `Base.metadata.create_all` directly instead of running Alembic migrations, when Module 06 taught migrations as the correct way to change a schema?
4. Walk through `test_one_user_cannot_get_another_users_quest_by_id` and explain, in your own words, exactly which real application code decision (and which file) makes the `404` assertion correct.
5. Name one concrete situation, specific to a *future* QuestLog feature, where this lesson's SQLite decision would need to be revisited.
