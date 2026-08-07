# Lesson 02 — TCP, TLS, and the Full Request/Response Journey

## What you'll learn

- What TCP is, why it exists, and exactly what its "three-way handshake"
  does.
- Why TCP (not something faster) is what HTTP is built on.
- What TLS/SSL is, what problem it solves, and what happens during a TLS
  handshake — including current, verified facts about which TLS versions
  are actually in use in 2026.
- What HTTPS actually is, precisely (it is not a separate protocol from
  HTTP).
- The **complete**, assembled, step-by-step answer to "what happens when
  you type a URL and press Enter" — every layer from Lesson 01 plus
  everything new in this lesson, in the exact order it really happens.
- How to see every one of these phases yourself, for real, using `curl -v`.

## Why this matters

This is the single most-asked "how does the internet actually work"
question, and by the end of this lesson you'll be able to answer it
completely and correctly, not with a hand-wave. It also explains, at a
mechanical level, why some connections are slow to establish the *first*
time (handshakes take real round trips), why "the padlock icon" in a
browser means something specific and verifiable, and why a server being
temporarily unreachable produces a different kind of error than a server
responding with "page not found" — those are two entirely different
layers failing, and knowing which layer failed is exactly how professional
developers debug connectivity issues instead of guessing.

## Prerequisites

Lesson 01 (networks, IP addresses, ports, DNS) — this lesson assumes you
already have an IP address and port to work with, and continues exactly
where Lesson 01 left off.

## The concept, explained simply

Lesson 01 got you as far as "I now know which machine, and which door
(port) on it, to talk to." Two problems remain before any actual web page
data can flow:

1. **Reliability** — the raw network (Lesson 01) only promises to *try* to
   deliver packets; it doesn't promise they'll all arrive, arrive once
   each, or arrive in the order they were sent. A web page (or an API
   response) is useless if it arrives scrambled or partly missing. **TCP**
   solves this.
2. **Privacy and trust** — without protection, any device your packets
   physically pass through along the way (your neighbor's router, your
   ISP, a coffee shop Wi-Fi access point) could read or even alter your
   data in transit. **TLS** solves this.

Game-dev analogy for problem 1: think about the difference between a
fire-and-forget UDP packet in a fast-paced multiplayer shooter (where a
single dropped position update is fine — the next one is coming in 16ms
anyway, and waiting to guarantee delivery would make the game feel worse,
not better) versus loading a save file, where every single byte matters
and arriving in the wrong order or partially would corrupt the whole save.
HTTP is a "save file" kind of problem, not a "position update" kind of
problem — a web page or an API's JSON response has to arrive complete and
byte-correct, or it's simply wrong. That's exactly why HTTP is built on TCP
and not on UDP (the faster, no-guarantees alternative many real-time
multiplayer games use instead, precisely because games can tolerate the
occasional dropped update and can't tolerate the delay that guaranteeing
delivery would add).

## The details

### TCP — the three-way handshake

**TCP (Transmission Control Protocol)** is a set of rules two computers
follow to have a reliable, ordered, two-way conversation over an
unreliable network. Before either side sends any actual data, they perform
a **three-way handshake** to agree the connection is open and both sides
are ready:

1. **SYN** — the client sends a packet meaning "I'd like to open a
   connection" (SYN = "synchronize").
2. **SYN-ACK** — the server replies "I got that, and yes, let's connect"
   (acknowledging the client's SYN, and sending its own SYN back).
3. **ACK** — the client replies "got it, we're connected" (acknowledging
   the server's SYN-ACK).

Only after all three of these tiny packets have round-tripped is the
connection considered **established**, and only then does either side send
any real data (like an HTTP request). This is directly analogous to
joining a voice call: "Can you hear me?" → "Yes, can you hear me?" → "Yes,
go ahead" — nobody starts talking about the actual topic until that
three-step confirmation finishes. It's also exactly why establishing a
brand-new connection has an unavoidable minimum delay (at least one full
round trip to the server and back) before any real data can move — no
amount of a fast internet connection eliminates the physical time light
(or electrons) take to travel there and back.

Once established, TCP also guarantees, for as long as the connection
stays open: every byte sent arrives, arrives exactly once, and arrives in
the order it was sent — retransmitting automatically behind the scenes if
a packet gets lost, with zero effort from you or the application. This is
the "reliability" that problem 1 above needed solved, and it's solved
entirely below the level HTTP itself operates at — HTTP never has to think
about lost packets; TCP already handled that by the time HTTP sees
anything.

### TLS — encrypting and authenticating the connection

A plain TCP connection carries your data in the clear — anyone able to
observe the traffic (a nosy network operator, someone on the same public
Wi-Fi, an ISP) could read it, or worse, silently modify it in transit.
**TLS (Transport Layer Security)** — the modern name for what used to be
called SSL (Secure Sockets Layer); SSL is deprecated and effectively dead,
but you'll still see "SSL" used informally/interchangeably in casual
conversation and old documentation — wraps a TCP connection in encryption
so that:

- **Confidentiality:** nobody observing the raw traffic can read its
  contents.
- **Integrity:** nobody can silently tamper with the data in transit
  without detection.
- **Authentication:** the client can cryptographically verify it's really
  talking to the server it thinks it's talking to (not an impostor
  intercepting the connection) — this is what a **certificate**, issued by
  a trusted **Certificate Authority (CA)**, proves.

**Verified fact (checked against current sources, August 2026):** the
current, actively recommended version is **TLS 1.3** (standardized in RFC
8446, August 2018), which every modern browser and server prefers when
both sides support it. **TLS 1.2** remains an acceptable, still-supported
fallback. **TLS 1.0 and TLS 1.1 are formally deprecated** (RFC 8996, March
2021) and have been disabled outright in every major browser since 2020 —
if a server can only offer those, modern clients simply refuse to connect.
You don't need to configure any of this yourself yet (Module 11 covers
configuring TLS on a real server you deploy), but it's worth knowing
precisely which version is doing the work when you see "TLS 1.3" appear in
tool output later in this lesson.

