# Module 07 Capstone — QuestLog Gets Real, Multi-User Auth

## What this is

Module 06's QuestLog worked, and persisted data — but it had no real
users at all: every quest was silently owned by one seeded "default"
account, and anyone who could reach the API could see and change every
quest. This capstone's code is **already built** for you at
`project/questlog/` (copied forward from Module 06, with real
signup/login/JWT auth and per-user quest ownership fully wired in) — your
job for this capstone is to **get it running yourself, verify the entire
auth flow works end to end for real, and be able to explain every piece**,
not to write it from scratch. (The hands-on *writing* practice for this
module's concepts is concentrated in Exercises 01–04, which have you
build the individual pieces — hashing, JWT inspection, a protected route,
and finally a full auth wire-up on a separate starter copy of this
backend — directly.)

## Concepts this capstone uses

Every lesson in this module: authentication vs. authorization (01),
password hashing with bcrypt and salts (02), sessions vs. JWTs (03), JWT
structure and signing (04), OAuth2's conceptual shape (05, borrowed by
this app's login endpoint), building real signup/login routes (06),
protecting routes with FastAPI dependencies and owner-scoped queries
(07), why the ORM already prevents SQL injection (08, unchanged code,
now explained), XSS/CSRF and why this app's design is resistant to one
but not the other (09), CORS configured correctly for local development
(10), and secrets/config management via `pydantic-settings` (11).

## What to do

1. **Follow [`lessons/00-setup.md`](../lessons/00-setup.md)** — install
   this module's five new backend packages, drop and recreate the
   `questlog` database, apply migrations, generate a real `SECRET_KEY`,
   and create your own `.env`, if you haven't already from the exercises.
2. **Get the backend running:**
   ```bash
   cd project/questlog/backend
   python -m venv .venv
   source .venv/Scripts/activate
   pip install -r requirements.txt
   cp .env.example .env
   python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
   alembic upgrade head
   uvicorn app.main:app --reload
   ```
3. **Get the frontend running** (a second terminal):
   ```bash
   cd project/questlog/frontend
   npm install
   npm run dev
   ```
4. **Walk through the entire auth flow yourself, in the real browser
   UI, and confirm each step:**
   - Visiting the app with no token stored redirects you to `/login`.
   - Sign up for a brand-new account (`/signup`) with an email and
     password you haven't used before. You should land on the Quest
     Board, logged in, seeing **zero** quests (a fresh account owns none).
   - Log out. Confirm you're returned to `/login` and the Quest Board is
     no longer reachable (try navigating to `/` directly — you should be
     redirected back).
   - Log back in with the **seeded demo account**
     (`player@questlog.local` / `dragon-slayer-1` — see
     `backend/README.md`). Confirm you now see the five seeded quests.
   - Create a new quest while logged in as the demo account. Log out, log
     back in as your own new account from earlier, and confirm you do
     **not** see that quest — it belongs to a different account.
5. **Prove authorization is enforced server-side, not just by the
   frontend** (Lesson 07's central point): while logged in as your own
   new account, open your browser's developer console and run:
   ```js
   fetch("http://localhost:8000/api/quests").then(r => r.status).then(console.log)
   ```
   Confirm this prints `401` (no `Authorization` header attached, since
   you called `fetch` directly, bypassing `src/api/http.ts` entirely).
   Then find one of the demo account's real quest ids (ask the demo
   account's `/api/quests` for one, using its own token) and, still
   logged in as your *own* account, call:
   ```js
   fetch("http://localhost:8000/api/quests/PASTE_DEMO_ACCOUNTS_QUEST_ID", {
     headers: { Authorization: "Bearer " + localStorage.getItem("questlog_token") }
   }).then(r => r.status).then(console.log)
   ```
   Confirm this prints `404` — not `403` — even though that quest
   genuinely exists. Write down, in your own words, why `404` (not `403`)
   is the deliberately correct answer here, then check your reasoning
   against `app/repository.py`'s `get_quest` docstring (Lesson 07).
6. **Inspect a real token.** Copy an access token from either account
   (`localStorage.getItem("questlog_token")` in the console, or a
   `curl` login response) and decode its payload by hand, using Lesson
   04's exact base64url-decoding snippet, without pasting it into any
   website. Confirm you can read the `sub`/`iat`/`exp` claims directly,
   with no secret key involved at all — the concrete proof behind
   Lesson 04's "signed, not encrypted" point.
7. **Complete Exercises 01–04** if you haven't already — they're the
   hands-on component this capstone assumes is done.

## Acceptance criteria

- [ ] The backend runs against a freshly migrated database with a real, generated `SECRET_KEY` in a git-ignored `.env`.
- [ ] A brand-new account, created via `/signup`, sees zero quests until it creates its own.
- [ ] The seeded demo account (`player@questlog.local`) still shows its five original quests.
- [ ] A direct `fetch()` call with no token returns `401`; the same call with a valid token for the *wrong* account, targeting another account's real quest id, returns `404` (confirmed directly, not just read about).
- [ ] You can decode a real token's payload by hand and correctly state which claims it contains.
- [ ] Your own written explanation of "why 404, not 403" (step 5) is genuinely yours, checked against Lesson 07 only after writing it.
- [ ] All 4 exercises are complete.

## What to submit for review

When you say "check my module," point the AI at: your own "why 404, not
403" explanation (step 5), confirmation of the direct-`fetch()` test
(step 5) and the token-decoding step (step 6) — a short description of
what you did and saw is enough — and your completed exercises' `solution/`
files.

## Why this capstone is "run and understand" rather than "build from scratch"

Exactly the same reasoning Module 06's capstone gave, still true here:
the actual code-writing practice for *this specific* module's concepts
(hashing a password directly, decoding/tampering with a JWT, adding a
protecting dependency to a route, and finally wiring a full
signup/login/ownership flow into a backend that's missing it) is
concentrated in Exercises 01–04, which have you make real, hands-on
changes yourself, with a real solution to check against. Making you also
re-derive this module's entire auth system from a blank file in the
capstone too would either force premature, ungraded duplicate practice,
or force the capstone itself to under-teach by handing you a skeleton —
neither serves you as well as: exercises for hands-on practice, capstone
for proving you can run, verify, and truly explain the finished result
end to end, including proving its security properties directly rather
than just trusting that they're true.
