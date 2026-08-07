# Lesson 04 — JWT Structure in Depth: Header, Payload, Signature

## What you'll learn

- Exactly what the three, dot-separated parts of a JWT are, and what's inside each one.
- What **base64url** encoding is (and, just as importantly, what it is *not* — it is not encryption).
- What a **claim** is, and what QuestLog's specific claims (`sub`, `iat`, `exp`) mean.
- What "signed, not encrypted" really means, mechanically — how a signature is computed and verified, and why that's enough to detect tampering without hiding anything.
- How to decode a real JWT by hand (no library) and with PyJWT, and how to prove to yourself that tampering with one breaks verification.

## Why this matters

Lesson 03 established *why* QuestLog uses a JWT instead of a session. This
lesson opens the token itself up completely — nothing about it should
feel like unexplained magic by the end. This matters beyond just passing
a self-check: understanding that a JWT's contents are *readable by
anyone* (Exercise 02 has you prove this with your own eyes) is the single
most important, most commonly misunderstood fact about JWTs, and getting
it wrong leads directly to real security bugs (putting secrets inside a
token's payload, for instance).

## Prerequisites

Lesson 03 (sessions vs. JWTs — this lesson assumes you already know
*why* QuestLog picked a JWT; this lesson is entirely about *what one
actually is*). Some passing familiarity with hashing helps (Lesson 02
already covered one-way functions), though this lesson explains HMAC
signing from scratch.

## The concept, explained simply

A JWT ("JSON Web Token," pronounced "jot") is a plain **text string**
made of three parts, separated by two dots (`.`):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3MjM0NTY3ODl9.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
└──────────────── header ────────────────┘└──────────────── payload ──────────────────┘└──────────── signature ────────────┘
```

A useful game-dev analogy: think of a JWT like a **sealed, tamper-evident
evidence bag** at a crime scene — anyone can *read* what's written on the
outside label (the header and payload are plainly readable, no key
needed), but if anyone opens the bag and swaps what's inside, the tamper
seal (the signature) visibly breaks, and whoever checks the seal later
(the server, Lesson 07's `decode_access_token`) will know immediately
that something changed. The bag doesn't *hide* its contents — it proves
its contents haven't been altered since it was sealed.

## The details

### Part 1 — The header

The first part, decoded, is a small JSON object:

```json
{"alg": "HS256", "typ": "JWT"}
```

- `typ` — just states "this is a JWT" (rarely used for anything by
  verifying code, but part of the spec).
- `alg` — names the exact signing algorithm used, so the verifier knows
  how to check the signature. `HS256` means **HMAC using SHA-256**
  (explained fully below) — this course's choice, matching
  `app/config.py`'s `algorithm: str = "HS256"` default.

### Part 2 — The payload (the claims)

The second part, decoded, is another JSON object — the actual
information the token carries, called **claims**. QuestLog's
`create_access_token` (`app/security.py`) sets exactly three:

```json
{"sub": "3f2504e0-...", "iat": 1723453189, "exp": 1723456789}
```

- **`sub`** ("subject") — a standard JWT claim name meaning "who/what
  this token is about." QuestLog's convention: the authenticated user's
  id (a string), so `get_current_user` (Lesson 07) can look the row up
  directly with zero extra work.
- **`iat`** ("issued at") — when the token was created, as a **Unix
  timestamp** (an integer count of seconds since January 1, 1970 —
  Module 01's `datetime` lesson likely already introduced this concept).
- **`exp`** ("expiration") — the exact moment this token stops being
  valid, also a Unix timestamp. `jwt.decode` (Lesson 07) checks this
  claim **automatically** — this app never manually compares timestamps
  itself.

Claims whose three-letter names are part of the official JWT
specification (like `sub`, `iat`, `exp`) are called **registered
claims** — using the standard names means any JWT library, in any
language, understands them the same way, without QuestLog inventing its
own conventions.

### Part 3 — The signature

The third part is what actually makes this scheme trustworthy. It is
**not** a hash of the payload alone — it's an **HMAC** (Hash-based
Message Authentication Code) computed over the header and payload
*together*, using a **secret key** only the server knows
(`settings.secret_key`, `app/config.py`, generated in Lesson 00).

Conceptually: `signature = HMAC-SHA256(header + "." + payload, secret_key)`.
Two facts follow directly from this:

1. **Anyone can verify a signature if they know the secret key** — because
   verifying just means recomputing the same HMAC and checking it matches.
   Only QuestLog's own backend knows `settings.secret_key`, so only
   QuestLog's own backend can produce (or verify) a valid signature for
   *any* payload — including a tampered one.
2. **Nobody can produce a *new*, valid signature without the key** —
   which is exactly what stops someone from editing the payload (say,
   changing `"sub": "user-42"` to `"sub": "user-1"` to impersonate another
   user) and having the result still pass verification. Editing the
   payload without knowing the secret key means the new payload's
   correct signature is unknowable — the old signature won't match the
   new payload, and there's no way to compute the right new one.

### base64url — and why it is NOT encryption

The header and payload aren't stored as raw JSON text in the token
string — they're each **base64url-encoded** first. Base64url is closely
related to the general-purpose base64 encoding you may have seen before
(e.g. for embedding small images directly in HTML/CSS), with two small
differences making it safe to put inside a URL or an HTTP header without
special characters causing problems (`+`/`/` are replaced with `-`/`_`,
and trailing `=` padding is typically dropped).

**This is encoding, not encryption, and the distinction matters a lot.**
Encoding is a fully public, reversible, no-key-required transformation —
anyone, with no secret at all, can decode a base64url string right back
to the original JSON. Try it yourself, with no library at all, using
nothing but Python's standard library:

```bash
python -c "
import base64, json
payload_b64 = 'eyJzdWIiOiIxMjMiLCJleHAiOjE3MjM0NTY3ODl9'
# base64url sometimes drops '=' padding; add it back if the length needs it
padded = payload_b64 + '=' * (-len(payload_b64) % 4)
decoded_bytes = base64.urlsafe_b64decode(padded)
print(json.loads(decoded_bytes))
"
```

**Expected output:** `{'sub': '123', 'exp': 1723456789}` — the payload,
in plain sight, decoded with zero knowledge of any secret key
whatsoever. This is exactly what Lesson 03 meant by "anyone with the
token can read every claim inside it" — **only the signature requires
the secret key; the payload itself is always, unavoidably, plainly
readable to anyone holding the token.** This is why `app/security.py`'s
own docstring says JWTs are "signed, not encrypted" — the signature
proves authenticity and integrity (it hasn't been tampered with since
QuestLog issued it); it does nothing at all to keep the contents secret.

**Try it yourself:** paste any real QuestLog access token (from Lesson
00's `curl` verification, or Exercise 02) into
`https://jwt.io` — a well-known public tool for exactly this — and
confirm you can read its header and payload instantly, with no secret
key entered anywhere on that page. (You will need to enter the secret
key on that page only if you also want jwt.io to *verify the signature*
— reading the payload itself never requires it.)

### Proving tampering breaks verification

`app/security.py`'s `decode_access_token` calls `jwt.decode(token,
settings.secret_key, algorithms=[settings.algorithm])`. If you take a
real, valid token and change even one character anywhere in it — the
payload, the header, or the signature — this call raises
`jwt.InvalidTokenError` (specifically `jwt.exceptions.DecodeError` or
`InvalidSignatureError`, both of which are subclasses of it), because the
signature PyJWT recomputes from the (now-different) header+payload no
longer matches the signature riding along in the token. Exercise 02 has
you do exactly this by hand and observe the failure directly.

### Why this app picked HS256 (a **symmetric** algorithm)

`HS256` is a **symmetric** signing algorithm: the exact same secret key
both *creates* and *verifies* signatures. This is the right fit when one
single backend (QuestLog's own FastAPI process) is the only party that
ever needs to create or check its own tokens. Some systems instead use an
**asymmetric** algorithm (commonly `RS256`), where a **private key**
signs tokens and a separate, publicly shareable **public key** verifies
them — useful when *other* services need to verify tokens without ever
being trusted with the ability to *create* new ones (a pattern you'll see
again conceptually in Lesson 05's OAuth2 discussion, where a third-party
identity provider signs, and many different apps only ever verify).
QuestLog has exactly one party doing both jobs, so the simpler symmetric
approach is the right, deliberate choice here.

## Common mistakes & gotchas

- **Putting a password, credit card number, or anything else genuinely
  secret inside a JWT's payload.** Anyone holding the token can read it,
  full stop — see the base64url decoding demonstration above. QuestLog's
  payload holds only a user id, deliberately nothing more sensitive.
- **Assuming a JWT is automatically invalid the moment it's tampered
  with, "because it's cryptographic."** It's invalid because
  **verification code specifically checks the signature** — a system that
  never calls something like `jwt.decode()` at all (or that decodes a
  token without ever checking its signature — some libraries offer an
  unsafe "decode without verifying" mode, meant only for debugging) would
  happily accept a forged token. The safety comes entirely from the
  verifying code actually doing its job, every time, on every request —
  which is exactly what `get_current_user` (Lesson 07) does, unconditionally.
- **Confusing "expired" with "invalid."** An expired token has a
  perfectly valid signature — the signing math doesn't care about time at
  all. `jwt.decode`'s expiration check is a *separate*, deliberate check
  it performs after signature verification succeeds, specifically
  comparing the `exp` claim against the current time. `jwt.ExpiredSignatureError`
  (still a subclass of the same `InvalidTokenError` base class
  `get_current_user` catches) is the specific exception this raises.

## How this connects

Lesson 03 explained why QuestLog carries authentication state in a token
at all; this lesson explained exactly what that token contains and why
it can be trusted despite being fully readable. Lesson 05 steps back to
the *conceptual*, real-world pattern (OAuth2) that this app's login
endpoint deliberately borrows the shape of, without actually being
third-party OAuth2. Lesson 06 is where `create_access_token` finally gets
called from a real route, and Lesson 07 is where `decode_access_token`
becomes the gatekeeper every protected route depends on.

## Quick self-check

1. Name the three parts of a JWT, in order, and what each one contains.
2. What specifically does base64url encoding do, and why is it not the same thing as encryption?
3. What claims does QuestLog's own `create_access_token` set, and what does each one mean?
4. If you change one character in a valid JWT's payload and try to verify it, what specifically happens, and why?
5. Why is HS256 (a symmetric algorithm) the right choice for QuestLog specifically, and in what situation would an asymmetric algorithm like RS256 be preferred instead?
