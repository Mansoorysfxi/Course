# Exercise 01 — Hash and Verify a Password

**Difficulty:** Easy. If you've read Lesson 02 carefully, this should be
almost impossible to fail.

## Concepts this exercise uses (and where they're taught)

- What hashing is, and why it's used instead of encryption for passwords — [Lesson 02](../../lessons/02-password-hashing.md), "The concept, explained simply."
- What `bcrypt.gensalt()` and `bcrypt.hashpw()` do, and why a salt makes identical passwords hash differently — Lesson 02, "What a salt actually is."
- What `bcrypt.checkpw()` does and how it re-derives the salt from the stored hash — Lesson 02, "QuestLog's actual code, line by line."
- bcrypt's 72-byte limit — Lesson 02, "The 72-byte limit."

## What to build

A standalone script, `hash_practice.py`, with **no FastAPI, no database,
no QuestLog code at all** — just you and the `bcrypt` package, exactly
like Lesson 02's own runnable snippets. The starter file has four
functions with `# TODO` markers; fill each one in.

1. `hash_a_password(password: str) -> str` — hash a password and return the hash as a string.
2. `verify_a_password(password: str, hashed: str) -> bool` — check a password attempt against a stored hash.
3. `demonstrate_salting()` — hash the **same** password twice, print both hashes, and print whether they're equal.
4. `demonstrate_verification()` — hash a password once, then verify it against: (a) the correct password, (b) a wrong password. Print both results.

## Setup

```bash
cd exercises/01-hash-and-verify-a-password/starter
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Running it

```bash
python hash_practice.py
```

## Acceptance criteria

- [ ] `hash_a_password` returns a string starting with `$2b$` (bcrypt's own format marker).
- [ ] `verify_a_password` returns `True` for the correct password and `False` for any other password, against the same hash.
- [ ] `demonstrate_salting()`'s two printed hashes are **different** strings, even though the input password is identical both times — and your printed output explicitly states this is because of `bcrypt.gensalt()` generating a fresh salt each call.
- [ ] `demonstrate_verification()`'s output clearly shows `True` for the correct password and `False` for the wrong one.
- [ ] Running the whole script twice in a row produces different hash values each time (proof you didn't accidentally hardcode a fixed salt anywhere).

## What to submit for review

The completed `hash_practice.py`, plus the actual printed output from
running it once (copy-paste the terminal output, or a screenshot).

## Hints

**Level 1:** Every function you need is already named and explained, line
by line, in Lesson 02's "QuestLog's actual code, line by line" section —
this exercise asks you to write the same two functions yourself, from
scratch, not copy them from `app/security.py` without understanding them.

**Level 2:** Remember `bcrypt.hashpw` and `bcrypt.checkpw` both expect
**bytes**, not `str` — you need `.encode("utf-8")` on the way in, and
`.decode("utf-8")` on the way out of `hash_a_password` specifically (since
this function's return type is `str`, matching how `app/security.py`
stores it in a database `String` column).

**Level 3:** If `demonstrate_salting()` prints the same hash twice, you
likely called `bcrypt.gensalt()` **once** and reused the result for both
calls to `bcrypt.hashpw`, instead of calling `bcrypt.gensalt()` fresh,
inside `hash_a_password`, every single time that function runs.
