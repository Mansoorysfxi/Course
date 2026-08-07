# Reference Solution — Raw SQL Practice

Don't read this until you've made a genuine attempt.

```sql
-- 1.
SELECT * FROM quests;

-- 2.
SELECT title, priority FROM quests WHERE done = false;

-- 3.
SELECT title FROM quests ORDER BY created_at DESC LIMIT 2;

-- 4.
INSERT INTO quest_lines (id, name) VALUES ('ql-practice', 'Practice');

-- 5.
INSERT INTO quests (id, title, description, priority, done, created_at, quest_line_id, owner_id)
VALUES ('q-practice', 'Practice Quest', 'A throwaway row for Exercise 01.', 'low', false, now(),
        'ql-practice', (SELECT id FROM users LIMIT 1));

-- 6.
UPDATE quests SET priority = 'high' WHERE id = 'q-practice';

-- 7.
DELETE FROM quests WHERE id = 'q-practice';

-- 8.
DELETE FROM quest_lines WHERE id = 'ql-practice';
```

## Notes on grading this yourself

- Step 3 without `ORDER BY created_at DESC` would return rows in whatever
  order Postgres happens to store them internally — not guaranteed to be
  insertion order or any order at all. If your query worked "by luck"
  without `ORDER BY`, that's a real gap to flag in your own review.
- If step 8 failed for you, you likely ran it before step 7 — the exact
  foreign-key protection Lesson 03 demonstrated.
