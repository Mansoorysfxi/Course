"""See lessons/06-building-signup-login.md for `auth.router` (new), and
lessons/10-cors-in-depth.md for this file's CORS configuration -- the full
explanation Module 05 and Module 06 both deferred to "Module 07's job" is
finally delivered there; this file's own CORS lines below now read from
`settings.cors_origins` (app/config.py) instead of a hardcoded list, and
that lesson explains exactly why that's the right change to make together
with adding real authentication.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import AsyncSessionLocal
from app.routers import auth, quests
from app import repository


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
