"""Exercise 01 -- Hash and Verify a Password (reference solution).

See INSTRUCTIONS.md for the full task, and Lesson 02 for the full
explanation of every line below -- this solution matches
`backend/app/security.py`'s own `hash_password`/`verify_password`
functions, extended with two small demonstration functions.
"""

import bcrypt


def hash_a_password(password: str) -> str:
    """Return a bcrypt hash of `password`, as a plain `str` (not bytes)."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_a_password(password: str, hashed: str) -> bool:
    """Return True if `password` matches the bcrypt hash `hashed`, False
    otherwise."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def demonstrate_salting() -> None:
    """Hash the SAME password twice and print both hashes, plus whether
    they're equal."""
    password = "dragon-slayer-1"
    hash_one = hash_a_password(password)
    hash_two = hash_a_password(password)

    print(f"Password (both times): {password!r}")
    print(f"Hash 1: {hash_one}")
    print(f"Hash 2: {hash_two}")
    print(f"Equal?  {hash_one == hash_two}")
    print(
        "Explanation: bcrypt.gensalt() generates a brand-new random salt "
        "every time hash_a_password() runs, and that salt is baked directly "
        "into the returned string. Same password, different random salt "
        "each call -> completely different-looking hash output, even "
        "though both hashes will correctly verify against the same "
        "original password."
    )


def demonstrate_verification() -> None:
    """Hash one password, then verify it against the correct password and
    a wrong one."""
    correct_password = "correct-horse-battery-staple"
    wrong_password = "incorrect-horse-battery-staple"
    hashed = hash_a_password(correct_password)

    print(f"Stored hash: {hashed}")
    print(
        f"verify_a_password(correct_password, hashed) = "
        f"{verify_a_password(correct_password, hashed)}   (expected: True)"
    )
    print(
        f"verify_a_password(wrong_password, hashed)   = "
        f"{verify_a_password(wrong_password, hashed)}   (expected: False)"
    )


if __name__ == "__main__":
    print("=== Salting demonstration ===")
    demonstrate_salting()
    print()
    print("=== Verification demonstration ===")
    demonstrate_verification()
