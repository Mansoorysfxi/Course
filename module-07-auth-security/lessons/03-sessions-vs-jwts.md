# Lesson 03 — Sessions vs. JWTs: Two Ways to Stay Logged In

## What you'll learn

- The problem both approaches solve: HTTP is stateless (Module 02), so *something* has to remind the server, on every single request, who you are.
- How **session-based** authentication works: a server-side record plus a session-id cookie.
- How **token-based** authentication (JWTs specifically) works: a self-contained, signed piece of data the client holds instead.
- A genuine, side-by-side comparison — the real trade-offs, not "JWTs are just better."
- Why QuestLog uses a JWT, specifically, and where that JWT actually lives in this app (a plain `Authorization` header, not a cookie).

## Why this matters

Module 02 taught you, from first principles, that **HTTP is stateless** —
every request arrives at the server with no built-in memory of any
previous request. A logged-in user making their tenth request in a row
looks, to a bare HTTP server, exactly as anonymous as their first one,
unless *something* in the request itself carries proof of who they are.
This lesson is about the two dominant, genuinely different answers to
"what should that something be" — an architectural decision every real
backend has to make, and one this course's `RUNNING_PROJECT.md` already
committed to (JWT) for reasons this lesson finally justifies in full.

## Prerequisites

Module 02's Lesson 04 (headers, cookies, and statelessness — this lesson
assumes you already know what a **cookie** is and what "stateless" means).
Lesson 01 (authentication vocabulary) and Lesson 02 (password hashing —
both sessions and JWTs pick up *after* a password has already been
verified once).

## The concept, explained simply

Think back to Module 02's cookie lesson, and the "stateless" problem it
described: a web server, by default, treats every request like a
stranger it's never met, even if the exact same browser sent a request
ten seconds ago. Something has to bridge that gap. Two fundamentally
different strategies exist:

- **Sessions**: after a successful login, the server creates a record —
  "user 42 is logged in" — and keeps that record itself, in its own
  memory or database. It hands the browser back a small, random,
  meaningless-looking id (a **session id**) via a cookie. On every future
  request, the browser automatically resends that cookie (Module 02's own
  cookie mechanics), and the server looks the id up in its own
  session-record store to figure out who's making the request. The
  session id itself proves nothing on its own — it's just a lookup key;
  all the *real* information ("who is this, are they still logged in")
  lives server-side.
- **Tokens (JWTs)**: after a successful login, the server creates a
  self-contained package of information — "this is user 42, issued at
  this time, expires at that time" — and cryptographically **signs** it
  (Lesson 04 explains exactly how), then hands the *entire signed package*
  to the client. The server keeps **no record of this at all**. On every
  future request, the client sends the whole token back, and the server
  simply re-checks the signature — if it's valid, the server trusts every
  claim inside the token, without looking anything up anywhere.

The one-sentence version: **a session id is a claim check for
information the server is still holding; a JWT is the information
itself, sealed so it can't be tampered with.**

## The details

### Session-based auth, step by step

