# Lesson 01 — Authentication vs. Authorization

## What you'll learn

- The precise difference between authentication ("who are you") and authorization ("what are you allowed to do") — two words that sound alike and get confused constantly, including by working developers.
- Why almost every real system needs both, and why they're implemented as genuinely separate steps.
- The vocabulary this entire module builds on: **principal**, **credentials**, **session**, **access control**.
- Where QuestLog will implement each of these, concretely, later in this module.

## Why this matters

Nearly every security bug this module discusses, and nearly every
security bug in real production systems, traces back to confusing these
two concepts, or implementing one while forgetting the other exists. A
system can authenticate someone perfectly (it knows exactly who they are)
and still have a catastrophic bug if it never checks whether that person
is *authorized* to do the thing they're asking to do. Module 06 built a
QuestLog API with **neither** concept implemented — anyone who could
reach it at all could do anything to any quest. This lesson names the two
missing pieces precisely, before any code adds them.

## Prerequisites

Module 02 (HTTP methods, status codes, headers — especially the
`Authorization` header, already defined in the glossary from that
module) and Module 05 (FastAPI routes, dependencies). No new code in this
lesson — it's entirely conceptual, laying vocabulary for every lesson
after it.

## The concept, explained simply

Imagine walking into a large studio's office building for a job:

- **Authentication** is the security guard at the front desk checking
  your badge and confirming *you are who your badge says you are* — maybe
  by checking a photo, maybe by asking you to type a PIN. The guard's only
  job is answering one question: **"who is this person?"**
- **Authorization** is what happens *after* that, at every door inside the
  building. Your badge (now that the guard has confirmed it's really
  yours) might open the general office, but not the server room, not the
  finance department's files, not another team's private project folder.
  Every one of those doors asks a *different* question: **"is this
  specific, already-identified person allowed through THIS door?"**

Critically: **you cannot authorize someone before you've authenticated
them.** A door that just says "let anyone through" has skipped
authentication and authorization both, which is exactly Module 06's
QuestLog. A door that carefully checks *whether* the badge in someone's
hand is real, but never checks *which rooms that specific badge-holder is
allowed into*, has authentication but no authorization.

## The details

### Authentication: "Who are you?"

**Authentication** ("authn" for short, in casual shorthand — you'll see
this in code comments and documentation) is the process of verifying a
claimed identity. In QuestLog, this happens in exactly one place: the
`POST /api/auth/login` route (built in Lesson 06), which takes an email
and password and answers one yes/no question — "does this password match
what we have on file for this email?" If yes, the system now knows *who*
is making requests. It hands back a **credential** — in this app's case,
a JWT (Lesson 03/04) — that the browser will present on every future
request as proof "I already authenticated, here's the token that proves
it," so the user doesn't have to retype a password on every single click.

The word **principal** is the general term for "the identified entity" —
usually a user, but in some systems it could be another service, a
script, or a device. Every route in QuestLog that requires login
ultimately resolves "who is making this request" down to one principal:
a row in the `users` table.

### Authorization: "What are you allowed to do?"

