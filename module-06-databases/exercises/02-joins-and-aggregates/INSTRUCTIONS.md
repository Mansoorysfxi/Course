# Exercise 02 — JOINs and Aggregates (Guided)

**Concepts this exercise uses** (taught in
[`lessons/04-joins-and-group-by.md`](../../lessons/04-joins-and-group-by.md)):
`JOIN`, `LEFT JOIN`, `GROUP BY`, `COUNT`, `SUM`, `CASE WHEN`.

## What to do

Using `psql -U questlog -d questlog -h localhost` against the real,
seeded database:

1. Write a query joining `quests` to `quest_lines` that returns each
   quest's `title` alongside its quest line's `name` (aliased as
   `quest_line_name`).
2. Write a query that returns, per quest line, the total number of quests
   in it (`quest_line`, `total`), using `GROUP BY`.
3. Extend query 2 to also show how many of each quest line's quests are
   done (`quest_line`, `total`, `done_count`) — this should end up
   matching what `repository.py`'s `quest_line_stats` function computes.
4. Insert a brand-new `quest_lines` row (name `'Empty Line'`) with zero
   quests referencing it, then write both a plain `JOIN` and a `LEFT JOIN`
   version of query 1's style query, and confirm `'Empty Line'` appears in
   the `LEFT JOIN` version's output but not the plain `JOIN` version's.
5. Clean up: delete the `'Empty Line'` row you added.

## Acceptance criteria

- [ ] Query 3's numbers match what `GET /api/quests/stats` returns for the same database state (verify by hitting that endpoint while the backend is running, or reasoning through the seeded data by hand).
- [ ] You can explain, in your own words, exactly why query 4's two versions differ.
- [ ] Cleanup (step 5) was actually run.

## What to submit

All 4 queries (not counting cleanup) plus their output, in `solution/QUERIES_AND_OUTPUT.md`.

## Hints

- If query 3 is hard, build it in two pieces first: get `COUNT(quests.id)` working alone, then add the `SUM(CASE WHEN ...)` piece — re-read Lesson 04's worked example if the `CASE WHEN` syntax isn't clicking.
- If step 4's plain `JOIN` version is still showing `'Empty Line'`, you've written a `LEFT JOIN` by mistake somewhere — double check the keyword.
