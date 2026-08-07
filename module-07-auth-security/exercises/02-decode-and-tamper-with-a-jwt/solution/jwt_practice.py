"""Exercise 02 -- Decode and Tamper With a JWT (reference solution).

See INSTRUCTIONS.md for the full task, and Lesson 04 for the full
explanation of every technique used below.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import jwt

SECRET = "exercise-02-practice-secret-do-not-reuse"


def create_a_token(user_id: str, secret: str) -> str:
    """Build and sign a JWT: `sub` = user_id, `iat` = now, `exp` = 60
    minutes from now."""
    now = datetime.now(timezone.utc)
    claims = {"sub": user_id, "iat": now, "exp": now + timedelta(minutes=60)}
    return jwt.encode(claims, secret, algorithm="HS256")


def decode_payload_by_hand(token: str) -> dict:
    """Extract and decode ONLY the payload of `token`, using nothing but
    the standard library."""
    _header_b64, payload_b64, _signature_b64 = token.split(".")
    # base64url can omit trailing '=' padding; add back whatever's needed
    # so base64.urlsafe_b64decode doesn't choke on a non-multiple-of-4 length.
    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    decoded_bytes = base64.urlsafe_b64decode(padded)
    return json.loads(decoded_bytes)


def verify_a_token(token: str, secret: str) -> dict:
    """Use jwt.decode(...) to verify the signature and return the claims."""
    return jwt.decode(token, secret, algorithms=["HS256"])


def tamper_and_observe(token: str, secret: str) -> None:
    """Change exactly one character in the token's payload and observe
    verification fail."""
    header_b64, payload_b64, signature_b64 = token.split(".")
    # Flip the last character of the payload to something different.
    last_char = payload_b64[-1]
    replacement = "A" if last_char != "A" else "B"
    tampered_payload_b64 = payload_b64[:-1] + replacement
    tampered_token = f"{header_b64}.{tampered_payload_b64}.{signature_b64}"

    print(f"Original payload segment:  {payload_b64}")
    print(f"Tampered payload segment: {tampered_payload_b64}")

    try:
        verify_a_token(tampered_token, secret)
        print("Uh oh -- tampered token verified successfully (this should not happen)!")
    except jwt.InvalidTokenError as e:
        print(f"Tampered token correctly REJECTED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    token = create_a_token("user-42", SECRET)
    print(f"Created token: {token}")
    print()

    print("=== Decoding the payload by hand (no secret used) ===")
    payload = decode_payload_by_hand(token)
    print(f"Payload: {payload}")
    print()

    print("=== Verifying with jwt.decode (secret required) ===")
    claims = verify_a_token(token, SECRET)
    print(f"Verified claims: {claims}")
    print()

    print("=== Verifying with the WRONG secret ===")
    try:
        verify_a_token(token, "totally-wrong-secret")
        print("Uh oh -- this should have raised an exception!")
    except jwt.InvalidTokenError as e:
        print(f"Correctly rejected: {type(e).__name__}: {e}")
    print()

    print("=== Tampering with the payload ===")
    tamper_and_observe(token, SECRET)
    print()

    print(
        "Why is this safe? The payload is just base64url -- a public, "
        "reversible ENCODING, not encryption -- so anyone can decode it with "
        "no key at all (proven above). The signature, though, is an HMAC "
        "computed over the header+payload using a secret only the server "
        "knows; recomputing the CORRECT signature for a changed payload "
        "requires that same secret, which an attacker editing the token "
        "doesn't have -- so the old signature simply stops matching the new "
        "payload, and jwt.decode() catches that mismatch every time."
    )
