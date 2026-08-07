# Exercise 01 — Hello World and Path Params

**Lessons:** [`lessons/00-setup.md`](../../lessons/00-setup.md) (venv, install, running with Uvicorn), [`lessons/01-what-a-backend-does-and-your-first-routes.md`](../../lessons/01-what-a-backend-does-and-your-first-routes.md) (routes, decorators), [`lessons/02-path-and-query-parameters.md`](../../lessons/02-path-and-query-parameters.md) (path parameters and type conversion).

**Difficulty:** Very easy. If you've read Lessons 00–02, every piece of this exercise is something you've already typed out and run yourself. This exercise should be almost impossible to fail.

## The task

`starter/` contains an empty venv-ready project (a `requirements.txt`, no `main.py` yet). Create `main.py` with exactly these three routes:

1. `GET /` — returns `{"message": "QuestLog API is alive."}`.
2. `GET /greet/{name}` — takes a path parameter `name` (a string) and returns `{"message": f"Hello, {name}!"}`.
3. `GET /power/{base}/{exponent}` — takes two path parameters, `base` and `exponent`, **both integers**, and returns `{"base": base, "exponent": exponent, "result": base ** exponent}`.

## Concepts this exercise uses (all already taught)

| Concept | Taught in |
|---|---|
| Creating a venv, installing FastAPI + Uvicorn | [Lesson 00](../../lessons/00-setup.md) |
| Running a server with `uvicorn main:app --reload` | [Lesson 00](../../lessons/00-setup.md) |
| `@app.get(...)` and what it does mechanically | [Lesson 01](../../lessons/01-what-a-backend-does-and-your-first-routes.md) |
| A route function returning a plain `dict` | [Lesson 01](../../lessons/01-what-a-backend-does-and-your-first-routes.md) |
| Path parameters, and type-hint-driven conversion (`str` vs `int`) | [Lesson 02](../../lessons/02-path-and-query-parameters.md) |

## Acceptance criteria

- [ ] `uvicorn main:app --reload` starts with no errors.
- [ ] `curl http://127.0.0.1:8000/` returns exactly `{"message":"QuestLog API is alive."}`.
- [ ] `curl http://127.0.0.1:8000/greet/Aria` returns exactly `{"message":"Hello, Aria!"}`.
- [ ] `curl http://127.0.0.1:8000/power/2/10` returns `{"base":2,"exponent":10,"result":1024}` — with `base`, `exponent`, and `result` as real JSON numbers, not strings (confirming they were actually converted to `int`, not left as text).
- [ ] `curl -i http://127.0.0.1:8000/power/2/not-a-number` returns `422 Unprocessable Content` (you don't need to write any code to make this happen — if your path parameters are correctly type-hinted `int`, FastAPI does this for you automatically, per Lesson 02).
- [ ] Visiting `http://127.0.0.1:8000/docs` shows all three routes, and "Try it out" works for each.

## What to submit

Point your AI session at your completed `starter/main.py` and say *"Review my solution for exercise 01."*

## Hints

**Level 1:** Lesson 00's Step 3 already showed you the exact shape of a minimal `main.py` — start from that, then add the two new routes.

**Level 2:** `/power/{base}/{exponent}` needs **two** path parameters in the same route — the decorator string just needs both names in curly braces, and the function needs both as parameters, matched by name (Lesson 02).

**Level 3 (near-answer):** Your function signature for the third route should look like `def power(base: int, exponent: int):` — the type hints are what make FastAPI convert the URL's text into real integers before your function runs at all.
