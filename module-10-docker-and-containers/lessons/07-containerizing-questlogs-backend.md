# Lesson 07 — Containerizing QuestLog's Backend, and Adding a Real Redis Cache

**Verified against (August 2026):** `python:3.14-slim` and `redis==8.1.0`
confirmed current per Lessons 00/06's headers; `redis.asyncio` confirmed,
via PyPI's own current `redis` package page, as the maintained async
client — the older, standalone `aioredis` package is archived, its final
release (2.0.1) unmaintained, its own functionality merged into `redis-py`
since version 4.2.0. `host.docker.internal` (used in this lesson's
hands-on section) confirmed as current, standard Docker Desktop behavior
on Windows/macOS via a live web search while writing this lesson — it is
**not** available by default on a plain Docker Engine install on native
Linux, a distinction called out explicitly below.

## What you'll learn

- How `backend/Dockerfile` (already shown in full in Lessons 02-03)
  applies this module's own teaching to QuestLog's real, actual backend.
- Exactly what changed in `backend/app/` to add a real Redis cache to
  `GET /api/quests`, and why each specific change is where it is.
- Why this app's migrations run automatically on every container start,
  and what that choice deliberately does and doesn't solve.
- How this project's test suite runs with **zero** real Redis server
  present, and why that's the correct choice, not a shortcut.
- How to build and run the backend container standalone, confirm the
  cache genuinely works via a response header, and watch invalidation
  happen in real time.

## Why this matters

This is the lesson where the whole module stops being toy examples and
becomes QuestLog itself, for real. Everything Lessons 01-06 taught —
layers, caching, multi-stage builds, networking, volumes, Compose, and
what a cache actually is — gets applied here to an application you've
been building since Module 04.

## Prerequisites

- **Lessons 01-06 in full.**
- **Module 07's FastAPI dependency-injection lesson** — this lesson's
  `RedisClient` dependency is a direct, deliberate parallel to that
  module's `DbSession`; if `Depends()` still feels unfamiliar, revisit
  `module-05-backend-fastapi/lessons/04-middleware-and-dependency-injection.md`
  first.
- **Module 08's testing lesson on the SQLite-for-tests decision** — this
  lesson's own "why a fake Redis for tests" reasoning directly mirrors
  it.
