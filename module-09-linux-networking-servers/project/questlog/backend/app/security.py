"""Password hashing (bcrypt) and JWT creation/verification (PyJWT).

See lessons/02-password-hashing.md for hash_password/verify_password and
lessons/04-jwt-structure-in-depth.md for create_access_token/
decode_access_token. This is the only file in the backend that imports
`bcrypt` or `jwt` directly -- app/routers/auth.py and app/dependencies.py
call these functions, never the underlying libraries, exactly the same
"one seam" discipline app/repository.py already applies to
app/db_models.py (see that file's own docstring).

Library choices, verified via real web research while writing this module
(August 2026), not from memory -- see lessons/00-setup.md's header for the
full citations:
- **bcrypt** (the `bcrypt` PyPI package, used directly) for password
  hashing -- not `passlib`, which multiple sources (including FastAPI's
  own GitHub discussions) confirm is effectively unmaintained and breaks
  outright on current Python versions. `bcrypt` itself remains an
  actively maintained, OWASP-acceptable choice; Argon2id is the newer
  algorithm official FastAPI docs now lead with, but this course teaches
  bcrypt specifically (per this module's own curriculum) because its
  mechanics -- a visible, inspectable salt baked into the hash string
  itself -- make an excellent first example of "what a salt actually
  is." lessons/02-password-hashing.md's "a note on Argon2" box discusses
  the newer alternative honestly.
- **PyJWT** for encoding/decoding JWTs -- not `python-jose`, which the
  same research confirms FastAPI's own maintainers moved away from after
  concluding it was abandoned; PyJWT is the actively maintained library
  FastAPI's current official docs use.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.config import settings


def hash_password(plain_password: str) -> str:
    """Turns a plain-text password into a bcrypt hash string, safe to
    store in the database. Never store `plain_password` itself anywhere,
    ever -- this function's entire job is making that unnecessary.

    `bcrypt.gensalt()` generates a fresh, random salt (lessons/02 explains
    exactly what this means and why it matters) every single time this
    function runs -- which is *why* hashing the same password twice
    produces two completely different-looking output strings (Exercise 01
    has you observe this directly). `bcrypt.hashpw` combines the password
    and that salt through bcrypt's hashing algorithm and returns the
    result -- with the salt itself embedded in the returned string, so
    `verify_password` below never needs the salt passed in separately.

    bcrypt's underlying algorithm only ever looks at a password's first
    72 bytes -- anything after that is silently ignored. This is a real,
    documented limitation of bcrypt itself (lessons/02's "the 72-byte
    limit" box), not a bug in this function.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # bcrypt.hashpw returns bytes; the database column is a string
    # (String(255) in db_models.py), so decode back to text before
    # returning -- the bytes are already ASCII-safe base64-ish characters,
    # so this decode can never fail.
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a plain-text password attempt against a stored hash.
    `bcrypt.checkpw` re-derives the salt from *inside* `hashed_password`
    itself (that's the whole point of embedding it there), hashes
    `plain_password` with that exact same salt, and compares the result to
    `hashed_password` -- returning `True` only if they match exactly.
    There is no "decrypt the hash back into the password" step, because
    hashing (unlike encryption) is one-way by design; see
    lessons/02-password-hashing.md's "hashing is not encryption" section.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str) -> str:
    """Builds and signs a JWT whose `sub` (subject) claim is the given
    user id. See lessons/04-jwt-structure-in-depth.md for exactly what a
    "claim" is and what each of the three claims below means:

    - `sub` -- who this token is about (this app's convention: the user's
      id, a string, so `app/dependencies.py`'s `get_current_user` can look
      the row up directly with no extra database query needed to resolve
      an email into an id).
    - `iat` ("issued at") -- when this token was created, as a Unix
      timestamp. Not currently used for any decision by this app, but a
      near-universal, cheap-to-include JWT convention worth knowing.
    - `exp` ("expiration") -- the exact moment this token stops being
      valid. `jwt.decode` (below) checks this automatically and raises
      `jwt.ExpiredSignatureError` on its own if the current time is past
      it -- this app never has to check expiry by hand.

    `jwt.encode` does three things in one call: turns the claims dict into
    JSON, base64url-encodes the header and that JSON payload (see
    lessons/04's "the three parts" section for exactly what base64url is
    and isn't), and computes an HMAC-SHA256 signature over both, using
    `settings.secret_key` -- then joins all three pieces with `.` into the
    final token string.
    """
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    claims: dict[str, Any] = {"sub": subject, "iat": now, "exp": expire}
    return jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Verifies a JWT's signature and expiry, and returns its claims dict
    if both check out. Raises `jwt.InvalidTokenError` (PyJWT's base
    exception class -- `jwt.ExpiredSignatureError` and several others all
    inherit from it) if the signature doesn't match, the token is
    malformed, or it's expired -- app/dependencies.py's `get_current_user`
    is the only place that catches this, turning it into a clean HTTP 401.

    This is the "verification" half of what lessons/04 calls JWTs being
    **signed, not encrypted**: this function proves the claims haven't
    been *tampered with* since this app issued them (because recomputing
    the correct signature requires `settings.secret_key`, which only this
    server knows) -- it does not, and cannot, make the claims themselves
    secret, since anyone can base64url-*decode* (not decrypt) a JWT's
    payload without any key at all. Exercise 02 has you prove this to
    yourself directly.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
