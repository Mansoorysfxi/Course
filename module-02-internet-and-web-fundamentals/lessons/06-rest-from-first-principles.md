# Lesson 06 — REST, From First Principles

## What you'll learn

- Where REST actually came from, and what kind of thing it is (a style, not
  a protocol or a standard you can "install").
- Every one of REST's real architectural constraints, explained plainly,
  each with a concrete example.
- How to actually evaluate whether a real API is "RESTful," instead of just
  assuming any JSON-over-HTTP API automatically qualifies.
- Resource-oriented URL design conventions used throughout the rest of this
  course.

## Why this matters

Every backend you build starting in Module 05 will be described, by you
and everyone you work with, as "a REST API" or "RESTful." Right now that
phrase is mostly a buzzword you've heard without a precise definition —
by the end of this lesson it will mean something exact and checkable, and
you'll be able to look at any real API (starting with the two this module
has used throughout) and say specifically which REST constraints it
satisfies and which it doesn't, rather than either blindly calling
everything "REST" or dismissing the term as meaningless marketing.

## Prerequisites

Lessons 01–05 — REST is the lesson where everything else in this module
gets organized into one coherent design philosophy. If any of methods,
status codes, headers/statelessness, or client/server/API/JSON feel shaky,
this lesson will be much harder to follow; go back first.

## The concept, explained simply

**REST (REpresentational State Transfer)** is not a protocol, a library, a
file format, or something you install. It's an **architectural style** — a
named set of design constraints/principles for building networked
systems — first described in Roy Fielding's year-2000 doctoral
dissertation (Fielding was one of the original authors of the HTTP
specification itself, so REST and HTTP were designed with each other very
much in mind). "REST" describes *how you should design a system that uses
HTTP*, not a new thing bolted on top of HTTP.

An analogy: think of REST the way you'd think of a coding style guide for
a large game codebase — it's not a compiler feature or a language
addition, it's an agreed set of conventions ("name classes this way,
structure files this way, don't do X") that makes a codebase predictable
and maintainable across a whole team, precisely because everyone follows
the same conventions rather than everyone inventing their own. REST is
that, for the shape of a web API: URLs, methods, and responses should
relate to each other in specific, predictable ways, so that any client
that understands "REST" in general can reasonably guess how *any*
RESTful API in particular behaves, without reading custom documentation
for every single endpoint from scratch.

## The details

### Seeing "uniform interface" and "cacheable" in one command

Before breaking down every constraint in the abstract, look at both of two
constraints at once, in real output you can generate yourself:

```bash
curl -i https://pokeapi.co/api/v2/pokemon/ditto -o /dev/null
```

**Expected output (headers only, abridged):**

```
HTTP/2 200
content-type: application/json; charset=utf-8
cache-control: public, max-age=86400
```

**What to notice:** the URL itself (`/pokemon/ditto`) is a clean noun
identifying one resource — no verb anywhere in the path (constraint 4,
"uniform interface," below) — and the response explicitly states its own
caching rules via `cache-control` (constraint 3, "cacheable," below),
rather than leaving a client to guess whether reusing this response is
safe. Both constraints are visible in this single response, before you've
even read their formal definitions — which is exactly the point of
looking at real evidence first.

**Try it yourself:** run the exact same command again a few seconds
later, then compare it to running `curl -i https://httpbingo.org/get -o /dev/null`
instead. Predict, before running the second one, whether you'll see a
`cache-control` header at all. (httpbingo.org's `/get` endpoint is a
request-echo tool with nothing meaningful to cache, and typically omits
`cache-control` entirely or marks itself explicitly non-cacheable — a
live reminder that cacheability is a deliberate choice a server's
designer makes, not something HTTP forces on every response
automatically.)

### REST's constraints, one at a time, with real examples

**1. Client–server separation.** The client and server must be cleanly
separated, communicating only through requests and responses — the client
never reaches into the server's internals, and the server never reaches
into the client's. You've had this the entire module: `curl` (client) and
PokeAPI (server) know nothing about each other's internal implementation;
they only agree on the *shape* of requests/responses (Lessons 03–05). This
separation is *why* PokeAPI's team can completely rewrite their server's
internals tomorrow, in a different language even, and every existing
client (including your own `curl` commands from this module) would keep
working unchanged, as long as the request/response shape stays the same.

