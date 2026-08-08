# Lesson 06 — Monitoring, Logging, and Error Tracking

**Verified against (August 2026), via live web search and direct fetch of
official documentation:** Sentry's Developer (free) plan — 5,000
errors/month, 1 user, 30-day retention, free forever, no card required
(cross-checked against multiple current sources). `sentry-sdk[fastapi]`
`2.62.0` (PyPI) and `@sentry/react` `^10.69.0` (npm) both confirmed
current. Sentry's FastAPI integration auto-activates when `fastapi` is
importable in the same environment (no separate FastAPI-specific install
step beyond `sentry-sdk` itself, per Sentry's own current Python SDK
docs). Sentry's React/Vite integration recommends calling `Sentry.init()`
as early as possible, before any other application code runs.

## What you'll learn

- The real difference between **logs**, **metrics**, **uptime
  monitoring**, and **error tracking** — four related but genuinely
  distinct concepts people often blur together.
- What a **health check** actually needs to prove, and the real design
  decision behind QuestLog's own `/health` endpoint (which dependency
  failures should fail the check, and which shouldn't).
- How to read `backend/app/main.py`'s real, working Sentry setup and
  `frontend/src/monitoring.ts`'s real, working Sentry setup, line by
  line — both genuinely optional, both off by default.
- Where to actually look at logs for a real Render deployment.

## Why this matters

A CI/CD pipeline (Lessons 01-03) gets code deployed automatically.
Nothing so far in this module tells you *anything* about whether that
deployed code is actually working, for real users, right now. This
lesson is about closing that second gap — the difference between
"deployed" and "known to be working."

## Prerequisites

- **Module 08's testing material** — monitoring answers a genuinely
  different question than testing does; this lesson explicitly draws
  that distinction (see "How this connects").
- **Lesson 04** — Render's own dashboard, referenced here for where logs
  actually live.

## The concept, explained simply

Picture a live game server, already shipped to players, running right
now. Four different tools tell you four different things about it, and
none of them substitute for the others:

