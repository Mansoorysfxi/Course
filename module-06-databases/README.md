# Module 06 — Databases

**Phase:** 2 — Backend Engineering
**Estimated time:** 12–16 hours
**Verified against:** PostgreSQL 18.4, SQLAlchemy 2.0.51, Alembic 1.19.0, asyncpg 0.31.0 — all current as of August 2026.

## What this module is

Module 05's QuestLog API worked, but it forgot everything the moment
Uvicorn restarted — a Python `dict` living entirely in RAM. This module
replaces that with a real database: PostgreSQL, accessed through
SQLAlchemy (an ORM — Object-Relational Mapper) and managed with Alembic
(a migration tool). By the end, QuestLog's data survives restarts,
crashes, and redeploys, exactly like any real production application.

This is also the module where you learn SQL itself, from scratch — not
just "how to use an ORM," but what's actually happening underneath it,
so nothing about SQLAlchemy ever feels like unexplained magic.

## What you'll be able to do after this module

- Explain the relational model (tables, rows, keys, relationships) and why it beats storing everything as loose files or dicts.
- Write real SQL: `SELECT`/`INSERT`/`UPDATE`/`DELETE`, `JOIN`s, `GROUP BY`, and explain what an index and a transaction actually do.
- Use SQLAlchemy 2.0's declarative models and async session pattern, wired into FastAPI's dependency injection.
- Generate, read, and apply Alembic migrations — and know why hand-editing a production schema is a bad idea.
- Explain when a document store or key-value store fits better than a relational database.
- Design a normalized schema from a set of requirements, and justify every table in it.

## Prerequisites

Module 05 (the QuestLog API and its FastAPI/Pydantic patterns), Module 01
(Python OOP, decorators/context managers, venv/pip), and Module 00 (Git
Bash as this course's shell).

## Module structure

```
module-06-databases/
├── README.md                              ← you are here
├── lessons/
│   ├── 00-setup.md                        ← install PostgreSQL, create the questlog db/user
│   ├── 01-why-a-database-and-the-relational-model.md
│   ├── 02-indexes-transactions-and-acid.md
│   ├── 03-sql-select-insert-update-delete.md
│   ├── 04-joins-and-group-by.md
│   ├── 05-orms-and-sqlalchemy-basics.md
│   ├── 06-sqlalchemy-with-fastapi.md
│   ├── 07-alembic-migrations.md
│   ├── 08-nosql-overview.md
│   ├── 09-normalization-and-schema-design.md
│   └── 10-designing-questlogs-schema.md
├── exercises/
│   ├── 01-raw-sql-practice/
│   ├── 02-joins-and-aggregates/
│   ├── 03-add-an-index/
│   ├── 04-alembic-migration/
│   └── 05-new-stats-endpoint/
├── project/
│   ├── BRIEF.md                            ← capstone: run + verify + explain real persistence
│   └── questlog/                           ← QuestLog, copied forward from Module 05, now Postgres-backed
│       ├── frontend/                         ← unchanged from Module 05
│       └── backend/                           ← the real database layer added this module
└── CHECKLIST.md
```

Read the lessons in order — Lesson 00's setup is not optional, everything
after it assumes PostgreSQL is running. Lessons 01–04 teach SQL and the
relational model with no ORM in sight; Lessons 05–07 introduce SQLAlchemy
and Alembic; Lesson 08 is a conceptual detour into NoSQL; Lessons 09–10
bring it all together on QuestLog's actual schema.

## How to work through this module

Follow the workflow in the [root README](../README.md). Note this
module's capstone (`project/BRIEF.md`) is shaped a little differently from
prior modules — it has you run, verify, and explain the already-built
database-backed QuestLog rather than build it from a blank file, because
the hands-on coding practice for this module's concepts is concentrated in
Exercises 03–05, which modify this exact codebase directly.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's finished
`project/questlog/` is exactly what Module 07 will copy forward and add
real authentication to.
