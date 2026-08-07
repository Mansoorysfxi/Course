from fastapi import FastAPI

from app.routers import quests
from app import store

app = FastAPI(title="Quest API (Exercise 05)")

app.include_router(quests.router)


@app.on_event("startup")
def startup() -> None:
    store.seed()


@app.get("/")
def root():
    return {"message": "Quest API (Exercise 05). See /docs."}
