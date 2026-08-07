# Lesson 05 — ORMs and SQLAlchemy 2.0 Basics

## What you'll learn

- What an ORM is and the problem it solves.
- SQLAlchemy 2.0's declarative model syntax (`Mapped`, `mapped_column`).
- What an engine and a session are.
- How `relationship()` differs from a real foreign key column.

## Why this matters

Lessons 03–04 wrote raw SQL as text strings. That works, but string-built
SQL doesn't get autocomplete, doesn't get type-checked, and is exactly how
SQL-injection bugs happen when strings are built carelessly from user
input (a full security treatment is Module 07's job — for now, know that
writing queries as Python objects instead of raw strings is part of what
keeps you safe by default). An **ORM** (Object-Relational Mapper) lets you
describe tables as Python classes and write queries as Python expressions
instead.

## Prerequisites

Lessons 01–04, and Module 01's OOP lesson (classes, inheritance) — an ORM
class is a real Python class.

## The concept, explained simply

An ORM maps ("O-R-Maps") **rows** to Python **objects** and **tables** to
Python **classes**. Instead of writing
`SELECT * FROM quests WHERE id = '...'` as a string, you write
`select(Quest).where(Quest.id == quest_id)` — real Python, checked by your
editor, using the exact same `Quest` class your application already thinks
in terms of.

## The details

### Declaring a table as a class

Look at `app/db_models.py`'s `QuestLine` class (trimmed):

```python
class Base(DeclarativeBase):
    pass  # (defined once, in app/database.py)

class QuestLine(Base):
    __tablename__ = "quest_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    quests: Mapped[list["Quest"]] = relationship(back_populates="quest_line")
```

**Line by line:**
- `class QuestLine(Base):` — inheriting from `Base` (Module 01's
  inheritance, applied for real) registers this class with SQLAlchemy's
  metadata, so it's tracked as one of "this project's tables."
- `__tablename__ = "quest_lines"` — the actual Postgres table name this
  class maps to.
- `id: Mapped[str] = mapped_column(...)` — this is a *type-annotated class
  attribute* (Module 01, Lesson 09's type hints, applied for real):
  `Mapped[str]` tells your editor/type-checker "this attribute is a
  string," and `mapped_column(...)` is what actually tells SQLAlchemy
  *how* to store it (`String(36)`, primary key, a default value factory).
  This two-part syntax (`Mapped[T] = mapped_column(...)`) is exactly SQLAlchemy
  2.0's declarative style — different, more type-hint-friendly syntax than
  older 1.x tutorials you might find online use (Rule 7's version-pinning
  matters here specifically: if a tutorial shows `Column(String, primary_key=True)`
  with no `Mapped[...]` annotation, it's teaching the older 1.x style —
  don't mix the two).
- `relationship(back_populates="quest_line")` — see "relationship() vs a
  foreign key column" below.

### `mapped_column` options you'll actually use

`nullable=False` (Postgres will reject a row missing this value —
Lesson 02's Consistency, enforced), `default=_new_id` (a Python callable
run once per new row, *before* it's sent to Postgres — contrast with a
database-side default), `unique=True`/`UniqueConstraint(...)` (Postgres
itself rejects a duplicate — see `QuestLine`'s `UniqueConstraint("name",
...)`), `ForeignKey("other_table.id")` (declares the actual foreign key
constraint from Lesson 01).

### `relationship()` vs a foreign key column — a crucial distinction

`db_models.py`'s `Quest` class has *both*:
```python
quest_line_id: Mapped[str] = mapped_column(String(36), ForeignKey("quest_lines.id"), nullable=False)
quest_line: Mapped["QuestLine"] = relationship(back_populates="quests")
```
`quest_line_id` is a **real column** — Postgres stores it, Alembic
generates a migration for it (Lesson 07), and it's what the actual foreign
key constraint from Lesson 01 is built on. `quest_line` is a **pure
Python/ORM convenience** — it is not a database column at all, and Alembic
will never generate anything for it. It lets you write
`some_quest.quest_line.name` in Python and have SQLAlchemy automatically
run the lookup query behind the scenes, instead of you writing
`SELECT name FROM quest_lines WHERE id = ...` by hand every time. This is
exactly why `repository.py` uses `selectinload(QuestRow.quest_line)`
(covered more in Lesson 06) — to control *when* that extra lookup query
actually runs, rather than it happening unpredictably.

### Engine and Session

An **engine** (`app/database.py`'s `engine = create_async_engine(...)`) is
the object that knows how to actually open network connections to
Postgres and manages a pool of them for reuse — you create exactly one per
application, at startup. A **session** (`AsyncSession`) is a short-lived
workspace for one unit of work (Lesson 02's transaction) — you open one,
do some queries/changes, commit or roll back, then close it. `app/
database.py`'s `AsyncSessionLocal` is a *factory* that produces a fresh
session on demand — Lesson 06 shows exactly how FastAPI gets a fresh one
per request.

### A basic query, translated from SQL

Lesson 03's `SELECT title FROM quests WHERE done = false;` becomes:
```python
from sqlalchemy import select
stmt = select(Quest).where(Quest.done == False)  # noqa: E712 (SQLAlchemy overloads == specifically for this)
rows = (await session.scalars(stmt)).all()
```
`select(Quest)` builds a query object (it does not run anything yet —
exactly like Module 01's generators being lazy). `.where(Quest.done ==
False)` adds the filter — note `Quest.done == False` isn't actually
comparing booleans the normal Python way; SQLAlchemy overrides `==` on
mapped columns specifically so this reads naturally while actually
building a SQL `WHERE done = false` clause. `session.scalars(stmt)` is what
actually sends it to Postgres and gets results back, as `Quest` *instances*,
not raw tuples.

**Try it yourself:** find this exact pattern in `repository.py`'s
`list_quests` function and match each Python line back to the SQL it would
produce.

## Common mistakes & gotchas

- **Forgetting `nullable=False` and being surprised Postgres accepted a
  row with a missing value.** SQLAlchemy defaults `mapped_column` to
  nullable unless told otherwise — always be explicit.
- **Confusing a `relationship()` attribute with a real column** when
  writing a migration by hand — Alembic (Lesson 07) only ever looks at
  real columns.
- **Comparing with `is` instead of `==` on mapped columns.** `Quest.done
  is True` does not build a SQL clause the way `Quest.done == True` does —
  always use `==`/`!=` (or `.is_(...)`/`.is_not(...)` for explicit NULL
  checks) on mapped attributes, never `is`.

## How this connects

Lesson 06 shows this exact syntax wired into FastAPI's dependency
injection (Module 05, Lesson 04) via `get_db`. Lesson 07 shows how Alembic
reads these same classes to generate migrations automatically.

## Quick self-check

1. What problem does an ORM solve compared to writing SQL as raw strings?
2. What's the difference between `quest_line_id` and `quest_line` on the `Quest` class?
3. What is an engine, and how many does an application typically create?
4. Why does `Quest.done == False` work as a query filter instead of just evaluating to a Python bool immediately?
