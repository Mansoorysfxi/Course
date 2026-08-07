# Exercise 05 — A New Endpoint, End to End (Independent)

**Concepts this exercise uses:**
`LEFT JOIN`/`GROUP BY` ([`lessons/04-joins-and-group-by.md`](../../lessons/04-joins-and-group-by.md)),
SQLAlchemy queries ([`lessons/05-orms-and-sqlalchemy-basics.md`](../../lessons/05-orms-and-sqlalchemy-basics.md)
and [`lessons/06-sqlalchemy-with-fastapi.md`](../../lessons/06-sqlalchemy-with-fastapi.md)),
plus everything from Module 05 about routes, Pydantic response models, and status codes.

This exercise gives you the *goal*, not the exact steps — you decide how
to structure the code, based on the patterns already used throughout
`app/repository.py` and `app/routers/quests.py`.

## What to build

A new endpoint: **`GET /api/quest-lines`**, returning **every** quest line
that exists — including ones with zero quests — each with a quest count:

```json
[
  {"name": "Main Story", "questCount": 1},
  {"name": "Village Errands", "questCount": 2},
  {"name": "Side Quests", "questCount": 2},
  {"name": "Empty Line", "questCount": 0}
]
```

This is deliberately different from the existing `GET /api/quests/stats`
endpoint: that one only shows quest lines that have *at least one* quest
(it uses a plain `JOIN`). This new endpoint must show *every* quest line
that exists, zero-quest ones included — which requires the `LEFT JOIN`
concept from Lesson 04, not a plain `JOIN`.

## Suggested structure (you can deviate if you have a good reason)

1. A new Pydantic model in `app/models.py` (e.g. `QuestLineSummary`, with
   `name: str` and `quest_count: int = Field(alias="questCount")`).
2. A new function in `app/repository.py` (e.g. `list_quest_lines`) using a
   `LEFT JOIN` and `GROUP BY`, following the pattern `quest_line_stats`
   already uses, but starting `FROM quest_lines` with a `LEFT JOIN` to
   `quests` instead of the other way around.
3. A new route in `app/routers/quests.py` (or a new router file if you
   prefer) — decide its exact path carefully given the route-ordering
   lesson from Module 05 (does this new path risk colliding with
   `/{quest_id}`-shaped routes anywhere?).

## Acceptance criteria

- [ ] To prove the `LEFT JOIN` is genuinely needed (not just present), insert a test quest line with zero quests via `psql` first, and confirm it appears in your new endpoint's response with `questCount: 0` — then confirm it does *not* appear in the existing `/api/quests/stats` endpoint's response, demonstrating the real difference.
- [ ] The endpoint is tested with both `curl` and Swagger UI's `/docs`.
- [ ] Clean up your test quest line afterward.

## What to submit

In `solution/CHANGES.md`: your diffs to `models.py`, `repository.py`, and
`routers/quests.py` (or your new router file), plus the `curl` output
proving the zero-quest quest line appears here but not in `/api/quests/stats`.

## Hints

- **Level 1:** Which existing function in `repository.py` is closest in
  shape to what you need, and what's the one keyword you'd need to change
  in its `JOIN` to make empty quest lines show up?
- **Level 2:** `quest_line_stats` starts its query `FROM quest_lines
  ... JOIN quests`. Starting from `quest_lines` and changing `JOIN` to
  `LEFT JOIN quests` is most of the fix — the aggregate functions
  (`COUNT`) need no changes, since `COUNT` of a `NULL`-joined column
  correctly counts zero, not one.
- **Level 3:** If you're still stuck on the SQLAlchemy syntax for an
  explicit outer join with `select()`, look at how `.join(...)` is called
  in `quest_line_stats` and check SQLAlchemy's own current docs for
  `.outerjoin(...)` or `.join(..., isouter=True)`.
