# Module 07 — Auth, Security & API Best Practices

**Phase:** 2 — Backend Engineering
**Estimated time:** 14–18 hours
**Verified against:** FastAPI 0.141.1, SQLAlchemy 2.0.51, Alembic 1.19.0, asyncpg 0.31.0 (all unchanged from Module 06); `bcrypt` 5.0.0, `PyJWT` 2.13.0, `pydantic-settings` 2.14.2, `python-multipart` 0.0.32, `email-validator` 2.3.0 — all current as of August 2026, verified via PyPI and FastAPI's own current documentation/maintainer discussions (see `lessons/00-setup.md`'s header for the full citations, including why this course deliberately does **not** use `passlib` or `python-jose`, both confirmed unmaintained).

## What this module is

Every module through Module 06 built QuestLog up to a real, persistent,
but fundamentally single-user API — anyone who could reach it at all
could see and change every quest, silently attributed to one seeded
"default" user. This module makes QuestLog genuinely **multi-user**: real
signup, real login, a real password (hashed, never stored in plain text),
a real JWT issued on login and required on every quest route, and every
quest now provably owned by, and visible only to, the account that
created it.

Beyond the hands-on capstone, this module is also this course's
dedicated, from-scratch tour of web application security: what
authentication and authorization actually mean and how they differ; how
password hashing, salts, and JWTs actually work under the hood; how OAuth2
works conceptually (even though QuestLog itself doesn't use third-party
OAuth2); and the concrete mechanics behind SQL injection, XSS, CSRF, and
CORS — the handful of attacks and browser behaviors that, more than
almost anything else in web development, "everyone gets bitten by" at
least once.

## What you'll be able to do after this module

- Explain authentication vs. authorization precisely, and identify which one a given piece of code/behavior actually implements.
- Hash and verify passwords correctly with `bcrypt`, and explain exactly what a salt does and why hashing the same password twice produces different output.
- Explain a JWT's three parts (header, payload, signature), what "signed, not encrypted" really means, and decode/verify one by hand.
- Compare session-based and JWT-based authentication honestly, including real trade-offs, not just "JWTs are better."
- Explain OAuth2's Authorization Code flow step by step, and correctly identify which (much narrower) part of OAuth2's shape QuestLog's own login endpoint borrows.
- Protect a FastAPI route with a real dependency chain (`OAuth2PasswordBearer` → `get_current_user` → `CurrentUser`), and scope a database query to the authenticated user, avoiding IDOR.
- Explain why SQLAlchemy's query-building API already prevents SQL injection, and recognize the one way to reintroduce it anyway (raw, string-interpolated `text()`).
- Explain XSS and CSRF, why QuestLog's specific architecture is naturally resistant to one but not the other, and name the standard defenses for both.
- Explain CORS in real depth: origins, preflight requests, and every header involved — and configure it correctly and safely for local development.
- Manage secrets and configuration correctly (never commit a real secret; fail loudly, not silently, when one is missing) and explain where rate limiting and structured logging fit into a real system.

## Prerequisites

Module 06 (QuestLog's Postgres-backed backend — this module's project is
a direct copy-forward of Module 06's finished code) and Module 05
(FastAPI routing, Pydantic models, `Depends`). Module 02 (HTTP methods,
headers, cookies, statelessness) is leaned on especially heavily in
Lessons 03, 09, and 10.

## Module structure

```
module-07-auth-security/
├── README.md                                    ← you are here
├── lessons/
│   ├── 00-setup.md                              ← new packages, a fresh DB, a real SECRET_KEY
│   ├── 01-authentication-vs-authorization.md
│   ├── 02-password-hashing.md
│   ├── 03-sessions-vs-jwts.md
│   ├── 04-jwt-structure-in-depth.md
│   ├── 05-oauth2-conceptual.md
│   ├── 06-building-signup-login.md
│   ├── 07-protecting-routes-with-dependencies.md
│   ├── 08-sql-injection-and-orm-safety.md
│   ├── 09-xss-and-csrf.md
│   ├── 10-cors-in-depth.md
│   └── 11-secrets-config-and-logging.md
├── exercises/
│   ├── 01-hash-and-verify-a-password/            ← easy — almost impossible to fail if Lesson 02 was read
│   ├── 02-decode-and-tamper-with-a-jwt/           ← guided
│   ├── 03-protect-a-route-with-a-dependency/       ← guided, more independent
│   └── 04-wire-up-questlog-auth/                    ← independent — the fullest hands-on practice before the capstone
├── project/
│   ├── BRIEF.md                                       ← capstone: QuestLog gains real, working, multi-user auth
│   └── questlog/                                       ← QuestLog, copied forward from Module 06, now with real auth
│       ├── frontend/                                     ← login/signup UI, AuthContext, ProtectedRoute (new)
│       └── backend/                                       ← real password hashing, JWTs, protected + owner-scoped routes (new)
└── CHECKLIST.md
```

Read the lessons in order. Lesson 00's setup is not optional — every
lesson after it assumes the new packages are installed and a real
`SECRET_KEY` exists. Lessons 01–07 build QuestLog's actual auth feature,
piece by piece, ending with a fully working signup/login/protected-route
system; Lessons 08–10 turn to specific, named attacks and browser
behaviors (SQL injection, XSS, CSRF, CORS) that a real multi-user system
now has meaningfully more at stake in defending against; Lesson 11 closes
with the operational discipline (secrets, config, rate limiting, logging)
that applies to everything built in this module and beyond it.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without looking
at its solution, ask for a review, revise if needed, then move on. This
module's exercises go from very easy (Exercise 01, hashing a password
outside any API at all) to fully independent (Exercise 04, wiring real
auth into a full copy of QuestLog's backend from a starter that's missing
it) — do them in order.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's `project/questlog/` is
Module 06's finished, Postgres-backed QuestLog, copied forward and given
real signup, login, JWT issuing/verification, and per-user quest
ownership — the exact payoff of `Quest.owner_id` and the `users` table
having existed since Module 06, specifically so this module didn't need
an awkward migration to add them retroactively. This module's finished
`project/questlog/` is exactly what Module 08 will copy forward and add a
real automated test suite to.
