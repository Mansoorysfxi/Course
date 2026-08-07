# Lesson 05 — Clients, Servers, APIs, and JSON

## What you'll learn

- What "client" and "server" formally mean as *roles*, not specific
  technologies.
- The full anatomy of a URL, every part, named correctly.
- What an API is, in general, and specifically what a **web API** is.
- What JSON is, its complete grammar (all of it — it's small), and why it
  became the dominant data format on the web.

## Why this matters

You'll use the words "client," "server," and "API" in nearly every
sentence for the rest of this course, across React (Module 04), FastAPI
(Module 05), and beyond — and JSON is the format nearly every request
body and response body you'll ever write or read will be in, starting
immediately with your own FastAPI endpoints. Getting sloppy about any of
these terms now causes real confusion later, when "the API" and "the
server" and "the backend" start getting used almost interchangeably in
casual conversation and you need to know precisely which one someone
means.

## Prerequisites

Lessons 01–04. You've been using a client (`curl`), talking to a server
(PokeAPI/httpbingo.org), calling an API, and staring at JSON bodies this
entire module without a full definition of any of those three words — this
lesson closes that gap.

## The concept, explained simply

**Client** and **server** are *roles* in a single interaction, not fixed
identities a program permanently has. A **client** is whichever side
*initiates* a request. A **server** is whichever side *listens* and
*responds*. The exact same program can be a server in one interaction and
a client in another — your future FastAPI backend will be a *server* when
your React frontend calls it, but a *client* the moment it, in turn, calls
some third-party API (like PokeAPI) to fetch data it needs.

If you've built or played online multiplayer games, you already have a
working intuition for this: a **dedicated server** sits somewhere,
listening, running the authoritative simulation, and every connected
player's game instance is a **client** — it sends inputs/requests to the
server and receives back the server's authoritative state. The core shape
— one side listens and holds the "truth," other sides connect in and ask
things of it — is the exact same shape as a web server and its clients.
The differences are in *what* gets exchanged (HTTP requests/JSON instead
of game-specific packets) and *how often* (a web client typically makes
one request and gets one response, then the connection may close, rather
than a continuous real-time stream) — but the client/server *role split*
is identical. `curl` has been playing "client" this entire module; PokeAPI
and httpbingo.org have been playing "server."

## The details

### Anatomy of a URL

You've been typing URLs all module without a formal breakdown. Take this
one apart completely:

```
https://pokeapi.co/api/v2/pokemon/pikachu?limit=20#results
└─┬──┘   └───┬────┘└──────┬───────────────┘└───┬───┘└──┬──┘
scheme      host              path            query   fragment
```

- **Scheme** (`https`) — which protocol to use, and implicitly, which
  default port (Lesson 01–02: `https` → 443, `http` → 80).
- **Host** (`pokeapi.co`) — the domain name (Lesson 01) identifying which
  server to connect to.
- **Path** (`/api/v2/pokemon/pikachu`) — identifies *which specific
  resource* on that server you want. (Note the same word, "path," you saw
  on the HTTP request line in Lesson 03 — it's the exact same thing; the
  URL's path *becomes* the request line's path once a request is actually
  sent.)
- **Query string** (`?limit=20`) — optional extra parameters, as
  `key=value` pairs joined by `&` if there's more than one (e.g.
  `?limit=20&offset=40`), used commonly for filtering, sorting, or paging
  through results, without needing a different path for every possible
  combination.
- **Fragment** (`#results`) — a piece of the URL that never even gets sent
  to the server at all — it's purely for the client's own use (classically,
  "jump to this specific spot on the page" once loaded). Genuinely worth
  knowing this one is different in kind from the rest: everything before
  it is sent over the network; the fragment isn't.

Try a real query string against PokeAPI's list endpoint:

```bash
curl -s "https://pokeapi.co/api/v2/pokemon?limit=3&offset=0" | head -c 400
```

**Expected output (abridged):**

```json
{"count":1302,"next":"https://pokeapi.co/api/v2/pokemon?offset=3&limit=3","previous":null,"results":[{"name":"bulbasaur","url":"https://pokeapi.co/api/v2/pokemon/1/"},...
```

