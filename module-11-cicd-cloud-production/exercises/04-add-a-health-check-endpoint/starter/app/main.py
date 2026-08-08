"""A tiny, deliberately trivial FastAPI app -- the whole point of this
exercise is the CI *pipeline* around it, not the app itself. See
lessons/03-a-real-ci-pipeline-for-questlog.md for the real, full-size
version of everything you're about to build here, in miniature.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from the CI/CD toy app!"}


@app.get("/add/{a}/{b}")
def add(a: int, b: int):
    return {"result": a + b}
