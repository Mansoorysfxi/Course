# Module 02 Capstone — API Exploration Report

## What this is

Per [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md), Module 02 has **no
QuestLog code** — this capstone is a standalone written
exploration/documentation deliverable against a real public API. You will
use `curl` (and, optionally, the REST Client VS Code extension from
`lessons/00-setup.md`) to explore
**[PokeAPI](https://pokeapi.co/docs/v2)** across several endpoints, plus
**[httpbingo.org](https://httpbingo.org)** for deliberately triggering
behavior PokeAPI itself won't let you trigger on demand (specific error
codes, redirects, cookies), and produce one structured document proving
you understand everything this module taught — not by restating the
lessons, but by demonstrating it against real, live requests you actually
ran.

**Why these two APIs, verified (August 2026):** PokeAPI is confirmed free,
requires no authentication or API key at all, has had rate limiting
removed entirely since November 2018 (a fair-use policy applies instead),
and is versioned at a stable `/api/v2/` base URL with current, accurate
documentation — verified directly by making live requests against it
while this module was written. httpbingo.org is an actively maintained
(security-patched as recently as April 2026), free, public instance of
`go-httpbin`, purpose-built for exactly the kind of deliberate HTTP
behavior demonstration this capstone needs, and was likewise verified live
while writing this module.

## Concepts this project uses

Every concept below has a dedicated section in this module's lessons —
none of this should require material this module didn't already teach:

| Concept | Taught in |
|---|---|
| DNS resolution | [Lesson 01](../lessons/01-networks-ip-addresses-and-dns.md) |
| IP addresses, ports | [Lesson 01](../lessons/01-networks-ip-addresses-and-dns.md) |
| TCP three-way handshake | [Lesson 02](../lessons/02-tcp-tls-and-the-request-response-journey.md) |
| TLS handshake / HTTPS | [Lesson 02](../lessons/02-tcp-tls-and-the-request-response-journey.md) |
| Request line, methods, idempotency/safety | [Lesson 03](../lessons/03-http-methods-and-status-codes.md) |
| Status codes and categories | [Lesson 03](../lessons/03-http-methods-and-status-codes.md) |
| Headers (request and response) | [Lesson 04](../lessons/04-headers-cookies-and-statelessness.md) |
| Cookies (`Set-Cookie`/`Cookie`) | [Lesson 04](../lessons/04-headers-cookies-and-statelessness.md) |
| Statelessness | [Lesson 04](../lessons/04-headers-cookies-and-statelessness.md) |
| Client/server roles, URL anatomy, APIs | [Lesson 05](../lessons/05-clients-servers-apis-and-json.md) |
| JSON structure | [Lesson 05](../lessons/05-clients-servers-apis-and-json.md) |
| REST's constraints | [Lesson 06](../lessons/06-rest-from-first-principles.md) |

## What to build

Produce one document, `notes/API_EXPLORATION_REPORT.md` (create the
`notes/` folder inside this `project/` folder), with exactly these
sections, in this order:

### 1. Overview
Which API you explored (PokeAPI), one paragraph on what it does, and a
one-line note confirming it's free/no-auth (you can simply state this —
you don't need to re-verify what this brief already verified above).

### 2. Endpoint walkthrough — Resource A
A full request/response cycle walkthrough (same depth as Exercise 03) for
one PokeAPI endpoint of your choice: resolved IP, TCP/TLS evidence from
`curl -v`, the exact request line and headers sent, the exact status line
and headers received, and an excerpt of the JSON body with at least three
different JSON value types identified.

### 3. Endpoint walkthrough — Resource B
The same full depth as section 2, for a **different kind of resource**
(different path pattern, e.g. if section 2 used `/pokemon/{name}`, this
one should use something like `/type/{name}`, `/move/{name}`, or the
paginated list form `/pokemon?limit=...&offset=...` — pagination is
specifically encouraged here since it lets you also discuss the `next`/
`previous` links from Lesson 05/06).

### 4. Deliberate error
Deliberately trigger **at least one** error status code and document it.
You may do this either against PokeAPI (request a resource that doesn't
exist → real `404`) or against httpbingo.org's `/status/{code}` endpoint
for a status PokeAPI won't naturally give you (e.g. `500`, `429`). Show
the exact command, the exact status line, and explain *why* that specific
code applies here, using Lesson 03's category framework (which digit,
whose "fault" structurally).

### 5. Headers catalogue
A table of **every distinct header** you actually observed across
sections 2–4 (both request and response headers), one row each, with a
one-sentence explanation of what it means — pull these from your own
actual command output, don't just copy Lesson 04's examples verbatim.

### 6. Cookies
PokeAPI does not set any cookies (you should confirm this yourself and
say so). Use httpbingo.org to demonstrate a real `Set-Cookie`/`Cookie`
round-trip (same mechanism as Exercise 02, your choice of cookie
name/value), and then explicitly answer: **why doesn't a read-only public
data API like PokeAPI need cookies at all?** Connect your answer to
Lesson 04's statelessness section specifically — this is a real design
choice, not an oversight.

### 7. REST principles mapping
Go through **all five required REST constraints** (client-server
separation, statelessness, cacheability, uniform interface — including
explicitly discussing HATEOAS, and layered system) for PokeAPI
specifically, citing real evidence from your own sections 2–4 for each
one (a specific header value, a specific repeated-request result, a
specific `next` link you actually saw). State plainly whether PokeAPI
satisfies each constraint fully, partially, or not at all, and why.

### 8. Reflection
Two to four sentences: one thing that surprised you about seeing this
"under the hood" for the first time, and one open question you still
have, if any.

## Acceptance criteria

- [ ] All 8 sections are present, in order, with real command output
  backing every factual claim (not paraphrased or invented output).
- [ ] Sections 2 and 3 use genuinely different PokeAPI path *patterns*,
  not just two different specific values of the same pattern.
- [ ] Section 4's deliberate error correctly names the status category
  and explains *whose* fault it structurally represents.
- [ ] Section 5's header table contains at least 8 distinct headers,
  each with a correct, specific (not generic/copy-pasted) explanation.
- [ ] Section 6 correctly connects PokeAPI's lack of cookies to
  statelessness as a deliberate design fit, not a missing feature.
- [ ] Section 7 addresses all five required constraints individually,
  each with specific supporting evidence, and is honest about partial
  satisfaction (especially HATEOAS) rather than claiming perfect
  compliance across the board.

## What to submit

Point your AI session at `notes/API_EXPLORATION_REPORT.md` and say *"check
my module"* — this capstone is graded per
[GRADING_PROTOCOL.md](../../GRADING_PROTOCOL.md) alongside a re-check of
Exercises 01–03 as part of the full Module 02 module-end review.

## Why this project, specifically

Every other module's capstone in this course produces code. This one
deliberately doesn't — Module 02's entire point is building an accurate
mental model of what's actually happening beneath every HTTP call you'll
ever make in code starting with FastAPI in Module 05. Writing the full
explanation yourself, backed by real evidence you personally gathered
rather than lesson text you're restating, is the actual skill being
tested: the ability to look at *any* unfamiliar API in your future career
and correctly reason about its request/response cycle, its status codes,
and how RESTful it really is — not just PokeAPI specifically.
