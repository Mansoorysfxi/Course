# Reference Solution — Two Real Migrations, Chained

Don't read this until you've made a genuine attempt.

## Migration A — `..._add_notes_to_quests.py`

```python
def upgrade() -> None:
    op.add_column('quests', sa.Column('notes', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('quests', 'notes')
```

## Migration B — `..._add_due_date_to_quests.py`

```python
def upgrade() -> None:
    op.add_column('quests', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column('quests', 'due_date')
```

## `alembic history` (abbreviated, newest first)

```
<rev-B> (head), Add due_date to quests
<rev-A>, Add notes to quests
<rev-index>, Add index on quests.quest_line_id
<rev-initial>, Initial schema: users, quest_lines, quests
```

## Step 8 — downgrade/upgrade cycle

**After `alembic downgrade -1`:**
```
Column           |  Type
...
notes            | character varying
```
(`due_date` is gone; `notes` remains — proving exactly one migration was
undone, not two.)

**After `alembic upgrade head` again:**
```
Column           |  Type
...
notes            | character varying
due_date         | timestamp with time zone
```

## Notes on grading this yourself

- Both migrations being nullable additions is the important design choice
  here — this is exactly why Lesson 09's `owner_id` discussion called out
  a *non-nullable* addition on a populated table as the harder case; these
  two were safe by comparison specifically because they're optional.
- If `alembic history` showed a branch (two migrations both claiming the
  same `down_revision`), that's a sign a model change was generated twice
  without applying the first — Alembic's `alembic merge` command resolves
  this, but for this exercise the fix is simpler: delete the stray
  unapplied migration file and regenerate cleanly.
