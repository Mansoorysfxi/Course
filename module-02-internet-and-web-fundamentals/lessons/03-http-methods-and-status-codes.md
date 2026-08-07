# Lesson 03 — HTTP Methods and Status Codes

## What you'll learn

- The exact anatomy of an HTTP request line and a response status line.
- Every commonly-used HTTP method (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`,
  `HEAD`, `OPTIONS`) and what each one actually means.
- What "safe" and "idempotent" mean for a method, and why those two
  properties matter enormously in real systems.
- Every status code category (1xx–5xx) and the specific codes you'll meet
  constantly, verified against the current official specification.
- How to trigger and observe real methods and status codes yourself with
  `curl`.

## Why this matters

Methods and status codes are the vocabulary of every API you will ever
call or build for the rest of this course, starting with your own FastAPI
backend in Module 05. Getting these wrong in real code causes real bugs:
using `GET` for something that changes data breaks caching and can get
accidentally re-triggered by browsers/crawlers; returning `200` for an
error confuses every client talking to your API; not knowing the
difference between `401` and `403` will cost you real debugging time in
Module 07 (Auth). This lesson gives you the precise, correct vocabulary so
none of that happens by accident.

## Prerequisites

Lesson 02 — you should already know that an HTTP request/response is what
travels inside the TCP+TLS "envelope" once it's open. This lesson opens
that envelope and looks at exactly what's written inside it.

## The concept, explained simply

An HTTP request is a plain-text message with a strict shape, not a binary
blob or something exotic. If you've ever looked at an Unreal `.ini` config
file or a simple key-value save format, the shape will feel familiar: a
specific first line stating intent, followed by a block of key: value
pairs (headers — fully covered in Lesson 04), optionally followed by a
body. A response has the exact same shape, mirrored: a first line stating
the outcome, headers, then a body.

The **method** is the verb of the request — what the client is *asking the
server to do*. The **status code** is the three-digit number that's the
first word of the server's answer — a machine-readable "how did that go."
This lesson covers both in full.

## The details

### The request line

Every HTTP request's very first line has exactly this shape:

```
GET /api/v2/pokemon/pikachu HTTP/1.1
```

Three parts, space-separated: the **method** (`GET`), the **path** (the
part of the URL after the domain — Lesson 05 covers URLs fully), and the
**HTTP version** being used. You saw this exact line (well, its HTTP/2
form) fly past in Lesson 02's `curl -v` output, on the line starting with
`>`.

### The status line

The response's very first line mirrors it:

```
HTTP/1.1 200 OK
```

The HTTP version, then the three-digit **status code**, then a short
human-readable **reason phrase** (`OK` here — this text is only for human
convenience; code should always check the *number*, never parse this
text, since it's not guaranteed to match exactly across servers).

### HTTP methods, one at a time

Run each of these now, using `-i` (which prints response headers *and*
body, unlike plain `curl`, which prints body only) so you can see exactly
what each method actually does against a real, live API:

```bash
curl -i https://pokeapi.co/api/v2/pokemon/pikachu
```

**`GET`** — "give me this resource, don't change anything." This is by far
the most common method; every plain link you've ever clicked in a browser
issues a `GET`. **Expected:** `HTTP/1.1 200 OK` (or `HTTP/2 200`), followed
by headers, followed by a large JSON body describing Pikachu.

`GET` is **safe**: a formal term meaning *this method must not cause the
server to change anything*. A `GET` is "read-only" by contract — a client,
a browser prefetching links, or a search engine crawler should be able to
issue a `GET` at any resource with zero risk of side effects. This matters
in real systems: if you ever build an endpoint that, say, deletes a record
when visited with `GET`, you've broken this contract, and something as
innocent as a browser prefetching a link or a crawler indexing your site
could accidentally trigger deletions. `GET` is also **idempotent** — a
separate, related property meaning *making the exact same request multiple
times has the same effect as making it once*. Repeating `GET
/pokemon/pikachu` a hundred times still just returns Pikachu's data a
hundred times — nothing accumulates or changes because of the repetition.

**`POST`** — "here's data; do something with it, typically creating a new
resource." Unlike `GET`, `POST` is neither safe (it's explicitly allowed,
often expected, to change something on the server) nor idempotent by
default — submitting the same `POST` twice (e.g., "place this order")
could create two separate orders, not update the same one. PokeAPI is
read-only and doesn't accept `POST`, so instead, use the small HTTP-testing
service this module also uses for exactly this kind of deliberate
demonstration:

```bash
curl -i -X POST https://httpbingo.org/post -d "quest=slay the dragon"
```

**Line by line:** `-X POST` explicitly sets the method (without `-X`,
`curl` defaults to `GET`; `-d` (short for "data") both switches the method
to `POST` automatically *and* attaches the given text as the request
**body** — the first time you've deliberately sent a body rather than only
receiving one. **Expected:** `HTTP/1.1 200 OK`, and inside the JSON body, a
`"form"` field showing back `{"quest": ["slay the dragon"]}` — httpbingo.org's
`/post` endpoint exists specifically to *echo back* exactly what it
received, which makes it an excellent tool for seeing precisely what a
`curl` command actually sent, side by side with what you typed.

**`PUT`** — "replace this exact resource entirely with what I'm sending."
`PUT` *is* idempotent: sending the exact same `PUT` twice should leave the
resource in the exact same final state both times (you're not "adding
another one," you're saying "this resource should now look exactly like
this," which produces the same end state no matter how many times you say
it).

```bash
curl -i -X PUT https://httpbingo.org/put -d "hp=100"
```

**`PATCH`** — "apply a partial update to this resource" (change just one
field, rather than replacing the whole thing, which is what `PUT` implies).
`PATCH` is **not** guaranteed idempotent in general (e.g., "increment this
counter by 1" is a perfectly valid `PATCH` semantically, and repeating it
twice deliberately produces a *different* result each time) — though many
real-world `PATCH` endpoints are written to behave idempotently anyway
(e.g., "set this field to exactly this value" behaves idempotently even as
a `PATCH`). The honest rule: `PUT`'s *contract* guarantees idempotency;
`PATCH`'s does not, even though a specific `PATCH` implementation might
happen to behave that way.

```bash
curl -i -X PATCH https://httpbingo.org/patch -d "hp=50"
```

**`DELETE`** — "remove this resource." Idempotent by contract: deleting an
already-deleted resource should still (conceptually) result in "it's
gone" — repeating the request doesn't make it "more deleted."

```bash
curl -i -X DELETE https://httpbingo.org/delete
```

**`HEAD`** — identical to `GET`, except the server sends back only the
headers, never a body. Useful for cheaply checking things like "does this
resource exist, and how large is it" without downloading the whole thing.

```bash
curl -i -X HEAD https://pokeapi.co/api/v2/pokemon/pikachu
```

**Expected:** you'll see the exact same headers a `GET` would return, but
no JSON body at all afterward — proof `HEAD` really is "`GET`, minus the
body."

**`OPTIONS`** — "tell me what methods are actually allowed at this URL,
without doing any of them." You won't use this directly much yet, but it
becomes directly relevant in Module 07, where browsers issue automatic
`OPTIONS` requests ("preflight requests") as part of CORS — filed away for
now, defined properly then.

### Status codes, by category

Verified against **RFC 9110** ("HTTP Semantics," June 2022) — the current,
official specification that defines what every status code means. RFC 9110
superseded the older RFC 7231 and consolidated several other older HTTP
RFCs; if you ever see a tutorial citing "RFC 2616," know that it's citing a
document that's been formally obsolete for years — RFC 9110 is what to
trust.

The **first digit** of every status code tells you its category before
you even need to know the specific number:

- **1xx — Informational.** The request was received, processing continues.
  Rare to encounter directly; you can safely set these aside for now.
- **2xx — Success.** The request was received, understood, and accepted.
- **3xx — Redirection.** Further action (usually: go look somewhere else)
  is needed to complete the request.
- **4xx — Client Error.** The request itself has a problem — bad syntax,
  asking for something that doesn't exist, not allowed to do this. **This
  category means: you, the client, did something the server won't
  accept.**
- **5xx — Server Error.** The request was probably fine, but the server
  failed to fulfill it anyway. **This category means: the server broke,
  not you.**

This single distinction — is the first digit a `4` or a `5`? — is often the
very first thing a professional developer checks when something goes
wrong, because it immediately tells you *which side of the connection to
start debugging.*

**The specific codes you'll meet constantly:**

| Code | Meaning | Notes |
|---|---|---|
| `200 OK` | Generic success | The workhorse of `GET`/`PUT`/`PATCH` success |
| `201 Created` | Success, and a new resource now exists | Typical `POST` success response |
| `204 No Content` | Success, but there's deliberately no body | Common for a successful `DELETE` |
| `301 Moved Permanently` | This resource now lives at a new URL, permanently | Search engines update their records; future requests should use the new URL |
| `302 Found` | This resource is *temporarily* at a different URL | Don't update bookmarks/records — ask again next time |
| `304 Not Modified` | You already have the latest version cached — reuse it | Ties directly into caching headers, Lesson 04 |
| `400 Bad Request` | The request itself is malformed | E.g., broken JSON syntax in the body |
| `401 Unauthorized` | You must authenticate, and haven't (or your credentials are invalid) | Despite the name, this is really "unauthenticated" — Module 07 unpacks this properly |
| `403 Forbidden` | You *are* identified, but you're not allowed to do this | The key contrast with `401`: the server knows who you are and is refusing anyway |
| `404 Not Found` | Nothing exists at this path | The most famous status code in existence |
| `405 Method Not Allowed` | This path exists, but not for the method you used | E.g., `POST`-ing to a `GET`-only endpoint |
| `409 Conflict` | The request conflicts with the resource's current state | E.g., trying to create something that already exists |
| `422 Unprocessable Content` | Well-formed syntactically, but semantically invalid | You'll see this constantly once Pydantic validation arrives in Module 05 |
| `429 Too Many Requests` | You're being rate-limited | Slow down and/or retry later |
| `500 Internal Server Error` | The server hit an unhandled problem | The generic "something broke server-side" |
| `502 Bad Gateway` | A server acting as a go-between got an invalid response from the *next* server upstream | Common once reverse proxies appear in Module 09 |
| `503 Service Unavailable` | The server is temporarily unable to handle the request | Often deliberate — maintenance, overload |

You already met `200` in every earlier example. Now deliberately trigger a
few others:

```bash
curl -i https://pokeapi.co/api/v2/pokemon/not-a-real-pokemon
```

**Expected:** `HTTP/1.1 404 Not Found` (or the HTTP/2 equivalent — the
number is what matters), because no Pokémon by that name exists.
PokeAPI's own body for this even includes a small JSON error message,
which you can read directly.

```bash
curl -i https://httpbingo.org/status/500
```

**Expected:** `HTTP/1.1 500 Internal Server Error` — this specific
httpbingo.org path exists purely to let you deliberately request whatever
status code you want, for exactly this kind of learning/testing purpose
(try `/status/403`, `/status/301` yourself next).

Now trigger a real redirect, and see the two different ways `curl` can
handle one:

```bash
curl -i https://httpbingo.org/redirect/1
```

**Expected:**

```
HTTP/1.1 302 Found
location: /relative-redirect/0
```

By default, `curl` shows you the redirect response itself and stops —
exactly what the status line and `location` header say, with `curl`
making no decision of its own about what to do next. Add `-L` ("follow
redirects, if any status code says to") to make `curl` behave the way a
browser normally would — automatically re-requesting whatever URL the
`location` header points to, as many times as necessary, until it reaches
a final, non-redirect response:

```bash
curl -i -L https://httpbingo.org/redirect/1
```

**Expected:** you'll see the `302`/`location` pair fly past, followed
immediately by a second, full response — this time a `200 OK` with a real
JSON body — because `-L` chased the redirect for you instead of stopping
at the first response. Whether to use `-L` matters: without it, you're
inspecting exactly what one specific server response contains; with it,
you're reproducing what an end user's browser would actually end up
seeing after every hop.

**Try it yourself:** before running it, predict what
`curl -i https://httpbingo.org/status/204` will show in its body, given
what `204` means above. Run it and confirm. (You should see headers, then
literally nothing after them — `204` explicitly means "success, and I'm
telling you upfront there is no body coming," which is different from a
`200` that merely happens to have an empty body.)

## Common mistakes & gotchas

- **Using `GET` for anything that changes data.** Breaks the "safe method"
  contract; caching layers, browsers, and crawlers all assume `GET` is
  side-effect-free and may re-issue it without warning.
- **Treating `401` and `403` as interchangeable.** `401` = "I don't know
  who you are (or your credentials are invalid) — authenticate." `403` =
  "I know exactly who you are, and the answer is still no." Confusing
  these in your own API's design leaks information about *why* something
  failed incorrectly.
- **Assuming `PATCH` is always idempotent just because it "sounds like"
  `PUT`.** It isn't, by contract — only check idempotency claims against a
  specific API's actual documented behavior, not the method name alone.
- **Panicking at a `4xx`/`5xx` without checking which digit.** A `404` means
  you (the client) asked for something that doesn't exist — check your
  URL/path first. A `500` means the *server* broke — your request may have
  been perfectly correct; there's nothing to fix on your end except maybe
  retrying later or reporting the bug.
- **Citing "RFC 2616" as the current HTTP spec.** It's obsolete; RFC 9110
  (plus its companions RFC 9111–9114 for caching and version-specific
  syntax) is current as of this lesson's verification date.

## How this connects

You now know exactly what's on the request line and status line — the
"headline" of every HTTP message. Lesson 04 opens up everything *around*
those lines: headers (the key:value metadata riding alongside them) and
cookies, plus the crucial concept of statelessness that headers and
cookies exist partly to work around.

## Quick self-check

1. What's the difference between "safe" and "idempotent," and which
   methods have each property?
2. You get a `403` from an API. Does that mean you're not logged in, or
   something else? Contrast with `401`.
3. Why might a well-designed API return `422` instead of `400` for a
   request whose JSON is syntactically valid but has, say, a negative
   number in a field that must be positive?
4. If a request fails with a `5xx`, whose "fault" is it, structurally —
   and does that change what you should try next compared to a `4xx`?
5. What's the actual difference between `HEAD` and `GET`?
