# Lesson 04 — Headers, Cookies, and Statelessness

## What you'll learn

- What an HTTP header is, precisely, and the specific headers you'll see
  constantly in real work.
- What a cookie is, exactly how it gets set and sent back, and the
  attributes that control its behavior.
- What "HTTP is stateless" actually means, why the protocol was designed
  that way on purpose, and how cookies (and later, tokens) work around it.

## Why this matters

Headers are where almost all of the *interesting* metadata in a real
request/response lives — content type, caching rules, authentication,
rate-limit information. You'll be reading and setting headers constantly
starting with your own FastAPI backend in Module 05, and CORS (Module 07)
is, mechanically, entirely a story about headers. Statelessness is one of
those ideas that seems abstract until the exact moment you build a login
system and discover the server has no idea who you are between two
requests unless you deliberately did something about it — that "something"
is what this lesson teaches.

## Prerequisites

Lesson 03 (methods and status codes) — headers sit in the same
request/response messages you already know the request/status lines of.

## The concept, explained simply

A **header** is a single line of the form `Name: Value`, sitting between
the request/status line and the body. If the request/status line is the
"headline," headers are the fine-print metadata — not the main content
itself, but facts *about* that content or the request: what format the
body is in, how big it is, who's asking, what's allowed to be cached, and
so on. You've already seen dozens fly past in `curl -v`/`curl -i` output in
the last two lessons without a full explanation — this lesson gives you
one.

**Statelessness** is a design decision: by default, an HTTP server treats
every single request as a completely fresh event, with zero memory of any
previous request — even one that arrived one second earlier from the exact
same client. Think of a vending machine: every transaction is entirely
self-contained. It doesn't remember that you bought a soda five minutes
ago, doesn't build a running relationship with you, and doesn't need to —
each coin-insert-and-press-button is a complete transaction on its own.
Plain HTTP is exactly this deliberately "forgetful" by design, and the
rest of this lesson explains both *why* and what to do when you genuinely
need the server to remember something about you across requests.

## The details

### Common request headers

Run this again, paying attention only to the lines starting with `>` (the
request being sent):

```bash
curl -v https://pokeapi.co/api/v2/pokemon/pikachu -o /dev/null 2>&1 | grep '^>'
```

**Expected output:**

```
> GET /api/v2/pokemon/pikachu HTTP/2
> Host: pokeapi.co
> User-Agent: curl/8.16.0
> Accept: */*
```

**Line by line:**
- `Host` — which domain you're talking to. This matters more than it might
  look: a single server (one IP address, one port) can host *many
  different domains* simultaneously, so the server needs `Host` to know
  which one you actually meant. Without it, a server hosting both
  `siteA.com` and `siteB.com` on the same machine couldn't tell them apart.
- `User-Agent` — identifies *what software* is making the request (here,
  which exact `curl` version). Browsers send long, historically-baroque
  `User-Agent` strings identifying the browser and OS; servers can use this
  to serve different content to different clients (occasionally useful,
  occasionally abused).
- `Accept` — tells the server which response body formats the client can
  understand (`*/*` here means "anything, I don't care" — `curl`'s
  default). A browser requesting a web page might send
  `Accept: text/html,application/xhtml+xml,...` instead.

Add one more header yourself, using `-H`:

```bash
curl -i -H "Accept: application/json" https://pokeapi.co/api/v2/pokemon/pikachu -o /dev/null -D -
```

**Line by line:** `-H "Accept: application/json"` adds that exact header
to the outgoing request, explicitly (rather than relying on `curl`'s
default `*/*`). `-D -` ("dump headers to stdout") prints just the response
headers (paired here with `-o /dev/null` to suppress the body, since we
only care about headers in this specific example).

### Common response headers

Look at the response side now:

```bash
curl -i https://pokeapi.co/api/v2/pokemon/pikachu -o /dev/null -D -
```

**Expected output (abridged):**

```
HTTP/2 200
content-type: application/json; charset=utf-8
content-length: 39234
cache-control: public, max-age=86400
date: Tue, 12 Aug 2026 09:14:02 GMT
server: cloudflare
```