**Authorization** ("authz") is a *separate* check, made after
authentication has already succeeded, deciding whether an already-known
principal is allowed to perform a specific action on a specific resource.
QuestLog's authorization rule, stated in one sentence, is: **a user may
read, update, or delete only the quests they themselves created.**
That's it — this app has no admin roles, no teams, no shared quests. Real
systems often have far richer authorization rules (role-based access —
"only admins can delete any user's account"; resource-based access —
"only this document's owner or people they've explicitly shared it with
can open it"), but QuestLog's simple "you own it or you don't" rule is
enough to demonstrate the concept fully, and is itself an extremely
common real-world pattern (most personal-data apps — email, notes,
photos — work exactly this way).

The general term for "the rules deciding who can do what" is **access
control**. This app's authorization strategy is a common, named pattern:
every resource (a quest) carries an **owner** (`Quest.owner_id`, already
present since Module 06 — see that module's `db_models.py` docstring for
exactly why it was added a module early), and the access-control rule is
simply "the current principal's id must match the resource's owner id."

### Where each one lives in QuestLog's actual code (previewed — built in Lessons 06–07)

| Concept | Where it lives | What it checks |
|---|---|---|
| Authentication | `POST /api/auth/login` (Lesson 06) | Is this email+password combination valid? |
| Authentication | `app/dependencies.py`'s `get_current_user` (Lesson 07) | Is this request's JWT genuine and unexpired, and does it name a real user? |
| Authorization | `app/repository.py`'s `get_quest`, `update_quest`, `delete_quest` (Lesson 07) | Does the quest this request is about belong to the authenticated principal? |

Notice these are **three separate pieces of code**, not one — exactly the
"separate step" framing from the concept section above. `get_current_user`
answers "who is this" and stops there; it has no idea what a "quest" even
is. The `owner_id` checks inside `repository.py` answer "is this
specific quest theirs" and don't care *how* the caller proved their
identity, only that `current_user.id` was already resolved by the time
they run.

### A session vs. the "authentication" word itself

You'll sometimes hear "session" used loosely to mean "the period during
which a user is considered logged in." Lesson 03 gives this word a
precise, technical meaning (a literal server-side record of a login) and
contrasts it with QuestLog's actual approach (a JWT, which needs no such
server-side record at all) — for now, just know that "authenticated" and
"has an active session" are related but not identical ideas, and Lesson
03 is where that distinction actually matters.

## Common mistakes & gotchas

- **Checking authentication and calling it done.** The single most common
  real-world security bug in this space (an entire category called
  "Broken Access Control," consistently near or at the top of the
  industry-standard OWASP Top 10 list of web application risks) is a
  system that correctly requires *some* valid login, but then serves up
  *any* resource to *any* logged-in user without checking ownership —
  exactly what Module 06's QuestLog did (any request could see/edit any
  quest, because there was no login at all yet, let alone an ownership
  check). `app/repository.py`'s `get_quest` docstring (Lesson 07) names
  this exact bug by its formal name, IDOR (Insecure Direct Object
  Reference), and explains precisely how this module's query shape avoids it.
- **Confusing "401 Unauthorized" with authorization.** HTTP's own status
  code naming is, unfortunately, a little misleading here: a `401` status
  code actually means an **authentication** failure ("I don't know who
  you are, or your credentials are bad") — Lesson 07 uses `401` for
  exactly this. `403 Forbidden` is HTTP's actual **authorization** failure
  code ("I know exactly who you are, and the answer is no"). QuestLog
  deliberately uses `404`, not `403`, for "this quest exists but isn't
  yours" — see `app/repository.py`'s `get_quest` docstring (Lesson 07) for
  the deliberate reasoning.
- **Assuming the frontend checking something is the same as the backend
  enforcing it.** A "Log out" button, a redirect to `/login` when
  `useAuth()` has no user (`src/components/ProtectedRoute.tsx`) — none of
  that is a real security boundary. It's a UX convenience. The *only*
  real enforcement is server-side code that runs no matter what the
  frontend did or didn't check — Lesson 07 makes this point explicitly,
  with a concrete way to prove it to yourself (calling the API directly,
  bypassing the frontend entirely).

## How this connects

Every remaining lesson in this module is really just "the concrete
mechanics of authentication" (Lessons 02–06 — hashing passwords, JWTs,
OAuth2, the login endpoint itself) or "the concrete mechanics of
authorization" (Lesson 07 — dependencies, ownership checks) built on top
of the vocabulary this lesson defined. The attack-focused lessons (08–09)
are largely about what goes wrong when either half is missing or
implemented sloppily.

## Quick self-check

1. In your own words, what's the one-sentence difference between authentication and authorization?
2. Which HTTP status code corresponds to an authentication failure, and which to an authorization failure? Which one does QuestLog actually use when you request someone else's quest, and why?
3. Name the specific column, and specific function, in QuestLog's backend that implements its one authorization rule.
4. Why is a frontend redirect to `/login` not, by itself, a real security boundary?
5. Give an example (not from QuestLog) of a system that would need role-based authorization (not just ownership-based) — what would the roles be?