- **Logs** are the server's own detailed diary — a timestamped record of
  specific events ("player 4821 joined lobby 12," "inventory sync failed
  for player 91"). You read logs *after* something specific happened, to
  understand exactly what occurred and in what order.
- **Metrics** are aggregated numbers over time — "average players per
  server, per hour," "average frame time" — telling you the overall
  health *trend* without needing to read a single individual log line.
- **Uptime monitoring** is a completely external service periodically
  asking "is this server even reachable at all, right now?" — the
  simplest possible check, run from OUTSIDE your own infrastructure
  specifically so it catches "the whole server is down" even in the
  worst case where your own server can't even report its own logs
  anymore.
- **Error tracking** is a specialized tool that catches, deduplicates,
  and alerts on unhandled exceptions/crashes specifically — not every
  log line, just the ones that represent a genuine bug — with enough
  context (a full stack trace, which user, which request) to actually
  fix the underlying problem, not just know it happened.

A **health check** is a distinct, fifth idea: a single, specific endpoint
(`/health`, this lesson's own concrete example) a piece of *automation*
(not a human) polls to make an automatic decision — "should I route real
traffic to this specific instance, right now, or not."

## The details

### QuestLog's own `/health` endpoint, read in full

Open `project/questlog/backend/app/main.py` and find `health()`:

```python
@app.get("/health")
async def health(session: DbSession, redis: RedisClient):
    try:
        await session.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception:
        database_status = "unreachable"

    try:
        await redis.ping()
        cache_status = "ok"
    except Exception:
        cache_status = "unreachable"

    healthy = database_status == "ok"
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "ok" if healthy else "unhealthy",
            "database": database_status,
            "cache": cache_status,
        },
    )
```

The real design decision here, worth naming explicitly: **a database
failure fails this whole check; a Redis failure does not.** This isn't
an oversight — it's a deliberate judgment call about which of QuestLog's
own dependencies are load-bearing (nothing works at all without
Postgres) versus optional accelerators (Module 10's own cache is
explicitly a "read constantly, write rarely" optimization, not something
any route hard-requires to function *correctly*, even though — an honest
limitation, also worth naming — the current `app/routers/quests.py` code
would actually raise an unhandled exception if Redis were unreachable
mid-request, rather than gracefully falling back to Postgres; fixing that
gap is a good, real "Try it yourself" extension, not something this
course's own Module 11 scope requires). Real production health checks
make exactly this kind of judgment call constantly — the goal is never
"fail on any imperfection," it's "fail specifically when this instance
genuinely can't do its job."

Note this endpoint deliberately requires **no authentication** — the
automation polling it (Render, in this module's case) has no QuestLog
account or JWT, and shouldn't need one; a health check that required
login would defeat its own purpose.

**Try it yourself:** with the full Compose stack running
(`docker compose up -d` in `project/questlog/`), run:
```bash
docker compose stop postgres
curl -i http://localhost:8000/health
```
**Predict, before running the curl command,** the exact status code and
JSON body you'll see, then confirm it, then bring Postgres back:
```bash
docker compose start postgres
curl -i http://localhost:8000/health
```

### Sentry — what it is, and QuestLog's real, optional setup

**Sentry** is a hosted error-tracking service: your app sends it a
structured report the moment an unhandled exception happens (or, on the
frontend, an uncaught JavaScript error), including a full stack trace,
which specific request/user/browser was involved, and how many times an
identical-looking error has happened before — turning "a user emailed
support saying something was broken, three days ago, with no detail at
all" into "here's the exact line that threw, the exact input that
triggered it, and forty-one other times it's happened this week."

**Backend — `backend/app/main.py`:**
```python
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
```
- `if settings.sentry_dsn:` — the entire "off unless you configure it"
  mechanism. `settings.sentry_dsn` (`app/config.py`) defaults to `None`;
  Sentry is never initialized at all unless a real DSN is present in the
  environment.
- `dsn=` — the actual, real, secret-ish address Sentry gave you when you
  created a project (Lesson 00-setup.md's Step 3) — this is what tells
  the SDK *which* Sentry project receives these events. Treat it the way
  you'd treat any other credential: an environment variable, never
  committed to Git (this project's own `.gitignore` already excludes
  `.env`).
- `environment=` — a label ("production," "development") attached to
  every event, so Sentry's own dashboard can separate "this happened to
  a real user" from "this happened while running the test suite
  locally."
- `traces_sample_rate=0.1` — Sentry can also do **performance tracing**
  (timing real requests in detail), which costs more of your free-tier
  quota than error tracking alone; `0.1` means only 10% of requests get
  full tracing — a reasonable default for a hobby project's real traffic
  volume.
- `send_default_pii=False` — never sends request headers, cookies, or
  bodies to Sentry by default. QuestLog's own requests can carry a real
  JWT in an `Authorization` header and a real password in a signup
  request body; there's no reason a third-party service would ever need
  to see either.

**Because `fastapi` is already installed** (QuestLog's own
`requirements.txt`), Sentry's FastAPI integration activates
**automatically** the moment `sentry_sdk.init(...)` runs — no separate
`FastApiIntegration()` object to construct or pass in yourself, per
Sentry's own current documentation. From that point on, any unhandled
exception any QuestLog route raises is automatically captured and sent,
with zero further code needed anywhere else in the app.

**Frontend — `frontend/src/monitoring.ts`:**
```typescript
import * as Sentry from "@sentry/react";

const dsn = import.meta.env.VITE_SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    environment: import.meta.env.VITE_ENVIRONMENT ?? "development",
    tracesSampleRate: 0.1,
  });
}
```
Same shape, same "off unless configured" guard, same conservative
tracing rate — deliberately mirroring the backend's own decision, so
learning one half of this teaches the other. `frontend/src/main.tsx`
imports this file **first**, before anything else:
```typescript
import "./monitoring.ts"; // NEW in Module 11
import "./index.css";
import App from "./App.tsx";
```
Importing a file purely for its side effect (there's nothing to actually
use from it — no `export` this project imports elsewhere) is a
deliberate, real, if slightly unusual JavaScript pattern: the import
itself is what runs `Sentry.init(...)`, and importing it before anything
else means Sentry is already watching by the time any other application
code — including code that could itself throw during startup — actually
runs.

### Turning Sentry on for real (only if you completed Lesson 00's Step 3)

```bash
# backend/.env
SENTRY_DSN=https://your-real-key@o0.ingest.sentry.io/0
ENVIRONMENT=development
```
```bash
# frontend/.env
VITE_SENTRY_DSN=https://your-real-key@o0.ingest.sentry.io/0
VITE_ENVIRONMENT=development
```
Restart the backend/frontend after editing either `.env` (both only read
their environment at startup/build time, never live). To confirm it's
genuinely working, deliberately trigger a real error — e.g., temporarily
add a route that does `1 / 0` — hit it once, then check your Sentry
project's own dashboard. **Expected:** the error appears within seconds,
with a full Python traceback, the exact request path, and QuestLog's own
`environment` label attached. Remove the temporary route afterward.

### Where Render's own logs actually live

Every Render service's dashboard has a **Logs** tab — a live, streaming
view of exactly what that container printed to stdout/stderr, plus
Render's own deploy/restart events interleaved. This is the direct
equivalent of `docker compose logs` (Module 10), just for a real,
deployed container instead of one running on your own machine. Render
also polls `render.yaml`'s own `healthCheckPath` (this lesson's `/health`
endpoint) both right after a new deploy (before routing any real traffic
to it) and periodically afterward, restarting a container that starts
failing its own health check — this is uptime monitoring and automated
recovery, built directly into the platform, requiring zero extra
configuration beyond `healthCheckPath` already existing.

## Common mistakes & gotchas

- **A health check that's "too strict."** A health check that fails on
  ANY imperfection (including genuinely non-critical ones) causes a
  platform to restart or stop routing to an instance that's actually
  fine for real users — QuestLog's own choice to not fail on a Redis
  outage is a direct, deliberate defense against exactly this.
- **Sentry silently not receiving anything**, most commonly because
  `SENTRY_DSN`/`VITE_SENTRY_DSN` is set in the wrong `.env` file (recall
  this module's own multiple-`.env` gotcha from Lesson 00-setup.md), or
  because the frontend's Docker build didn't actually receive
  `VITE_SENTRY_DSN` as a build argument (it's a build-time value, baked
  into the compiled JavaScript — setting it as a normal runtime
  environment variable on an already-built container does nothing at
  all; see `frontend/Dockerfile`'s own `ARG`/`ENV` pair).
- **Treating error tracking as a replacement for tests.** Sentry tells
  you a bug happened in production, after a real user already hit it —
  strictly worse than Module 08's own automated tests catching the same
  bug before it ever shipped. The two are complementary, not
  substitutes: tests catch what you thought to test for; error tracking
  catches everything else, after the fact.
- **Logging sensitive data by accident.** A `print()`/log statement that
  includes a password, a full JWT, or a credit card number is a real,
  common security mistake — QuestLog's own `send_default_pii=False`
  choice (backend) is one layer of defense against a *third-party
  service* seeing such data; it's not a substitute for never logging it
  in the first place.

## How this connects

Testing (Module 08) answers "does this code do what I expect, under
conditions I thought to check, before it ships." Monitoring (this
lesson) answers "is this code actually doing what I expect, right now,
in the real world, under conditions I may never have thought to test."
Both matter; neither replaces the other. Lesson 07 shifts to a different
question again — not "is this one instance healthy," but "how do you run
and manage MANY instances of something at once," which is exactly
Kubernetes's whole reason for existing.

## Quick self-check

1. Give one concrete example of something logs would show you that
   metrics wouldn't, and vice versa.
2. Why does QuestLog's own `/health` endpoint fail on a database problem
   but not a Redis problem — what's the actual reasoning behind that
   specific asymmetry?
3. Why does `frontend/src/main.tsx` import `./monitoring.ts` before
   anything else, including `./index.css`?
4. Why would setting `VITE_SENTRY_DSN` as a runtime environment variable
   on an already-built, already-running frontend container do absolutely
   nothing?
5. Name one real reason error tracking and automated testing are
   complementary rather than one making the other unnecessary.
