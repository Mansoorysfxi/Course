"""Exercise 02 -- Decode and Tamper With a JWT.

See INSTRUCTIONS.md for the full task. Fill in every function marked
with a `# TODO`, then run this file directly:

    python jwt_practice.py
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import jwt

SECRET = "exercise-02-practice-secret-do-not-reuse"


def create_a_token(user_id: str, secret: str) -> str:
    """Build and sign a JWT: `sub` = user_id, `iat` = now, `exp` = 60
    minutes from now. Use `jwt.encode(...)` with algorithm "HS256".
    """
    # TODO: implement this function.
    raise NotImplementedError


def decode_payload_by_hand(token: str) -> dict:
    """Extract and decode ONLY the payload of `token`, using nothing but
    the standard library (`base64`, `json`) -- no PyJWT call anywhere in
    this function. This proves the payload needs no secret key to read.
    """
    # TODO: implement this function.
    raise NotImplementedError


def verify_a_token(token: str, secret: str) -> dict:
    """Use jwt.decode(...) to verify the signature and return the claims.
    Let PyJWT's own exception propagate if verification fails -- do not
    catch anything in this function.
    """
    # TODO: implement this function.
    raise NotImplementedError


def tamper_and_observe(token: str, secret: str) -> None:
    """Take a real, valid token, change exactly one character somewhere
    in its PAYLOAD, and call verify_a_token on the result inside a
    try/except block. Print whether verification succeeded or failed,
    and which exception (if any) was raised.
    """
    # TODO: implement this function.
    raise NotImplementedError


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
        "Why is this safe? TODO: write one sentence here explaining why the "
        "payload is readable without the secret, but the signature can't "
        "be forged without it."
    )
