"""Unit tests for app/security.py -- password hashing and JWT creation.

"Unit" test means exactly what lessons/01-why-tests-and-the-testing-pyramid.md
defines: these tests call plain Python functions directly, with no HTTP
request, no FastAPI app, and (unlike tests/test_auth.py and
tests/test_quests.py) no database at all. They sit at the bottom of the
testing pyramid on purpose -- fast, focused, and they pin down exactly what
Module 07's app/security.py promises, independent of anything built on
top of it.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import jwt
import pytest

from app.config import settings
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_return_the_plain_password():
    hashed = hash_password("dragon-slayer-1")
    assert hashed != "dragon-slayer-1"
    # A real bcrypt hash always starts with one of these version prefixes.
    assert hashed.startswith(("$2a$", "$2b$", "$2y$"))


def test_hashing_the_same_password_twice_gives_different_output():
    """See lessons/03-parametrize-and-mocking.md's "what a salt actually
    is" section -- this is that claim, proven, not just asserted."""
    first = hash_password("dragon-slayer-1")
    second = hash_password("dragon-slayer-1")
    assert first != second


def test_verify_password_accepts_the_correct_password():
    hashed = hash_password("dragon-slayer-1")
    assert verify_password("dragon-slayer-1", hashed) is True


def test_verify_password_rejects_the_wrong_password():
    hashed = hash_password("dragon-slayer-1")
    assert verify_password("not-the-password", hashed) is False


def test_create_access_token_round_trips_the_subject():
    token = create_access_token(subject="user-123")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"


def test_decode_access_token_rejects_a_tampered_signature():
    token = create_access_token(subject="user-123")
    # Flips the last character of the signature -- the third part after
    # the second `.` -- which is exactly what "tampering" with a JWT
    # means. See lessons/03-parametrize-and-mocking.md's JWT tampering
    # test for the fully worked, line-by-line version of this idea.
    header, payload_part, signature = token.rsplit(".", 2)
    tampered_char = "A" if signature[-1] != "A" else "B"
    tampered_token = f"{header}.{payload_part}.{tampered_char}{signature[1:]}"
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered_token)


def test_expired_token_is_rejected():
    """A **mock** (lessons/03-parametrize-and-mocking.md defines this term
    from scratch) standing in for "the real current time," so this test
    can deterministically simulate an hour passing without a real
    `time.sleep(3600)` ever executing. `unittest.mock.patch` temporarily
    replaces `app.security.datetime` -- note the target is
    `app.security.datetime`, the name as *security.py* imported it, not
    `datetime.datetime` -- for exactly the duration of this `with` block,
    then restores the real one automatically, even if this test fails.
    """
    frozen_now = datetime.now(UTC) - timedelta(hours=2)

    class _FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return frozen_now if tz else frozen_now.replace(tzinfo=None)

    with patch("app.security.datetime", _FrozenDatetime):
        token = create_access_token(subject="user-123")

    # `settings.access_token_expire_minutes` (60 by default) has long since
    # passed relative to `frozen_now` -- decoding now (with the real,
    # un-mocked clock again, since the `with` block above already exited)
    # must raise specifically because the token's `exp` claim is in the past.
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)

    # Sanity check the fixture itself isn't accidentally always failing:
    # confirm this app's real configured expiry is shorter than the 2-hour
    # gap this test manufactured above.
    assert settings.access_token_expire_minutes < 120
