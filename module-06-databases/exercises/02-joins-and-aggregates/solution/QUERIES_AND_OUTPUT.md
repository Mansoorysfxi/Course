# Reference Solution — JOINs and Aggregates

Don't read this until you've made a genuine attempt.

```sql
-- 1.
SELECT quests.title, quest_lines.name AS quest_line_name
FROM quests
JOIN quest_lines ON quests.quest_line_id = quest_lines.id;

-- 2.
SELECT quest_lines.name AS quest_line, COUNT(quests.id) AS total
FROM quest_lines
JOIN quests ON quests.quest_line_id = quest_lines.id
GROUP BY quest_lines.name;

-- 3.
SELECT
  quest_lines.name AS quest_line,
  COUNT(quests.id) AS total,
  SUM(CASE WHEN quests.done THEN 1 ELSE 0 END) AS done_count
FROM quest_lines
JOIN quests ON quests.quest_line_id = quest_lines.id
GROUP BY quest_lines.name
ORDER BY quest_lines.name;

-- 4a. setup
INSERT INTO quest_lines (id, name) VALUES ('ql-empty', 'Empty Line');

-- 4b. plain JOIN — 'Empty Line' will NOT appear
SELECT quest_lines.name, quests.title
FROM quest_lines
JOIN quests ON quests.quest_line_id = quest_lines.id;

-- 4c. LEFT JOIN — 'Empty Line' WILL appear, with title = NULL
SELECT quest_lines.name, quests.title
FROM quest_lines
LEFT JOIN quests ON quests.quest_line_id = quest_lines.id;

-- 5. cleanup
DELETE FROM quest_lines WHERE id = 'ql-empty';
```

## Notes on grading this yourself

- Query 3's output should match `GET /api/quests/stats` on the seeded
  data: `Main Story` (1 total, 0 done), `Village Errands` (2 total, 1
  done), `Side Quests` (2 total, 1 done) — verify against your own actual
  seeded rows, since re-seeding or prior exercises may have changed counts.
- If step 5's cleanup is skipped, `'Empty Line'` will linger and confuse
  later exercises' counts — always clean up rows you added purely for
  practice.
