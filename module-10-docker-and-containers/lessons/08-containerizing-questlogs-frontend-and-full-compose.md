# Lesson 08 — Containerizing QuestLog's Frontend, and the Full Compose Stack

**Verified against (August 2026):** `node:24-alpine` (Node 24, current
Active LTS since October 28, 2025 per nodejs.org's own release schedule)
and `nginx:1.30-alpine` (Nginx 1.30.4, matching the exact version
Module 09, Lesson 06 already verified) both confirmed current via Docker
Hub while writing this lesson. `postgres:18-alpine` confirmed current
(18.4-alpine, matching the PostgreSQL 18.x this course's `backend/`
already runs against locally) via Docker Hub. The `npm ci` +
`optionalDependencies` platform-skip behavior described below was
confirmed via multiple current sources on npm's own documented
`EBADPLATFORM` behavior.

## What you'll learn

- Why the frontend's Dockerfile needs a multi-stage build far more
  essentially than the backend's (Lesson 03's claim, made concrete here).
- The real, necessary `package.json` change this module made, and
  exactly why `npm ci` would otherwise fail inside a Linux container.
- How `frontend/nginx.conf` compares, line by line, to Module 09's
  hand-written `deploy/nginx/questlog.conf` — and the one line that's
  genuinely different, and why.
- How to assemble and run QuestLog's **entire** stack — Postgres, Redis,
  backend, frontend — with one `docker-compose.yml` and one command.
- What this containerized setup still deliberately does not do, honestly
  accounted for, the same way Module 09, Lesson 08 did for the manual
  deploy.

## Why this matters

This is this module's capstone payoff: the exact multi-service
application Module 09 deployed by hand, painfully, one `apt install` at
a time, now starts — identically, every time, on any machine with Docker
installed — with `docker compose up --build`.

## Prerequisites

- **Lessons 01-07 in full** — this lesson assumes every concept from
  layers through networking through the backend's own Redis wiring.
- **Module 09, Lesson 08** — this lesson repeatedly compares against it
  directly; skim it again now if it's not fresh.

## The concept, explained simply

Module 09, Lesson 08 already established the core idea by hand: build
the frontend on a machine with a JavaScript toolchain, ship only the
resulting static files (`dist/`) to wherever they'll actually be served
from, and never install Node.js on the server that serves them at all.
`frontend/Dockerfile`'s multi-stage build (Lesson 03 introduced the
mechanism; this lesson applies it) is the packaged, automatic version of
exactly that same idea: Stage 1 is a disposable, ephemeral "build
machine" that exists only for the seconds it takes to run `npm run
build`; Stage 2 is "the server" — plain Nginx, with zero Node.js inside
it at all.

## The details

### The real, necessary `package.json` change

Open `frontend/package.json`. Compare it against Module 09's own copy —
exactly one change: `@oxlint/binding-win32-x64-msvc` and
`@rolldown/binding-win32-x64-msvc` moved from `devDependencies` into a
new `optionalDependencies` block.

**Why this is genuinely required, not a style preference:** both
packages are Windows-only native binaries (added in Module 08,
`lessons/00-setup.md`, to fix a real, documented Windows-specific npm
bug). As plain `devDependencies`, npm's own platform-matching rules
treat an `os`-field mismatch as a **hard error** (`EBADPLATFORM`) — `npm
ci` (or `npm install`) inside `frontend/Dockerfile`'s Linux-based
`node:24-alpine` build stage would fail outright the moment it reached
either package, because neither one's own declared platform (`win32`)
matches the Linux container actually running the install. Moving them
into `optionalDependencies` tells npm the opposite: "install this if
your platform matches, silently skip it otherwise" — the exact same
mechanism that *already*, automatically, correctly selects Linux-specific
native binaries for other packages in this project (`rolldown`,
`oxlint` themselves each ship their own per-platform `optionalDependencies`
this project's `package-lock.json` already resolves correctly). This is
a `package.json`/`package-lock.json`-only change — **nothing under
`src/` was touched**, and `npm run dev`/`npm run build` on your own
Windows machine behave completely identically to before (confirmed:
Module 10's own regeneration of `package-lock.json`, plus a full
`npm run test` and `npm run build` pass, both done while preparing this
module).

### `npm ci` vs. `npm install`

`frontend/Dockerfile` uses `npm ci`, never `npm install`. `npm ci`
("clean install") deletes any existing `node_modules` first and installs
**exactly** what `package-lock.json` specifies, failing outright if
`package.json` and `package-lock.json` have drifted out of sync with
each other at all. `npm install` would instead silently update the
lockfile to reconcile any such drift. A Docker build should never have
that kind of silent, unreproducible behavior — this course wants
"build this image" to produce the same result today as a year from now,
given the same two files, which is exactly what `npm ci` guarantees and
`npm install` does not.

### `frontend/Dockerfile`, read in full

Open `frontend/Dockerfile` now and read every comment in it. The two
stages, concretely:

- **Stage 1 (`build`, `FROM node:24-alpine`)** — `COPY package.json
  package-lock.json ./` then `RUN npm ci` **before** `COPY . .`, for
  exactly Lesson 02's layer-caching reason: editing a `.tsx` file should
  never force a full dependency reinstall. Then `ARG VITE_API_BASE_URL=""`
  /`ENV VITE_API_BASE_URL=$VITE_API_BASE_URL` followed by `RUN npm run
  build` — this is Module 09, Lesson 08, Step 1's exact
  `VITE_API_BASE_URL= npm run build` trick (empty string, baked in at
  build time so the compiled JavaScript makes same-origin, relative API
  requests), just declared as a Docker build argument instead of typed
  by hand before a command.
- **Stage 2 (`FROM nginx:1.30-alpine`)** — `COPY --from=build /app/dist
  /usr/share/nginx/html` is this whole Dockerfile's entire payoff:
  **zero** trace of Node.js, npm, or any of this project's ~170 npm
  packages exists anywhere in the final, shipped image — only the
  finished, static `dist/` files. `COPY nginx.conf
  /etc/nginx/conf.d/default.conf` installs this lesson's own Nginx
  config (next section) in place of the official image's own default.

### `frontend/nginx.conf` vs. Module 09's `deploy/nginx/questlog.conf`

Open both files side by side (Module 09's copy is preserved, unused, at
`project/questlog/deploy/nginx/questlog.conf` — see
`project/questlog/deploy/SUPERSEDED.md`). They are **nearly identical**
— same `listen`, same `root`/`index`, same `location /api/` block
structure, same `try_files $uri /index.html;` SPA fallback (Module 09,
Lesson 06 explained exactly why that line is necessary for a
client-side-routed React app). **The one real difference:**
```nginx
# Module 09 (same machine, same localhost):
proxy_pass http://127.0.0.1:8000;

