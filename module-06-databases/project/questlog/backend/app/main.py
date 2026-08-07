"""See lessons/06-sqlalchemy-with-fastapi.md for the full, line-by-line
explanation of this file, and specifically for why startup seeding is now
a `lifespan` context manager instead of Module 05's `@app.on_event(...)`
(deprecated in favor of `lifespan` -- confirmed against FastAPI's own
current docs while writing this module, see that lesson's header).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import AsyncSessionLocal
from app.routers import quests
from app import repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once, before the app starts accepting requests. Opens its own
    # short-lived session (not one borrowed from a request, since there is
    # no request yet) purely to seed starting data -- creating the actual
    # *tables* is Alembic's job (lessons/07), done once, ahead of time, via
    # `alembic upgrade head`, never by the running app itself.
    async with AsyncSessionLocal() as session:
        await repository.seed_if_empty(session)
    yield
    # (nothing needed on shutdown for this app; the engine's connection
    # pool closes automatically when the process exits)


app = FastAPI(
    title="QuestLog API",
    version="0.2.0",
    description=(
        "A PostgreSQL-backed CRUD API for QuestLog's quests, built in "
        "Module 06. Same routes and JSON shapes as Module 05's in-memory "
        "version -- see project/BRIEF.md for exactly what changed and why."
    ),
    lifespan=lifespan,
)

# Unblocks Module 04's frontend (running on Vite's default dev port) from
# calling this API -- unchanged from Module 05. Full explanation of CORS
# itself is Module 07's job.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quests.router)


@app.get("/")
def root():
    return {"message": "QuestLog API. See /docs for interactive documentation."}
