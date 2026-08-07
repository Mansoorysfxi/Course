# Capstone Brief — Containerize QuestLog's Full Stack With Docker Compose

## What you're doing

Take this module's `project/questlog/` — Module 09's finished,
deployed-by-hand QuestLog, copied forward, plus this module's own small,
real Redis cache addition — and run its **entire** stack (backend,
frontend, PostgreSQL, Redis) as four containers, wired together with one
`docker-compose.yml`, started and stopped with one command each.

This is mostly not a coding exercise — `project/questlog/backend/app/`
and `project/questlog/frontend/src/` are already exactly what this
module's Lesson 07 documented, and `docker-compose.yml`,
`backend/Dockerfile`, and `frontend/Dockerfile` already exist, fully
built and explained in Lessons 07-08. Your job is to **run it, verify it
genuinely works end to end, break something on purpose and diagnose it,
and write up what you found** — the same "understand it well enough to
explain and to fix" standard Module 09's own capstone used.

## Before you start

- [ ] All six exercises in this module are done and reviewed.
- [ ] You've read Lessons 00-08 in full, in order.
- [ ] Docker Desktop is installed, WSL2 integration is on, and
      `docker compose version` succeeds (Lesson 00's own verification
      section).
- [ ] You've read `project/questlog/README.md` and
      `project/questlog/deploy/SUPERSEDED.md` so you know exactly what
      changed since Module 09 and why.

## What to actually do

### Part 1 — Run the whole stack from a cold start

```bash
cd module-10-docker-and-containers/project/questlog
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
docker compose up --build
```
Confirm, in order: `postgres` and `redis` both report healthy in the
logs, `backend`'s own `alembic upgrade head` runs and Uvicorn reports
`Application startup complete.`, and `frontend`'s build stage completes
without the `EBADPLATFORM` error this module's `package.json` change
specifically prevents.

### Part 2 — Verify it end to end, like a real user

Open `http://localhost:8080` in a real browser (not `curl` for this
part). Log in with `player@questlog.local` / `dragon-slayer-1`. Confirm
the Quest Board loads five real quests. Using your browser's developer
tools (Network tab), confirm:

- The `GET /api/quests` request's `Request URL` is same-origin
  (`http://localhost:8080/api/quests`), never `localhost:8000` directly.
- Reloading the page twice within 30 seconds shows `x-cache: MISS` on
  the first `GET /api/quests` response and `x-cache: HIT` on the second.
- Creating a new quest, then reloading, shows the new quest immediately
  (proof cache invalidation on write is working — not a 30-second-stale
  answer).

### Part 3 — Prove persistence, then prove its absence, on purpose

```bash
docker compose down
docker compose up -d
```
Log in again; confirm your created quest from Part 2 is still there
(`questlog_pgdata`'s named volume, Lesson 05, survived).

```bash
docker compose down -v
docker compose up -d
```
Log in again; confirm you're back to exactly the five seeded quests, and
your Part-2 quest is genuinely gone — explain, in your own write-up,
precisely why.

### Part 4 — Break something on purpose, then fix it

Deliberately reproduce **one** of the following (pick whichever you
haven't already hit by accident while working through this module), then
diagnose and fix it using only `docker compose logs`:

- Remove or misspell a required environment variable in `.env` (e.g.
  delete `SECRET_KEY`'s line entirely) and observe exactly how the
  `backend` container fails.
- Change `frontend/nginx.conf`'s `proxy_pass` target back to
  `http://127.0.0.1:8000` (Module 09's now-superseded value) and observe
  exactly how `/api/*` requests fail once containerized.
- Temporarily revert `frontend/package.json`'s `optionalDependencies`
  change back to `devDependencies` and observe the exact `EBADPLATFORM`
  error during `docker compose up --build`.

Fix it, confirm the stack works again, and document exactly what broke,
what the real error message said, and how you diagnosed the cause.

## Deliverables

Write up a short report (a new file, `project/CONTAINERIZATION_REPORT.md`
— create this yourself; no fixed template, honest content matters more
than a fixed shape) covering:

1. **Confirmation of Parts 1-3**, with real command output/screenshots
   (or a precise description of what you observed).
2. **Part 4's deliberately broken-then-fixed scenario** — the exact
   error, how you found it, and the fix.
3. **Your own answers to Lesson 08's "what this containerized setup
   deliberately does not yet do" list** — for each named gap, explain in
   your own words why it's acceptable for now and which later module
   fixes it.
4. **A comparison, in your own words, of at least three specific things**
   that were manual, error-prone steps in Module 09's deploy and are now
   handled automatically by this module's Dockerfiles/Compose file —
   name the specific Module 09 phase/step and its Module 10 replacement
   for each.

## Acceptance criteria (what "done" looks like)

- [ ] `docker compose up --build` succeeds from a clean checkout, with no
      manual intervention beyond creating `.env`.
- [ ] Part 2's cache-hit/cache-miss/invalidation behavior is genuinely
      observed, not just asserted.
- [ ] Part 3's volume-persistence and volume-deletion behaviors are both
      genuinely observed.
- [ ] `CONTAINERIZATION_REPORT.md` exists and covers all four numbered
      points above, honestly.
- [ ] You can explain, without looking anything up, the full request
      path a browser's `GET /api/quests` takes through this containerized
      system, naming every container and network hop involved, in order,
      including exactly where the Redis cache sits in that path on a hit
      versus a miss.
- [ ] No stray containers, images, or volumes from this capstone are left
      running on your machine when you're done — `docker compose down`
      (or `-v`, if you want a fully clean slate) before considering this
      finished.

## A note on scope

This capstone does **not** ask you to deploy this containerized stack to
a real, internet-reachable server — that's Module 11's job, building on
these exact, unchanged Dockerfiles. This capstone's whole point is
proving the *packaging* itself is correct and reproducible on your own
machine, the same honest, staged approach Module 09 took toward its own
real-VPS requirement.