# This module (separate containers):
proxy_pass http://backend:8000;
```
This is Lesson 04's entire networking lesson, made concrete in one line:
Module 09's Nginx and backend were two *processes* on the *same*
machine, sharing one real `localhost`. This module's Nginx and backend
are two *containers*, each with their own private network namespace and
their own private `localhost` — `backend` is not a placeholder, it's the
literal service name `docker-compose.yml` (next section) gives the
backend container, resolvable purely because both containers share the
network Compose creates automatically (Lesson 04's user-defined-network
DNS resolution, for real).

### Assembling the full `docker-compose.yml`

Open `project/questlog/docker-compose.yml` now, in full, alongside its
own extensive comments. Every piece is something you've already learned,
combined:

- **`postgres`** — `postgres:18-alpine`, a named volume
  (`questlog_pgdata`, Lesson 05) for its data directory, a `healthcheck`
  using `pg_isready` (Lesson 06's healthcheck pattern, applied to
  Postgres instead of Redis this time).
- **`redis`** — `redis:8-alpine`, its own named volume
  (`questlog_redisdata`), a `redis-cli ping` healthcheck (exactly
  Lesson 06's toy example).
- **`backend`** — `build: ./backend` (Lesson 07's own Dockerfile),
  `environment:` pointing `DATABASE_URL`/`REDIS_URL` at `postgres`/
  `redis` **by service name** (Lesson 04), `depends_on:` with
  `condition: service_healthy` for **both** dependencies (Lesson 06's
  healthcheck-based form — this app genuinely needs both ready before it
  starts, not just started).
- **`frontend`** — `build: ./frontend` with `args: VITE_API_BASE_URL: ""`
  (this lesson's own section above), `depends_on: - backend` (a plain
  form here — Nginx itself starts fine even if the backend isn't ready
  the instant it starts; a request arriving before the backend is ready
  would just fail that one request, not crash Nginx itself, so a
  healthcheck-based dependency isn't strictly necessary here the way it
  is for the backend's own database connections).
- **`volumes:`** (top-level) — declares `questlog_pgdata` and
  `questlog_redisdata` so Compose knows to create and manage them.

### Running the whole stack

```bash
cd module-10-docker-and-containers/project/questlog
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
docker compose up --build
```
**Expected:** Compose builds `backend` and `frontend`, pulls `postgres`
and `redis`, and starts all four, in dependency order — you'll see
`postgres` and `redis` report healthy in the logs before `backend`'s own
`alembic upgrade head` / `Application startup complete.` lines appear.

Open `http://localhost:8080` in a real browser. **Expected:** QuestLog's
login page. Log in with `player@questlog.local` / `dragon-slayer-1`.
**Expected:** the Quest Board loads five real quests — proof the entire
chain (browser → `frontend` container's Nginx on port 8080 → proxied,
container-to-container, to `backend` on `http://backend:8000` → SQLAlchemy
→ `postgres` container, with `redis` caching the unfiltered list call
along the way) genuinely works, end to end, started by one command.

