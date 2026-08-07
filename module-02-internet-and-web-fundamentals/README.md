# Module 02 — Internet & Web Fundamentals

**Phase:** 1 — How the Web Actually Works + Frontend
**Estimated time:** 8–12 hours over one week
**Verified against (August 2026):** live requests against
[PokeAPI](https://pokeapi.co/docs/v2) `/api/v2/` (confirmed free, no
authentication required, rate limiting removed since November 2018) and
[httpbingo.org](https://httpbingo.org) (an actively maintained, security-
patched public instance of `go-httpbin`, verified live); HTTP semantics
against **RFC 9110** (June 2022, the current authoritative HTTP
specification); TLS status against RFC 8446 (TLS 1.3, current preferred
standard) and RFC 8996 (TLS 1.0/1.1 formally deprecated, disabled in all
major browsers since 2020); `curl` bundling confirmed as part of Git for
Windows (installed in Module 00, living at
`C:\Program Files\Git\mingw64\bin\`); the recommended optional REST
client, VS Code's **REST Client** extension (`humao.rest-client`),
verified as a current, free, actively-used, no-account, no-usage-cap
option in 2026. See each lesson for exactly what was checked and when.

## What this module is

Every module from here to the end of this course involves a client
talking to a server over HTTP, in some form — a React app calling your
FastAPI backend, your backend calling a database or an LLM API, an AI
agent calling a tool over the network. This module builds, from
absolute zero, a correct and complete mental model of what's actually
happening in every one of those interactions: what a network even is,
how a domain name becomes a reachable machine, how a connection gets
opened and secured, what an HTTP request and response actually look
like on the wire, what makes HTTP "stateless," what an API and a REST
API specifically are, and why JSON is what you'll be reading and writing
almost everywhere for the rest of this course.

Per the master plan, this module is deliberately **not** compressed —
every layer, from "what is a network" upward, is built up explicitly,
assuming zero prior web knowledge. Per
[`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md), this module contains **no
QuestLog code** — its capstone is a standalone written exploration of a
real public API, because the goal here is understanding the protocol
itself, not writing an application yet. QuestLog's own web incarnation
begins in Module 04.

## What you'll be able to do after this module

- Explain, completely and in the correct order, everything that happens
  between typing a URL and seeing a response: DNS resolution, the TCP
  three-way handshake, the TLS handshake, the HTTP request, and the HTTP
  response.
- Correctly use and interpret `curl` for real HTTP exploration: methods,
  headers, status codes, verbose/debug output, and cookie jars.
- Name every common HTTP method and correctly state whether each is safe
  and/or idempotent, and why that distinction matters in real systems.
- Categorize and correctly interpret HTTP status codes by their first
  digit, and know the specific codes you'll meet constantly (200, 201,
  204, 301/302, 304, 400, 401, 403, 404, 409, 422, 429, 500, 502, 503).
- Explain what HTTP headers and cookies are, and precisely what "HTTP is
  stateless" means and how cookies work around it.
- Explain client/server roles, what an API and specifically a web API
  are, and read/write valid JSON confidently.
- Evaluate whether a real-world API actually satisfies REST's
  architectural constraints, constraint by constraint, rather than
  assuming any JSON-over-HTTP API automatically qualifies as "REST."

## Prerequisites

**Module 00, specifically:** comfort with Git Bash and the shell (this
module runs every example as a shell command) is assumed with no
re-teaching. This module's setup lesson briefly re-verifies `curl`
(already installed via Module 00's Git for Windows setup) but does not
re-teach shell basics. No Module 01 (Python) knowledge is required for
this module's content, though Lesson 05's JSON discussion references
Python's `dict`/`list`/`json` module from Module 01 for comparison.

## Module structure

```
module-02-internet-and-web-fundamentals/
├── README.md                                          ← you are here
├── lessons/
│   ├── 00-setup.md                                   ← curl already installed; optional REST client
│   ├── 01-networks-ip-addresses-and-dns.md           ← networks, IP addresses, ports, DNS
│   ├── 02-tcp-tls-and-the-request-response-journey.md ← TCP, TLS, the full "type a URL" walkthrough
│   ├── 03-http-methods-and-status-codes.md           ← methods, safety/idempotency, status codes
│   ├── 04-headers-cookies-and-statelessness.md       ← headers, cookies, what "stateless" means
│   ├── 05-clients-servers-apis-and-json.md           ← client/server roles, URLs, APIs, JSON
│   └── 06-rest-from-first-principles.md              ← REST's real constraints, evaluated against a real API
├── exercises/
│   ├── 01-first-requests-with-curl/                  ← very easy
│   ├── 02-status-codes-redirects-and-cookies/        ← guided
│   └── 03-request-response-walkthrough/              ← independent
├── project/
│   └── BRIEF.md                                      ← API Exploration Report capstone
└── CHECKLIST.md
```

Read the lessons in numeric order — later lessons assume earlier ones
without re-explaining. Lesson 00 is intentionally short: this module needs
almost no new setup (you already have `curl`), and padding a setup lesson
with unnecessary steps would waste your time. Still, don't skip it — it
verifies `curl` is really working and covers the one optional tool
recommendation.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson
fully, answer its self-check questions, do the matching exercise without
peeking at the solution, then ask your AI session *"Review my solution
for exercise 0N."* After all three exercises and the capstone are done,
say *"Check my module"* for the full module-end review.

## A note on the capstone

The Module 02 capstone (`project/BRIEF.md`) has you produce a written
**API Exploration Report** — not code. You'll use `curl` (and optionally
the REST Client extension) against two real, verified-live public APIs
(PokeAPI for genuine data exploration, httpbingo.org for deliberately
triggering specific status codes, redirects, and cookie behavior) to
document, with real evidence, the full request/response cycle across
multiple endpoints, a deliberately-triggered error, every header you
observed, and a constraint-by-constraint REST evaluation. This is the
first capstone in the course that produces a document instead of running
code — and it's exactly as rigorous as the code-based ones, graded the
same way per [GRADING_PROTOCOL.md](../GRADING_PROTOCOL.md).
