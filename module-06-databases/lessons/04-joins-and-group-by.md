# Lesson 04 — JOINs and GROUP BY

## What you'll learn

- What a `JOIN` does and why splitting data into tables (Lesson 01) requires it.
- The difference between `INNER JOIN` and `LEFT JOIN`.
- What `GROUP BY` does, with aggregate functions like `COUNT` and `SUM`.
- How this maps directly to `repository.py`'s `quest_line_stats` function.

## Why this matters

Lesson 01 split "quest line name" out into its own table specifically to
avoid duplication. The cost of that decision is that reading a quest's
*name* (not just its id) now requires combining two tables back together —
that combination is a `JOIN`. This is the single most important SQL
concept for working with any properly normalized (Lesson 09) schema.

## Prerequisites

Lessons 01–03.

## The concept, explained simply

Recall Lesson 01's two tables:
```
quest_lines(id, name)          quests(id, title, quest_line_id, ...)
```
To show a quest's title *and* its quest line's *name* in one result, you
need to match each quest's `quest_line_id` against `quest_lines.id` and
pull the `name` across. A **JOIN** is exactly this: "for each row in table
A, find the matching row(s) in table B (by some condition), and combine
their columns into one result row."

## The details

### INNER JOIN

```sql
SELECT quests.title, quest_lines.name AS quest_line_name
FROM quests
JOIN quest_lines ON quests.quest_line_id = quest_lines.id;
```
**Line by line:** `FROM quests` starts with every row in `quests`. `JOIN
quest_lines ON ...` says "for each of those rows, find the `quest_lines`
row where `id` matches this quest's `quest_line_id`." `AS quest_line_name`
renames the output column (an **alias**) since both tables have a column
literally named `name`/`title` that could otherwise be ambiguous. This is
called an **INNER JOIN** (the word `JOIN` alone defaults to this) — it only
returns quests that *do* have a matching quest line. Since `quest_line_id`
is `nullable=False` in `db_models.py`, every quest always has a match here,
but that's not true for every possible relationship.

### LEFT JOIN

```sql
SELECT quest_lines.name, quests.title
FROM quest_lines
LEFT JOIN quests ON quests.quest_line_id = quest_lines.id;
```
A **LEFT JOIN** keeps *every* row from the left-hand table (`quest_lines`
here) even if there's no match on the right — a quest line with zero
quests would still appear, with `NULL` in the `quests.title` column,
instead of vanishing from the result entirely the way an inner join would.
Use a `LEFT JOIN` whenever "show me everything on this side, whether or not
it has a match" is the actual question — e.g., "show every quest line, even
empty ones" (an inner join would silently hide empty quest lines).

**Try it yourself:** predict the difference in row count between the
`JOIN` version and the `LEFT JOIN` version above, for a database where one
quest line currently has zero quests. (The plain `JOIN` omits that quest
line entirely; the `LEFT JOIN` includes it once, with `title = NULL`.)

### GROUP BY and aggregate functions

```sql
SELECT quest_lines.name AS quest_line, COUNT(quests.id) AS total
FROM quest_lines
JOIN quests ON quests.quest_line_id = quest_lines.id
GROUP BY quest_lines.name;
```
`GROUP BY quest_lines.name` collapses all rows sharing the same quest line
name into one summary row per name. `COUNT(quests.id)` is an **aggregate
function** — it operates across every row *within* each group, not one row
at a time. **Expected output:** one row per quest line, each showing how
many quests belong to it.

This is the plain-SQL version of exactly what `repository.py`'s
`quest_line_stats` function computes:

```sql
SELECT
  quest_lines.name AS quest_line,
  COUNT(quests.id) AS total,
  SUM(CASE WHEN quests.done THEN 1 ELSE 0 END) AS done
FROM quest_lines
JOIN quests ON quests.quest_line_id = quest_lines.id
GROUP BY quest_lines.name
ORDER BY quest_lines.name;
```
`SUM(CASE WHEN quests.done THEN 1 ELSE 0 END)` counts only the done ones —
`CASE WHEN ... THEN ... ELSE ... END` is SQL's inline if/else expression,
turning each row's boolean `done` into `1` or `0` before summing. Compare
this directly against `app/repository.py`'s `quest_line_stats` function —
it builds this exact query using SQLAlchemy's Python API instead of a raw
string, covered fully in Lesson 05.

## Common mistakes & gotchas

- **Selecting a column that's neither grouped nor aggregated.** `SELECT
  quests.title, COUNT(*) FROM quests GROUP BY quest_line_id` is invalid in
  Postgres (and most databases) — `quests.title` isn't in the `GROUP BY`
  list and isn't wrapped in an aggregate function, so Postgres has no way
  to know *which* title to show for a group containing many different
  titles. Every selected column must be either in `GROUP BY` or inside an
  aggregate.
- **Using `JOIN` when you meant `LEFT JOIN`.** The most common real bug
  this causes: rows silently disappearing from a report because they had
  no match on the joined side, and nobody noticed until someone asked "why
  isn't X showing up?"
- **Ambiguous column names across joined tables.** If both tables have an
  `id` column and you write bare `SELECT id`, Postgres will error
  ("column reference is ambiguous") — always qualify with the table name
  (`quests.id`) once more than one table is involved.

## How this connects

Lesson 05 shows how SQLAlchemy expresses `JOIN`/`GROUP BY` in Python
(`.join(...)`, `.group_by(...)`) — you'll recognize every piece from this
lesson. Lesson 10 uses joins as the justification for why QuestLog's schema
is split into three tables instead of one wide `quests` table.

## Quick self-check

1. What's the practical difference between `JOIN` and `LEFT JOIN`?
2. Why does `GROUP BY` require every non-aggregated selected column to be in the `GROUP BY` list?
3. What does `COUNT(quests.id)` compute, per group?
4. Rewrite, in your own words, what `SUM(CASE WHEN quests.done THEN 1 ELSE 0 END)` is doing.
