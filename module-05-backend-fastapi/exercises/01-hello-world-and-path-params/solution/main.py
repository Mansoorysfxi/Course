from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "QuestLog API is alive."}


@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}


@app.get("/power/{base}/{exponent}")
def power(base: int, exponent: int):
    return {"base": base, "exponent": exponent, "result": base ** exponent}
