# Lesson 11 — Secrets, Config, Rate Limiting, and Logging Done Right

## What you'll learn

- Why configuration values split into three real categories (safe defaults, per-environment settings, and genuine secrets), and why each deserves different handling.
- How `pydantic-settings` (installed in Lesson 00, used throughout this module's `app/config.py`) makes "missing required config" a loud startup failure instead of a silent, confusing runtime bug.
- What actually happens when a secret leaks into Git history, and why "just delete the file in a later commit" does not fix it.
- What **rate limiting** is, why it matters even for a small app, and where it's actually implemented in most real systems (often not in your own application code at all).
- What "logging done right" means: what to log, what never to log, and why a stray `print(password)` is a real, if easily overlooked, security bug.

## Why this matters

This is this module's "operational hygiene" lesson — the practices that
don't show up as a single dramatic vulnerability the way SQL injection or
XSS do, but that quietly determine whether a real production incident
(a leaked key, a brute-force campaign, a debugging session that
accidentally exposes user data) is a minor, contained problem or a
genuine disaster. Every piece of code this module has already written —
`app/config.py`, every route's careful avoidance of ever handling a
plain-text password past the line that hashes/verifies it — was already
built with these practices in mind; this lesson makes that reasoning
explicit.

## Prerequisites

Lesson 00 (this module's `.env`/`SECRET_KEY` setup — this lesson explains
the reasoning behind what that lesson had you do), Lesson 02 (password
hashing — this lesson's logging discussion directly extends that
lesson's "never log a plain-text password" point).

## The concept, explained simply

Think of everything a running application needs to know as falling into
one of three trust levels, the way a game studio might classify
information: **public** (anyone can see it — a build number, a default
port), **internal** (fine for any developer on the team to see, but not
posted publicly — a staging server's hostname), and **restricted** (a
small, deliberately limited set of people/systems, ever — a signing
key, a production database password). Treating all three the same way —
committing everything straight into the same Git repository, in the same
file, with the same access — is the root cause of a huge fraction of
real-world "secret leaked" incidents. This lesson's job is teaching you
to keep those three categories genuinely separate, in QuestLog and in
any real system you build after this course.

## The details

### Three kinds of configuration, and how QuestLog's `app/config.py` treats each

- **Safe, shareable defaults** — `algorithm: str = "HS256"`,
  `access_token_expire_minutes: int = 60`. These are fine to commit
  directly in code, because knowing them gives an attacker no real
  advantage (they're already documented, publicly, in this very lesson).
- **Per-environment settings** — `database_url`, `cors_origins_raw`.
  These *could* be committed as a sensible local-dev default (and
  `database_url`'s default is exactly that), but a real deployment would
  override them via a real environment variable, pointing at a real
  production database and a real production frontend's origin — never
  the same value used in local development.
- **Genuine secrets** — `secret_key`. Notice, precisely, that this is the
  **only** field in `Settings` with no default value at all
  (`app/config.py`). This isn't an accident or an oversight — it's the
  entire mechanism this lesson is about: because `secret_key: str` has no
  default, `pydantic-settings` raises a loud `ValidationError` the
  instant the app starts, if no real value is found anywhere (an
  environment variable, or `.env`) — a genuine secret should never have a
  "sensible fallback," because any fallback shared across every
  installation of an app stops being a secret at all, and a loud startup
  crash is *far* preferable to a silent bug where every deployment
  accidentally shares one hardcoded key.

### What "never commit `.env`" actually protects against, and why deleting it later isn't enough

`backend/.gitignore` lists `.env` specifically so Git never tracks it —
Lesson 00 had you confirm this with `git check-ignore -v .env`. If a real
secret ever *does* get committed by accident (someone removes the
`.gitignore` entry, or force-adds the file), simply deleting it in a
later commit **does not remove it from the repository's history** — every
previous commit that included it is still sitting there, retrievable by
anyone who can access the repository (including, for a public GitHub
repo, literally anyone on the internet, forever, via that commit's own
hash — automated bots are known to scan public GitHub commits
specifically looking for leaked keys, often within minutes of a push).
The only real fix, once a secret has been committed, is treating it as
**permanently compromised**: rotate it (generate a brand-new secret and
deploy it, invalidating the old one — for QuestLog, that means every
existing JWT signed with the old key stops verifying, forcing everyone to
log in again) and, separately, actually purging the old value from Git
history if the repository's history itself needs cleaning up (a genuinely
involved process, using tools built for exactly this, well beyond this
lesson's scope — the practical lesson here is "prevent this in the first
place," which is exactly what `.gitignore` plus a `.env.example` template
(Lesson 00) is for).

### Rate limiting

**Rate limiting** is restricting how many requests a single client (by
IP address, by account, or both) may make in a given time window,
specifically to blunt two kinds of abuse this module's other lessons
already made newly relevant: **brute-force login attempts** (an attacker
trying thousands of password guesses per second against `POST
/api/auth/login`, now that this app has real accounts worth guessing at)
and simple denial-of-service style overload (one client hammering an API
so hard that it can't serve anyone else).

QuestLog's own code does **not** implement rate limiting — this is a
genuine, honestly-stated gap, not a hidden one, and it's worth knowing
*why* it's reasonable to defer, and where this responsibility usually
actually lives in a real system:

- Rate limiting is frequently implemented **outside** the application's
  own code entirely — at a reverse proxy or load balancer sitting in
  front of it (Module 09's own upcoming networking module introduces
  reverse proxies like Nginx; Module 11's cloud module covers managed
  rate-limiting features many cloud platforms offer directly), precisely
  because that's a layer that already sees every request to every backend
  service, and can reject abusive traffic before it ever reaches your
  application code (and, unlike your own Python process, before it even
  costs your application any CPU or database time).
- For a Python/FastAPI app that *does* want to rate-limit inside its own
  code, a dedicated, well-maintained library (e.g. `slowapi`, built
  specifically around FastAPI's own dependency system) is the standard
  approach — conceptually, it works by tracking request counts per
  client (often backed by Redis, which Module 06's own NoSQL lesson
  already introduced as exactly this kind of fast, ephemeral counter
  store) and rejecting requests once a limit is exceeded, typically with
  HTTP's own `429 Too Many Requests` status code.

This course defers hands-on rate-limiting implementation to later
modules that introduce the infrastructure (a reverse proxy, Redis in
real use) it naturally builds on — naming it here, honestly, rather than
silently skipping it, satisfies this lesson's job of making sure you know
this gap exists and roughly how it gets closed in a real system.

### Logging done right

A **log** is a durable, timestamped record of events a running
application writes as it operates — essential for debugging problems
after the fact, and for noticing suspicious activity (repeated failed
logins from one source, say). Two rules matter most, and both are
already honored by every line of code this module wrote:

1. **Never log a secret, a password, or a full token.** A stray
   `print(f"login attempt: {email} / {password}")` "just for debugging"
   is a real, if easily-introduced, security bug — log files often have
   far weaker access controls than a database itself, and outlive the
   debugging session someone added that line for. Go re-read
   `app/routers/auth.py`'s `login` route: it never writes `form_data.password`
   anywhere except into `verify_password`'s one argument. If this app
   added structured request logging (many real production systems do,
   often via middleware — Module 05's middleware lesson explained the
   general mechanism), a well-designed logging setup deliberately
   excludes an `Authorization` header's actual value and any request
   body field named anything like `password`, precisely to make this
   mistake structurally hard to make even under time pressure.
2. **Log enough to actually answer "what happened," without logging
   everything.** A login failure is worth logging (which email was
   attempted, when, from where) — the *password* that was tried is never
   worth logging, because there is no legitimate operational reason to
   ever need it back, and every reason not to keep a record of it.

**Structured logging** — writing log entries as machine-parseable data
(commonly JSON) with consistent fields (`timestamp`, `level`, `event`,
relevant ids) rather than free-form sentences — is current best practice
for anything beyond a small local project, because it lets you actually
*query* your logs later ("show me every failed login for this email in
the last hour") instead of manually reading scrollback. This course
doesn't add structured logging to QuestLog's own code in this module (a
reasonable scope decision, matching this module's focus on auth
mechanics over observability infrastructure), but Module 11's own
monitoring/observability lesson picks this up directly, once QuestLog is
running somewhere real logs actually need to be searched.

## Common mistakes & gotchas

- **Committing a real `.env` "just once, I'll remove it right after."**
  See the "history is forever" explanation above — there is no truly safe
  "just once."
- **Reusing the same `SECRET_KEY` across local development and any real
  deployment.** A key that's ever been written down in a lesson, a shared
  Slack message, or a local `.env` you're not 100% sure never left your
  machine should be treated as non-secret going forward — generate a
  fresh one (Lesson 00's exact command) for anything that actually matters.
- **Assuming rate limiting is "someone else's problem" forever, with no
  plan at all.** Deferring it to infrastructure this course hasn't built
  yet (per the honest gap above) is fine *as a stated, known gap* — it's
  a different thing entirely from never having considered it, which is
  the actual risky version of this mistake.
- **Logging an entire request object "for debugging" without checking
  what's actually inside it.** A generic `logger.info(request.__dict__)`
  style line can easily capture headers (including `Authorization`) or
  body fields (including `password`) nobody intended to write to a log
  file at all — always log specific, named fields you've deliberately
  chosen, never an entire raw object, once real logging is added to a
  project.

## How this connects

This lesson closes out this module's core teaching material by tying
together a thread that ran through every earlier lesson without being
named explicitly until now: `app/config.py`'s `secret_key` having no
default (Lesson 00), `hash_password`/`verify_password` never letting a
plain-text password escape their own small boundary (Lesson 02), and this
app's deliberate honesty about what it *hasn't* implemented (rate
limiting) are all the same underlying discipline — treat secrets and
sensitive data as things to minimize, isolate, and never write down
carelessly, as a habit, not just when a lesson happens to be about
security directly. This is also the last lesson before the capstone
(`project/BRIEF.md`), which asks you to actually build the full,
integrated signup/login/protected-routes flow this entire module has been
building toward one piece at a time.

## Quick self-check

1. Name the three categories configuration values fall into, and give one QuestLog example of each.
2. Why does `secret_key` have no default value in `app/config.py`, and what happens at startup if none is provided anywhere?
3. If a real secret is accidentally committed to Git and then deleted in a later commit, is it actually gone? What's the real fix?
4. What is rate limiting, what specific problem (newly relevant this module) does it address, and where does QuestLog currently implement it?
5. What two rules govern "logging done right," and where in QuestLog's own `login` route can you point to code already honoring the first one?