- A working local PostgreSQL (Module 06/08's own setup) still installed
  and running — this lesson's hands-on section reuses it directly,
  rather than requiring the full Compose stack (Lesson 08) just to prove
  the backend container works at all.

## The concept, explained simply

Module 09 got QuestLog's backend running on a real server by hand:
create a system user, create a venv, `pip install`, write a `.env`,
write a `systemd` unit file, `systemctl enable --now`. `backend/Dockerfile`
(Lessons 02-03 already showed you its full contents) replaces every one
of those manual steps with a single, reproducible, version-controlled
recipe — and this lesson's Redis addition demonstrates that a real,
production application can gain a genuinely new capability (a cache)
through nothing more than a few new files and a few careful edits to
existing ones, no framework, no magic.

## The details

### `backend/Dockerfile`, applied to QuestLog specifically

Open `backend/Dockerfile` (in this module's own
`project/questlog/backend/`) and read it in full now, alongside its own
extensive inline comments — every instruction in it is a direct
application of Lessons 02-03's teaching:

- The two-stage `builder`/final split, and `--prefix=/install` +
  `COPY --from=builder /install /usr/local`, is exactly Lesson 03's
  multi-stage pattern.
- `COPY requirements.txt .` before `RUN pip install`, before `COPY app
  ./app`, is exactly Lesson 02's layer-caching order.
- The dedicated `appuser` (`useradd --system --shell /usr/sbin/nologin`)
  is the containerized version of Module 09, Lesson 07, Phase 4's
  `questlog` system account — same reasoning, same specific flags,
  applied one layer further in.

**One genuinely new decision, specific to this lesson:**
```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```
This runs `alembic upgrade head` **every single time** this container
starts, before Uvicorn ever accepts a request — a real difference from
Module 09's manual deploy, where migrations were applied once, by hand,
in their own explicit step (Phase 8). This is safe specifically because
Alembic tracks which migrations have already been applied in the
database itself — running `upgrade head` against an already-current
database is a fast no-op, not a repeated, destructive re-run. **What
this deliberately does not solve:** if you ever ran *multiple* backend
container replicas at once (out of scope for this module's single-replica
Compose setup, but a real production concern), two replicas starting
simultaneously could both attempt a migration at the same moment,
racing each other — a real, known limitation of "run migrations on every
start," worth knowing about even though this module's own scope doesn't
need to solve it.

### The Redis cache, file by file

**`app/config.py`** — one new field:
```python
redis_url: str = "redis://localhost:6379/0"
```
Exactly the same `pydantic-settings` pattern `database_url` already
used — read from the `REDIS_URL` environment variable if set, this
sensible local default otherwise. `redis://<host>:<port>/<database-number>`
is Redis's own connection-URL scheme; `/0` selects database number `0`
(Redis ships 16 numbered databases per instance, `0`-`15`, by default —
QuestLog only ever uses the default).

**`app/cache.py`** (entirely new file) — read it in full now. The two
things worth calling out explicitly:
- `ConnectionPool.from_url(...)`, created once at import time, mirrors
  `app/database.py`'s `engine = create_async_engine(...)` exactly: one
  real, expensive-to-create object per process, reused for the process's
  entire lifetime, never recreated per-request.
- `get_redis_client()` is a **FastAPI dependency**, the exact same shape
  as `get_db`. Unlike `get_db`, it isn't an `async def` generator with a
  `yield` — there's no per-request "session" needing guaranteed cleanup
  the way a SQL transaction does; a `Redis` object built from an
  existing pool is cheap to construct fresh on every call.

**`app/dependencies.py`** — one new line:
```python
RedisClient = Annotated[Redis, Depends(get_redis_client)]
```
The exact same alias pattern as the existing `DbSession = Annotated[AsyncSession, Depends(get_db)]`
— any route that wants a Redis client just writes `redis: RedisClient`
in its signature, and FastAPI resolves it, exactly like `session:
DbSession` already worked.

**`app/routers/quests.py`** — the actual wiring, all of it in this one
file, **`app/repository.py` completely untouched**:
```python
@router.get("", response_model=list[Quest])
async def list_quests(
    response: Response,
    session: DbSession,
    current_user: CurrentUser,
    redis: RedisClient,
    done: bool | None = None,
    priority: str | None = None,
    quest_line: str | None = None,
):
    if done is not None or priority is not None or quest_line is not None:
        response.headers["X-Cache"] = "BYPASS"
        return await repository.list_quests(
            session, owner_id=current_user.id, done=done, priority=priority, quest_line=quest_line
        )

    cache_key = quest_list_cache_key(current_user.id)
    cached_json = await redis.get(cache_key)
    if cached_json is not None:
        response.headers["X-Cache"] = "HIT"
        return [Quest(**item) for item in json.loads(cached_json)]

    quests = await repository.list_quests(session, owner_id=current_user.id)
    response.headers["X-Cache"] = "MISS"
    await redis.set(
        cache_key,
        json.dumps([quest.model_dump(by_alias=True) for quest in quests]),
        ex=QUEST_LIST_CACHE_TTL_SECONDS,
    )
    return quests
```
Read this against Lesson 06's cache-hit/cache-miss explanation directly:
a filtered request (`?done=true`, etc.) always `BYPASS`es the cache
entirely — this module's own deliberate scope decision (Lesson 06, "why
Redis," and `app/cache.py`'s own module docstring both explain why only
the *unfiltered* call is worth caching here). An unfiltered request
checks Redis first (`redis.get`); a `HIT` deserializes the cached JSON
straight back into real `Quest` objects and returns immediately, **never
touching Postgres at all**; a `MISS` falls through to the exact same
`repository.list_quests` call this route always made, then stores the
result in Redis (`redis.set(..., ex=QUEST_LIST_CACHE_TTL_SECONDS)` — the
TTL from Lesson 06) before returning it.

Every mutating route follows the exact same one-line addition:
```python
await redis.delete(quest_list_cache_key(current_user.id))
```
placed immediately after each successful `repository.create_quest` /
`update_quest` / `delete_quest` call — Lesson 06's **active cache
invalidation**, applied for real: the instant a user's quest list
changes, their cached copy is deleted outright, so the very next `GET`
is guaranteed a fresh `MISS`, never a stale `HIT`.

### Why this is layered in the router, never inside `repository.py`

`app/repository.py` — every actual SQL query — did not change at all.
This is a deliberate architectural choice, not an oversight: the router
decides *when* a cached answer can be trusted instead of asking
Postgres; the repository stays exactly what it always was, "the only
code that knows how to talk to the database," with zero awareness a
cache exists anywhere. This separation means a future change to how
quests are queried (a new filter, a schema change) never has to think
about caching at all, and a future change to caching strategy never has
to touch a single SQL query.

### Testing code that talks to Redis, with no Redis server present

`tests/conftest.py`'s `FakeRedis` class is a small, hand-written stand-in
implementing only the three methods `app/routers/quests.py` actually
calls (`get`, `set`, `delete`), with the same async signatures
`redis.asyncio.Redis` has. `app.dependency_overrides[get_redis_client] =
lambda: fake_redis` (in the `client` fixture) swaps it in wherever a
route asks for `RedisClient` — the exact same
`app.dependency_overrides[get_db] = override_get_db` trick Module 08's
own test suite already used for the database. This mirrors Module 08's
own SQLite-for-tests decision exactly (`module-08-testing-and-quality/lessons/06-testing-with-a-database.md`):
this backend's test suite should never need a real external service
running just to exercise its own route logic. Confirm it yourself:

```bash
cd module-10-docker-and-containers/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -v
```
**Expected:** `37 passed` — 31 unchanged from Module 08, plus 6 new,
in `tests/test_caching.py`, covering cache hits, misses, the filtered-
query bypass, invalidation on every mutating route, and that two users
never share a cached answer (a real, serious bug this exact test would
catch if the cache key ever forgot to include the owner's own ID). **No
Redis server needs to be running anywhere on your machine for this to
pass.**

### Building and running the backend container, standalone

You don't need the full Compose stack (Lesson 08) to prove this specific
container works — you already have a real, local PostgreSQL running
(Module 06/08's own setup). Start just a Redis container alongside it:
```bash
docker run -d --name questlog-redis -p 6379:6379 redis:8-alpine
```
Build the backend image:
```bash
cd module-10-docker-and-containers/project/questlog/backend
docker build -t questlog-backend .
```
**Expected:** a successful, multi-stage build (Lesson 03) ending in
`naming to docker.io/library/questlog-backend:latest`.

Run it, pointed at your **host machine's** own already-running Postgres
and the Redis container you just started — both reachable from inside a
Docker Desktop container via the special hostname `host.docker.internal`
(confirmed, this lesson's header, as standard Docker Desktop behavior on
Windows — **not** available by default on a plain Docker Engine install
on native Linux, where you'd instead need `--network host` or a real
user-defined network, Lesson 04):
```bash
docker run -d --name questlog-backend-test \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://questlog:questlog_dev_password@host.docker.internal:5432/questlog" \
  -e REDIS_URL="redis://host.docker.internal:6379/0" \
  -e SECRET_KEY="$(python -c "import secrets; print(secrets.token_hex(32))")" \
  questlog-backend
```
```bash
docker logs questlog-backend-test
```
**Expected:** Alembic's own `Running upgrade ... -> ...` lines (a no-op
if your local database is already current), then Uvicorn's
`Application startup complete.`

Now watch the cache work, for real:
```bash
curl -si -X POST http://localhost:8000/api/auth/login \
  -d "username=player@questlog.local&password=dragon-slayer-1" | grep access_token
```
Copy the token from the response, then:
```bash
TOKEN="<paste the access_token value here, no quotes>"
curl -si http://localhost:8000/api/quests -H "Authorization: Bearer $TOKEN" | grep -i x-cache
```
**Expected:** `x-cache: MISS` — the first call, nothing was cached yet.
```bash
curl -si http://localhost:8000/api/quests -H "Authorization: Bearer $TOKEN" | grep -i x-cache
```
**Expected:** `x-cache: HIT` — this exact answer just came back from
Redis, without touching Postgres at all.

**Try it yourself:** create a new quest with
`curl -si -X POST http://localhost:8000/api/quests -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"title":"Test","description":"x","priority":"low","questLine":"Test"}'`,
then immediately repeat the `GET /api/quests` call above. **Predict,
before running it**, whether you'll see `HIT` or `MISS` this time, and
why — then confirm.

Clean up:
```bash
docker rm -f questlog-backend-test questlog-redis
```

## Common mistakes & gotchas

- **The container crashes immediately with a `pydantic_core.ValidationError`
  mentioning `secret_key`.** `SECRET_KEY` has no default (Module 07's
  own deliberate choice) — this `docker run` command must always include
  a real `-e SECRET_KEY=...` value; forgetting it is the single most
  common way to see this container fail on its very first start.
- **`could not translate host name "host.docker.internal"` on native
  Linux (not Windows/macOS Docker Desktop).** Confirmed in this lesson's
  header: `host.docker.internal` is a Docker Desktop convenience, not a
  universal Docker feature — on a real Linux server (like the ones
  Module 09/11 target), you'd instead reach services via a real Docker
  network (Lesson 04) or `--network host`.
- **`x-cache` header never shows `HIT`, ever, even on an immediate
  second identical request.** Double check you're calling the truly
  unfiltered route (`GET /api/quests`, no query string at all) — any
  query parameter at all (even `?done=`) routes through this lesson's
  own deliberate `BYPASS` path, never the cache.
- **Forgetting `-e REDIS_URL=...` and getting a connection-refused error
  the moment `GET /api/quests` is called** (but not before — this app
  doesn't connect to Redis until the first request that actually needs
  it, unlike `DATABASE_URL`, which Alembic touches immediately on
  startup). Double check both `-e` flags are present.

## How this connects

This lesson containerized and extended QuestLog's backend in isolation;
Lesson 08 does the same for the frontend, and — critically — assembles
**all four** services (backend, frontend, Postgres, Redis) into one real
`docker-compose.yml`, replacing this lesson's manual `host.docker.internal`
workaround with the proper, Compose-managed networking Lesson 04 already
explained.

## Quick self-check

1. Why does caching logic live inside `app/routers/quests.py` rather
   than inside `app/repository.py`?
2. What specifically does `X-Cache: BYPASS` mean, and which requests
   trigger it?
3. Why does this backend's test suite pass with zero real Redis server
   running anywhere, and what class makes that possible?
4. What real, known limitation does running `alembic upgrade head` on
   every container start deliberately not solve?
5. Why does `host.docker.internal` work in this lesson's hands-on
   section, but wouldn't necessarily work the same way once QuestLog is
   deployed to a real Linux server (Module 11)?