**2. Statelessness.** Already taught in full in Lesson 04 — each request
must contain everything the server needs to understand and fulfill it, with
no reliance on the server remembering anything from a previous request.
PokeAPI satisfies this completely: every request you made this module was
fully self-contained; nothing about `GET /pokemon/pikachu` depended on any
earlier request you'd made.

**3. Cacheability.** Responses must explicitly state whether, and for how
long, they can be cached and reused, so clients don't have to re-fetch
unchanged data. This is exactly the `Cache-Control` header from Lesson 04.
PokeAPI satisfies this directly — recall its
`cache-control: public, max-age=86400` response header from Lesson 04,
telling every client explicitly that a response is safe to reuse for a
full day without asking again.

**4. Uniform interface.** This is the constraint with the most moving
parts — it itself breaks down into four sub-ideas:

   - **Resource identification via URLs.** Everything the API exposes is a
     named **resource**, addressed by a URL — `/pokemon/pikachu` identifies
     *the resource* "Pikachu," distinctly from `/pokemon/25` (Pikachu's
     numeric ID) or `/ability/static`. A resource is a *noun* — a thing —
     not an action.
   - **Manipulation of resources through representations.** You don't get
     the "real," internal Pikachu object living in PokeAPI's own database —
     you get a **representation** of it, specifically as JSON (Lesson 05).
     A different API might represent that exact same underlying resource
     as XML, or HTML, or something else — the resource and its
     representation are conceptually separate.
   - **Self-descriptive messages.** Each request/response should carry
     enough information (methods, headers — especially `Content-Type`) to
     be understood on its own, without needing out-of-band context. A
     response declaring `Content-Type: application/json` is
     self-describing in exactly this sense — you don't need to already
     know, from somewhere else, what format is coming back.
   - **Hypermedia as the engine of application state (HATEOAS).** Ideally,
     a response should include links guiding a client to related/next
     actions, rather than the client needing to construct further URLs by
     hand from prior knowledge. You already saw a genuine, real example of
     this in Lesson 05: PokeAPI's paginated list response included a ready-
     to-use `"next"` URL for the following page — that's HATEOAS, in
     miniature, working exactly as intended. **Being honest about this
     one:** most real-world APIs, PokeAPI included, only implement HATEOAS
     partially (a `next`/`previous` link here and there) rather than fully
     (comprehensive links describing every possible next action from every
     response) — full HATEOAS is the constraint real APIs most commonly
     fall short of, and it's worth knowing that upfront rather than being
     surprised later.

**5. Layered system.** A client shouldn't need to know whether it's
talking directly to the "real" server or to some intermediary
(load balancer, cache, proxy) sitting in front of it — each layer should
be swappable/insertable without the client needing to change. Recall the
`Server: cloudflare` header from Lesson 04 — Cloudflare sits *in front of*
PokeAPI's actual application server, and as a client, you never needed to
know or care about that layering to successfully get Pikachu's data.

**6. Code on demand (optional).** The server may optionally send back
executable code the client runs (classically, JavaScript sent to a
browser). This constraint is genuinely optional even in Fielding's own
definition, and irrelevant to a JSON API like PokeAPI — mentioned here
only so you recognize the name if you ever see all six constraints listed
together elsewhere; it won't come up again in this course in this form.

### Resource-oriented URL design

Beyond the formal constraints above, REST-style APIs converge on shared
URL conventions, all visible directly in PokeAPI's own design:

- **Nouns, not verbs, in paths.** `/pokemon/pikachu`, not
  `/getPokemon?name=pikachu`. The *method* (Lesson 03) supplies the verb;
  the path names the *thing*. This is a real, common beginner mistake to
  watch for in your own future API designs (Module 05) — reaching for
  `/deleteQuest` instead of `DELETE /quests/{id}` re-invents, in the URL
  itself, something the method already exists to express.
- **Plural collections, singular items within them.** `/pokemon` (the
  whole collection) vs. `/pokemon/pikachu` (one specific member of it) —
  same base noun, one addresses the group, one addresses an individual.
- **Query parameters for filtering/paging, not new paths.** `/pokemon`
  vs. `/pokemon?limit=20&offset=40` — same underlying resource
  ("Pokémon"), the query string (Lesson 05) narrows/pages *which* subset
  you want, rather than inventing a differently-named path for every
  possible combination of filters.
