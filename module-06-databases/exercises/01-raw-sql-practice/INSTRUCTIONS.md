# Exercise 01 — Raw SQL Practice (Very Easy)

**Concepts this exercise uses** (all taught in
[`lessons/03-sql-select-insert-update-delete.md`](../../lessons/03-sql-select-insert-update-delete.md)):
`SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `INSERT`, `UPDATE`, `DELETE`.

## Setup

Make sure the backend has been run at least once (so `seed_if_empty` has
populated real data), or insert a couple of rows yourself per Lesson 03.
Connect with:
```bash
psql -U questlog -d questlog -h localhost
```

## What to do

Write and run each of these queries, in order, against the real
`questlog` database:

1. Select every column of every row in `quests`.
2. Select only `title` and `priority`, for quests where `done = false`.
3. Select the 2 most recently created quests (by `created_at`, newest first).
4. Insert a new row directly into `quest_lines` named `'Practice'`.
5. Insert a new quest into `quests` that references the `'Practice'` quest line you just created and the existing seeded user (use a subquery for the user id, per the lesson's example).
6. Update that quest's `priority` to `'high'`.
7. Delete that quest.
8. Delete the `'Practice'` quest line (this should succeed now that no quest references it — if it fails, you deleted things in the wrong order).

## Acceptance criteria

- [ ] Each query ran without error, in the order listed.
- [ ] Step 8 succeeded — proving you understand *why* order mattered (Lesson 03's foreign-key-protection example).
- [ ] You can explain, for step 3, why `ORDER BY` was necessary and what would happen without it.

## What to submit

Paste all 8 queries plus their output into `solution/MY_QUERIES.md`.

## Hints

- If step 8 fails with a foreign key error, you deleted in the wrong order — re-read Lesson 03's `DELETE` warning about referenced rows.
- If step 5's subquery returns more than one row, add `LIMIT 1` to it.
