# Exercise 03 — Add a Real Index (Guided)

**Concepts this exercise uses:**
Indexes ([`lessons/02-indexes-transactions-and-acid.md`](../../lessons/02-indexes-transactions-and-acid.md)),
SQLAlchemy models and queries ([`lessons/05-orms-and-sqlalchemy-basics.md`](../../lessons/05-orms-and-sqlalchemy-basics.md)),
Alembic migrations ([`lessons/07-alembic-migrations.md`](../../lessons/07-alembic-migrations.md)).

## Setup

Work directly in your own running copy of
`module-06-databases/project/questlog/backend/` (the one you set up in
Lesson 00 and have been running through this module's other exercises) —
this exercise makes a small, real, permanent change to it.

## What to do

1. In `app/db_models.py`, add an index to `Quest.quest_line_id` (per
   Lesson 02's reasoning: `repository.py`'s `list_quests` filters on this
   column when a `quest_line` query parameter is given, and foreign keys
   are *not* automatically indexed by Postgres). Add `index=True` to that
   column's `mapped_column(...)` call.
2. Generate a migration:
   ```bash
   alembic revision --autogenerate -m "add index on quests.quest_line_id"
   ```
3. **Open the generated migration file and read it before applying it** —
   confirm it contains an `op.create_index(...)` call and nothing you
   didn't expect.
4. Apply it: `alembic upgrade head`.
5. Verify the index actually exists in Postgres:
   ```bash
   psql -U questlog -d questlog -h localhost -c "\d quests"
   ```
   Look for a line under "Indexes:" referencing your new index.
6. Write a short SQLAlchemy query (a throwaway Python script, or directly
   in a Python REPL with the venv active) using `select(Quest).where(Quest
   .quest_line_id == some_id)` — confirm it still returns correct results
   (an index changes *performance*, not *correctness* — this step is about
   confirming that fact directly).

## Acceptance criteria

- [ ] `app/db_models.py` has the new `index=True`.
- [ ] A real migration file exists and was read before being applied, not blindly trusted.
- [ ] `\d quests` in `psql` shows the new index.
- [ ] You can explain what this index costs (Lesson 02) in exchange for what it speeds up.

## What to submit

In `solution/CHANGES.md`: the exact diff to `db_models.py`, the generated
migration file's full contents, and the `\d quests` output showing the new
index.

## Hints

- If `alembic revision --autogenerate` produces an empty migration (no
  `op.create_index`), double-check you actually saved `db_models.py` and
  that `index=True` is spelled correctly on the right column.
- If you're unsure what `\d quests` is, it's a `psql` client command (not
  SQL) that describes a table's structure, including its indexes.
