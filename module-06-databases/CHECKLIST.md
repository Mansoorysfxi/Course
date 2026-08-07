# Module 06 — Checklist

Complete this after finishing all five exercises and the capstone project,
and after your module-end review ("Check my module").

## Self-assessment

- [ ] I can explain why an in-memory dict isn't good enough for a real application, in terms of ACID's Durability guarantee specifically.
- [ ] I can write a `SELECT` with `WHERE`/`ORDER BY`/`LIMIT`, an `INSERT`, an `UPDATE`, and a `DELETE` without looking anything up.
- [ ] I understand why `UPDATE`/`DELETE` without `WHERE` is dangerous, and why Postgres refused to delete a `quest_lines` row still referenced by a quest.
- [ ] I can explain the difference between `JOIN` and `LEFT JOIN` and give a concrete example of when each is correct.
- [ ] I can read `app/db_models.py` and explain every `Mapped`/`mapped_column`/`relationship()` line without help.
- [ ] I understand why `get_db` uses `yield` and why every route needed to become `async def` with a `session` parameter.
- [ ] I have generated, read (before applying), and applied a real Alembic migration — and rolled one back with `downgrade -1`.
- [ ] I can explain, in my own words, why `Quest.owner_id` exists a full module before real authentication does.
- [ ] I can explain when a document store or key-value store would be a better fit than PostgreSQL.
- [ ] All five exercises were reviewed and scored 7/10 or higher (or revised until they were).
- [ ] The capstone's restart-persistence test was actually performed, not just read about.

## Spaced-repetition review questions from earlier modules

1. **(Module 00)** What do the three Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) each represent?
2. **(Module 01)** What's the difference between a Python list and a generator, and why does that difference matter for memory usage?
3. **(Module 02)** What does "stateless" mean about HTTP, and how does it relate to why QuestLog needs a database at all rather than the API just "remembering" things itself?
4. **(Module 04)** What is a stale closure, and how does React's `useEffect` dependency array help avoid one?
5. **(Module 05)** What does FastAPI's `Depends` actually do, and how does `DbSession` (this module) use that exact same mechanism?

## Before you move on to Module 07

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your Module 06 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 07 README to see what's coming next.