- **`Content-Type`** — states exactly what format the body is in. Here,
  `application/json` tells the client "parse this body as JSON" (Lesson 05
  covers JSON itself in full) — without this header, a client would have
  to *guess* the format, which is fragile and error-prone. You will set
  this header explicitly, constantly, once you're writing your own API
  responses starting in Module 05.
- **`Content-Length`** — the body's exact size in bytes, letting the
  client know precisely how much data to expect and when the body is fully
  received.
- **`Cache-Control`** — instructions about whether, and for how long, a
  client is allowed to reuse this exact response instead of asking again.
  `max-age=86400` means "this is good for 86,400 seconds (24 hours) — don't
  bother re-fetching it before then." This directly enables the `304 Not
  Modified` status code from Lesson 03: a client can ask "has this
  changed since I last got it?" and the server can cheaply answer "nope,
  reuse what you have" without resending the whole body.
- **`Date`** — when the server generated this response.
- **`Server`** — identifies the server software (here, Cloudflare, a
  service that sits in front of many websites — you'll learn exactly what
  that architecture is for, "reverse proxies," in Module 09).

**Try it yourself:** run the same command against `https://httpbingo.org/get`
instead and compare its response headers to PokeAPI's. You should notice
different values for `Server` and no `Cache-Control` at all — a live
demonstration that headers aren't fixed by HTTP itself; every server
chooses which ones to send and what to put in them.

### Cookies

A **cookie** is a small piece of data a server asks the client to store
and automatically send back on every future request to that same site.
The mechanism is two headers working as a pair:

- **`Set-Cookie`** (response header) — the server's way of saying "please
  remember this."
- **`Cookie`** (request header) — the client's way of sending back
  whatever it was told to remember, on every subsequent request to that
  site.

Try this using `curl`'s cookie-jar flags, which mimic exactly what a real
browser does automatically:

```bash
curl -i -c cookies.txt "https://httpbingo.org/cookies/set?quest=slay-the-dragon"
```

**Expected:** among the response headers, a line like:

```
set-cookie: quest=slay-the-dragon; Path=/
```

**Line by line:** `-c cookies.txt` tells `curl` "save any cookies you're
given into this file" (a **cookie jar** — the same term browsers use
internally). The request itself hits httpbingo.org's `/cookies/set`
endpoint, built specifically to respond by setting whatever cookie you
asked for in the query string (`?quest=slay-the-dragon` — query strings
are covered fully in Lesson 05).

Now make a *second*, separate request, this time reading the jar back:

```bash
curl -i -b cookies.txt https://httpbingo.org/cookies
```

**Expected:** the JSON response body shows `{"quest": "slay-the-dragon"}`
— the server received your cookie back and is echoing what it saw.
**Line by line:** `-b cookies.txt` ("load cookies from this jar") makes
`curl` attach a `Cookie: quest=slay-the-dragon` header to this request,
exactly the way a browser automatically attaches every cookie it's
holding for a domain, on every request to that domain, with zero manual
effort from a web page's JavaScript.

**Cookie attributes** (set alongside a cookie's value in `Set-Cookie`,
controlling its behavior):

- **`Expires`/`Max-Age`** — when the cookie should be deleted automatically.
  Without either, a cookie is a **session cookie** — deleted when the
  browser fully closes.
- **`Domain`/`Path`** — scopes exactly which site/paths the cookie gets
  sent back to.
