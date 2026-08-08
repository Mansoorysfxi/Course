"""See lessons/06-building-signup-login.md for `auth.router` (new), and
lessons/10-cors-in-depth.md for this file's CORS configuration -- the full
explanation Module 05 and Module 06 both deferred to "Module 07's job" is
finally delivered there; this file's own CORS lines below now read from
`settings.cors_origins` (app/config.py) instead of a hardcoded list, and
that lesson explains exactly why that's the right change to make together
with adding real authentication.

**NEW in Module 11:** optional Sentry initialization (see
lessons/06-monitoring-logging-and-error-tracking.md) and a real `/health`
endpoint (see lessons/08-deploying-questlog-with-ci-cd.md) that Render's
own deploy process polls before routing any real traffic to a new
container -- see that lesson for exactly why a health check needs to
prove the app can *do its job* (reach the database), not merely that the
process is alive.
"""

from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import repository
from app.config import settings
from app.database import AsyncSessionLocal
from app.dependencies import DbSession, RedisClient
from app.routers import auth, quests

# Sentry is only turned on if a real DSN is configured -- see
# app/config.py's `sentry_dsn` field docstring for why `None` (never an
# empty string) is this setting's "off" value. Every lesson/exercise in
# this course that never sets SENTRY_DSN runs with Sentry completely
# inert: `sentry_sdk.init` is simply never called, and every
# `sentry_sdk.capture_exception`-style call Sentry's own FastAPI
# integration makes internally becomes a silent no-op. This check has to
# run at import time, before `FastAPI()` is constructed below, because
# Sentry's FastAPI/Starlette integration instruments the app by patching
# things Starlette does as it builds request-handling machinery -- turning
# Sentry on *after* the app object already exists would miss requests.
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        # A conservative default: capture full details on 100% of errors
        # (the whole reason Sentry exists), but only *trace* (time, in
        # detail) 10% of requests for performance monitoring -- see
        # lessons/06's "traces_sample_rate" box for why tracing every
        # single request is rarely worth its own overhead once a real app
        # has meaningful traffic, even though it's harmless for a hobby
        # project's actual volume.
        traces_sample_rate=0.1,
        # Never sends request bodies, cookies, or headers to Sentry by
        # default -- QuestLog's requests can carry a real JWT in an
        # Authorization header, and a password in a signup/login request
        # body; there is no reason Sentry, a third-party service, would
        # ever need to see either. See lessons/06's "send_default_pii"
        # box.
        send_default_pii=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once, before the app starts accepting requests. Opens its own
    # short-lived session (not one borrowed from a request, since there is
    # no request yet) purely to seed starting data -- creating the actual
    # *tables* is Alembic's job (Module 06, lessons/07), done once, ahead
    # of time, via `alembic upgrade head`, never by the running app itself.
    async with AsyncSessionLocal() as session:
        await repository.seed_if_empty(session)
    yield
    # (nothing needed on shutdown for this app; the engine's connection
    # pool closes automatically when the process exits)


app = FastAPI(
    title="QuestLog API",
    version="0.3.0",
    description=(
        "A PostgreSQL-backed, per-user CRUD API for QuestLog's quests, "
        "built in Module 07. Every quest now belongs to a real, "
        "authenticated account -- see project/BRIEF.md for exactly what "
        "changed since Module 06 and why."
    ),
    lifespan=lifespan,
)

# Unblocks the frontend (running on Vite's default dev port) from calling
# this API. `settings.cors_origins` (app/config.py) is read from the
# `CORS_ORIGINS` environment variable / `.env` entry, defaulting to just
# `http://localhost:5173` -- see lessons/10-cors-in-depth.md for a full,
# line-by-line explanation of every argument below (`allow_origins`,
# `allow_methods`, `allow_headers`), what a CORS "preflight" `OPTIONS`
# request is, and specifically why `allow_credentials` is deliberately
# left at its default (`False`) in this app -- this backend's auth token
# travels in a plain `Authorization` header the frontend sets itself
# (see frontend/src/api/http.ts), never in a cookie, so the browser never
# needs to be told to *send credentials* (cookies) cross-origin at all;
# turning `allow_credentials` on for a token scheme that doesn't use
# cookies would add a real security consideration for zero benefit.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(quests.router)


@app.get("/")
def root():
    return {"message": "QuestLog API. See /docs for interactive documentation."}


@app.get("/health")
async def health(session: DbSession, redis: RedisClient):
    """A **liveness-and-readiness** check -- see
    lessons/08-deploying-questlog-with-ci-cd.md for the full explanation
    of why this is a real, load-bearing endpoint in Module 11 (Render
    itself polls exactly this path, via `healthCheckPath` in
    `render.yaml`, before sending real traffic to a freshly deployed
    container, and again periodically afterward, to decide whether to
    restart a container that's stopped responding correctly).

    Deliberately takes `session: DbSession` and `redis: RedisClient` --
    the exact same FastAPI dependencies every other route in this app
    already uses (app/dependencies.py) -- rather than reaching for
    `app.database.engine` directly. Two real reasons, not just
    consistency for its own sake: (1) this endpoint's own test
    (tests/test_health.py) can then reuse the exact same
    `app.dependency_overrides` mechanism every other test in this suite
    already relies on, pointing this check at the test's in-memory
    SQLite database and `FakeRedis` instead of a real Postgres/Redis that
    doesn't exist in a test run; (2) it keeps this file honest about what
    "the database" even means in this app -- there is deliberately no
    second, separate way to reach it.

    A **database** failure fails this whole check (`SELECT 1` is the
    smallest possible real proof "this connection can talk to Postgres
    right now" -- Module 06's own lesson on what a connection actually
    is) because QuestLog cannot serve a single real request without one.
    A **Redis** failure is reported but does *not* fail the check: this
    app's own cache (app/cache.py) is a deliberately optional
    optimization, not a hard dependency -- see that file's own docstring
    for the "read constantly, write rarely" reasoning -- so marking the
    whole app "unhealthy" (and having Render restart a perfectly good
    container, or refuse to route it any traffic) over a temporarily
    unreachable *cache* would make an already-degraded moment worse, not
    better. This distinction -- which dependencies are load-bearing versus
    which are optional accelerators -- is itself a real, common health-
    check design decision, not a QuestLog-specific quirk.
    """
    try:
        await session.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception:
        # A health check's own error handling is one of the few places in
        # this entire codebase where catching `Exception` this broadly is
        # correct rather than lazy: this endpoint's entire job is to turn
        # ANY failure reaching the database into a calm, structured "not
        # healthy" response -- never to raise a 500 itself, which would
        # give whoever/whatever is polling this endpoint (Render, or a
        # human running curl) a confusing error instead of the clear
        # signal it exists to provide.
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
