# Module 10 — Docker & Containers

**Phase:** 3 — DevOps & Deployment (middle module)
**Estimated time:** 14-18 hours (includes real hands-on time building
and running containers — budget more than a pure-reading module, less
than Module 09's real-VPS-deployment time)
**Verified against (August 2026):** Docker Desktop **4.85.0** (released
August 3, 2026); `docker compose` (Compose V2, built into the Docker
CLI) confirmed current, the standalone hyphenated `docker-compose` (V1)
confirmed deprecated; `python:3.14-slim`, `node:24-alpine`,
`nginx:1.30-alpine`, `postgres:18-alpine`, `redis:8-alpine` all confirmed
current via Docker Hub; `redis` (PyPI) `8.1.0` confirmed current,
providing the maintained `redis.asyncio` client (the old standalone
`aioredis` package is archived/merged into `redis-py`, not used
anywhere in this module). Every fact above was checked with a live web
search or a direct fetch of the relevant official source while writing
this module, not recalled from memory — see each lesson's own header for
the specific source.

## What this module is

Module 09 deployed QuestLog to a real server **by hand** — every
command typed out, every config file written from scratch, on purpose,
so the pain of doing it manually would be real and memorable. This
module is the payoff of that pain: **Docker** packages an application
together with the exact runtime and dependencies it needs, as a
portable, reproducible **image**, so "get a fresh, correctly-configured
copy of QuestLog running" stops being a multi-page runbook of manual
steps and becomes one command: `docker compose up --build`.

This module also does one small, real, deliberate thing beyond pure
DevOps: it gives QuestLog's backend a genuine Redis-backed cache for its
busiest read (`GET /api/quests`), specifically so this module's Compose
capstone has a real, non-trivial second service to wire up — Redis was
promised, conceptually, back in Module 06's databases lesson, and
becomes real, running code here.

## What you'll be able to do after this module

- Explain the actual problem containers solve ("works on my machine"),
  and the genuine, structural difference between a container and a
  virtual machine — namespaces and cgroups, not "a smaller VM."
- Write a `Dockerfile` from scratch, understand image layers and why
  instruction order determines what Docker's build cache can and can't
  reuse, and write a genuine multi-stage build that ships a meaningfully
  smaller final image.
- Explain exactly how two separate containers find and talk to each
  other over a network — and why a container's own `localhost` never
  means what it used to mean once an application is containerized.
- Explain the difference between a container's disposable writable layer
  and a named volume, and know which one QuestLog's own Postgres data
  depends on to survive a rebuild.
- Write a `docker-compose.yml` from scratch for a multi-service
  application (app + database + cache), including healthcheck-based
  startup ordering.
- Explain what a cache is, why you'd reach for Redis specifically instead
  of an in-process data structure, and what a TTL and cache invalidation
  are — then point to the exact lines of real code in QuestLog's backend
  that put every one of those ideas to work.
- Containerize QuestLog's own full stack — backend, frontend, Postgres,
  Redis — and run the entire thing, from a cold start, with one command.

## Prerequisites

- **Module 09 in full** — this module's capstone containerizes the exact
  application that module deployed by hand; its own `deploy/` folder
  (systemd unit, Nginx config, runbook) is kept, unused, specifically so
  this module can compare against it directly (see
  `project/questlog/deploy/SUPERSEDED.md`).
- **Module 07's dependency-injection lesson** — this module's own
  `RedisClient` FastAPI dependency is a direct, deliberate parallel to
  that module's `DbSession`.
- **Module 08's testing-with-a-database decision** — this module's own
  "test with a fake Redis, never a real one" choice mirrors it exactly.
- A Windows machine with WSL2 already set up (Module 00/09) — this
  module's own `lessons/00-setup.md` re-verifies it, per this course's
  standing Rule 8, rather than assuming it's still fine.

## Module structure

```
module-10-docker-and-containers/
├── README.md                                                          ← you are here
├── lessons/
│   ├── 00-setup.md                                                     ← Docker Desktop + WSL2 backend, re-verified
│   ├── 01-containers-vs-vms-and-your-first-container.md                 ← the problem, the mechanism, your first real container
│   ├── 02-dockerfiles-layers-and-caching.md                              ← Dockerfile syntax, layers, build caching
│   ├── 03-multi-stage-builds-and-image-size.md                            ← multi-stage builds, -slim vs -alpine
│   ├── 04-docker-networking.md                                              ← EXPOSE vs -p, name-based DNS on user-defined networks
│   ├── 05-docker-volumes-and-persistence.md                                  ← named volumes, bind mounts, real data-loss demos
│   ├── 06-docker-compose-multi-service-apps.md                                ← Compose syntax + what a cache/TTL/invalidation actually are
│   ├── 07-containerizing-questlogs-backend.md                                  ← backend/Dockerfile + the real Redis cache wiring
│   └── 08-containerizing-questlogs-frontend-and-full-compose.md                 ← frontend/Dockerfile + assembling the full stack
├── exercises/
│   ├── 01-first-container/                                              ← easy — run/inspect/clean up a container
│   ├── 02-writing-a-dockerfile/                                          ← guided — write a cache-friendly Dockerfile
│   ├── 03-multi-stage-image-size/                                        ← guided/independent — convert single-stage to multi-stage
│   ├── 04-docker-networking/                                             ← independent — two containers, one user-defined network
│   ├── 05-volumes-and-persistence/                                       ← independent — prove persistence and its absence
│   └── 06-compose-two-services/                                          ← independent — write docker-compose.yml from scratch
├── project/
│   ├── BRIEF.md                                                          ← capstone: containerize QuestLog's full stack with Compose
│   └── questlog/                                                         ← QuestLog, copied forward from Module 09, now containerized
│       ├── frontend/                                                        ← Dockerfile + nginx.conf added; one small package.json fix
│       ├── backend/                                                         ← Dockerfile added; real Redis cache wired into app/
│       ├── docker-compose.yml                                                ← the whole stack, one file
│       └── deploy/                                                            ← Module 09's manual artifacts, kept as a labeled, superseded reference
└── CHECKLIST.md
```

Read the lessons in order. Lessons 01-03 cover images and the build
process itself; Lessons 04-05 cover networking and storage; Lesson 06
covers Compose syntax and the caching concepts this module's Redis work
depends on; Lessons 07-08 are the capstone walkthrough, applying
everything to QuestLog specifically.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without
looking at its solution, ask for a review, revise if needed, then move
on. Once all six exercises are done, work through `project/BRIEF.md`.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's `project/questlog/`
is Module 09's finished, deployed-by-hand QuestLog, copied forward, with
`backend/app/` changed in exactly one small, real, documented way (a
Redis cache for `GET /api/quests`, wired into `app/cache.py`,
`app/config.py`, `app/dependencies.py`, and `app/routers/quests.py` —
`app/repository.py` untouched) and `frontend/` changed in exactly one
small, real, documented way (`package.json`'s two Windows-only native
binding packages moved to `optionalDependencies`, so the frontend's own
Docker build succeeds on Linux). See
`project/questlog/README.md` for the complete, itemized account of both
changes.
