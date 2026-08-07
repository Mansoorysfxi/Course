"""Exercise 01 -- Hash and Verify a Password.

See INSTRUCTIONS.md for the full task. This file has no FastAPI, no
database, and no QuestLog code -- just you and the `bcrypt` package,
exactly like Lesson 02's own runnable snippets. Fill in every function
marked with a `# TODO`, then run this file directly:

    python hash_practice.py
"""

import bcrypt


def hash_a_password(password: str) -> str:
    """Return a bcrypt hash of `password`, as a plain `str` (not bytes).

    See Lesson 02's "QuestLog's actual code, line by line" section for
    the exact three-step shape this function needs: encode to bytes,
    generate a fresh salt, hash, then decode back to a string.
    """
    # TODO: implement this function.
    raise NotImplementedError


def verify_a_password(password: str, hashed: str) -> bool:
    """Return True if `password` matches the bcrypt hash `hashed`, False
    otherwise.
    """
    # TODO: implement this function.
    raise NotImplementedError


def demonstrate_salting() -> None:
    """Hash the SAME password twice and print both hashes, plus whether
    they're equal. They should NOT be equal -- print a short explanation
    of why, in your own words, as part of this function's output.
    """
    # TODO: implement this function.
    raise NotImplementedError


def demonstrate_verification() -> None:
    """Hash one password, then verify it against (a) the correct
    password and (b) a different, wrong password. Print both results
    clearly labeled.
    """
    # TODO: implement this function.
    raise NotImplementedError


if __name__ == "__main__":
    print("=== Salting demonstration ===")
    demonstrate_salting()
    print()
    print("=== Verification demonstration ===")
    demonstrate_verification()