Open your browser's developer tools (Network tab), reload the Quest
Board once, then reload it again within 30 seconds. **Expected:** the
`GET /api/quests` request's response headers show `x-cache: MISS` the
first time and `x-cache: HIT` the second — the exact same behavior
Lesson 07 demonstrated with a standalone container, now happening inside
the real, full, containerized stack.

Tear down:
```bash
docker compose down
```
Bring it back up (no `--build` needed this time — nothing changed):
```bash
docker compose up -d
```
Log in again. **Expected:** the same five seeded quests, plus any you
created — proof `questlog_pgdata`'s named volume (Lesson 05) genuinely
survived the containers being removed and recreated.

**Try it yourself:** run `docker compose down -v` this time (the
destructive flag), then `docker compose up -d` again, and log in with
the demo account once more. **Predict, before running it**, whether
you'll see five quests or zero — then confirm, and explain, in your own
words, exactly which named volume's removal caused the result you saw.

## What this containerized setup deliberately does not yet do (honest accounting, same as Module 09)

- **No HTTPS.** Plain `http://localhost:8080` — Module 11 adds a real
  domain and TLS.
- **No automated, hands-off deployment anywhere.** `docker compose up
  --build` still has to be run by a human, on some machine. Module 11
  automates this into a real CI/CD pipeline.
- **A single replica of everything, no redundancy.** If the one
  `backend` container crashes in a way `restart: unless-stopped` can't
  recover from (or the one `postgres` container's disk fills up),
  QuestLog is offline until a human intervenes — identical, honestly,
  to Module 09's own accepted trade-off at this scale.
- **This exact stack has only ever run on your own machine.** Everything
  in this lesson proves the multi-container packaging itself works
  correctly and reproducibly — it does not yet prove it on a real,
  internet-reachable server. That's Module 11's job, building on this
  module's own images directly (the same `backend/Dockerfile` and
  `frontend/Dockerfile`, unchanged, become exactly what a real cloud
  deployment builds and runs).

## Common mistakes & gotchas

- **`npm ci` fails inside the `frontend` build stage with an
  `EBADPLATFORM` error**, if you ever revert or hand-edit
  `package.json` back to the original `devDependencies` placement.
  Confirm `@oxlint/binding-win32-x64-msvc` and
  `@rolldown/binding-win32-x64-msvc` are under `optionalDependencies`,
  and that `package-lock.json` was regenerated to match (an `npm install`
  run once, locally, after any such edit, keeps both files in sync).
- **The frontend loads, but every `/api/...` request fails.** Almost
  always `frontend/nginx.conf`'s `proxy_pass` target — double-check it
  says `http://backend:8000`, not `http://127.0.0.1:8000` (Module 09's
  now-superseded value) or `http://localhost:8000` (which, inside the
  `frontend` container, means the `frontend` container itself, per
  Lesson 04).
- **`backend` container keeps restarting in a crash loop right after
  `postgres`/`redis` report healthy.** Check `docker compose logs
  backend` first — the most common real cause is a missing or malformed
  `SECRET_KEY` in your `.env` file (see this project's own
  `.env.example`); the second most common is a typo in `DATABASE_URL`/
  `REDIS_URL`'s service-name hostnames.
- **A change to `frontend/src/` doesn't seem to take effect after
  `docker compose up`.** Remember Lesson 06's own gotcha: Compose
  doesn't always rebuild automatically just because you ran `up` again —
  use `docker compose up --build` while actively iterating on either
  Dockerfile or the application code it packages.

## How this connects

This lesson completes this module's capstone: QuestLog, the exact
application built since Module 04, now runs as four containers, wired
together with everything Lessons 01-07 taught, started and stopped with
one command each. `project/BRIEF.md` has this module's full capstone
deliverables and acceptance criteria. Module 11 picks up exactly here —
these same Dockerfiles, unchanged, become the images a real CI/CD
pipeline builds and deploys automatically, to a real server, with HTTPS
and a real domain.

## Quick self-check

1. Why does the frontend's multi-stage build matter *more* than the
   backend's, in terms of what's actually discarded between stages?
2. What specifically would happen, and why, if `package.json` still had
   the two Windows-only binding packages under `devDependencies` when
   `frontend/Dockerfile`'s `npm ci` step ran?
3. What is the one line that's genuinely different between
   `frontend/nginx.conf` and Module 09's `deploy/nginx/questlog.conf`,
   and why?
4. In `docker-compose.yml`, why does `backend` use a healthcheck-based
   `depends_on` for both `postgres` and `redis`, while `frontend` uses a
   plain `depends_on` for `backend`?
5. After `docker compose down -v` and a fresh `docker compose up -d`,
   why does the demo account's five seeded quests reappear, but any
   quest you created yourself does not?
