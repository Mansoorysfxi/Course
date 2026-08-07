# Lesson 03 — SQL: SELECT, INSERT, UPDATE, DELETE

## What you'll learn

- SQL syntax for reading data (`SELECT`, `WHERE`, `ORDER BY`, `LIMIT`).
- SQL syntax for writing data (`INSERT`, `UPDATE`, `DELETE`).
- How to run these directly against QuestLog's real tables with `psql`.

## Why this matters

SQLAlchemy (Lesson 05 onward) generates SQL for you — but it generates
*real* SQL, and every bug you'll ever debug in a database-backed app
eventually comes down to understanding the actual query that ran. Learning
raw SQL first means SQLAlchemy's syntax will read as "a Python way to
write the SQL I already understand," not as unexplained magic.

## Prerequisites

Lessons 00–02 (Postgres running, tables/rows/keys, indexes/transactions).

## The concept, explained simply

SQL (Structured Query Language) is a small, declarative language for
describing *what* data you want, not *how* to fetch it — you never write a
loop; you describe the shape of the result and Postgres figures out the
most efficient way to produce it (using indexes where they exist, per
Lesson 02).

## The details

Connect to QuestLog's real database and follow along:

```bash
psql -U questlog -d questlog -h localhost
```
(You'll need real rows to query — Exercise 01 has you insert some by hand
first if the app hasn't seeded any yet via `seed_if_empty()`.)

### SELECT — reading data

```sql
SELECT * FROM quests;
```
`*` means "every column." **Expected output:** every row currently in
`quests`, as a table.

```sql
SELECT title, priority FROM quests WHERE done = false;
```
Only the two named columns, only for rows where `done` is `false`.
`WHERE` filters rows — exactly what `repository.py`'s `list_quests`
function builds via SQLAlchemy's `.where(...)` when a `done` query
parameter is supplied.

```sql
SELECT title FROM quests ORDER BY created_at DESC LIMIT 3;
```
`ORDER BY ... DESC` sorts newest-first (recall Lesson 01: rows have no
inherent order — you must always ask). `LIMIT 3` caps the result to the
first three rows after sorting.

**Try it yourself:** predict the output of
`SELECT title FROM quests ORDER BY priority;` before running it — is
`"high"` guaranteed to sort before `"low"` alphabetically? (No —
alphabetically `"high" < "low"` is false; `h` does come before `l`, so it
actually *does* sort correctly here by coincidence of English spelling, but
this is exactly the kind of assumption that breaks the moment priorities
were named e.g. `"P1"/"P2"/"P3"` instead — don't rely on a text column
sorting in a meaningful order unless you've explicitly designed it to.)

### INSERT — creating data

```sql
INSERT INTO quest_lines (id, name) VALUES ('ql-test', 'Testing');
INSERT INTO quests (id, title, description, priority, done, created_at, quest_line_id, owner_id)
VALUES ('q-test', 'Test the SQL lesson', 'Run every command by hand.', 'low', false, now(),
        'ql-test', (SELECT id FROM users LIMIT 1));
```
Every column without a default must be given a value. `now()` is a
Postgres function returning the current timestamp. The nested
`(SELECT id FROM users LIMIT 1)` is a **subquery** — a `SELECT` used as a
value inside another statement, here grabbing whichever user id already
exists (the seeded default user) so the foreign key is valid.

### UPDATE — modifying data

```sql
UPDATE quests SET done = true WHERE id = 'q-test';
```
**Always include a `WHERE` clause on `UPDATE`** — without one, this
statement would set `done = true` on *every single row in the table*, not
just one. This is one of the most common, most damaging beginner SQL
mistakes.

### DELETE — removing data

```sql
DELETE FROM quests WHERE id = 'q-test';
DELETE FROM quest_lines WHERE id = 'ql-test';
```
Same warning applies even more forcefully: `DELETE FROM quests;` with no
`WHERE` deletes every row in the table, permanently, with no undo — Postgres
has no Recycle Bin any more than `rm` did in Module 00.

**Try it yourself:** before running it, predict what happens if you run
`DELETE FROM quest_lines WHERE id = 'ql-test';` *before* deleting the quest
that references it. (It fails — Postgres's foreign key constraint refuses
to delete a `quest_lines` row that a `quests` row still points at, protecting
exactly the consistency guarantee from Lesson 02's "C" in ACID.)

### Exit psql

```sql
\q
```

## Common mistakes & gotchas

- **`UPDATE`/`DELETE` with no `WHERE`.** Covered above — always double
  check before pressing Enter, exactly like Module 00's `rm` warning.
- **Forgetting quotes around text values.** `WHERE title = Test` (no
  quotes) is a syntax error or misinterpreted as a column name; text
  literals need single quotes: `WHERE title = 'Test'`.
- **Case sensitivity of string comparisons.** `WHERE priority = 'HIGH'`
  will not match a row storing `'high'` — SQL string comparisons are
  case-sensitive by default.
- **Trying to delete a row another table's foreign key still references.**
  Covered above — this is Postgres protecting referential integrity, not a
  bug.

## How this connects

Lesson 04 builds on exactly this syntax to combine data across tables
(`JOIN`) and aggregate it (`GROUP BY`) — both used for real in
`repository.py`'s `quest_line_stats` function. Lesson 05 shows how
SQLAlchemy generates statements shaped exactly like these, from Python.

## Quick self-check

1. Why is `WHERE` mandatory-in-spirit on every `UPDATE`/`DELETE` you write?
2. What does `ORDER BY ... DESC LIMIT 3` do together?
3. What is a subquery, concretely, in the `INSERT` example above?
4. Why did deleting a referenced `quest_lines` row fail before its dependent `quests` row was deleted?