**Try it yourself:** before running it, predict what changing to
`?limit=5&offset=3` would do to the `"previous"` field (currently `null`
because offset `0` is the very first page — there's nothing before it).
Run `curl -s "https://pokeapi.co/api/v2/pokemon?limit=5&offset=3" | head -c 300`
and confirm: `"previous"` should now be a real URL pointing back to
`offset=0` (or similar), no longer `null`.

**Line by line:** `limit=3` asked for only 3 results at a time;
`offset=0` asked to start from the very beginning. Note the `"next"`
field in the response — a *complete, ready-to-use URL* for the next page
of results, with `offset` already advanced. This is a real, working
example of an API guiding a client to what's next, rather than the client
having to construct that next URL by hand — you'll see this idea named
formally (part of REST's "uniform interface" constraint) in Lesson 06.

### What an API is

**API** stands for **Application Programming Interface**. Stripped of the
acronym, it means exactly what it says: a defined way one piece of
software lets *another* piece of software use its functionality, without
the second program needing to know anything about how the first one is
actually implemented internally. This concept isn't web-specific at all —
you already have direct experience with APIs, even if you never called
them that: Unreal Engine's own C++ class hierarchy and Blueprint node
library *are* an API — a defined set of functions/classes/nodes other
code (yours) can call, without you ever needing to read the engine's own
internal source to use `UGameplayStatics::GetPlayerController()`
correctly. Any library you've ever `#include`d and called functions from
was an API in exactly this general sense.

A **web API** narrows this general idea to one specific delivery
mechanism: instead of calling functions in the same running program (like
an Unreal API call) or importing a library, a web API exposes
functionality *over HTTP*, to any client anywhere capable of making an
HTTP request — which is precisely what you've been doing to PokeAPI this
entire module. PokeAPI's "functionality" is "give me data about Pokémon";
its API is the specific set of URLs (endpoints), methods, and response
shapes it defines for accessing that functionality remotely.

An **endpoint** is one specific URL (or URL pattern) an API exposes for
one specific piece of functionality — `/api/v2/pokemon/{name}` is an
endpoint; so is `/api/v2/ability/{name}`. An API is, structurally, just a
defined collection of endpoints, plus documentation of what each one
expects and returns.

### JSON — full grammar

**JSON (JavaScript Object Notation)** is a plain-text format for
representing structured data. Despite the name (it originated from
JavaScript's own object syntax), it is now a completely
language-independent standard, used by APIs written in every language —
including every response body you've seen from PokeAPI this whole module.
Its entire grammar is genuinely small enough to state completely, unlike,
say, all of CSS or all of Python:

- **Objects** — `{ "key": value, "key2": value2 }` — unordered
  key→value pairs, keys are *always* double-quoted strings (never single
  quotes, never unquoted).
- **Arrays** — `[ value, value2, value3 ]` — ordered lists of values.
- **Strings** — always double-quoted: `"pikachu"`.
- **Numbers** — `25`, `4.5`, `-3` — no quotes.
- **Booleans** — `true` / `false` — lowercase, no quotes.
- **Null** — `null` — lowercase, means "no value," JSON's equivalent to
  Python's `None` (recall from
  [Module 01, Lesson 01](../../module-01-python-properly/lessons/01-variables-types-and-control-flow.md)).

That's the *entire* grammar — every JSON document, however large, is built
from nothing but nested combinations of these six things. Look at a real
one, piece by piece:

```bash
curl -s https://pokeapi.co/api/v2/ability/static | head -c 300
```

**Expected output (abridged):**

```json
{"effect_changes":[],"effect_entries":[{"effect":"Whenever...","language":{"name":"en","url":"https://pokeapi.co/api/v2/language/9/"}}],"generation":{"name":"generation-iii","url":"..."},"id":9,"is_main_series":true,"name":"static"
```

**Line by line:** the whole thing is one **object** (outer `{ }`).
`"effect_entries"` maps to an **array** (`[ ]`) of more **objects**.
`"id": 9` is a **number**, no quotes. `"is_main_series": true` is a
**boolean**. `"name": "static"` is a **string**. Every value you'll ever
see in any JSON API response — no matter how deeply nested or how large —
decomposes into exactly these same six building blocks, nested inside each
other.

**Why JSON won** over its main historical competitor, XML (a more verbose,
tag-based format many older APIs used, and some legacy systems still do):

1. **Far less verbose.** The same data in XML requires opening *and*
   closing tags for every single field (`<name>pikachu</name>` vs. JSON's
   `"name": "pikachu"`) — real bandwidth and readability savings at scale.
2. **Maps almost directly onto native data structures in nearly every
   language.** A JSON object *is*, structurally, a Python `dict` (you
   already know this from
   [Module 01, Lesson 08](../../module-01-python-properly/lessons/08-file-io-and-json.md));
   a JSON array *is* a Python `list`. JavaScript, unsurprisingly, parses
   JSON into its native objects/arrays with zero translation work at all
   — it's *literally* JavaScript's own object literal syntax, which is
   exactly where the format originated. Parsing/generating JSON in almost
   any modern language is close to a non-event.
3. **Simple enough to hand-write and hand-read.** XML's fuller feature set
   (namespaces, attributes vs. elements, schemas) solves real problems
   but adds real complexity most APIs never actually needed.

None of this makes JSON strictly "better" in every possible sense — XML
still has legitimate uses (some document formats, some enterprise/legacy
systems) — but for the specific job of "structured data traveling between
a web client and a web server," JSON's simplicity and its near-zero
translation cost into native code decisively won out, and by the mid-2010s
it had become the overwhelming default for new web APIs, which is exactly
why every response you've seen in this entire module has been JSON.

### The `Content-Type` connection

Recall from Lesson 04: a response declares its body format via the
`Content-Type` header. For JSON, that header reads
`application/json` — you've seen this exact value in every PokeAPI
response this module. This is the formal link between "the bytes on the
wire" and "how to interpret them" — a client should always check this
header rather than just assuming a body is JSON because it happens to look
like it.

## Common mistakes & gotchas

- **Writing JSON with single quotes or unquoted keys** (`{name: 'pikachu'}`)
  — invalid JSON. Every string, including every key, must use double
  quotes, no exceptions.
- **Leaving a trailing comma** (`{"a": 1, "b": 2,}`) — also invalid JSON,
  unlike Python, where a trailing comma in a dict/list literal is
  perfectly fine. This trips up nearly everyone coming from Python at some
  point.
- **Assuming JSON *is* a Python dict.** It's extremely close, and
  `json.loads()` (Module 01, Lesson 08) converts one into the other almost
  transparently, but they are not literally the same thing — JSON is text
  on the wire; a `dict` is a live Python object in memory. This distinction
  becomes important again in Module 05 when Pydantic sits between the two.
- **Confusing "client/server" with "frontend/backend."** They're closely
  related but not identical: your React app (frontend) is a client when it
  calls your FastAPI backend (server) — but your FastAPI backend *itself*
  becomes a client the moment it calls some other external API. "Frontend"
  and "backend" describe *what a program is for*; "client" and "server"
  describe *the role it's playing in one specific interaction*.
- **Forgetting the fragment (`#...`) never reaches the server.** If you're
  ever debugging "why doesn't my server see this URL parameter" and it
  turns out to be after a `#`, that's the answer — move it into the query
  string instead.

## How this connects

You now have every individual piece this module set out to teach: DNS/IP
(Lesson 01), TCP/TLS (Lesson 02), methods/status codes (Lesson 03),
headers/cookies/statelessness (Lesson 04), and now client/server roles,
APIs, and JSON. Lesson 06 is where all of these snap together into one
coherent architectural *style* — REST — that describes how a well-designed
web API's URLs, methods, and responses should relate to each other, and
lets you evaluate whether a real API (like PokeAPI) actually follows it.

## Quick self-check

1. Is a program ever "just" a client or "just" a server, or does that
   depend on which interaction you're looking at? Give an example from
   this course.
2. Name all five parts of a URL, in order, and state which one never
   actually gets sent to the server.
3. Give one API example from outside the web (i.e., not an HTTP-based
   one) that you already have direct experience with.
4. Write, from memory, a syntactically valid JSON object with one string
   field, one number field, one boolean field, and one nested array.
5. State two concrete reasons JSON displaced XML as the web's dominant
   data format.
