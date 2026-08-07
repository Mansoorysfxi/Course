# Lesson 06 — Docker Compose for Multi-Service Apps (and: What a Cache Actually Is)

**Verified against (August 2026):** `docker compose` (Compose V2, built
into the Docker CLI) confirmed current per Lesson 00; the Compose file's
top-level `version:` key confirmed obsolete/ignored via Docker's own
current documentation (`docs.docker.com/reference/compose-file/legacy-versions/`)
— this lesson's own example, and this module's real
`project/questlog/docker-compose.yml`, both omit it entirely, on
purpose. `redis:8-alpine` and the `redis` PyPI package (`8.1.0`,
providing `redis.asyncio`) confirmed current via Docker Hub and PyPI
respectively.

## What you'll learn

- Why running several related containers by hand, with separate `docker
  run` commands, gets unmanageable fast — and how `docker-compose.yml`
  fixes that.
- Every piece of Compose file syntax this course actually uses:
  `services`, `image` vs. `build`, `environment`, `ports`, `volumes`,
  `depends_on` (including the healthcheck-based form), `restart`, and
  top-level `volumes:`.
- The `docker compose` commands you'll use constantly: `up`, `up -d`,
  `up --build`, `down`, `down -v`, `logs`, `ps`.
- What a **cache** actually is, why you'd reach for Redis specifically
  instead of, say, a plain Python dictionary, and what a **TTL** and
  **cache invalidation** mean — the conceptual groundwork Lesson 07
  applies to QuestLog's own, real `GET /api/quests` route.

## Why this matters

Every real application worth containerizing is more than one process.
QuestLog alone needs a backend, a database, a cache, and a frontend —
four separate containers that all need to start in a sensible order, find
each other over the network (Lesson 04), and keep their data across
restarts (Lesson 05). `docker-compose.yml` is the one file that describes
all of that, together, so the entire application starts (or stops) with
one command instead of four separately-remembered `docker run` invocations
with a dozen flags each.

## Prerequisites

- **Lessons 01-05 in full** — this lesson's whole point is combining
  everything they taught (containers, layers, networking, volumes) into
  one declarative file, so it assumes you're comfortable with each piece
  individually first.
- **Module 06's databases lesson** — a rough sense of what Redis is as a
  "NoSQL, key-value" option, mentioned there conceptually; this lesson
  is where that mention finally becomes real, running code.

## The concept, explained simply

### Why Compose exists

Running QuestLog's four services by hand would mean four separate,
long `docker run` commands, typed in the right order, every single time,
remembering every port mapping, every environment variable, every
volume, every network flag — and manually working out that Postgres
needs to be up before the backend tries to connect to it. `docker
compose` replaces all of that with one YAML file describing every
service, once, declaratively — "here's what I want to exist," not "here's
the exact sequence of commands to run" — and one command,
`docker compose up`, that reads it and makes it so.

### What a cache actually is

QuestLog's `GET /api/quests` route currently (Module 07 onward) runs a
real SQL query against Postgres, every single time it's called, even
though a given user's own quest list usually hasn't changed between one
page load and the next. A **cache** is a copy of an expensive-to-produce
answer, kept somewhere much faster to read from, specifically so a
repeated request for the same answer doesn't have to redo the expensive
work.

**Game-dev analogy:** this is exactly the same idea as caching an
expensive-to-compute value (say, a navmesh, or a baked lighting result)
so a level doesn't recompute it from scratch on every single frame or
every single load — you compute it once, store the result somewhere
fast to re-read, and only redo the real work when the underlying data
that produced it has actually changed.

**Why not just use a plain Python dictionary as the cache**, sitting in
a global variable in `app/`? For a single, one-process toy script, that
would work fine. It breaks down for two very real reasons this course's
own architecture already has to account for: (1) a Python dict lives
entirely inside **one running process's own memory** — restart that
process (which happens on every single code deploy, and every single
`docker compose up --build`) and the dict, and every "cached" value in
it, is gone; (2) a real production deployment often runs **more than one
copy** of a backend process at once, for reliability — a dict living
inside Process A's own memory is completely invisible to Process B, so
two users hitting different backend replicas could see inconsistent,
uncached-vs-cached answers with no way to keep them in sync. **Redis**
solves both problems by being a **separate, external process** (its own
container, in this course) that every backend replica can reach over the
network — one shared cache, survives an individual backend process
restarting, visible identically to every replica.

### TTL and cache invalidation

