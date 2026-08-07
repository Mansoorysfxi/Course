# Lesson 10 — CORS, Explained Minutely

## What you'll learn

- What an **origin** actually is, precisely (not "domain" — a specific combination of three things).
- The **Same-Origin Policy**: the browser's own default rule that CORS exists as a controlled exception to.
- The difference between a "simple" cross-origin request and one that triggers a **preflight** `OPTIONS` request first — and exactly what determines which one happens.
- What each CORS response header actually means: `Access-Control-Allow-Origin`, `-Methods`, `-Headers`, `-Credentials`.
- The single most confusing fact about CORS errors: **the request usually still reaches your server and succeeds there** — the browser blocks the *frontend JavaScript* from reading the response, not the server from processing it.
- Exactly what QuestLog's own `CORSMiddleware` configuration does, line by line, and why `allow_credentials` is deliberately left off.

## Why this matters

The master plan for this course calls this out by name: "everyone gets
bitten by CORS" — and it's true precisely because a CORS error looks,
superficially, like a networking failure or a backend bug, when it's
neither. Module 05 and Module 06 both already had a CORS-enabling line in
`app/main.py`, with a comment explicitly deferring the full explanation to
this module. This lesson pays that off completely.

## Prerequisites

Module 02 (HTTP methods, headers, status codes — especially `OPTIONS`,
already defined in that module's glossary entry as "used automatically by
browsers as a CORS preflight request," a promise this lesson now keeps).
Module 03/04 (that a React app running via Vite's dev server is a real,
separate HTTP server, on its own port).

## The concept, explained simply

Think of a browser tab as a guest at a hotel with a single room key. That
key (think of it as everything the browser knows and trusts about
`http://localhost:5173`, the page currently open) opens *that room only*
by default — the hotel's own security policy refuses to let that key open
any other room's door, even a room the same guest is also staying in
under a different reservation. **CORS is the hotel's own, very specific
procedure for a guest to request temporary access to a second room** —
the second room's own front desk (the *server* at that second address,
`http://localhost:8000`) has to explicitly say "yes, that specific guest's
key is allowed in here" before the door will open, and it says so via a
specific set of response headers this lesson explains in full.

## The details

### What an "origin" actually is

An **origin** is the exact combination of three things: **scheme**
(`http` vs `https`), **host** (`localhost`, `questlog.app`, ...), and
**port** (`5173`, `8000`, `443`, ...). Two URLs share an origin only if
**all three** match exactly. This trips up almost everyone the first
time:

| URL A | URL B | Same origin? |
|---|---|---|
| `http://localhost:5173` | `http://localhost:8000` | **No** — different port |
| `http://localhost:5173` | `https://localhost:5173` | **No** — different scheme |
| `http://localhost:5173` | `http://127.0.0.1:5173` | **No** — different host, even though both mean "this machine" to a human |
| `http://questlog.app` | `http://questlog.app:80` | **Yes** — port 80 is HTTP's own default, so it's the same effective origin |

QuestLog's frontend (`http://localhost:5173`, Vite's default dev port)
and backend (`http://localhost:8000`) are, by this exact definition,
**two different origins** — despite both running on the very same
machine, during local development. This is precisely why CORS is
relevant to this project at all, right now, in local development, not
just in some hypothetical future production deployment.

### The Same-Origin Policy — the default browsers actually enforce

Browsers apply a security rule called the **Same-Origin Policy**: by
default, JavaScript running on a page from origin A **cannot read the
response** of a request it makes to origin B, even though the browser is
often still fully capable of *sending* that request. This default exists
to stop a malicious page from silently reading data out of, say, your
already-logged-in banking site in another tab, by issuing background
requests to it and inspecting the responses (a distinct concern from
CSRF, Lesson 09 — CSRF is about a forged request's *side effects*; the
Same-Origin Policy is about *reading a response's contents*).

**CORS (Cross-Origin Resource Sharing) is the controlled, explicit
mechanism for a server to opt back into allowing this** — a server says,
via specific response headers, "requests from this other specific origin
are allowed to read my responses," and the *browser itself* (not the
server, and not your own JavaScript code) checks those headers and
decides whether to actually hand the response to the calling JavaScript.

