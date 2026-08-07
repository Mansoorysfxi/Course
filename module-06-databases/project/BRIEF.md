# Module 06 Capstone — QuestLog Gets Real Persistence

## What this is

Module 05's QuestLog API worked, but it forgot everything on every
restart. This capstone's code is **already built** for you at
`project/questlog/` (copied forward from Module 05, with a real PostgreSQL
database wired in) — your job for this capstone is to **get it running
yourself, verify it end to end, and be able to explain every piece**, not
to write it from scratch. (The hands-on *writing* practice for this
module's concepts is in Exercises 01–05, which have you modify this exact
codebase directly.)

## Concepts this capstone uses

Every lesson in this module: the relational model and keys (01), indexes/
transactions/ACID (02), SQL CRUD (03), joins/GROUP BY (04), SQLAlchemy
basics (05), SQLAlchemy-with-FastAPI wiring (06), Alembic migrations (07),
NoSQL overview (08, conceptual only — no code here), normalization (09),
and QuestLog's actual schema design (10).

## What to do

1. **Follow [`lessons/00-setup.md`](../lessons/00-setup.md)** to install
   PostgreSQL and create the `questlog` database/user, if you haven't
   already from the exercises.
2. **Get the backend running against a real database:**
   ```bash
   cd project/questlog/backend
   python -m venv .venv
   source .venv/Scripts/activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```
3. **Confirm persistence actually works** — the entire point of this
   module, made concrete: create a quest via `curl` or `/docs`, then
   **stop the Uvicorn process entirely** (Ctrl+C) and **start it again**.
   Fetch `/api/quests` again. Your quest must still be there. (Compare this
   directly against Module 05's behavior, where it would have vanished —
   write down, in your own words, exactly why the outcome is different now.)
4. **Run both frontend and backend together**, per
   [`project/questlog/README.md`](./questlog/README.md), and confirm the
   Quest Board renders real, persisted data through the full stack
   (browser → React → fetch → FastAPI → SQLAlchemy → PostgreSQL → back).
5. **Read `app/db_models.py` end to end** and, without looking at Lesson
   10, write a short explanation (a paragraph or two) of why `owner_id`
   exists already even though there's no real login yet. Then check your
   explanation against Lesson 10's actual reasoning.
6. **Complete Exercises 01–05** if you haven't already — they're the
   hands-on component this capstone assumes is done.

## Acceptance criteria

- [ ] PostgreSQL is installed, running, and the `questlog` database/user exist.
- [ ] `alembic upgrade head` has been run and the schema exists (verify with `psql`'s `\d` command, or `\dt` to list all tables).
- [ ] A quest created via the running API survives a full backend restart.
- [ ] Frontend and backend were run together and a real end-to-end request was observed working.
- [ ] Your own written explanation of the `owner_id` design decision is genuinely yours, not copied from Lesson 10 — check it against Lesson 10 only after writing it.
- [ ] All 5 exercises are complete.

## What to submit for review

When you say "check my module," point the AI at: your own `owner_id`
explanation (step 5), confirmation of the restart-persistence test (step
3) — a short description of what you did and saw is enough, and your
completed exercises' `solution/` files.

## Why this capstone is "run and understand" rather than "build from
scratch"

Every other module's capstone in this course has you write the running
project's code yourself. This one is different on purpose: the actual
code-writing practice for *this specific* module's concepts (SQLAlchemy
models, Alembic migrations, real queries) is concentrated in Exercises
03–05, which have you make real, permanent changes to this exact backend.
Making you also re-derive the entire persistence layer from a blank file in
the capstone would either force premature, ungraded practice duplicating
the exercises, or force the capstone itself to under-teach by handing you
a skeleton — neither serves you as well as: exercises for hands-on
practice, capstone for proving you can run, verify, and truly explain the
finished result end to end.
