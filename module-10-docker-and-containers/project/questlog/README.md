# QuestLog — Module 10 (containerized: app + PostgreSQL + Redis via Compose)

Per `RUNNING_PROJECT.md`, this folder is Module 09's finished,
deployed-by-hand `questlog/` copied forward. `backend/app/` and
`frontend/src/` are unchanged from Module 09 **except for one small,
deliberate, documented change**: a Redis-backed cache for
`GET /api/quests`'s unfiltered quest list, wired into
`backend/app/routers/quests.py` and backed by the new
`backend/app/cache.py` — see
[`lessons/06-docker-compose-multi-service-apps.md`](../../lessons/06-docker-compose-multi-service-apps.md)
for the full "what is a cache, and why Redis" explanation and
[`lessons/07-containerizing-questlogs-backend.md`](../../lessons/07-containerizing-questlogs-backend.md)
for exactly what changed, line by line, and why. `backend/frontend`'s
`package.json` also changed in one small way — see "Why `package.json`
changed" below.

```
project/questlog/
├── docker-compose.yml           — NEW this module: the whole stack, one command
├── .env.example                  — NEW: template for docker-compose.yml's required secrets
├── .pre-commit-config.yaml       — unchanged from Module 08
├── backend/
│   ├── Dockerfile                  — NEW: multi-stage Python build
│   ├── .dockerignore                — NEW
│   ├── app/cache.py                   — NEW: Redis client + cache-key helpers
│   └── ...                               — everything else unchanged from Module 09
├── frontend/
│   ├── Dockerfile                  — NEW: multi-stage Node build -> Nginx
│   ├── nginx.conf                   — NEW: this container's own Nginx site config
│   ├── .dockerignore                  — NEW
│   └── ...                               — src/ unchanged; package.json has one small change (below)
└── deploy/                        — Module 09's manual deploy artifacts, KEPT as a labeled,
                                       superseded historical reference — see deploy/SUPERSEDED.md
```

See
[`lessons/07-containerizing-questlogs-backend.md`](../../lessons/07-containerizing-questlogs-backend.md)
and
[`lessons/08-containerizing-questlogs-frontend-and-full-compose.md`](../../lessons/08-containerizing-questlogs-frontend-and-full-compose.md)
for the full, explained capstone walkthrough, and
[`../BRIEF.md`](../BRIEF.md) for this module's capstone deliverables.

## Running the whole stack with Docker Compose (this module's whole point)

```bash
cd module-10-docker-and-containers/project/questlog
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
docker compose up --build
```

**Expected:** Compose builds the `backend` and `frontend` images, pulls
`postgres:18-alpine` and `redis:8-alpine`, starts all four containers,
and streams every container's logs to your terminal, interleaved and
color-coded by service name. Once `backend` logs a line ending in
`Application startup complete.`, open:

```
http://localhost:8080
```

**Expected:** QuestLog's login page. Log in with the seeded demo account
(`player@questlog.local` / `dragon-slayer-1`). The Quest Board loads
five real quests — proof the entire chain (your browser → the `frontend`
container's Nginx on port 8080 → proxied to the `backend` container on
its own private network address → SQLAlchemy → the `postgres` container)
is genuinely working. Stop everything with `Ctrl+C`, then:

```bash
docker compose down
```

**Expected:** every container stops and is removed; the two named
volumes (`questlog_pgdata`, `questlog_redisdata`) are left intact — run
`docker compose up` again and your data is still there. `docker compose
down -v` additionally deletes both volumes, for a genuinely clean slate.

See
[`lessons/06-docker-compose-multi-service-apps.md`](../../lessons/06-docker-compose-multi-service-apps.md)
and
[`lessons/08-containerizing-questlogs-frontend-and-full-compose.md`](../../lessons/08-containerizing-questlogs-frontend-and-full-compose.md)
for the full, line-by-line explanation of every part of this.

## What changed in `backend/app/`, exactly, and why

Only three files changed, all additive:

- **`app/config.py`** — one new field, `redis_url` (defaults to
  `redis://localhost:6379/0`).
- **`app/cache.py`** (new file) — the Redis client (built on
  `redis.asyncio`, NOT the old, now-archived standalone `aioredis`
  package — see that file's own header) plus the cache-key/TTL policy.
- **`app/dependencies.py`** — one new alias, `RedisClient`, the same
  shape as the existing `DbSession`.
- **`app/routers/quests.py`** — `list_quests` now checks the cache first
  for the unfiltered case; `create_quest`/`update_quest`/`delete_quest`
  each invalidate it afterward.

`app/repository.py` — every actual database query — is **completely
untouched**. Caching is layered entirely in the router, on top of the
same, unmodified database logic Module 07 wrote. See
`lessons/06-docker-compose-multi-service-apps.md` for the full reasoning
behind picking this one, narrow, real use case (a per-user quest-list
cache) instead of a more general caching layer.

## Why `package.json` changed

`frontend/package.json` moved `@oxlint/binding-win32-x64-msvc` and
`@rolldown/binding-win32-x64-msvc` from `devDependencies` into
`optionalDependencies`. Both are Windows-only native binaries (added in
Module 08 to fix a real Windows-specific npm bug — see that module's own
`lessons/00-setup.md`). As plain `devDependencies`, `npm ci` inside this
module's Linux-based `frontend/Dockerfile` build stage would fail
outright with an `EBADPLATFORM` error the moment it tried to install a
Windows-only package on Linux. As `optionalDependencies`, npm correctly
recognizes the platform mismatch and silently skips them instead — the
same mechanism that already makes npm select the right Linux-specific
native binaries for other packages in this project automatically. See
`lessons/08-containerizing-questlogs-frontend-and-full-compose.md`'s
dedicated section on this exact change for the full explanation,
including why this is a `package.json`-only change — nothing under
`src/` was touched, and `npm run dev`/`npm run build` on Windows behave
identically to before.

## Running the test suites (both still pass, unchanged expectations)

```bash
cd backend && python -m pytest -v          # expect: 37 passed (31 from Module 08 + 6 new caching tests)
cd ../frontend && npm run test              # expect: Tests  17 passed (17), unchanged from Module 08
```

The backend test suite runs against a fake, in-memory Redis stand-in
(`tests/conftest.py`'s `FakeRedis`), never a real Redis server — see
`lessons/07-containerizing-questlogs-backend.md`'s "testing code that
talks to Redis" section for the full reasoning, which mirrors Module
08's own decision to use in-memory SQLite instead of a real Postgres for
tests.

## Running it WITHOUT Docker (unchanged from Module 09, for comparison)

Still works exactly as before — Docker is this module's better way to
run the stack, not the only way. The one difference: `backend/.env` now
optionally accepts `REDIS_URL` (defaults to `redis://localhost:6379/0`;
you'd need a locally-running Redis for the cache to actually engage — if
Redis is unreachable and you run the backend this way without one, every
`GET /api/quests` call will raise a connection error the moment it tries
`redis.get(...)`, since this module's own scope doesn't include making
the cache optional/fail-open — see `lessons/06`'s "Try it yourself" for
an exercise exploring exactly this).

```bash
cd module-10-docker-and-containers/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

```bash
cd module-10-docker-and-containers/project/questlog/frontend
npm install
npm run dev
```

## Deploying this to a real server

Module 09 did this by hand — see `deploy/SUPERSEDED.md` for exactly
which of those manual steps this module's Docker/Compose setup now
replaces, and why the `deploy/` folder itself is kept, unused, as a
historical reference rather than deleted. Automatically deploying a
container stack like this one to a real, internet-reachable server is
Module 11's job.
