"""See lessons/08-building-the-questlog-api.md for the full, line-by-line
explanation of this file."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import quests
from app import store

app = FastAPI(
    title="QuestLog API",
    version="0.1.0",
    description=(
        "An in-memory CRUD API for QuestLog's quests, built in Module 05. "
        "No database yet -- see Module 06."
    ),
)

# Unblocks Module 04's frontend (running on Vite's default dev port) from
# calling this API at all -- see lessons/00-setup.md Step 6 and
# lessons/05-middleware.md's CORS note. Full explanation of CORS itself is
# Module 07's job.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quests.router)


@app.on_event("startup")
def startup() -> None:
    store.seed()


@app.get("/")
def root():
    return {"message": "QuestLog API. See /docs for interactive documentation."}