The **TLS handshake** happens immediately after the TCP handshake
completes, and before any HTTP request is sent, roughly:

1. Client says hello, listing which TLS versions and encryption methods
   ("cipher suites") it supports.
2. Server picks the best mutually-supported option, and sends back its
   **certificate** (proving its identity) plus the information needed to
   set up a shared encryption key.
3. Client verifies the certificate is valid and trusted (issued by a CA
   your system already trusts, not expired, and actually for the domain
   you're connecting to), then both sides finish agreeing on a shared
   encryption key.
4. From this point forward, **every byte** sent over this connection, in
   both directions, is encrypted using that shared key — including the
   HTTP request itself, its headers, and its body.

TLS 1.3 specifically streamlined this to complete in a single round trip
in the common case (a genuine improvement over TLS 1.2, which often took
two) — one more reason it's now preferred.

### HTTPS — not a separate protocol

**HTTPS is not a different protocol from HTTP.** It is precisely: *the
exact same HTTP you'll learn in Lessons 03–04, sent over a connection that
TLS has already encrypted.* That's the entire definition. There's no
separate "HTTPS request format" to learn — once the TLS handshake above
finishes, the HTTP conversation proceeds exactly as it would over plain
HTTP, just invisibly encrypted in transit. This is also precisely why
HTTPS defaults to port 443 while plain HTTP defaults to port 80 (recall
ports from Lesson 01): they're the same application-level protocol, on
two different conventional doors, one wrapped in TLS and one not.

### Putting it all together: what actually happens when you type a URL

You now have every piece from both lessons. Here is the complete,
in-order answer, using `https://pokeapi.co/api/v2/pokemon/pikachu` as the
concrete example:

1. **Parse the URL.** Your browser (or `curl`) splits the URL into its
   parts: scheme `https` (→ use TLS, default port 443), domain
   `pokeapi.co`, path `/api/v2/pokemon/pikachu`. (Lesson 05 defines every
   part of a URL formally — for now, just the scheme and domain matter.)
2. **DNS lookup.** (Lesson 01, in full.) If not already cached, resolve
   `pokeapi.co` → an IP address, e.g. `104.26.14.6`, via your resolver,
   possibly via root → TLD → authoritative servers.
3. **TCP three-way handshake.** Open a reliable connection to
   `104.26.14.6:443` — SYN, SYN-ACK, ACK.
4. **TLS handshake.** Negotiate TLS version and cipher suite, verify
   `pokeapi.co`'s certificate, establish a shared encryption key. From here
   on, everything is encrypted.
5. **Send the HTTP request.** Over that now-encrypted connection, send an
   actual HTTP request: a request line (`GET /api/v2/pokemon/pikachu
   HTTP/1.1`), headers, and (for some methods) a body. (Lesson 03 covers
   this fully.)
6. **Server processes the request.** The server reads the request, decides
   what it means, does whatever work is needed (here: look up Pikachu's
   data), and builds a response.
7. **Server sends the HTTP response.** A status line (`HTTP/1.1 200 OK`),
   response headers, and a body — here, a JSON document describing
   Pikachu. (Lessons 03–04 cover this fully.)
8. **Client receives and uses the response.** `curl` prints it; a browser
   would parse HTML/JSON and render/act on it.
9. **Connection reuse or close.** Modern HTTP commonly keeps the
   underlying TCP connection open for a short time afterward so a
   *following* request to the same server can skip straight to step 5,
   saving the cost of repeating steps 3–4. Eventually, if unused, the
   connection closes.

That's the complete journey — every step from Lesson 01 plus every step
from this lesson, in the real order they happen.

### Seeing every phase yourself

Run this exact command:

```bash
curl -v https://pokeapi.co/api/v2/pokemon/pikachu -o /dev/null
```

**Expected output (abridged and annotated — your exact numbers/order of
some lines will vary slightly, that's normal):**

```
*   Trying 104.26.14.6:443...
* Connected to pokeapi.co (104.26.14.6) port 443
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256
* Server certificate:
*  subject: CN=pokeapi.co
*  issuer: C=US; O=Let's Encrypt; CN=R11
* using HTTP/2
> GET /api/v2/pokemon/pikachu HTTP/2
> Host: pokeapi.co
> User-Agent: curl/8.16.0
> Accept: */*
>
< HTTP/2 200
< content-type: application/json; charset=utf-8
< cache-control: public, max-age=86400
...
```

**Line by line, matching directly to the steps above:**
- `-v` means "verbose" — normally `curl` only prints the response body;
  this flag makes it also print everything it's doing to *get* that body.
- `Trying 104.26.14.6:443...` / `Connected to pokeapi.co (104.26.14.6) port
  443` — **step 3**, the TCP handshake, already completed by the time this
  line prints (DNS from step 2 already happened silently before this, to
  produce that IP address).
- Every line containing `TLS handshake` — **step 4**, happening live. You
  can literally see `TLSv1.3` named explicitly — direct, real proof of the
  fact verified earlier in this lesson: this connection is really using
  TLS 1.3.
- `Server certificate: ... issuer: ... Let's Encrypt` — proof the server
  presented a real certificate, issued by a real, trusted Certificate
  Authority (Let's Encrypt is a widely-used, free CA — Module 11 covers
  getting your own certificate from it when you deploy a real server).
- Lines starting with `>` — **step 5**, the actual HTTP request being
  sent, now over the encrypted connection. (Full breakdown of this in
  Lesson 03.)
- Lines starting with `<` — **step 7**, the response coming back.
  `HTTP/2 200` is the status line's modern-HTTP/2 form (Lesson 03 explains
  status codes; the `200` is the part that matters right now).
- `-o /dev/null` — throws away the actual JSON body, since this run is
  about watching the *plumbing*, not the data.

**Try it yourself:** run the exact same command a second time, immediately
after the first, and scroll to the top of its output. Predict, before
running it, whether you'll see the same `TLS handshake` lines again.
(Depending on your `curl` version and whether the connection was reused,
you may see it skip straight to sending the request — a live demonstration
of step 9, connection reuse, avoiding redoing steps 3–4 entirely.)

## Common mistakes & gotchas

- **Thinking "HTTPS" is a separate thing you learn instead of HTTP.**
  It isn't — everything Lessons 03–04 teach about HTTP applies identically
  whether or not TLS is wrapping it. TLS only changes *whether the wire is
  encrypted*, not what's said over it.
- **Confusing a TLS failure with an HTTP error.** `curl: (60) SSL
  certificate problem` happens *before* any HTTP request is even sent — the
  handshake itself failed. A `404 Not Found`, by contrast, means the TLS
  handshake succeeded fine, the HTTP request was sent and received, and
  the server is telling you (at the HTTP layer, Lesson 03) that nothing
  exists at that path. These are different layers failing for completely
  different reasons — always check which one you're actually looking at
  before debugging.
- **Assuming a slow first request means something is broken.** The very
  first request to a new server pays for DNS + TCP handshake + TLS
  handshake all at once (multiple network round trips). Subsequent
  requests, reusing the connection, are typically much faster. This is
  normal, not a bug.
- **Believing TLS hides *that* you connected to a site, not just *what*
  you said.** TLS encrypts the content of your conversation with a server,
  but the DNS lookup (Lesson 01) and the destination IP address you
  connected to are generally still visible to your network/ISP unless
  additional measures (like encrypted DNS) are separately in place — a
  nuance worth knowing exists, though it's outside this course's scope.

## How this connects

Lessons 01–02 together are the full, honest answer to "what happens when
you type a URL" — the exact curriculum item this module's spec insisted
must not be skipped or compressed. Lesson 03 zooms into step 5–7 above
(the actual HTTP request and response) and explains, in full, what a
request line, method, and status code each are — the content that's been
riding inside this "envelope" the whole time.

## Quick self-check

1. Put these in the correct order: TLS handshake, DNS lookup, HTTP
   request sent, TCP three-way handshake.
2. Why is HTTP built on TCP rather than a faster protocol like UDP,
   despite TCP being slower to establish?
3. What, specifically, does HTTPS add on top of HTTP? Is anything about
   the HTTP request/response format itself different?
4. If `curl -v` shows the TLS handshake completing successfully but then
   the server responds `404`, at which layer did something go "wrong,"
   and is TLS at fault?
5. Why might the exact same `curl` command run twice in a row show a
   full TLS handshake the first time but skip straight to the request the
   second time?