- **Nesting for genuine ownership/hierarchy.** Not exercised by PokeAPI
  directly, but the general convention (which you'll use constantly once
  you design QuestLog's own API in Module 05) is that a URL like
  `/users/{id}/quests` expresses "the quests belonging to this specific
  user" — nesting mirrors a real ownership relationship, not just any two
  things that happen to be related.

### Is PokeAPI actually "RESTful"? A real evaluation

Rather than take it on faith, here's the honest, constraint-by-constraint
verdict, which doubles as a template for evaluating *any* API you meet in
the future (including your own, starting in Module 05):

| Constraint | PokeAPI | Evidence from this module |
|---|---|---|
| Client–server separation | Yes | You never touched PokeAPI's internals — only URLs, methods, JSON |
| Stateless | Yes | Lesson 04 — repeating a request produced identical results, no login/session exists |
| Cacheable | Yes | `Cache-Control: public, max-age=86400` header, seen in Lesson 04 |
| Resource identification via URLs | Yes | `/pokemon/pikachu`, `/ability/static` — clean nouns |
| Manipulation via representations | Yes | Everything served as a JSON representation, never raw internal data |
| Self-descriptive messages | Yes | `Content-Type: application/json` present on every response |
| HATEOAS | Partial | `next`/`previous` links exist on list endpoints; individual resources don't link every related action |
| Layered system | Yes | Cloudflare sits in front, invisibly, per the `Server` header |

**Verdict:** PokeAPI satisfies the great majority of REST's real
constraints, with the well-known, common, and honestly-acknowledged gap
being *full* HATEOAS — exactly the situation with the vast majority of
APIs colloquially called "REST APIs" in the real world. This is precisely
why professionals distinguish, informally, between "a REST API" (loosely,
"a JSON-over-HTTP API that mostly follows REST conventions") and "a truly
RESTful API in Fielding's full original sense" (rare in practice, HATEOAS
and all). Both PokeAPI and, later, your own QuestLog API will fall
comfortably into the first, common category — and now you can say
specifically *why*, constraint by constraint, rather than shrugging and
calling it REST because it returns JSON.

## Common mistakes & gotchas

- **Thinking "REST" means "any API that returns JSON over HTTP."** It
  doesn't — an API using verbs in URLs, ignoring status codes (returning
  `200` for everything, including errors, with an error flag buried in the
  JSON body instead), or maintaining server-side session state for every
  client, could still return JSON over HTTP while violating REST
  constraints. "Returns JSON" and "is RESTful" are independent facts.
  about an API
- **Believing REST requires JSON specifically.** It doesn't — REST is
  format-agnostic; representations (constraint 4) could be JSON, XML, or
  anything else. JSON became the overwhelmingly common *choice*
  (Lesson 05) but it isn't part of REST's actual definition.
- **Using a verb in a path** (`/getUser`, `/deleteQuest`). Reach for the
  method instead: `GET /users/{id}`, `DELETE /quests/{id}`.
- **Assuming every real-world "REST API" satisfies every constraint
  perfectly.** As the PokeAPI table above shows, partial HATEOAS is
  extremely common and not considered a serious flaw in practice —
  knowing which specific constraint is commonly relaxed (and why) is more
  useful than a blanket "is it RESTful, yes or no."

## How this connects

This lesson is the capstone of the module, in the literal sense of tying
every previous lesson's individual piece into one coherent whole: DNS/TCP/
TLS got you connected (Lessons 01–02), methods/status codes gave you a
vocabulary for requests/responses (Lesson 03), headers/cookies/statelessness
explained the metadata and the "no memory" design (Lesson 04),
client/server/API/JSON named the roles and the format (Lesson 05), and now
REST explains *why* well-designed APIs are shaped the way they are. Every
API you design starting with your own QuestLog backend in Module 05 will
be built directly on these same conventions — you're not learning REST as
trivia, you're about to become the person deciding these exact choices for
your own API.

## Quick self-check

1. Is REST a protocol you install, or something else — and what,
   precisely?
2. Name all six of REST's constraints (five required, one optional), and
   for each, describe how PokeAPI does or doesn't satisfy it.
3. What's the difference between a "resource" and a "representation" of
   that resource, in REST terms?
4. Which REST constraint does PokeAPI (and most real-world "REST APIs")
   most commonly only partially satisfy?
5. Why is `/deleteQuest` considered bad REST-style URL design, and what
   would the corrected version look like?
