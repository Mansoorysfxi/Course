# Lesson 01 — Why a Database, and the Relational Model From Scratch

## What you'll learn

- Why an in-memory dict (or a plain file) stops being good enough.
- What a relational database actually is: tables, rows, columns.
- What a primary key and a foreign key are, and why references beat copies.
- How to picture Postgres as a program, not a file.

## Why this matters

Module 05's entire backend — every quest, every quest line — lived in one
Python `dict` inside `app/store.py`. It worked, but it had a fatal flaw you
already felt: restart the Uvicorn process, and everything's gone. This
lesson explains exactly what a database adds that a dict can't, and gives
you the vocabulary (table, row, key) that every other lesson in this module
builds on.

## Prerequisites

Lesson 00 (Setup) and Module 05 (you need to remember what `app/store.py`
actually did, to appreciate what's changing).

## The concept, explained simply

Think about a save-game system in Unreal: writing raw player state to a
single flat file works fine for one save slot with a simple struct. It
falls apart fast once you need multiple interrelated things — inventory
items that reference a shared item database, quests that reference NPCs,
NPCs that reference locations — all of which need to update consistently
and survive a crash mid-write without corrupting. A **database** is
software specifically built to solve that class of problem: storing
structured data permanently on disk, letting many pieces of code read and
write it safely at the same time, and guaranteeing it survives a crash.

A **relational database** (like PostgreSQL) organizes that data into
**tables** — think of a table as a spreadsheet with a fixed set of named
columns (e.g. a `quests` table with columns `id`, `title`, `priority`,
`done`). Each **row** is one specific record — one quest. This maps almost
exactly onto `app/store.py`'s dict-of-dicts, except it's enforced by the
database itself (every row *must* have a `title`, because the column says
so) and it survives a restart because it's written to disk, not RAM.

## The details

### Tables, rows, columns — the exact vocabulary

```
quests
┌──────────────────────┬───────────────┬──────────┬───────┐
│ id                    │ title         │ priority │ done  │
├──────────────────────┼───────────────┼──────────┼───────┤
│ 3f2b...               │ Slay the ...  │ high     │ false │
│ a91c...               │ Gather ...    │ low      │ true  │
└──────────────────────┴───────────────┴──────────┴───────┘
```
This is a **table**. Each column has a fixed **type** (Postgres enforces
this — you cannot put text into a column declared as a number, the same
guarantee Python's type hints only *suggest* but Postgres *enforces*).
Each horizontal line is a **row**.

### Primary keys

A **primary key** is a column (or set of columns) guaranteed unique across
every row in a table — it's how you unambiguously refer to *this exact
row* and no other. `db_models.py`'s `Quest.id` (a randomly generated UUID
string, exactly like `app/store.py`'s ids in Module 05) is the primary key
of the `quests` table. Every table in a well-designed relational database
has one.

### Foreign keys — references instead of copies

Here's the problem a foreign key solves. In Module 05, a quest's
`quest_line` field was just a free-typed string — `"Side Quests"`. Nothing
stopped a second quest from being created with `"side quests"` (different
casing) or `"Side Quest"` (missing an s) — three quests that *should* be
grouped together, silently split into three unrelated groups, because the
data was **copied** as text into every single quest instead of
**referenced**.

A **foreign key** fixes this: instead of copying a quest line's name into
every quest, you store one authoritative row per quest line in its own
table, and every quest stores just that row's *id*:

```
quest_lines                          quests
┌────────┬───────────────┐           ┌────────┬───────┬────────────────┐
│ id     │ name          │           │ id     │ title │ quest_line_id  │
├────────┼───────────────┤           ├────────┼───────┼────────────────┤
│ ql-1   │ Side Quests   │  ◄────────┤ q-1    │ ...   │ ql-1           │
│ ql-2   │ Main Story    │  ◄────────┤ q-2    │ ...   │ ql-1           │
└────────┴───────────────┘           └────────┴───────┴────────────────┘
```
Both `q-1` and `q-2` point at the exact same `ql-1` row. Rename "Side
Quests" once, in one place, and both quests reflect it instantly — because
there was only ever one copy of that name to begin with. This is precisely
what `db_models.py`'s `Quest.quest_line_id = mapped_column(..., 
ForeignKey("quest_lines.id"), ...)` declares, and precisely why
`repository.py`'s `_get_or_create_quest_line` function exists — it's the
code that finds-or-creates that one authoritative row.

**Try it yourself:** before reading ahead, predict what would go wrong if
`Quest` had kept a plain `quest_line: str` column (like Module 05) *and*
you wanted to rename a quest line used by 500 existing quests. (You'd have
to find and rewrite all 500 rows, and any that were slightly mistyped
originally would never get caught by the rename at all.)

### Relationships, named

A foreign key like this creates a **relationship** between two tables —
here specifically a **one-to-many** relationship: one quest line can have
*many* quests, but each quest belongs to exactly *one* quest line. You'll
see this exact shape again for `User` → `Quest` (one user, many quests) in
`db_models.py`.

### Postgres as a program, not a file

Unlike a single JSON file (Module 01's `save_system.py` capstone), a
Postgres database is not something you can just open and read with `cat`.
It's a running program (Lesson 00) with its own storage format, accessed
only through the network protocol `psql` and `asyncpg` both speak. This is
deliberate: it's what lets Postgres guarantee two things happening "at
once" don't corrupt each other — a guarantee a shared JSON file flatly
cannot make once more than one process might write to it.

## Common mistakes & gotchas

- **Confusing a foreign key column with the related object itself.**
  `Quest.quest_line_id` is just a string (a UUID) — it is not, by itself,
  the `QuestLine` row. `repository.py` has to explicitly query the
  `quest_lines` table using that id to get the actual name. (SQLAlchemy's
  `relationship()`, covered in Lesson 05, is a convenience that hides this
  extra query — but the underlying mechanic is still "look it up by id.")
- **Thinking a table needs a foreign key for every possible connection.**
  Only model a relationship as a foreign key when you'll actually query
  across it. Over-normalizing prematurely (a table for every conceivable
  concept) adds complexity without benefit — Lesson 09 covers this
  trade-off directly.
- **Forgetting a primary key is about uniqueness, not order.** Postgres
  rows have no inherent order — if you want a "createdAt, oldest first"
  ordering (like QuestLog's quest list), you must ask for it explicitly
  (`ORDER BY`, Lesson 03), never assume rows come back in insertion order.

## How this connects

This lesson is the vocabulary the rest of the module runs on. Lesson 03
teaches the actual SQL commands to read/write tables like these. Lesson 05
shows how SQLAlchemy lets you describe these same tables as Python classes
(`db_models.py`) instead of hand-written SQL. Lesson 09/10 use this exact
vocabulary to justify QuestLog's real schema design.

## Quick self-check

1. What's the difference between a table, a row, and a column?
2. Why is a foreign key better than copying a quest line's name into every quest?
3. What does "one-to-many" mean, concretely, for the `QuestLine`-to-`Quest` relationship?
4. Why can't you just `cat` a Postgres database the way you could `cat` Module 01's JSON save file?
