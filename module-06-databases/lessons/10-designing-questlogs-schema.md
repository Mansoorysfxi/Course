# Lesson 10 — Designing QuestLog's Real Schema

## What you'll learn

- Applying Lesson 09's five-step process to QuestLog specifically.
- Why the `users` table exists a full module before real authentication does.
- Why the API contract didn't need to change even though storage did.
- Reading `db_models.py` end to end with full context.

## Why this matters

This lesson is where every earlier lesson in this module converges on one
real decision: exactly the schema that's already sitting in
`app/db_models.py`. Understanding *why* it's shaped this way — not just
that it works — is what lets you design your *own* schemas correctly on a
future project this course won't hand you the answer for.

## Prerequisites

Lessons 01 and 09 (relational model, normalization process), and Module 05
(the domain: quests, priorities, quest lines).

## The concept, explained simply

Apply Lesson 09's process to QuestLog:

**1. List the things:** quests, quest lines, users.

**2. Each thing's own facts:**
- A quest: title, description, priority, done, created_at.
- A quest line: a name.
- A user: an email, a created_at.

**3. Relationships:**
- A quest belongs to exactly one quest line (one-to-many: one quest line,
  many quests).
- A quest belongs to exactly one user (one-to-many: one user, many quests).

**4. Turn into tables:** exactly `db_models.py`'s three classes —
`QuestLine`, `User`, `Quest` — with `Quest.quest_line_id` and
`Quest.owner_id` as the two foreign keys implementing step 3's
relationships.

**5. Anomaly check:** can you record a quest line with zero quests? Yes —
insert a `QuestLine` row directly. Can you rename a quest line in one
place? Yes — one `UPDATE` on `quest_lines`. Can you delete a quest without
losing the quest line's own existence? Yes — the two are stored
independently.

## The details

### Why `users` exists a full module before real authentication

This is the one decision in this schema that isn't a direct answer to "what
does the app need to work right now" — Module 06 doesn't have real login,
so why does a `users` table exist already, with every quest given a
`nullable=False` `owner_id` foreign key?

**The alternative, spelled out:** ship Module 06 with no `owner_id` column
at all, then have Module 07 add one when real users exist. That sounds
simpler, until you actually think through what Module 07's migration would
have to do: every quest already in the database at that point has *no*
owner. Adding a `nullable=False` foreign key column to a table that already
has rows either fails outright (Postgres can't put `NULL` in a column
declared `nullable=False`) or forces an awkward migration that has to
invent a real value for every existing row *before* the constraint can be
added — a messy, error-prone, one-time special case.

Adding `owner_id` now, while there's exactly one seeded "default" user
(`repository.py`'s `DEFAULT_USER_EMAIL`, created by `seed_if_empty`),
costs almost nothing today (every quest just points at that one default
user) and means Module 07's actual job — real signup/login/JWTs — never
has to touch this column's existence at all, only *which* user id gets
used. This is a real, common professional pattern: designing a column's
*existence* ahead of the feature that will make it meaningful, specifically
to avoid a painful migration later. It is not over-engineering — it is a
narrow, deliberate exception, not a general license to add speculative
columns "just in case" (Lesson 09's over-normalization warning still
applies to everything else).

### Why the API contract didn't need to change

Compare `app/models.py` (the Pydantic API shapes) field-for-field against
`db_models.py` (the SQLAlchemy storage shapes): `Quest`'s API shape still
has a plain `quest_line: str` field — a name, not an id — identical to
Module 05. The `QuestLine` table and the `quest_line_id` foreign key are
invisible to any HTTP client entirely; `repository.py`'s `_to_pydantic`
(Lesson 06) is the only code that ever translates between the two. This is
the concrete payoff of keeping storage concerns (`db_models.py`) and API
concerns (`models.py`) in two separate files from the start, back in
Module 05 — a decision that made this module's entire persistence swap
invisible to `module-06-databases/project/questlog/frontend/`, which
needed zero changes.

### Reading `db_models.py` end to end

Open `module-06-databases/project/questlog/backend/app/db_models.py` now
and read every class's docstring alongside this lesson — each one
references the exact lesson section that justifies a specific decision in
it (the `User` table's docstring points back to this section; `QuestLine`'s
docstring points back to Lesson 09's normalization argument). This is
intentionally the last thing this module asks you to do before the
exercises — you should be able to read that file and explain every single
line's purpose without external help at this point.

## Common mistakes & gotchas

- **Assuming every schema needs a "prepare for a future feature" column
  like `owner_id`.** This was a specific, reasoned exception because the
  cost of retrofitting a `nullable=False` foreign key onto an already-populated
  table is genuinely high. Most speculative columns don't clear that bar —
  don't treat this as general permission to add fields for hypothetical
  future modules.
- **Putting API-shape concerns into the storage model (or vice versa).**
  Merging `Quest` (Pydantic) and `Quest`/`QuestRow` (SQLAlchemy) into one
  class might seem like less code short-term, but it's exactly what would
  have forced a frontend change this module specifically avoided.

## How this connects

This is the last lesson before the exercises — everything from Lessons
00–09 was building toward being able to read and justify this exact
schema. Module 07 will extend the `users` table with real password
hashes and login, using the exact migration workflow from Lesson 07, on a
foundation this lesson explained was laid deliberately early.

## Quick self-check

1. Walk through Lesson 09's five-step process for QuestLog from memory, without re-reading this lesson.
2. Why does `Quest.owner_id` exist already, even though there's no real login yet?
3. What would go wrong if you tried to add a `nullable=False` foreign key to a table that already has rows with no sensible value for it?
4. Which single function is responsible for the fact that `frontend/` never needed to change when this module added Postgres?
