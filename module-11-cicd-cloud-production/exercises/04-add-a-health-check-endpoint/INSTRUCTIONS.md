# Exercise 04 — Add a Real Health Check Endpoint (Independent)

**Concepts this exercise uses (all taught in
[`lessons/06-monitoring-logging-and-error-tracking.md`](../../lessons/06-monitoring-logging-and-error-tracking.md)'s
"QuestLog's own `/health` endpoint, read in full" section):** what a
health check needs to prove, status codes for "healthy" vs. "unhealthy,"
and why a health check endpoint should require no authentication.

**Where to work:**
`exercises/04-add-a-health-check-endpoint/starter/` — Exercise 03's
toy app, with its Dockerfile and CI pipeline already in place.

This toy app has no database or cache at all, so its own health check
can't check either the way QuestLog's real one does — but it CAN check
something a real deployment platform would still want verified: that the
app's own configuration loaded correctly. This exercise gives the app one
tiny piece of required configuration specifically so there's something
real to check.

## Your task

1. In `app/main.py`, add a module-level constant,
   `GREETING = os.environ.get("GREETING")`, read directly from an
   environment variable named `GREETING` (no default value).
2. Add `GET /health` that:
   - Returns `200` with `{"status": "ok", "greeting_configured": true}`
     if `GREETING` is set to a non-empty value.
   - Returns `503` with `{"status": "unhealthy", "greeting_configured": false}`
     otherwise.
   - Requires no authentication (this toy app has none anyway, but name
     this explicitly in your own test, per the acceptance criteria).
3. Add at least two new tests in `tests/test_main.py` covering both the
   healthy and unhealthy cases (Module 08's own `monkeypatch`/fixture
   techniques for setting an environment variable inside a test — see
   that module's own testing lessons if this feels unfamiliar).
4. Update `Dockerfile`'s own `CMD` line (or add an `ENV`) so the built
   image has SOME value for `GREETING` by default, so `docker run` with
   no extra flags still produces a healthy container — then confirm you
   can also override it with `docker run -e GREETING=... `.

## Verify it yourself

```bash
cd exercises/04-add-a-health-check-endpoint/starter
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -v
```
**Expected:** all tests pass, including your two new ones.

```bash
docker build -t toy-ci-app .
docker run --rm -p 8000:8000 toy-ci-app
curl -i http://localhost:8000/health
```
**Expected:** `HTTP/1.1 200 OK`, `{"status":"ok","greeting_configured":true}`.

```bash
docker run --rm -p 8000:8000 -e GREETING= toy-ci-app
curl -i http://localhost:8000/health
```
**Expected:** `HTTP/1.1 503 Service Unavailable`,
`{"status":"unhealthy","greeting_configured":false}`.

## Acceptance criteria

- [ ] `GET /health` returns `200` when `GREETING` is set, `503`
      otherwise — never a `500` (unhandled exception) in either case.
- [ ] Two new tests genuinely exercise both branches (not just the happy
      path).
- [ ] `/health` requires no authentication (trivially true here, but
      confirm your test doesn't accidentally pass a header that would
      mask a real auth requirement if one existed).
- [ ] The CI workflow from Exercise 03 still passes unmodified — this
      exercise adds tests, it doesn't change how CI runs them.
- [ ] You can explain, in your own words, why a real deployment platform
      (Render, in this module's own case) needs a health check endpoint
      to return the CORRECT status code, not just any response at all —
      what decision does the platform make based on that code?

## Hints

<details>
<summary>Hint 1</summary>

`os.environ.get("GREETING")` returns `None` if the variable is entirely
unset, and an empty string `""` if it's set but empty — both should count
as "not configured" for this exercise's own health check.

</details>

<details>
<summary>Hint 2</summary>

pytest's own `monkeypatch.setenv("GREETING", "hello")` /
`monkeypatch.delenv("GREETING", raising=False)` fixture (built into
pytest, no extra install) is the standard way to set/unset an environment
variable for exactly one test, safely reverted afterward — but note
`app/main.py`'s own `GREETING` constant is read once, at IMPORT time, so
setting the environment variable inside a test won't retroactively change
an already-imported module-level constant. Look at how QuestLog's own
`app/config.py` handles this same problem (reading configuration through
a function, not a bare module-level constant) for the real, general
solution.

</details>

<details>
<summary>Hint 3</summary>

`FastAPI`'s `JSONResponse` (from `fastapi.responses`) lets you set a
non-default status code on a JSON response directly — the same pattern
QuestLog's own real `/health` endpoint uses.

</details>

A reference solution is in `solution/`.
