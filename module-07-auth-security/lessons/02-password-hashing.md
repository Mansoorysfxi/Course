# Lesson 02 — Password Hashing: Why bcrypt, and What a Salt Actually Is

## What you'll learn

- Why a real application must never store a plain-text password, ever — not even "just for now," not even encrypted.
- The precise difference between **hashing** and **encryption**, and why hashing (not encryption) is the right tool here.
- What a **salt** is, why it's needed, and why hashing the same password twice produces two different-looking results.
- Why this course uses `bcrypt` specifically — what makes it different from a generic hash function like SHA-256 — and honestly, where the newer Argon2 fits into this picture.
- How to actually call `hash_password`/`verify_password` in QuestLog's own `app/security.py`, line by line.

## Why this matters

Every account-based system on the internet stores *something* derived
from a password, and how it does that is one of the highest-stakes
decisions in that system's entire codebase — a mistake here doesn't just
break one feature, it can expose every user's password the moment a
database ever leaks (and databases leak constantly; a huge fraction of
real-world breaches are exactly "someone got a copy of the users table").
This lesson is the first lesson in this module to write real, runnable
code, and it's the code QuestLog's signup route (Lesson 06) depends on
completely.

## Prerequisites

Lesson 00 (this module's `bcrypt` package is installed and ready), Lesson
01 (authentication is "verifying who someone is" — this lesson is the
*mechanics* of the one piece of that: checking a password).

## The concept, explained simply

Imagine a locked box at a bank, and two totally different approaches to
"proving you know the combination":

- **Encryption** is *reversible*: you can lock something with a key and
  later unlock it with that same key (or a related one) to get the
  original content back. This is the right tool when the *system itself*
  needs to read the original data back later (e.g. a password manager
  needs to eventually show you your actual saved password so you can copy
  it — that's stored *encrypted*, deliberately, because the app must
  recover it).
- **Hashing** is *one-way, on purpose*: you run something through a hash
  function and get a fixed-size, scrambled-looking result, and there is
  no operation that takes that result back to the original input. A
  password is the perfect candidate for this, because the application
  **never actually needs the original password back** — it only ever
  needs to answer one yes/no question, forever: "does this new attempt
  match what I have on file?" You answer that by hashing the *new
  attempt* the same way and comparing the two hashes — never by
  "decrypting" anything.

This is why `app/security.py`'s docstring says, explicitly, "there is no
'decrypt the hash back into the password' step" — it's not an omission,
it's the entire design.

## The details

### Why a *generic* hash function (like SHA-256) is still not good enough

A plain cryptographic hash function like SHA-256 is genuinely one-way —
so why not just use it directly on a password? Two real, practical
problems:

1. **It's too fast.** SHA-256 is *designed* to hash gigabytes of data per
   second — exactly the wrong property for a password hash. If an
   attacker steals a database of SHA-256 password hashes, they can try
   billions of guesses per second on ordinary hardware (this is called a
   **brute-force attack**), because computing SHA-256 is cheap. A good
   password-hashing algorithm is *deliberately* slow — expensive enough
   that hashing one real login attempt (a fraction of a second) is fine,
   but trying billions of guesses becomes impractical.
2. **Identical passwords hash identically.** If two users pick the exact
   same password, plain SHA-256 gives them the exact same hash. An
   attacker with a stolen database (or anyone browsing it) can instantly
   see "these two accounts share a password" and can precompute a giant
   lookup table (a **rainbow table**) mapping common passwords to their
   SHA-256 hashes once, then instantly reverse *any* database that uses
   plain SHA-256, for free, forever. This is the exact problem a **salt**
   exists to solve — see below.

### What a salt actually is

A **salt** is a random value, generated fresh for every single password,
that gets mixed into the hashing process alongside the password itself.
Two users with the identical password `"dragon-slayer-1"` end up with
**completely different** stored hashes, because each got its own random
salt. This defeats rainbow tables outright (a precomputed table for one
salt is useless against a different salt) and means an attacker can no
longer even tell which two accounts share a password just by looking at
the hashes.

Critically: the salt is not a secret kept somewhere else — it's stored
**inside the hash string itself**, right alongside the actual hash, so
verification can find and reuse the exact same salt later. Try this
yourself:

```bash
python -c "
import bcrypt
h1 = bcrypt.hashpw(b'dragon-slayer-1', bcrypt.gensalt())
h2 = bcrypt.hashpw(b'dragon-slayer-1', bcrypt.gensalt())
print(h1)
print(h2)
print(h1 == h2)
"
```

**Expected output:** two long strings starting with `b'$2b$12$...'`, both
different from each other, followed by `False` — proof that hashing the
identical password twice gives two different results, entirely because
`bcrypt.gensalt()` produced a fresh random salt each time. (Exercise 01
has you do exactly this and inspect the structure of the output further.)

**`$2b$12$...` decoded:** bcrypt's own hash format packs everything it
needs into one string, separated by `$`: `2b` names the specific bcrypt
algorithm variant, `12` is the **cost factor** (below), and the next 22
characters are the salt itself — everything after that is the actual
hash. `bcrypt.checkpw` (used by `verify_password`) reads the salt back
out of this exact string; it never needs it passed in separately.

### The cost factor — bcrypt's answer to "too fast"

bcrypt has a second, adjustable parameter besides the salt: a **cost
factor** (sometimes called "rounds," default `12` in the `bcrypt`
package) controlling exactly how many times its internal algorithm
repeats itself. Doubling the cost factor roughly *doubles* how long one
hash takes to compute — which is the entire point: bcrypt is
*deliberately, tunably* slow, so that a login taking (say) 100
milliseconds is imperceptible to a real user, while an attacker trying
billions of password guesses against a stolen hash faces that same
100-millisecond cost **per guess**, making brute-forcing impractical even
with powerful hardware.

### QuestLog's actual code, line by line

`backend/app/security.py`:

```python
def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode("utf-8")
```

- `plain_password.encode("utf-8")` — bcrypt's underlying library works on
  raw bytes, not Python `str` objects, so this converts the text into
  bytes first (recall Module 01's string-encoding basics).
- `bcrypt.gensalt()` — generates a fresh, cryptographically random salt.
  Calling this fresh, every single time this function runs, is the
  *entire* mechanism behind "hashing the same password twice gives
  different output" — there's no separate "salt storage" step anywhere
  else in this app.
- `bcrypt.hashpw(password_bytes, salt)` — does the actual, slow, repeated
  hashing work, and returns bytes containing the algorithm identifier,
  cost factor, salt, and hash, all packed into the one string format
  shown above.
- `.decode("utf-8")` — converts back to a plain Python `str` for storage
  in the `users.hashed_password` column (`db_models.py`), which is a SQL
  `String`, not a binary column.

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
```

- `bcrypt.checkpw` reads the salt and cost factor back out of
  `hashed_password` itself, re-runs the exact same hashing process on
  `plain_password` using that same salt/cost, and compares the two
  results — returning `True` only on an exact match. This is the *only*
  place in this backend a login attempt's password is ever compared
  against anything — `app/routers/auth.py`'s `login` route calls exactly
  this function and nothing else.

**Try it yourself:** run the snippet above again, but this time change
one character of the second password attempt (e.g. `b'dragon-slayer-2'`)
before predicting: will `bcrypt.checkpw` return `True` or `False`? Then
actually run it and confirm.

### The 72-byte limit

bcrypt's underlying algorithm only ever examines a password's **first 72
bytes** — anything beyond that is silently ignored, which means
`"a-72-byte-password-XXXXXXXXX"` and that same string with 50 extra
characters appended would hash **identically**. This is a genuine,
documented limitation of the bcrypt algorithm itself (not this app's
`security.py`). QuestLog's `UserCreate.password` field
(`app/models.py`) caps input at `max_length=72` *characters* as a
practical safeguard — note this is characters, not bytes, so a password
using multi-byte Unicode characters (emoji, some non-Latin scripts) could
still technically exceed 72 bytes while under 72 characters; this course
accepts that edge case as an acceptable simplification for a learning
project rather than adding byte-counting validation logic.

### A note on Argon2 — an honest aside

FastAPI's own current official documentation leads with a different
algorithm, **Argon2** (via a modern library called `pwdlib`), as of the
research done for this module (August 2026) — the same research that
confirmed `passlib` is unmaintained. OWASP's own password-storage
guidance similarly lists Argon2id as its top recommendation, ahead of
bcrypt. Both bcrypt and Argon2 are considered acceptable, secure choices
by current standards; this course teaches bcrypt specifically because its
mechanics — a plainly visible, directly inspectable salt sitting right
inside the returned string — make it an unusually clear, concrete first
example of "what a salt actually is," the exact concept this lesson needs
to teach. If you build a real production system after this course, it's
worth knowing Argon2 exists and is, by a slim but real margin, the
current state of the art — but everything this lesson teaches about
*why* password hashing works the way it does (one-way, salted,
deliberately slow) applies to Argon2 identically; only the specific
algorithm name changes.

### Why this course doesn't police password complexity

`UserCreate.password` (`app/models.py`) only enforces a minimum length
(`min_length=8`) — no required uppercase letter, digit, or symbol.
Current guidance from NIST (the US National Institute of Standards and
Technology, whose SP 800-63B publication is widely treated as the modern
reference for this) explicitly recommends favoring length over
composition rules: forcing "at least one symbol" empirically pushes real
users toward predictable, guessable patterns (`Password1!` instead of a
genuinely stronger `correct-horse-battery-staple`-style long passphrase),
while providing little real security benefit against modern cracking
techniques. The other half of current best practice — checking a new
password against known-breached password lists — requires a real
breach-checking service (e.g. an API like Have I Been Pwned's), which is
outside this course's scope; a length minimum is this app's honest,
simplified stand-in for that.

## Common mistakes & gotchas

- **Writing `if password == stored_password:`.** This only works if
  `stored_password` is plain text — which it must never be. The correct
  comparison is always `verify_password(attempt, stored_hash)`, never a
  direct string comparison against anything derived from a real password.
- **Storing the salt in a separate column "to be safe."** Unnecessary —
  bcrypt already embeds the salt in its own output string, and
  `bcrypt.checkpw` already knows how to read it back out. A separate salt
  column is redundant, not more secure.
- **Reusing one hardcoded salt for every user "for simplicity."** This
  defeats the entire point of salting — it's functionally equivalent to
  not salting at all, since an attacker only needs one rainbow table for
  that one known salt to attack every account at once. `bcrypt.gensalt()`
  must be called fresh, per password, every time.
- **Logging a plain-text password "temporarily, for debugging."** A
  genuinely common real-world mistake — a stray `print(password)` or
  `logger.info(f"login attempt: {password}")` left in code can leak every
  password that ever passes through it into log files, which are often
  far less carefully protected than a database. Lesson 11 covers logging
  discipline directly; the rule from this lesson is simple: a plain-text
  password should never be assigned to a variable that outlives the one
  line converting it into a hash (or, for login, the one line comparing
  it via `verify_password`).

## How this connects

This lesson is the mechanical half of the authentication step named in
Lesson 01: `hash_password` is what `POST /api/auth/signup` calls before
ever writing to the database (Lesson 06); `verify_password` is what
`POST /api/auth/login` calls before ever issuing a token (Lesson 04
covers what that token actually is). Exercise 01 has you exercise both
functions directly, outside the API, to see this behavior with your own
eyes before it's wired into a full request.

## Quick self-check

1. Why is hashing, not encryption, the correct tool for storing a password?
2. What specifically is a salt, where is it stored, and what specific attack does it defeat?
3. Why is a generic, fast hash function like SHA-256 a bad choice for password hashing, even though it's genuinely one-way?
4. What does bcrypt's cost factor control, and why is "slower" a *good* property here?
5. Name one honest trade-off this course made (bcrypt vs. Argon2, or no composition rules) and the reasoning behind it.
