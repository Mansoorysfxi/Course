# Reference Solution — Add a Real Index

Don't read this until you've made a genuine attempt.

## 1. `app/db_models.py` diff

```diff
     quest_line_id: Mapped[str] = mapped_column(
-        String(36), ForeignKey("quest_lines.id"), nullable=False
+        String(36), ForeignKey("quest_lines.id"), nullable=False, index=True
     )
```

## 2. Generated migration (`alembic/versions/..._add_index_on_quests_quest_line_id.py`)

```python
def upgrade() -> None:
    op.create_index(
        op.f('ix_quests_quest_line_id'), 'quests', ['quest_line_id'], unique=False
    )

def downgrade() -> None:
    op.drop_index(op.f('ix_quests_quest_line_id'), table_name='quests')
```

## 3. `\d quests` output (relevant excerpt)

```
Indexes:
    "quests_pkey" PRIMARY KEY, btree (id)
    "ix_quests_quest_line_id" btree (quest_line_id)
```

## Notes on grading this yourself

- The index name `ix_quests_quest_line_id` is Alembic/SQLAlchemy's default
  naming convention (`ix_<table>_<column>`) — yours should match this
  pattern unless you customized it, which this exercise didn't ask for.
- If your migration's `upgrade()` is empty, `index=True` likely wasn't
  saved before running `--autogenerate` — re-save and regenerate.
- The cost/benefit to be able to explain: this index speeds up
  `WHERE quest_line_id = ...` lookups (used by `list_quests`'s
  `quest_line` filter) at the cost of a small amount of extra work on every
  `INSERT`/`UPDATE`/`DELETE` touching the `quests` table, per Lesson 02.
