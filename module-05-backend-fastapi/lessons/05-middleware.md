# Lesson 05 — Middleware: A Component in Every Request's Tick Chain

## What you'll learn

- What **middleware** actually is, and precisely how it differs from a route or a dependency (Lesson 04).
- How to write your own middleware function, and exactly when it runs relative to your routes.
- How multiple middleware layer together, and in what order.
- FastAPI's built-in `CORSMiddleware` — installed and briefly explained now, purely so this module's capstone frontend can actually reach it; the full explanation of *why* it's needed and how to configure it correctly is Module 07's job.

## Why this matters

Every request this module has handled so far went straight from Uvicorn to exactly one route function. Real APIs almost always need to do a handful of things to *every* request, or *every* response, regardless of which specific route ends up handling it — logging how long each request took, adding a security header, or (as flagged already in Lesson 00) allowing a browser running on one origin to actually reach this server at all. Middleware is FastAPI's mechanism for exactly that: code that runs on every request, in a defined order, before/after routing decides anything.

## Prerequisites

Lessons 01–04. Module 01, Lesson 10 (decorators — you'll use one more, specifically for middleware). Module 01, Lesson 11 (async/await — middleware functions are always `async def`).

## The concept, explained simply

Recall your own Unreal tick loop: every frame, a chain of systems runs in a defined order — input processing, then physics, then gameplay logic, then rendering — and (in many engines' actual architectures) individual components in an Actor's tick chain each get a turn to act on that Actor's state before the frame is considered "done." **Middleware is exactly this idea, applied to an HTTP request instead of a game frame:** a piece of code that sits *between* the raw incoming request and whichever specific route eventually handles it, given a chance to inspect or modify the request on the way in, and the response on the way out — for every single request that arrives, regardless of which route it's ultimately headed to. Where a **dependency** (Lesson 04) is opted into by a *specific* route (via a parameter on that one function), **middleware wraps everything, unconditionally**, exactly as a tick-chain component processes every actor passing through it, rather than being called deliberately by one specific piece of gameplay code.

## The details

### Writing your own middleware

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(elapsed)
    return response

@app.get("/quests/{quest_id}")
async def get_quest(quest_id: str):
    return {"quest_id": quest_id}
```

```bash
curl -i http://127.0.0.1:8000/quests/quest-001
```
**Expected:** among the response headers, a line like `x-process-time: 0.0000432` — a header no route function wrote directly.

**Line by line:**
- `@app.middleware("http")` — another decorator (Module 01, Lesson 10 continuing to pay off) registering the function below it as HTTP middleware. `"http"` names the specific *protocol* this middleware applies to — ASGI (Lesson 00) can carry other protocols too (WebSockets, briefly mentioned in Lesson 00's Uvicorn install), and this string is how you'd tell FastAPI "only for plain HTTP requests," which is every request in this module.
- `async def add_process_time_header(request: Request, call_next):` — always exactly this shape: an `async def` function (Module 01, Lesson 11 — middleware genuinely needs to `await` the rest of the chain, shown next), taking the incoming `Request` object and a special parameter, `call_next`.
- `request: Request` — a FastAPI/Starlette object representing the actual incoming request — its method, path, headers, and more — available for your middleware to inspect (or, less commonly, modify) before the matched route ever sees it.
- `response = await call_next(request)` — **this is the entire mechanism, stated precisely:** `call_next` is a function representing "everything that would otherwise happen next" — every other middleware still further down the chain, then whichever route actually matches this request. Calling and `await`-ing it runs all of that, and gives you back the real `Response` object that would otherwise have gone straight back to the client. Your middleware now holds that response in its hands, before it's actually sent.
- `response.headers["X-Process-Time"] = str(elapsed)` — modifies the response *after* the route has already produced it, adding a header the route function itself never wrote and doesn't know about.
- `return response` — hands the (possibly modified) response back up the chain. **If you forget this `return`, the client gets no response at all** — the request will simply hang until it times out, since nothing downstream of your middleware is what actually sends bytes back over the network; your middleware is the thing responsible for handing the final response onward.

### Multiple middleware — order matters, and it's a stack

```python
@app.middleware("http")
async def middleware_one(request: Request, call_next):
    print("one: before")
    response = await call_next(request)
    print("one: after")
    return response

@app.middleware("http")
async def middleware_two(request: Request, call_next):
    print("two: before")
    response = await call_next(request)
    print("two: after")
    return response
```

**Expected print order, for one incoming request** (registered in this order — `middleware_one` first, `middleware_two` second):
```
two: before
one: before
one: after
two: after
```

**Why this specific order, and not simply top-to-bottom:** each `@app.middleware("http")` registration wraps *around* everything registered before it — so the *last*-registered middleware ends up as the *outermost* layer, running first on the way in and last on the way out. This is exactly a stack (Module 01's data structures — think of each middleware as pushing itself onto a call stack that then unwinds in reverse) rather than a simple queue. In practice: don't rely on subtle ordering between several of your own middleware functions unless you've deliberately reasoned through this exact rule; keep each one focused on one clear job (timing, a security header, logging) to minimize how much this ordering ever actually matters.

### `CORSMiddleware` — enough to unblock the frontend, full explanation in Module 07

Recall Lesson 00's flag: a browser page served from `http://localhost:5173` (Module 04's Vite dev server) making a `fetch()` request to `http://localhost:8000` (this module's backend) is a cross-origin request, and browsers block these by default unless the server explicitly says otherwise. FastAPI ships a ready-made middleware for exactly this, and this module's capstone (Lesson 08) uses it, minimally:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Read this as "flip this switch," not as something to deeply understand yet — Module 07 is where CORS itself (what a cross-origin request actually is, what a "preflight" `OPTIONS` request does, and how to configure this safely for a real production deployment rather than a local dev server) gets the full treatment the master plan promises it.** For now, notice only the shape: `add_middleware(...)` is a different registration style than the `@app.middleware("http")` decorator above — it's used specifically for pre-built, importable middleware *classes* like `CORSMiddleware`, rather than a plain function you wrote yourself; `allow_origins` is a specific, explicit list of exactly which frontend origins are allowed to call this backend — during local development, this course's capstone lists only Module 04's dev server's exact address, `http://localhost:5173`.

## Common mistakes & gotchas

- **Forgetting `return response` at the end of a custom middleware function.** The request hangs with no response ever sent — check this first if a route that works fine via `curl` (bypassing any browser-side CORS concerns) still seems to "never finish" once you've added middleware.
- **Forgetting `await` before `call_next(request)`.** `call_next` is itself an async function — omitting `await` gives you a not-yet-run coroutine object (Module 01, Lesson 11's exact "forgot to await" mistake) instead of a real `Response`, and your middleware will fail trying to treat it like one.
- **Doing genuinely slow, blocking work inside middleware.** Every single request passes through every middleware you've registered — a slow, blocking operation here (Module 01, Lesson 11's warning about blocking the event loop) affects *every* route in your entire application, not just one.
- **Reaching for middleware when a dependency (Lesson 04) was the right tool.** If the logic only needs to apply to *some specific* routes and needs access to that route's own parameters (a path param, a validated request body), a dependency is almost always the better fit; reserve middleware for things that genuinely apply to *every* request, regardless of which route it's headed to.
- **Assuming `allow_origins=["http://localhost:5173"]` is a safe, permanent production setting.** It's correct for local development against Module 04's dev server specifically; Module 07 covers what changes for a real deployed frontend at a real domain.

## How this connects

Middleware and dependencies (Lesson 04) are both ways of running shared code around your route logic, and you can now explain precisely how they differ: middleware is unconditional and generic (every request, before routing decides anything); a dependency is opted into by specific routes and can use everything Lesson 02–03 taught about path/query parameters and request bodies. Lesson 06 covers what happens when something genuinely goes wrong inside a route — structured error handling and status codes, tying directly back to Module 02's status-code vocabulary.

## Quick self-check

1. Using the tick-chain analogy, explain the specific difference between middleware and a dependency (Lesson 04) — which one applies to every request unconditionally, and which one is opted into by a specific route?
2. What does `call_next(request)` actually represent, and why must it be `await`-ed?
3. If you register `middleware_one` and then `middleware_two`, in that order, which one's "before" code runs first for an incoming request — and which one's "after" code runs first on the way out?
4. What specifically breaks if a custom middleware function forgets to `return response`?
5. Why does this lesson deliberately avoid fully explaining *why* CORS exists, even though it shows you the exact code to unblock it?