1. User submits email + password to a login endpoint.
2. Server verifies the password (Lesson 02's `verify_password`).
3. Server creates a new row in a **session store** (often a database
   table, or a fast key-value store like Redis — Module 06's own NoSQL
   overview lesson already introduced Redis for exactly this kind of job)
   recording "session id `xyz789` belongs to user 42."
4. Server responds with `Set-Cookie: session_id=xyz789; HttpOnly` (Module
   02's cookie mechanics).
5. Every future request from that browser automatically includes
   `Cookie: session_id=xyz789`.
6. The server looks `xyz789` up in its session store on *every single
   request* to find out who's making it.
7. Logging out is simple and immediate: delete that one row from the
   session store. The cookie itself becomes useless instantly, everywhere,
   the moment that row is gone.

### Token-based (JWT) auth, step by step — QuestLog's actual approach

1. User submits email + password to `POST /api/auth/login`.
2. Server verifies the password (`app/security.py`'s `verify_password`).
3. Server builds a JWT containing the user's id and an expiry time, and
   **signs** it with a secret key only the server knows
   (`create_access_token`, Lesson 04).
4. Server responds with `{"access_token": "eyJ...", "token_type": "bearer"}`
   — a JSON body, not a cookie.
5. The frontend stores this token itself (QuestLog stores it in the
   browser's `localStorage` — `src/api/http.ts`'s `setStoredToken`) and
   attaches it manually to every future request, as an
   `Authorization: Bearer eyJ...` header (`src/api/http.ts`'s `request()`).
6. The server, on every request, **re-verifies the signature** (Lesson
   04's `decode_access_token`) — no database lookup, no session store,
   nothing to check against except the token itself and the server's own
   secret key.
7. Logging out (QuestLog's `AuthContext.tsx`'s `logout`) simply deletes
   the token from `localStorage`. The server never "invalidates" it —
   it's mathematically still a perfectly valid, correctly signed token
   until its `exp` claim passes on its own. This is the single biggest,
   genuinely real trade-off of the JWT approach — see below.

### A real, honest comparison

| | Sessions | JWTs |
|---|---|---|
| Where's the "truth" about who's logged in? | Server-side (a database/session store) | Client-side (inside the signed token itself) |
| Per-request server work | A lookup (database or cache read) | Just a signature check — no lookup at all |
| Scales across multiple backend servers? | Needs a *shared* session store every server can reach (e.g. Redis) | Trivial — any server holding the same secret key can verify any token, independently, with no shared state |
| Instant logout / instant revocation | Easy — delete the session record | Genuinely hard — the token stays valid until it naturally expires, unless you build extra infrastructure (a "blocklist" of revoked tokens, which reintroduces a server-side lookup and gives up the main advantage) |
| What if the secret key leaks? | Session ids are meaningless without the store; leaking one id only exposes one session | Catastrophic — anyone with the key can forge a token claiming to be *any* user, instantly, undetectably |
| Typical transport | An `HttpOnly` cookie the browser manages automatically | Commonly a manually-set `Authorization` header (this app), sometimes a cookie |

### Why QuestLog uses a JWT

`RUNNING_PROJECT.md` fixed this decision before this module was written,
and the comparison above explains why it's a reasonable choice for this
app specifically: QuestLog's backend is a single, simple process with no
need to scale across multiple servers sharing session state, so the
"needs a shared session store" downside of sessions doesn't even apply
here — but the JWT approach is what real, modern APIs (especially ones
meant to be called by multiple different clients — a web app, a mobile
app, another service) overwhelmingly reach for today, and it's the
approach this course's later modules (13+, building an AI-powered
feature that calls this same API) will assume. The "hard to revoke
instantly" trade-off is accepted here deliberately, mitigated by keeping
`ACCESS_TOKEN_EXPIRE_MINUTES` short (60 minutes, `app/config.py`) — a
stolen token is only useful for at most an hour, not forever.

### Where QuestLog's token actually lives, and why not a cookie

QuestLog stores its JWT in the browser's `localStorage`
(`src/api/http.ts`) and attaches it manually via JavaScript on every
`fetch()` call, rather than letting the browser manage it automatically
via a cookie. This is a genuine, debatable design choice, not a free
lunch either way:

- A JWT in `localStorage`, read by JavaScript to set a header, is
  vulnerable to **XSS** (Lesson 09) — if an attacker ever gets malicious
  JavaScript running on this app's page, that script can read
  `localStorage` directly and steal the token.
- A JWT in an `HttpOnly` cookie is *invisible* to JavaScript entirely
  (that's what `HttpOnly` means), which closes that specific hole — but
  cookies are sent **automatically** by the browser on every request to
  the matching domain, which opens the door to **CSRF** (also Lesson 09)
  instead, a different attack this app's header-based approach happens to
  sidestep for free (Lesson 09 explains exactly why).

QuestLog picks the `localStorage` + manual header approach because it's
the simpler, more common pattern for a JWT-based API specifically (as
opposed to a session-cookie-based one), and because Lesson 09 teaches
real, concrete defenses against XSS regardless of where a token lives.
This is exactly the kind of "no perfect answer, only trade-offs" decision
real engineering involves — Lesson 09 revisits both attacks with the
full picture once you've seen how each one actually works.

## Common mistakes & gotchas

- **Thinking "JWT" means "encrypted."** It doesn't — Lesson 04 covers this
  in full, but the short version: a JWT's contents are trivially readable
  by anyone, including its own user. It's *signed* (tamper-proof), not
  *encrypted* (secret). Never put anything genuinely sensitive (a
  password, a credit card number) inside a JWT's payload.
- **Believing "logging out" a JWT-based app actually invalidates the
  token server-side.** It doesn't, in this app's design — it only removes
  the token from where the *frontend* was keeping it. The token itself
  remains valid, in principle, until it expires, if someone had a copy of
  it. This is the direct, real-world consequence of the "hard to revoke"
  row in the comparison table above, not a bug.
- **Mixing up "stateless" (HTTP itself) with "stateless" (this app's
  auth strategy).** They're related but distinct: HTTP has always been
  stateless (Module 02); a session-based app builds *statefulness* back
  in via a server-side store. A JWT-based app, like this one, stays
  architecturally stateless even for authentication — the server holds
  no session state to keep in sync across requests or servers at all.

## How this connects

Lesson 01 named authentication as a concept; this lesson names the two
real mechanisms for *staying* authenticated across multiple requests, and
commits QuestLog to one of them. Lesson 04 opens up exactly what's inside
a JWT and how the signature that makes this whole scheme trustworthy
actually works; Lesson 06 is where `create_access_token` and
`decode_access_token` (Lesson 02's password verification's natural next
step) get wired into real `/api/auth` routes.

## Quick self-check

1. In one sentence each: what does a session id actually contain, and what does a JWT actually contain?
2. Why does a session-based system need a shared session store to scale across multiple backend servers, while a JWT-based system doesn't?
3. What is the real, concrete downside of JWTs around "logging out," and how does QuestLog mitigate it (without solving it completely)?
4. Why would leaking a JWT-signing secret key be more catastrophic than leaking one session id from a session store?
5. Where does QuestLog's frontend store its JWT, and what real trade-off does that specific choice make (compared to a cookie)?
