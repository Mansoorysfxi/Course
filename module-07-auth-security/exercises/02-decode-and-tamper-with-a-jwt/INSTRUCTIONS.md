# Exercise 02 — Decode and Tamper With a JWT

**Difficulty:** Guided.

## Concepts this exercise uses (and where they're taught)

- The three parts of a JWT and what's in each — [Lesson 04](../../lessons/04-jwt-structure-in-depth.md), "The concept, explained simply" and "Part 1/2/3."
- base64url encoding, and why decoding a JWT's payload requires **no secret key at all** — Lesson 04, "base64url — and why it is NOT encryption."
- HMAC signing, and why tampering with a token breaks verification — Lesson 04, "The signature" and "Proving tampering breaks verification."
- The difference between "expired" and "invalid" — Lesson 04, "Common mistakes & gotchas."

## What to build

A script, `jwt_practice.py`, in four parts (the starter has all four as
separate functions with `# TODO` markers):

1. `create_a_token(user_id: str, secret: str) -> str` — build and sign a JWT using PyJWT, with `sub` set to `user_id`, and `iat`/`exp` claims (expiring 60 minutes from now).
2. `decode_payload_by_hand(token: str) -> dict` — extract and decode **only the payload** of a JWT, using nothing but Python's standard library `base64`/`json` modules — no PyJWT call anywhere in this function. This proves the payload needs no secret key to read.
3. `verify_a_token(token: str, secret: str) -> dict` — use PyJWT's own `jwt.decode(...)` to verify the signature and return the claims, raising/propagating PyJWT's own exception if verification fails.
4. `tamper_and_observe(token: str, secret: str) -> None` — take a real, valid token, change exactly one character somewhere in its payload, and call `verify_a_token` on the result inside a `try`/`except` block, printing whether verification succeeded or failed and why.

## Setup

```bash
cd exercises/02-decode-and-tamper-with-a-jwt/starter
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Running it

```bash
python jwt_practice.py
```

## Acceptance criteria

- [ ] `create_a_token` returns a string with exactly two `.` characters in it (three parts).
- [ ] `decode_payload_by_hand` correctly prints the `sub`, `iat`, and `exp` claims — using zero calls to `jwt.decode` or any other PyJWT function inside that specific function.
- [ ] `verify_a_token` returns the same claims dict as `decode_payload_by_hand` did, when given the correct secret.
- [ ] Calling `verify_a_token` with the **wrong** secret raises `jwt.InvalidTokenError` (or a subclass of it) — demonstrate this explicitly in your script's output.
- [ ] `tamper_and_observe` clearly prints that the tampered token failed verification, and names which exception was raised.
- [ ] Your script's printed output includes one sentence, in your own words, stating specifically *why* the payload is readable without the secret but the signature can't be forged without it.

## What to submit for review

The completed `jwt_practice.py`, plus the actual printed output from
running it once.

## Hints

**Level 1:** For decoding the payload by hand, split the token on `.`
first (`token.split(".")` gives you `[header, payload, signature]` as
three strings) — you only need the middle one.

**Level 2:** base64url sometimes omits trailing `=` padding characters
that Python's `base64.urlsafe_b64decode` still expects. Lesson 04's own
hand-decoding snippet shows the exact padding fix
(`padded = payload_b64 + "=" * (-len(payload_b64) % 4)`) — you need this
before calling `base64.urlsafe_b64decode`.

**Level 3:** For tampering, changing a character in the **signature**
part (not the payload) also breaks verification, but changing a
character in the **payload** is the more instructive demonstration,
because it proves the *specific* claim (like `sub`) can't be silently
edited without invalidating the whole token — try tampering with the
payload specifically, and if you're not sure your edit actually changed
anything meaningful, decode the tampered payload with
`decode_payload_by_hand` first and compare it to the original.
