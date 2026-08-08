# QuestLog — Module 11 (CI/CD pipeline, health checks, optional Sentry monitoring)

Per `RUNNING_PROJECT.md`, this folder is Module 10's finished, fully
containerized `questlog/` copied forward. `backend/app/` and
`frontend/src/` are unchanged from Module 10 **except for two small,
deliberate, documented changes**:

1. A real `/health` endpoint (`backend/app/main.py`) — see "The new
   `/health` endpoint" below.
2. Optional Sentry error tracking, on both backend and frontend, off by
   default — see "Optional Sentry monitoring" below.

Everything else new this module lives **alongside** the application, the
same pattern Module 09's `deploy/` folder and Module 10's
`docker-compose.yml`/Dockerfiles already established: a
`.github/workflows/ci-cd.yml` pipeline, and a `render.yaml` Blueprint
describing this app's production topology on Render (this module's
chosen deploy platform — see
[`lessons/04-cloud-fundamentals-and-your-chosen-platform.md`](../../lessons/04-cloud-fundamentals-and-your-chosen-platform.md)
for why).

```
project/questlog/
├── .github/workflows/ci-cd.yml   — NEW: test -> build -> push -> deploy pipeline
├── render.yaml                    — NEW: Render Blueprint (backend, frontend, Postgres, Redis)
├── docker-compose.yml             — unchanged from Module 10, plus two optional Sentry env vars
├── .env.example                    — unchanged, plus two optional Sentry lines
├── backend/
│   ├── app/main.py                   — NEW: /health endpoint + optional Sentry init
│   ├── app/config.py                  — NEW: sentry_dsn, environment settings fields
│   ├── tests/test_health.py             — NEW: 2 tests for /health
│   ├── tests/conftest.py                 — FakeRedis gained a `ping()` method
│   ├── requirements.txt                    — NEW: sentry-sdk[fastapi]
│   ├── Dockerfile                            — unchanged from Module 10
│   └── ...                                      — everything else unchanged from Module 10
├── frontend/
│   ├── src/monitoring.ts               — NEW: optional Sentry init (Sentry.init, guarded)
│   ├── src/main.tsx                      — NEW: one added import (./monitoring.ts)
│   ├── src/vite-env.d.ts                   — NEW: two added env var type declarations
│   ├── package.json                          — NEW: @sentry/react dependency
│   ├── Dockerfile                              — NEW: two added ARG/ENV pairs for Sentry build args
│   └── ...                                        — everything else, including nginx.conf, unchanged
└── deploy/                        — Module 09's manual artifacts + Module 10's SUPERSEDED.md,
                                       KEPT, plus a new SUPERSEDED_BY_MODULE_11.md
```

See
[`lessons/08-deploying-questlog-with-ci-cd.md`](../../lessons/08-deploying-questlog-with-ci-cd.md)
for the full, line-by-line capstone walkthrough, and
[`../BRIEF.md`](../BRIEF.md) for this module's capstone deliverables.

## The new `/health` endpoint

`GET /health` — no authentication required — checks that the backend can
actually reach Postgres (`SELECT 1`, via the exact same `DbSession`
dependency every other route uses) and reports Redis reachability too,
but only *fails* (`503`, `{"status": "unhealthy", ...}`) on a database
problem — a Redis outage is reported (`"cache": "unreachable"`) but still
returns `200`, because QuestLog's cache is an optional accelerator, not a
hard dependency. See `backend/app/main.py`'s own `health()` docstring for
the full reasoning, and
[`lessons/08-deploying-questlog-with-ci-cd.md`](../../lessons/08-deploying-questlog-with-ci-cd.md)
for why Render's own `render.yaml` (`healthCheckPath: /health`) depends
on exactly this endpoint before it will route real traffic to a freshly
deployed container.

```bash
curl -i http://localhost:8000/health
```
**Expected** (with the full Compose stack running):
```
HTTP/1.1 200 OK
...
{"status":"ok","database":"ok","cache":"ok"}
```

## Optional Sentry monitoring

Both `backend/app/config.py`'s `sentry_dsn` and
`frontend/src/vite-env.d.ts`'s `VITE_SENTRY_DSN` default to "off" (`None`
/ unset). Every lesson, every exercise, the entire test suite, and a
plain `docker compose up --build` with no extra configuration all run
with Sentry completely inert — nothing in this module *requires* a
Sentry account to work. See
[`lessons/06-monitoring-logging-and-error-tracking.md`](../../lessons/06-monitoring-logging-and-error-tracking.md)
for what Sentry actually is, current (August 2026) free-tier limits, and
exactly how to turn it on for real if you want to.

## Running the whole stack with Docker Compose (unchanged from Module 10)

```bash
cd module-11-cicd-cloud-production/project/questlog
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
docker compose up --build
```

Same expected behavior as Module 10 — see that module's own
`lessons/08-containerizing-questlogs-frontend-and-full-compose.md` for
the full walkthrough. One small addition: `backend`'s own
`docker-compose.yml` service block now includes a `healthcheck:` that
polls this module's new `/health` endpoint directly (previously,
Compose's `depends_on: condition: service_healthy` only existed for
`postgres`/`redis`; the backend itself had no healthcheck of its own at
all).

## Running the test suites (both still pass)

```bash
cd backend && python -m pytest -v          # expect: 39 passed (37 from Module 10 + 2 new /health tests)
cd ../frontend && npm run test              # expect: Tests  17 passed (17), unchanged from Module 10
```

## The CI/CD pipeline and deploying this for real

See
[`lessons/02-github-actions-from-zero.md`](../../lessons/02-github-actions-from-zero.md)
through
[`lessons/08-deploying-questlog-with-ci-cd.md`](../../lessons/08-deploying-questlog-with-ci-cd.md),
and `../BRIEF.md` for the full capstone. Short version: `.github/workflows/ci-cd.yml`
runs both test suites on every push/PR, then (only for a real push to
`main`) builds and pushes both Docker images to GitHub Container
Registry, then triggers a Render deploy via `render.yaml`'s two
image-backed web services. Both the workflow file and `render.yaml` are
written as if `project/questlog/` **is the root of your own, separate
GitHub repository** — see the workflow file's own header comment and
`lessons/00-setup.md`'s "which repo does this even run in" box for
exactly what that means and how to actually run this for real.

Module 09 deployed this app to a real VPS by hand; Module 10 packaged it
into containers; this module automates getting those exact containers
onto a real, internet-reachable, HTTPS-secured server, on every push —
see `deploy/SUPERSEDED_BY_MODULE_11.md` for the complete, itemized
comparison.
