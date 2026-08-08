"""A tiny, deliberately trivial FastAPI app -- the whole point of this
exercise is the CI *pipeline* around it, not the app itself. See
lessons/03-a-real-ci-pipeline-for-questlog.md for the real, full-size
version of everything you're about to build here, in miniature.

NEW in Exercise 04: a real /health endpoint, and GREETING is read via a
function (`get_greeting()`), not a bare module-level constant -- reading
it once, at import time, into a fixed variable would mean a test that
sets/unsets the GREETING environment variable AFTER this module was
already imported could never actually change what /health sees, since
app/main.py would already have "baked in" whatever value existed the
first time this file was ever imported (usually the very first test
collected). Reading it fresh, inside the route function itself, exactly
mirrors why QuestLog's own real app/config.py wraps its Settings() call
in a get_settings() function rather than trusting a bare import-time
value never needs to change during a test run.
"""

import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


def get_greeting() -> str | None:
    return os.environ.get("GREETING")


@app.get("/")
def read_root():
    return {"message": "Hello from the CI/CD toy app!"}


@app.get("/add/{a}/{b}")
def add(a: int, b: int):
    return {"result": a + b}


@app.get("/health")
def health():
    greeting_configured = bool(get_greeting())
    return JSONResponse(
        status_code=200 if greeting_configured else 503,
        content={
            "status": "ok" if greeting_configured else "unhealthy",
            "greeting_configured": greeting_configured,
        },
    )
