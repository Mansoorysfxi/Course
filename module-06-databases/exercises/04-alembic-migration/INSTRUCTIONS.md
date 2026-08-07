# Exercise 04 — Two Real Migrations, Chained (Guided/Independent)

**Concepts this exercise uses:**
Alembic migrations ([`lessons/07-alembic-migrations.md`](../../lessons/07-alembic-migrations.md)),
SQLAlchemy models ([`lessons/05-orms-and-sqlalchemy-basics.md`](../../lessons/05-orms-and-sqlalchemy-basics.md)),
schema design reasoning ([`lessons/09-normalization-and-schema-design.md`](../../lessons/09-normalization-and-schema-design.md)).

## Setup

Same as Exercise 03 — work directly in your own running
`project/questlog/backend/`. This exercise assumes Exercise 03's index
migration is already applied (`alembic upgrade head` up to date).

## What to do

**Migration A:**
1. Add a nullable `notes: Mapped[str | None] = mapped_column(String,
   nullable=True)` field to the `Quest` class in `app/db_models.py`.
2. Generate a migration (`alembic revision --autogenerate -m "add notes to
   quests"`), read it, apply it (`alembic upgrade head`).
3. Confirm via `psql`'s `\d quests` that the column exists.
4. Using `psql`, manually set a note on one existing quest
   (`UPDATE quests SET notes = 'test note' WHERE id = '...';`), then
   confirm a SQLAlchemy query (a quick script or REPL) reads it back
   correctly.

**Migration B:**
5. Add a second nullable field: `due_date: Mapped[datetime | None] =
   mapped_column(DateTime(timezone=True), nullable=True)` (you'll need to
   import `datetime` if not already imported).
6. Generate a *second* migration, read it, apply it.
7. Run `alembic history` and confirm you see both migrations chained in
   order (each one's `down_revision` pointing at the previous one).
8. **Now roll back just the second one:** `alembic downgrade -1`, confirm
   via `\d quests` that `due_date` is gone but `notes` is still there, then
   `alembic upgrade head` again to restore it.

## Acceptance criteria

- [ ] Two separate migration files exist, correctly chained (`alembic history` shows a single line, no branches).
- [ ] Both columns are nullable — an additive-only change, which is why this could be done safely on a table that already has rows (Lesson 09's `owner_id` discussion explained why the *opposite* — a non-nullable addition — is much harder).
- [ ] Step 8's downgrade/upgrade cycle was actually performed and confirmed via `\d quests`, not just assumed to work.

## What to submit

In `solution/MIGRATION_LOG.md`: both migration files' full contents, the
`alembic history` output, and the before/after `\d quests` excerpts from
step 8's downgrade/upgrade cycle.

## Hints

- If `alembic history` shows two unconnected chains instead of one, you
  likely branched — this can happen if you generated a migration, then
  reverted your model change and regenerated instead of building on top of
  what already existed. Ask for a hint if this happens rather than deleting
  migration files blindly.
- `downgrade -1` always undoes exactly the most recently applied migration
  — not migration "B" specifically by name, so make sure B really is the
  most recent before running it.