### The single most confusing fact about a CORS error

When your browser's console shows a CORS error, in the overwhelming
majority of cases **your backend already received the request, processed
it completely, and sent back a real, valid response.** The browser
computed the request, sent it over the network, got an answer back — and
then, seeing that the response's CORS headers didn't authorize
`http://localhost:5173` to read it, **discarded the response before your
JavaScript ever saw it**, and reported a CORS error to your `fetch()`
call's `catch` block instead. This is why a CORS failure often looks
exactly like "the backend isn't running" from the frontend's point of
view (an error is thrown, no data arrives) even though the backend
handled the request perfectly and even fully executed any database
writes it caused. **Always check your backend's own terminal output
first** — if you see the request logged there with a normal status code,
the backend did its job; the problem is entirely the CORS configuration
sitting between the two.

### Simple requests vs. preflighted requests

Not every cross-origin request behaves the same way. Browsers classify a
request as a **"simple" request** only if it meets a fairly narrow set of
conditions (roughly: uses `GET`/`HEAD`/`POST`, and only a small allowed
set of headers, with a `Content-Type` limited to a few plain values). A
simple request is sent directly, with the actual request and response
happening exactly once — the browser just refuses to hand the response to
your JavaScript afterward if the CORS headers don't allow it.

**Any request that doesn't qualify as "simple"** — which, critically,
includes every single one of QuestLog's real API calls, because they all
send `Content-Type: application/json` (not on the small "simple" allow-list)
and/or an `Authorization` header — triggers a **preflight request**
first: the browser automatically sends a separate `OPTIONS` request to
the same URL, *before* your real request, asking "if I were to send a
real request with this method and these headers, would that be allowed?"
Only if the server's `OPTIONS` response says yes does the browser then
send your actual request at all. This is exactly what Module 02's own
glossary entry for `OPTIONS` already promised: "used automatically by
browsers as a CORS preflight request" — you have now seen precisely when
and why.

### The response headers, one by one

- **`Access-Control-Allow-Origin`** — names which origin(s) may read this
  response. Must exactly match the requesting page's own origin (or be
  the literal wildcard `*`, meaning "any origin" — see the credentials
  restriction below) or the browser withholds the response.
- **`Access-Control-Allow-Methods`** — which HTTP methods (`GET`, `POST`,
  `PATCH`, `DELETE`, ...) the server permits for cross-origin requests,
  returned specifically in response to a preflight `OPTIONS` request.
- **`Access-Control-Allow-Headers`** — which request headers (beyond the
  small default-allowed set) the server permits — this is exactly why a
  cross-origin request setting a custom `Authorization` header, like
  every authenticated QuestLog request, needs this header present in the
  preflight's response, or the browser refuses to send the real request
  with that header at all.
- **`Access-Control-Allow-Credentials`** — a boolean flag specifically
  about **cookies** (and other "ambient" credentials like HTTP basic
  auth) being included in a cross-origin request. This has nothing to do
  with a manually-set `Authorization` header — QuestLog's frontend sets
  that header itself, in its own JavaScript (Lesson 03), which is a
  perfectly ordinary custom header from CORS's point of view, not a
  "credential" in this specific, cookie-focused sense.
- **The wildcard/credentials rule:** `Access-Control-Allow-Origin: *`
  combined with `Access-Control-Allow-Credentials: true` is explicitly
  forbidden by the CORS specification itself, and browsers will reject
  that combination outright — a server allowing *any* origin to read
  responses while *also* including the user's cookies would defeat the
  entire point of same-origin protections for cookie-based auth. This is
  precisely why, per this module's own research (Lesson 00's header),
  current guidance is unanimous: if you need `allow_credentials=True`
  anywhere, you must list explicit origins, never a wildcard.

### QuestLog's actual configuration, line by line

`backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- `allow_origins=settings.cors_origins` — a real Python list (read from
  the `CORS_ORIGINS` environment variable, `app/config.py`), defaulting
  to exactly `["http://localhost:5173"]` — the one origin this app's own
  frontend actually runs on during local development. Listing specific
  origins, rather than `"*"`, is current best practice generally (Lesson
  00's research), not only when credentials are involved.
- `allow_methods=["*"]` — permits every HTTP method this app actually
  uses (`GET`, `POST`, `PATCH`, `DELETE`) for cross-origin requests. A
  wildcard here is a reasonable simplification for a small app with one
  known frontend; a larger, more security-conscious API might instead
  list only the exact methods its routes really use.
- `allow_headers=["*"]` — permits any request header, including this
  app's `Content-Type: application/json` and `Authorization: Bearer ...`
  — both of which trigger a preflight (per the "simple request" rules
  above), and both of which must be explicitly allowed here or the
  browser refuses to send the real request that follows.
- **No `allow_credentials=True` anywhere.** This is deliberate, not an
  oversight — QuestLog never sends cookies at all; its JWT travels in a
  header the frontend sets manually (Lesson 03), which CORS's
  "credentials" flag has nothing to do with. Turning this flag on would
  add a real, specific security consideration (opening the door to
  sending cookies cross-origin) for a feature this app doesn't use at
  all — see `app/main.py`'s own comment for this exact reasoning.

`app.add_middleware(CORSMiddleware, ...)` must run **before** any routes
that need it apply — Module 05's middleware lesson already established
that middleware wraps every request/response passing through the app;
CORS is a textbook example of exactly that "runs on every request,
unconditionally" shape, which is why it's added once, globally, rather
than configured per-route.

## Common mistakes & gotchas

- **Adding the frontend's URL to `allow_origins` with a trailing
  slash.** `"http://localhost:5173/"` (with a trailing slash) is not the
  same string as `"http://localhost:5173"`, and CORS matching is exact —
  this single extra character is a genuinely common real-world cause of
  "I definitely added my origin and it still doesn't work."
- **Trying to "fix" a CORS error by adding CORS headers in the
  frontend's own `fetch()` call.** CORS headers are **response** headers
  the *server* controls — a frontend cannot grant itself permission to
  read a response by adding request headers; the fix always lives in the
  backend's CORS configuration.
- **Confusing a CORS failure with a `401` or `404`.** If your backend
  never received the request at all because of a failed preflight, you
  won't see any log line for it in your backend's terminal — check there
  first (per this lesson's "single most confusing fact" box) before
  assuming your own route code, or authentication, is at fault.
- **Setting `allow_origins=["*"]` "just to make it work," and leaving it
  in production.** Fine for a brief local debugging experiment, genuinely
  risky to ship — Lesson 00's research is explicit that this is
  development-only guidance, and doubly wrong the moment `allow_credentials`
  is also involved (the browser will reject that combination outright
  anyway, per the rule above).

## How this connects

This lesson closes a loop opened as early as Module 05's own setup lesson,
which flagged CORS by name and deferred it here explicitly. It's also the
first lesson in this module explaining a *browser*-enforced mechanism in
this much depth, connecting directly to Lesson 09's XSS/CSRF (both of
which are also fundamentally about what a browser will and won't do by
default) — CORS, XSS, and CSRF are frequently confused with each other by
newer engineers; you should now be able to state cleanly that they are
three genuinely different mechanisms solving three different problems.

## Quick self-check

1. Precisely define "origin." Are `http://localhost:5173` and `http://127.0.0.1:5173` the same origin? Why or why not?
2. When a CORS error appears in your browser's console, did your backend actually receive and process the request in most cases? What should you check first to confirm this?
3. What is a CORS preflight request, which HTTP method does it use, and what specifically about QuestLog's real requests makes every one of them trigger one?
4. What does `Access-Control-Allow-Credentials` actually control, and why does QuestLog's own configuration not need to set it?
5. Why is `Access-Control-Allow-Origin: *` combined with allowing credentials explicitly forbidden by the CORS spec?