- **`Secure`** — only ever send this cookie over HTTPS, never plain HTTP.
- **`HttpOnly`** — JavaScript running on the page can't read this cookie at
  all (only the browser's own HTTP layer can see/send it) — a real
  security measure against a category of attack (script maliciously
  stealing cookies) that Module 07 covers properly.
- **`SameSite`** — controls whether this cookie gets sent along with
  requests originating from a *different* site (relevant to the CSRF
  attacks Module 07 covers).

You don't need to configure any of these yourself yet — recognizing them
by name and knowing roughly what each does is the goal here; Module 07
puts them to real use once you build actual login sessions.

### Statelessness, precisely

Now the payoff. Run this:

```bash
curl -i https://pokeapi.co/api/v2/pokemon/pikachu -o /dev/null
curl -i https://pokeapi.co/api/v2/pokemon/pikachu -o /dev/null
```

Two separate requests, one after another, to the exact same URL.
**Nothing about the second request "knows" the first one happened** —
same headers, same response, no memory carried over at the HTTP level.
This is what **"HTTP is stateless"** means, formally: *the protocol itself
provides no built-in mechanism for a server to associate one request with
any previous request, unless the application deliberately adds one.*

**Why was HTTP designed this way on purpose?** Scalability. If a server
had to remember every client's ongoing "conversation" in its own memory,
that server would be permanently tied to whichever specific machine
served the first request — you couldn't freely spread incoming requests
across many interchangeable servers (load balancing, which Module 09
covers), because request #2 would *have* to land on the exact same
physical server that handled request #1, or the "memory" would be lost.
Stateless requests, by contrast, can be handled by *any* available
server, any time, since no request depends on another — a huge win once
you're running more than one server instance, which every production web
service eventually does.

**So how does a website "remember" you're logged in, then?** It doesn't,
at the HTTP level — the *application* built on top of HTTP adds memory
back deliberately, almost always using exactly the cookie mechanism you
just used by hand: the server sets a cookie (often containing a random,
meaningless-looking ID) once, on login; the browser automatically resends
that same cookie on every subsequent request; the server looks that ID up
in its own storage to recall "oh, this is the person who logged in
earlier." The *feeling* of a continuous, ongoing session is an illusion
built on top of a genuinely stateless protocol, using the exact mechanism
this lesson just showed you by hand with `-c`/`-b`. Module 07 builds this
for real, plus a newer alternative (JWTs) that avoids server-side storage
entirely — filed away for now, not needed yet.

## Common mistakes & gotchas

- **Assuming a server "remembers" a client without an explicit mechanism.**
  It doesn't, ever, at the HTTP level. If two requests need to be related,
  *something* (a cookie, a token, a session ID) has to carry that
  relationship explicitly — nothing does it for free.
- **Confusing `Cache-Control` (caching) with cookies (identity/state).**
  They're both headers, and both can affect what a browser "remembers,"
  but they solve completely different problems — one is about not
  re-fetching unchanged data, the other is about the server recognizing
  you across requests.
- **Forgetting to set `Content-Type` on a request with a body.** A server
  receiving a `POST`/`PUT` body with no (or a wrong) `Content-Type` may
  fail to parse it correctly, or parse it as the wrong format entirely —
  this becomes a very real, very common bug once you're calling your own
  FastAPI backend starting in Module 05.
- **Thinking `HttpOnly` cookies are invisible to the network, not just to
  JavaScript.** `HttpOnly` only blocks *page JavaScript* from reading the
  cookie — the browser still sends it over the wire on every request; it's
  a defense against one specific attack category (script-based theft), not
  a way to hide the cookie from the server or from network observation
  (which TLS, from Lesson 02, is what actually protects against).

## How this connects

You now understand every piece of the actual message riding inside the
TCP+TLS envelope: request/status lines (Lesson 03), headers, and cookies.
Lesson 05 steps back out to the bigger picture — what "client" and
"server" formally mean as roles, what an API is in general (not just a web
one), and what JSON — the format you've already been staring at in every
PokeAPI response body this whole module — actually is and why it became
the web's default data format.

## Quick self-check

1. What are the two headers involved in setting and then sending back a
   cookie, and which direction does each one travel?
2. In your own words, what does "HTTP is stateless" mean, and why was it
   designed that way rather than having servers remember clients
   automatically?
3. If a website keeps you "logged in" across many page loads, what
   mechanism is actually doing that work, given that HTTP itself has no
   memory?
4. What's the practical difference between what `Cache-Control` controls
   and what a cookie controls?
5. Why does a server need the `Host` header at all, if it already knows
   its own IP address and port?
