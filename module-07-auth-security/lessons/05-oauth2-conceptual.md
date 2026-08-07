# Lesson 05 — OAuth2, Conceptually: "Login with Google" Demystified

## What you'll learn

- What OAuth2 actually is: an **authorization** framework (not an authentication protocol, despite how it's usually used) for letting one application access resources on another's behalf, without ever handing over a password.
- The four roles OAuth2 defines, and what each one actually does.
- The most common real-world flow ("Authorization Code" flow) explained click by click, using a "Login with Google" button as the running example.
- What a **scope**, an **access token**, and a **refresh token** are in this context.
- Exactly which piece of OAuth2's *shape* QuestLog's own login endpoint borrows, and why QuestLog does **not** actually implement OAuth2 with a third party at all.

## Why this matters

You have clicked a "Sign in with Google" or "Continue with GitHub" button
dozens of times. This lesson opens up exactly what happens in the few
seconds between that click and landing back on the original site, already
logged in — a process that looks like magic and is, in fact, a very
specific, well-defined sequence of redirects and HTTP requests. This
lesson is explicitly **conceptual** — QuestLog itself never talks to
Google, GitHub, or any other third party; it has its own email+password
login (Lesson 06). Understanding OAuth2 anyway matters because it's one
of the most common real-world patterns you'll integrate with as a
working full-stack engineer, and because FastAPI's own security tools
(`OAuth2PasswordBearer`, `OAuth2PasswordRequestForm`, both used in
Lesson 06/07) are explicitly modeled on OAuth2's vocabulary and shapes,
even in QuestLog's non-OAuth2 setup.

## Prerequisites

Lesson 03 (sessions vs. JWTs — OAuth2 access tokens are conceptually
similar to what that lesson already covered) and Lesson 04 (JWT
structure — many, though not all, real OAuth2 implementations use JWTs
as their access token format).

## The concept, explained simply

Imagine you want to let a hotel valet park your car, without giving them
a copy of your house key, your wallet, or the ability to drive it
anywhere they want forever. What you actually hand over is a **valet
key** — a separate, limited key that starts the engine and opens the
door, but can't open the trunk or the glovebox, and that you can
invalidate at any time without changing your real key at all.

OAuth2 is the "valet key" pattern, applied to letting one application
(say, a photo-printing website) do something on your behalf at another
service (say, Google Photos) — **without you ever typing your Google
password into the photo-printing website at all.** Instead, you type your
password directly into Google's own login page, and Google hands the
photo-printing site a limited, revocable "valet key" (an **access
token**) that can only do exactly what you agreed to (e.g. "view your
photos," never "delete your account" or "read your email").

## The details

### The four roles OAuth2 names

Using "Login with Google" on a fictional site, `PrintMyPhotos.com`, as
the running example:

- **Resource Owner** — you, the actual human, who owns the data in
  question (your Google Photos).
- **Client** — the application requesting access on your behalf
  (`PrintMyPhotos.com`). Note this is a slightly confusing overload of a
  word you already know from Module 02 (client = whoever initiates an
  HTTP request) — here it specifically means "the application asking for
  delegated access," which happens to run partly on a server, partly in
  your browser.
- **Authorization Server** — the service that knows your real password
  and issues tokens (Google's own login/consent infrastructure).
- **Resource Server** — the service that actually holds the data being
  accessed and checks tokens on incoming requests (Google Photos' own
  API, which might even be a physically different service than the
  authorization server, though for a company like Google it's operated by
  the same organization).

### The Authorization Code flow, step by step

This is the specific, most common OAuth2 flow used by nearly every
"Login with X" button you've clicked (formally called the
**Authorization Code Grant**):

1. You click "Login with Google" on `PrintMyPhotos.com`.
2. `PrintMyPhotos.com`'s browser is **redirected** to a URL on Google's
   own domain — critically, `accounts.google.com`, not
   `PrintMyPhotos.com` — carrying a `client_id` (identifying which
   registered application is asking) and a list of requested **scopes**
   (below).
3. You log in **directly on Google's own page**, with your real Google
   password, which `PrintMyPhotos.com`'s code never sees at any point.
4. Google shows you a **consent screen**: "PrintMyPhotos.com wants to:
   view your Google Photos. Allow?" — naming the specific scopes
   requested in step 2, in plain language.
5. You click "Allow." Google redirects your browser **back** to a URL
   `PrintMyPhotos.com` registered in advance (the **redirect URI** — this
   registration step is exactly what stops a malicious site from
   pretending to be `PrintMyPhotos.com` and stealing this flow's result;
   Google will only ever redirect to a URL that specific `client_id`
   registered ahead of time), carrying a short-lived, one-time
   **authorization code** as a query parameter.
6. `PrintMyPhotos.com`'s own **server** (not your browser — this step
   happens machine-to-machine, away from anything you can see) takes that
   authorization code and exchanges it, along with a secret only
   `PrintMyPhotos.com`'s server knows (its **client secret**), for a real
   **access token**, by calling Google's token endpoint directly.
7. `PrintMyPhotos.com` can now call Google Photos' API, attaching that
   access token (in an `Authorization: Bearer <token>` header — notice
   this is the exact same header shape Lesson 03 already introduced for
   QuestLog's own JWT), and Google Photos' resource server verifies it and
   serves your photos.

At no point after step 3 does `PrintMyPhotos.com` ever see your Google
password — that is the entire point of the whole design.

### Why the flow bounces through your browser at all

Steps 2–5 happen in your own browser, visiting Google's own domain
directly, specifically so that your password is only ever typed into a
page Google itself served, over a connection to Google's own domain —
never into any page `PrintMyPhotos.com` controls. This is also why
phishing attempts that show you a *fake* Google-lookalike login page,
instead of a real redirect to `accounts.google.com`, are attacking this
exact trust boundary — always check the actual domain in your browser's
address bar during any real "Login with X" flow.

### Scopes, access tokens, and refresh tokens

- A **scope** is a named, specific permission being requested — e.g.
  `photos.readonly`. Requesting the narrowest set of scopes that actually
  gets the job done is considered good practice (the **principle of least
  privilege** — a term worth knowing generally, well beyond OAuth2).
- An **access token** is the actual credential the client uses on real
  requests to the resource server — conceptually similar to QuestLog's
  own JWT (Lesson 04), and, in many real OAuth2 systems, literally
  implemented as a JWT.
- A **refresh token** is a separate, longer-lived credential the client
  can exchange for a *new* access token once the old one expires, without
  making you log in again. This is exactly the mechanism real systems use
  to get the security benefit of a short-lived access token (Lesson 03's
  "stolen token only useful for a limited time" mitigation) without
  forcing you to re-enter your password every hour. QuestLog does **not**
  implement refresh tokens — its access tokens simply expire after 60
  minutes (`app/config.py`), and logging back in is this course's
  deliberately simple stand-in; a real production system would very
  likely add a refresh-token flow, which is a natural, realistic next
  step beyond this course's scope.

### What QuestLog actually borrows from OAuth2 — and what it doesn't

QuestLog implements **none** of the multi-party flow above — there is no
authorization server, no redirect to a third-party domain, no consent
screen, no client secret. QuestLog's own backend plays every role at
once: it's the resource owner's *direct* login target, the authorization
server, and the resource server, all in one FastAPI process, using a
plain email+password form (Lesson 06). This corresponds to a different,
narrower OAuth2 flow called the **Resource Owner Password Credentials
Grant** — historically part of the OAuth2 specification, but one modern
OAuth2 guidance (including the IETF's own current best-practice
documents) now actively discourages for real third-party scenarios,
*precisely because* it requires the client application to directly handle
the user's raw password — the exact thing the Authorization Code flow
above was designed to avoid.

So why does FastAPI's own `OAuth2PasswordRequestForm` and
`OAuth2PasswordBearer` (used throughout Lesson 06/07) reference OAuth2 at
all, if this app isn't doing third-party OAuth2? Because QuestLog *is* its
own resource owner, client, authorization server, and resource server —
there is no "third party" here to protect a password from, since the
party asking for the password (QuestLog's own backend) is also the party
that's allowed to know it. In that specific, narrower situation, the
Password Grant's request/response *shape* (a `username`/`password` form,
answered with an `{"access_token", "token_type"}` JSON body) is a
genuinely reasonable, simple, well-understood convention to reuse, and
FastAPI's own security utilities are built to make exactly that pattern
convenient — which is why QuestLog's `Token` Pydantic model
(`app/models.py`) uses OAuth2's own field names verbatim, even though no
actual third party, redirect, or consent screen is anywhere in this
app's design.

## Common mistakes & gotchas

- **Assuming "OAuth2" always means "Login with Google/Facebook/etc."**
  That's the Authorization Code flow specifically — the most common real
  use of OAuth2, but only one of several flows the specification defines,
  and QuestLog uses none of them for third-party purposes at all.
- **Confusing OAuth2 (authorization — "can this app access that data?")
  with OpenID Connect (authentication — "who is this person, really?").**
  In practice, "Login with Google" almost always layers a related, newer
  standard called **OpenID Connect** on top of OAuth2 specifically to
  answer "who is this person" (via an additional token called an **ID
  token**) — OAuth2 alone was designed to answer "can this app access
  this resource," a subtly different question. This distinction is worth
  knowing exists, even though this course doesn't build either integration.
- **Believing the client application ever needs to see your real
  password in a third-party OAuth2 flow.** The entire design goal of the
  Authorization Code flow is that it doesn't — if you ever find yourself
  typing your Google/Facebook password into a page that is *not* actually
  on Google's or Facebook's own domain, something is deeply wrong (very
  likely a phishing attempt), regardless of what the page claims to be.

## How this connects

Lessons 01–04 built up everything QuestLog's *own* login needs
conceptually and mechanically. This lesson deliberately stepped outside
QuestLog to explain the wider, real-world pattern its login endpoint's
shape is borrowed from, and to give you real, working vocabulary
(authorization server, scope, access/refresh token, redirect URI) you'll
need the moment you integrate with any real third-party API as a working
engineer — including, later in this course, calling the Anthropic API
(Module 13), which uses its own, simpler API-key based scheme rather than
full OAuth2, precisely because it has no browser-based "user consent"
step to manage. Lesson 06 returns fully to QuestLog's own, concrete
signup/login routes.

## Quick self-check

1. Name the four roles OAuth2 defines, and identify each one in a "Login with Google" example.
2. Why does the Authorization Code flow redirect your browser to the authorization server's own domain, rather than having the client application collect your password directly?
3. What is a scope, and why does "request the narrowest scopes needed" matter?
4. What's the difference between an access token and a refresh token, and which one (if either) does QuestLog implement?
5. Which specific OAuth2 grant does QuestLog's own login endpoint's *shape* resemble, and why is that grant considered inappropriate for a real third-party integration, even though it's fine for QuestLog's own single-party design?
