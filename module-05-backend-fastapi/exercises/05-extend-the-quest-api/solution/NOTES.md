# Notes on the reference solution

- `GET /stats` is registered **before** `GET /{quest_id}` in `quests.py`. Verified: without
  this ordering, `curl http://127.0.0.1:8000/api/quests/stats` was captured by the
  `{quest_id}` route (with `quest_id="stats"`), returning a `404` instead of real stats --
  concrete, reproduced proof of Lesson 02's route-matching-order rule, not a hypothetical.
- `complete-line/{quest_line}` did NOT need reordering relative to `{quest_id}` -- it has
  two path segments after `/api/quests`, `{quest_id}` only matches one, so there was never
  a real collision there; confirmed by testing both orders and seeing identical, correct
  behavior either way for that specific route.
- `require_quests_in_line` returns the full list of matching quests, but `complete_line`'s
  route only uses it for its 404-raising side effect (named `_quests_in_line` with a
  leading underscore, a common convention for "I need this parameter to exist for
  dependency injection to run, but I'm not going to use its value directly").
- `store.complete_line` reuses the existing `update_quest` function one quest at a time,
  rather than writing new, separate "bulk update" logic -- keeping exactly one place
  (`update_quest`) responsible for what "updating a quest" actually means.

**Verified:** run with `uvicorn app.main:app --reload`.
`curl http://127.0.0.1:8000/api/quests/stats` returns per-line counts;
`curl -X PATCH http://127.0.0.1:8000/api/quests/complete-line/Village%20Errands` marks
both Village Errands quests done and returns them;
`curl -i -X PATCH http://127.0.0.1:8000/api/quests/complete-line/Nonexistent%20Line`
returns `404`; every existing CRUD route re-tested and still correct. Also exercised
every new/changed route once through Swagger UI's "Try it out," per the acceptance
criteria.
