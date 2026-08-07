# Lesson 06 — Wiring SQLAlchemy Into FastAPI

## What you'll learn

- How `get_db` provides one fresh database session per HTTP request.
- Why every route function became `async def` with a `session` parameter.
- Exactly what changed, function by function, between Module 05's `store.py` and this module's `repository.py`.
- Why `lifespan` replaced `@app.on_event(...)` for startup seeding.

## Why this matters

This is where Lessons 00–05's separate pieces (Postgres running, tables,
SQLAlchemy classes) become an actual working API. Understanding this
wiring is what lets you debug "why is my session empty" or "why did my
route hang" bugs later — both come directly from misunderstanding this
lesson's content.

## Prerequisites

Lesson 05 (engine/session), and Module 05 Lesson 04 (`Depends`, dependency injection).

## The concept, explained simply

Every incoming HTTP request needs its *own* database session — two
requests running at the same time must not share one, or their transactions
(Lesson 02) would interfere with each other. FastAPI's dependency injection
(`Depends`, which you already learned handles "give this route something it
needs, freshly, per-request") is the natural mechanism for this: `get_db`
is a dependency that hands each route a session, and guarantees it's
closed when the request finishes — even if the route raised an exception.

## The details

### `get_db`, read closely

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```
This is a **generator-based dependency** — FastAPI recognizes `yield`
(instead of `return`) as "run everything before `yield`, hand the yielded
value to the route, then after the route finishes (successfully *or* with
an exception), run everything after `yield`." Here there's nothing after
`yield` because `async with` already guarantees the session closes when its
block exits, exception or not — the exact same guaranteed-cleanup job
Module 01 Lesson 10's context managers do generally, now applied to a
database session instead of a file handle.

### The `DbSession` alias

```python
DbSession = Annotated[AsyncSession, Depends(get_db)]
```
This is a plain Python type alias — not new FastAPI syntax — that lets
every route write `session: DbSession` instead of spelling out
`session: Annotated[AsyncSession, Depends(get_db)]` fresh every time.
Purely a readability convenience.

### The swap, concretely: `store.py` → `repository.py`

Compare Module 05's version of `list_quests`:
```python
def list_quests(done: bool | None = None) -> list[Quest]:
    quests = list(_store.values())
    if done is not None:
        quests = [q for q in quests if q.done == done]
    return quests
```
against this module's:
```python
async def list_quests(session: AsyncSession, done: bool | None = None, ...) -> list[Quest]:
    stmt = select(QuestRow).options(selectinload(QuestRow.quest_line))
    if done is not None:
        stmt = stmt.where(QuestRow.done == done)
    ...
    rows = (await session.scalars(stmt)).all()
    return [_to_pydantic(row) for row in rows]
```
Three real differences, and nothing else: (1) `async def` and `await` —
every real database call is I/O (Module 01 Lesson 11's async lesson,
applied for real: talking to Postgres over the network is exactly the kind
of "waiting on something slow" async exists for), (2) a `session`
parameter, since unlike a global dict, a database connection must be
explicitly passed around, (3) the filtering happens by building a SQL
`WHERE` clause instead of a Python list comprehension — Postgres does the
filtering, not your application code, which matters once a table has
millions of rows Python would be slow to loop over.

### `selectinload` — controlling when the extra query happens

Lesson 05 mentioned `relationship()` triggers an extra lookup query when
accessed. `selectinload(QuestRow.quest_line)` tells SQLAlchemy: "load every
matching quest's `quest_line` in one *additional* batched query, right
now, before returning results" — rather than one separate query *per quest*
the first time each one's `.quest_line` is touched (a classic ORM
performance trap called the "N+1 query problem": 1 query for the quests,
then N more, one per quest, for their quest lines). `_to_pydantic` can then
safely read `row.quest_line.name` without triggering a surprise query.

### `_to_pydantic` — the seam between storage and API contract

```python
def _to_pydantic(row: QuestRow) -> Quest:
    return Quest(id=row.id, title=row.title, ..., quest_line=row.quest_line.name, ...)
```
This one function is the entire boundary between "how it's stored"
(`db_models.py`'s `QuestRow`, with a `quest_line_id` foreign key) and "what
the frontend sees" (`models.py`'s `Quest`, with a plain `quest_line` name
string). **The contract doesn't change**: the frontend never learns that a
`QuestLine` table exists at all — it still receives exactly the same JSON
shape Module 05 always returned.

### `lifespan` instead of `@app.on_event("startup")`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        await repository.seed_if_empty(session)
    yield
```
FastAPI's own current documentation recommends `lifespan` (an
`asynccontextmanager`, Module 01 Lesson 10 again) over the older
`@app.on_event("startup")` decorator Module 05 might have reached for —
confirmed while writing this module against FastAPI's current docs.
Everything before `yield` runs once at startup; anything after `yield`
would run once at shutdown (nothing needed here).

## Common mistakes & gotchas

- **Forgetting `await` on an async database call.** This doesn't crash
  loudly the way you might expect — you get back a coroutine object
  (Module 01, Lesson 11) instead of a result, and confusing errors later
  when you try to use it as if it were the real value.
- **Sharing one session across requests.** Never store a session at module
  level and reuse it — always get a fresh one via `Depends(get_db)` per
  request, which is exactly what makes concurrent requests safe.
- **Expecting `relationship()` attributes to "just work" without
  `selectinload` (or accessing them outside an active session)**, causing
  a `MissingGreenlet`/lazy-load error in async SQLAlchemy specifically —
  always load what you'll need up front in async code.

## How this connects

Lesson 07 covers how the *tables* these classes describe actually get
created in Postgres (Alembic), separate from this lesson's concern of how
the *running app* talks to tables that already exist.

## Quick self-check

1. Why does `get_db` use `yield` instead of `return`?
2. Name the three concrete differences between Module 05's `store.py` functions and this module's `repository.py` functions.
3. What problem does `selectinload` solve, and what would happen without it?
4. Why did `_to_pydantic` need to exist at all, instead of returning `QuestRow` objects directly from routes?
