# Exercise 05 — Extend the Quest API

**Lessons:** every lesson in this module contributes something here, but the two doing the most direct work are [`lessons/08-building-the-questlog-api.md`](../../lessons/08-building-the-questlog-api.md) (the exact multi-file structure and store pattern you're extending) and [`lessons/04-dependency-injection-and-depends.md`](../../lessons/04-dependency-injection-and-depends.md) (a new dependency for the new "not found" case this exercise introduces). You'll also be reading and working inside real code from Lessons 01–03 and 06–07 (routing, Pydantic models, status codes, and testing via both `curl` and the interactive docs) without being told exactly where each applies — that's the point of this being the *independent* exercise.

**Difficulty:** Independent. This is the closest thing in this module to real work: extending an existing, unfamiliar-until-you-read-it multi-file FastAPI project with two genuinely new features, end to end, tested with both tools this course has given you.

## The task

`starter/` is a small, complete, working in-memory Quest API — structurally the same pattern as Lesson 08's QuestLog capstone backend (a `models.py`, a `store.py`, a `dependencies.py`, an `APIRouter`), but a separate, standalone copy so you can experiment freely without touching the real capstone in `project/`. It already has full CRUD: `GET /api/quests`, `GET /api/quests/{quest_id}`, `POST /api/quests`, `PATCH /api/quests/{quest_id}`, `DELETE /api/quests/{quest_id}`. Read it in full before changing anything.

Add two new endpoints:

1. **`GET /api/quests/stats`** — returns a JSON array, one entry per distinct quest line that currently has at least one quest, each shaped `{"quest_line": str, "total": int, "done": int}`. (Directly analogous to Module 04's own Exercise 05, "Quest Lines Overview" — that one computed this on the frontend, in React; this one computes the identical information on the backend, in Python, from the in-memory store.)
2. **`PATCH /api/quests/complete-line/{quest_line}`** — marks every quest currently in that exact quest line as `done`, and returns the updated list of quests that were changed. If no quest currently has that exact quest line, return `404` (add a small dependency for this — `require_quests_in_line` or similar — following Lesson 04's pattern, rather than checking inline in the route).

**Important ordering note, and a real FastAPI gotcha worth hitting once, deliberately:** `GET /api/quests/stats` and the existing `GET /api/quests/{quest_id}` both match a path with exactly one segment after `/api/quests` — `stats` is, shape-wise, indistinguishable from any other single-segment value like a real quest ID. FastAPI matches routes **in the order they're registered** — if `{quest_id}` is registered *before* `stats`, a request to `/api/quests/stats` gets incorrectly captured by the `{quest_id}` route instead (with `quest_id` literally set to the string `"stats"`, and — since no quest has that ID — a `404` where you expected your stats). Work out, from first principles (re-reading Lesson 02 if needed), which of your new route and the existing `{quest_id}` route needs to be registered first, and confirm your fix actually works with a real request — don't just take this paragraph's word for it. (Your `complete-line/{quest_line}` route has *two* segments after the prefix, so it can't collide with the single-segment `{quest_id}` route this same way — but reason through this yourself rather than assuming it from this note alone.)

## Concepts this exercise uses (all already taught)

| Concept | Taught in |
|---|---|
| `APIRouter`, multi-file structure | [Lesson 08](../../lessons/08-building-the-questlog-api.md) |
| Path parameters, and route-matching order | [Lesson 02](../../lessons/02-path-and-query-parameters.md) |
| A dependency for a "does this exist" check | [Lesson 04](../../lessons/04-dependency-injection-and-depends.md) |
| `response_model`, status codes | [Lesson 06](../../lessons/06-error-handling-status-codes-and-responses.md) |
| Testing with `curl` and Swagger UI | [Lesson 07](../../lessons/07-auto-docs-and-openapi.md), Module 02 |

## Acceptance criteria

- [ ] `GET /api/quests/stats` returns correct `total`/`done` counts per quest line, matching what's actually in the store at the time of the request.
- [ ] Adding a quest (via `POST /api/quests`) with a brand-new quest line, then calling `/stats` again, shows that new line with `total: 1`.
- [ ] `PATCH /api/quests/complete-line/{quest_line}` correctly marks every matching quest `done`, and leaves quests in *other* quest lines untouched.
- [ ] `PATCH /api/quests/complete-line/{quest_line}` for a quest line with zero quests returns `404`.
- [ ] A request to the existing `GET /api/quests/{quest_id}` with a real, existing quest ID still works correctly (i.e., you haven't broken the existing routes while adding new ones, including via any route-ordering fix).
- [ ] You tested every new/changed behavior through **both** `curl` and the Swagger UI (`/docs`) at least once each, and can explain, if asked, what each request/response looked like in each tool.
- [ ] `store.py`'s core dict-based storage mechanism is unchanged (you're adding new *functions*, not changing how `_quests` itself is stored).

## What to submit

Point your AI session at your completed `starter/` folder and say *"Review my solution for exercise 05."*

## Hints

**Level 1:** Start by reading `starter/app/routers/quests.py` in full — it already shows you the exact style (a `get_quest_or_404` dependency, `response_model`, `status_code`) your two new routes should match.

**Level 2:** For `/stats`, a `dict`-based tally (keyed by quest line) built in one pass over `store.list_quests()` is enough — you do not need any new storage, only a new read-only function in `store.py` (or directly in the route) that derives this from the existing quests.

**Level 3 (near-answer):** Register `@router.get("/stats")` **before** `@router.get("/{quest_id}")` in the file — first-registered wins for two routes whose shapes could otherwise both match the same incoming path. `complete-line/{quest_line}` doesn't strictly need to move (different segment count than `{quest_id}`), but placing all three new/existing routes in a deliberate, reasoned order, and testing each one, is the actual point of this hint — not just copying a fix blindly. If you're still stuck after reasoning through this and testing it, ask your AI session for the full solution rather than guessing further.