A cached value doesn't live forever. A **TTL (Time To Live)** is how long
a cached value is trusted before it's discarded automatically, even if
nothing ever explicitly told the cache "this is now wrong." **Cache
invalidation** is the opposite, active approach: deliberately deleting a
cached value the *instant* the underlying data changes, rather than
waiting for its TTL to run out on its own. There's a well-known, only
half-joking saying in software engineering: *"there are only two hard
things in computer science: cache invalidation and naming things"* — and
it's genuinely true. It's easy to invalidate **too little** (a user
creates a quest and doesn't see it appear, because a stale cached answer
is still being served) or **too much** (invalidating so aggressively that
the cache barely ever gets a chance to actually help). This course's own
QuestLog cache (Lesson 07) uses **both** together, deliberately, as a
safety net for each other: it actively invalidates on every
create/update/delete (so the common case is always correct, immediately),
**and** it sets a short, 30-second TTL anyway — so even if some future
code change ever added a new way to modify a quest and forgot to
invalidate the cache for it, the mistake would self-heal within 30
seconds on its own, rather than serving a permanently stale answer
forever.

## The details

### A toy multi-service Compose file: a visit counter, backed by Redis

Create a fresh scratch folder (outside this course's repo), with this
structure:
```
compose-demo/
├── docker-compose.yml
└── counter/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py
```

**`counter/requirements.txt`:**
```
redis==8.1.0
```

**`counter/app.py`:**
```python
from http.server import BaseHTTPRequestHandler, HTTPServer

import redis

# "redis" here is not a placeholder -- it's the exact service name this
# folder's own docker-compose.yml gives the Redis container, resolvable
# as a real hostname purely because both containers share the network
# Compose creates automatically. See lessons/04-docker-networking.md.
r = redis.Redis(host="redis", port=6379, decode_responses=True)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # INCR atomically increments a Redis key and returns the new
        # value -- "atomically" meaning even if two requests hit this at
        # the exact same instant, Redis guarantees neither increment is
        # lost, unlike a plain "read, add one, write back" done by hand
        # in Python, which has a real race condition under concurrent
        # requests.
        count = r.incr("visits")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"This page has been visited {count} times.\n".encode())


HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
```

**`counter/Dockerfile`:**
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```
(A single-stage build is fine for this toy example — one small, pure-
Python dependency, no meaningful size difference a multi-stage build
would improve. Lesson 03's own guidance was to reach for multi-stage
builds when they'd actually help, not reflexively every time.)

**`docker-compose.yml`** (in `compose-demo/`, alongside `counter/`, not
inside it):
```yaml
services:
  counter:
    build: ./counter
    ports:
      - "5000:5000"
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:8-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
```

**Line by line, everything new:**
- No top-level `version:` key at all — see this lesson's header;
  current `docker compose` ignores it, so this course never writes it.
- `services:` — the top-level key listing every container this file
  manages. Each key underneath it (`counter`, `redis`) becomes both that
  service's resolvable network hostname (Lesson 04) and the name you'll
  use in `docker compose` subcommands (e.g. `docker compose logs redis`).
- `build: ./counter` — instead of `image:` (naming an existing,
  already-built image, the way `redis:8-alpine` does below), `build:`
  tells Compose to build a new image itself, from a Dockerfile found in
  the given folder, before starting this service.
- `ports: - "5000:5000"` — YAML's list syntax for exactly the `-p`
  mapping Lesson 01/04 already covered by hand; `host:container`.
- `depends_on: redis: condition: service_healthy` — tells Compose not to
  start `counter` at all until `redis`'s own `healthcheck:` (below)
  reports healthy. This is the **healthcheck-based** form of
  `depends_on` — a plain `depends_on: - redis` (no `condition:`) would
  only wait for the `redis` **container process to have started**, not
  for Redis itself to actually be ready to accept connections yet — a
  real, common source of a backend crashing on its very first start with
  a connection-refused error, a fraction of a second too early.
- `healthcheck:` (under `redis`) — `test: ["CMD", "redis-cli", "ping"]`
  runs `redis-cli ping` *inside* the Redis container itself, on a
  repeating interval (`interval: 5s`), up to `retries: 5` times, each
  allowed up to `timeout: 5s` — Compose considers this service "healthy"
  the moment this command first succeeds (Redis's own `redis-cli` client
  is already installed inside the official `redis` image, so no extra
  setup is needed to use it as a healthcheck).

Run it:
```bash
cd compose-demo
docker compose up --build
```
**Expected:** interleaved, color-coded logs from both `redis` and
`counter`, ending with `counter`'s process quietly waiting (no crash) —
proof `depends_on`'s healthcheck condition worked as described.

In another terminal:
```bash
curl http://localhost:5000
curl http://localhost:5000
curl http://localhost:5000
```
**Expected:** `This page has been visited 1 times.`, then `2`, then `3`
— a real, working, Redis-backed counter.

**Now, the key demonstration** — prove this data lives in Redis, not in
the `counter` process's own memory:
```bash
docker compose restart counter
curl http://localhost:5000
```
**Expected:** `4`, not a reset back to `1` — even though the `counter`
process itself was just fully restarted, the count survived, because it
was never stored in that process's own memory at all; it lives in the
separate `redis` container the whole time. **This is the concrete,
hands-on proof of this lesson's earlier "why not just a Python dict"
explanation** — a dict-based counter would have reset to `0` the instant
`counter` restarted; this one didn't, because the state genuinely lives
somewhere else.

Stop everything:
```bash
docker compose down
```
**Expected:** both containers stop and are removed; no `volumes:` section
existed in this toy file at all, so nothing about Redis's own data
persistence was addressed here — Redis's counter value is gone the
moment this exact command runs (a deliberate simplification for this toy
example; the real `project/questlog/docker-compose.yml`, Lesson 08, does
give Redis a named volume, mirroring Lesson 05's own reasoning, even
though QuestLog's specific cache use only ever needs 30 seconds of
persistence in practice).

**Try it yourself:** add `environment: - PYTHONUNBUFFERED=1` under
`counter:` (a list-form `environment:` block — Compose also accepts a
mapping form, `KEY: value`, which this module's real
`project/questlog/docker-compose.yml` uses instead; both are valid,
equivalent YAML) and rebuild. Confirm with `docker compose logs counter`
that this changes nothing about the app's own behavior here (this
particular toy script doesn't buffer output meaningfully either way) —
the point of this exercise is purely getting comfortable adding an
`environment:` entry and confirming, via `docker compose up --build`,
that Compose picked it up.

### Compose commands you'll use throughout the rest of this module

| Command | What it does |
|---|---|
| `docker compose up` | Builds (if needed) and starts every service, attached to your terminal (`Ctrl+C` stops everything). |
| `docker compose up -d` | Same, but detached (background) — your terminal is free immediately. |
| `docker compose up --build` | Forces a rebuild of any service with a `build:` key, even if nothing looks changed (useful when you've edited a Dockerfile itself, which Compose doesn't always detect as needing a rebuild on its own). |
| `docker compose down` | Stops and removes every container and the network Compose created — **leaves named volumes alone**. |
| `docker compose down -v` | Same, **and** also removes every named volume this project defined — a genuinely clean slate. |
| `docker compose ps` | Lists this project's own containers and their status (a scoped version of `docker ps`). |
| `docker compose logs <service>` | Shows one specific service's logs (omit `<service>` for all of them). |

## Common mistakes & gotchas

- **`depends_on: - redis` (no `condition:`) "should have waited for
  Redis to be ready" but didn't.** Without an explicit
  `condition: service_healthy` (which itself requires that service to
  define its own `healthcheck:`), `depends_on` only waits for the
  dependency's **container to have started**, not for whatever's running
  inside it to actually be ready — see this lesson's own worked example
  for the fix.
- **Editing a Dockerfile, then running plain `docker compose up`, and
  seeing no changes take effect.** Compose doesn't always detect that a
  Dockerfile itself changed as reason enough to rebuild automatically —
  `docker compose up --build` forces it explicitly; this course's own
  habit is to just always include `--build` while actively developing a
  Dockerfile, and drop it once it's stable.
- **Running `docker compose down -v` reflexively, out of habit**, and
  being surprised real data (QuestLog's own quests, once Lesson 08's real
  compose file is in play) is gone. The `-v` flag is a genuinely
  destructive, deliberate choice — plain `docker compose down` is the
  safe default for "stop everything for now."
- **Two services both trying to reach each other before either one is
  actually ready, with no `depends_on` at all.** Compose starts services
  with no explicit `depends_on` relationship in parallel, in no
  guaranteed order — always declare real startup-order dependencies
  explicitly, as this lesson's example did.

## How this connects

This lesson's toy example — one app service, one Redis service, wired
together with `depends_on`'s healthcheck condition — is structurally
identical to what Lesson 08 does for QuestLog's real, four-service stack,
just with Postgres and a real FastAPI backend/React frontend in place of
this lesson's tiny counter script. Lesson 07 picks up the *cache*
half of this lesson's material and applies it to QuestLog's actual,
real `GET /api/quests` route.

## Quick self-check

1. Why does a cache backed by a plain Python dictionary break down once
   more than one backend process (or a restarted one) is in the
   picture, in a way Redis specifically solves?
2. What's the difference between a TTL and active cache invalidation,
   and why does this course's own QuestLog cache (Lesson 07) use both
   together rather than just one?
3. What specifically does `depends_on`'s `condition: service_healthy`
   wait for, that a plain `depends_on: - redis` (no condition) does not?
4. In the toy counter example, why did the visit count survive
   `docker compose restart counter`, but would NOT have survived if the
   counter had instead been stored in a plain Python variable inside
   `app.py`?
5. What is the practical difference between `docker compose down` and
   `docker compose down -v`, and which one would delete QuestLog's own
   stored quests (Lesson 08)?
