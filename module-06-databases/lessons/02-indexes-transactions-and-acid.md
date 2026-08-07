# Lesson 02 — Indexes, Transactions, and ACID

## What you'll learn

- What an index physically is, and why it makes lookups faster.
- The cost an index has (it's not a free win).
- What a transaction is and why grouping operations together matters.
- What ACID stands for and what each letter actually guarantees.

## Why this matters

Once QuestLog has real users and thousands of quests (Module 07 onward),
"find all quests for this user" needs to stay fast, and "create a quest and
its quest line together" needs to either fully succeed or fully fail — never
half-happen. Indexes and transactions are the two mechanisms Postgres gives
you for exactly those two problems.

## Prerequisites

Lesson 01 (tables, rows, keys).

## The concept, explained simply

**Index:** imagine a textbook with no index at the back — to find every
page mentioning "inventory system," you'd have to read every single page.
An index at the back of the book (sorted alphabetically, pointing to exact
page numbers) turns that into "look up the word, jump straight there." A
database **index** does exactly this for a column: instead of scanning
every row in a table to find matches (a "sequential scan"), Postgres
maintains a separate, sorted structure pointing directly at the rows that
have a given value, so a lookup by that column is dramatically faster once
a table has many rows.

**Transaction:** imagine a two-step save — updating a player's gold *and*
removing the item they just bought. If your game crashed exactly between
those two writes, the player could end up with the gold gone and the item
never received. A **transaction** groups multiple database operations into
one all-or-nothing unit — either every operation inside it takes effect, or
(if anything fails, or you explicitly cancel) none of them do. There is no
"halfway committed" state visible to anyone else.

## The details

### What an index physically is

An index is a genuinely separate data structure Postgres maintains
alongside a table — commonly a **B-tree**, a sorted tree structure that
lets Postgres find a matching row in roughly `log(n)` steps instead of
`n` steps (n = number of rows). Every primary key automatically gets an
index for free — that's part of why `WHERE id = '...'` lookups (Lesson 03)
stay fast even as a table grows. Foreign key columns are *not* automatically
indexed by Postgres (a common surprise) — if you'll frequently query
`WHERE quest_line_id = '...'` (exactly what `repository.py`'s `list_quests`
does when filtering by quest line), adding an explicit index on that
column is a real, common practice, covered as an exercise in this module.

```sql
CREATE INDEX idx_quests_quest_line_id ON quests (quest_line_id);
```

**The cost:** an index isn't free. Postgres must update every index on a
table every time a row is inserted, updated, or deleted — more indexes
means slower writes, in exchange for faster reads on the indexed columns.
This is a genuine trade-off, not "always add more indexes" — index the
columns you actually filter/sort/join on frequently, not every column.

**Try it yourself:** predict which of these QuestLog queries would benefit
most from an index, before reading Lesson 04: "get one quest by id,"
"list all quests for a given quest line," "list all quests, no filter."
(The first already benefits from the automatic primary-key index; the
second benefits from an index on `quest_line_id`; the third can't be sped
up by an index at all, since it has to return every row regardless.)

### Transactions and commit/rollback

Every one of `repository.py`'s write functions follows the same shape:

```python
session.add(row)
await session.commit()
```

Everything you do to a `session` (adds, updates, deletes) accumulates as a
**pending transaction** until you call `commit()` — at which point Postgres
applies all of it, atomically, or none of it if something fails partway
through. If an exception is raised before `commit()` runs, nothing you did
in that session takes effect at all — this is what `await session.
rollback()` does explicitly, and what happens implicitly if a session is
abandoned without committing.

`_get_or_create_quest_line` (Lesson 05/06 cover this function in full) is a
good concrete example of *why* this matters: it might insert a brand-new
`QuestLine` row, then the *same* transaction inserts the new `Quest` row
referencing it. If the quest insert failed for any reason, you would not
want an orphaned `QuestLine` left behind with no quest — the transaction
guarantees that either both inserts happen or neither does.

### ACID, one letter at a time

- **Atomicity** — a transaction is all-or-nothing (just covered above).
- **Consistency** — a transaction can never leave the database violating
  its own rules (e.g. a foreign key pointing at a `quest_line_id` that
  doesn't actually exist) — Postgres enforces this itself, rejecting any
  operation that would break it.
- **Isolation** — transactions running at the same time (e.g. two users
  hitting the API simultaneously) don't see each other's *uncommitted*
  changes — each transaction behaves as if it were running alone, even
  though Postgres is really juggling many at once.
- **Durability** — once a transaction commits, it survives — even a power
  loss immediately afterward can't undo it, because Postgres has already
  written it to disk, not just held it in memory. This is the literal
  answer to "why not just use a dict": a dict has zero durability.

## Common mistakes & gotchas

- **Assuming an index always helps.** Over-indexing slows down every write
  for a read speedup you may never need. Add indexes based on actual query
  patterns (Lesson 04's `WHERE`/`JOIN` columns), not preemptively on
  everything.
- **Forgetting to commit.** A session that adds/updates rows but never
  calls `commit()` (or that raises before reaching it) has done nothing
  from the database's point of view — this is a common source of "I added
  a row and it's not there" confusion.
- **Confusing isolation with "instant visibility."** Isolation guarantees
  correctness under concurrency, not that every change is instantly visible
  to every other connection the moment you *start* a transaction — only
  once it *commits*.

## How this connects

Lesson 03 uses transactions implicitly every time it shows an INSERT or
UPDATE. Lesson 05/06 show exactly how SQLAlchemy's `AsyncSession` wraps
this transaction model in Python. Exercise 03 in this module has you add a
real index to QuestLog's schema and observe query behavior with it.

## Quick self-check

1. What does an index trade away in exchange for faster reads?
2. Why didn't `db_models.py`'s foreign key columns get an index automatically?
3. What happens to a transaction if an exception is raised before `commit()`?
4. Which ACID guarantee is the direct answer to "why not just use a Python dict"?
