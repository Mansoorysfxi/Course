# Lesson 02 — pytest Fundamentals and Fixtures

## What you'll learn

- How to write your first real `pytest` test function, from a completely
  empty file, and exactly what makes `pytest` recognize it as a test at
  all.
- How `pytest`'s plain `assert` statement works, and why `pytest` needs no
  special assertion methods the way some other languages' test frameworks
  do.
- How `pytest` **discovers** tests automatically — the file and function
  naming rules that make this work, and what happens if you don't follow
  them.
- What a **fixture** actually is, from scratch, with a game-dev analogy —
  and how to write one, use one, and understand its **scope**.
- What `conftest.py` is for, and why fixtures defined there are available
  everywhere without an import.
- What test **coverage** means, and how to measure it.

## Why this matters

Every test this module (and your career) will ever write is built from
exactly the pieces in this lesson. Lesson 01 was about *why* to test;
this lesson is where you actually start doing it, on the simplest
possible code first — pure functions, no database, no HTTP, no async —
so every new idea from here on (parametrize, mocking, testing a real
FastAPI endpoint) adds exactly one new piece on top of a foundation
you've already used with your own hands.

## Prerequisites

Module 01's functions/`assert` statement, and this module's `lessons/00-setup.md`
(pytest installed and verified). Lesson 01 (why tests exist, the testing
pyramid) for the vocabulary this lesson uses throughout.

## The concept, explained simply

A **fixture** is best understood by analogy to something you already do
in game development: **level setup before a test scenario runs.** Imagine
an automated in-game test that checks "does picking up a health potion
restore 25 HP?" Before that test can even ask its real question, *something*
has to spawn a player Actor with a known starting HP and spawn a health
potion nearby — the same setup, needed by many different test scenarios
(a different test might check "can you still pick up a potion while at
full HP?"), copy-pasted into every single one, was always exactly this:
tedious, error-prone boilerplate.

A **fixture** is `pytest`'s name for a function whose entire job is doing
that setup work *once*, in one place, that any test can then simply ask
for by name — and, if that setup created something that needs cleaning up
afterward (a spawned Actor to destroy, a database connection to close), a
fixture can do that automatically too, every time, even if the test
itself failed partway through. You never call a fixture function directly
— you just *name it as a parameter* to your test function, and `pytest`
handles the rest, a mechanism this lesson opens the hood on completely,
piece by piece, below.

## The details

### Step 1 — The simplest possible test

Create a fresh scratch folder anywhere outside this course's repo (e.g.
`~/scratch/pytest-practice/`) and, inside it, a file `calculator.py`:

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b
```

Now a test file, `test_calculator.py`, **in the same folder**:

```python
# test_calculator.py
from calculator import add


def test_add_two_positive_numbers():
    result = add(2, 3)
    assert result == 5
```

Run it:
```bash
python -m pytest
```

**Expected output (abbreviated — the real header also prints your platform,
`pytest` version, and installed plugins, which vary by machine):**
```
============================= test session starts ==============================
collected 1 item

test_calculator.py .                                                       [100%]

============================== 1 passed in 0.01s ==============================
```

**Line by line:**
- `from calculator import add` — a completely ordinary Python import.
  `pytest` needs no special import of its own inside this file for the
  test to work — just plain Python, plus one `assert`.
- `def test_add_two_positive_numbers():` — the function's name starts
  with `test_`. This is not a style choice — it's how `pytest` finds
  this function at all. `pytest`'s **test discovery** rule: it looks in
  every file matching `test_*.py` or `*_test.py`, and inside each one,
  every function whose name starts with `test_` (and every class whose
  name starts with `Test`, containing methods that start with `test_` —
  this course sticks to plain functions throughout, the simpler and more
  common style for the kind of tests it teaches). A function named
  `check_add` or `add_test_case` would be **silently ignored** — no
  error, no warning, `pytest` just never calls it, which is exactly why
  this is this lesson's first "Common mistakes & gotchas" entry below.
- `result = add(2, 3)` — calls the real function, exactly like any other
  Python call.
- `assert result == 5` — the entire "did this work" check. If `result`
  really is `5`, `assert` does nothing at all and the test function
  returns normally, which `pytest` reports as **passed**. If `result`
  were, say, `6`, `assert` would raise an `AssertionError`, and `pytest`
  reports that as **failed** — catching the exception itself, so one
  failing test never crashes the whole run; every other test still runs.

**Try it yourself:** change `assert result == 5` to `assert result == 6`
and re-run `python -m pytest`. Before running it, predict exactly what
you'll see. (Expected: a `FAILED` line, plus a detailed `assert 5 == 6`
block showing the actual value `pytest` computed — this detail, showing
you the *real* left-hand value, not just "assertion failed," is one of
`pytest`'s most-loved features, called **assertion introspection**; most
older test frameworks require special methods like
`assertEqual(result, 5)` specifically so the framework can show you that
detail, while `pytest` gets it from a plain `assert` by rewriting your
test file's bytecode at collection time — genuinely "magic" in the sense
Rule 2 asks this course to open the hood on, though the mechanism itself
— bytecode rewriting — is well beyond this lesson's scope; what matters
practically is: plain `assert` is enough, always.)

### Step 2 — Several tests, and what "collected N items" means

Add two more tests to `test_calculator.py`:

```python
def test_add_negative_numbers():
    assert add(-2, -3) == -5


def test_add_zero():
    assert add(5, 0) == 5
```

Run `python -m pytest -v` (the `-v`, "verbose," flag lists every test by
name instead of just printing dots):

**Expected output:**
```
test_calculator.py::test_add_two_positive_numbers PASSED               [ 33%]
test_calculator.py::test_add_negative_numbers PASSED                   [ 66%]
test_calculator.py::test_add_zero PASSED                               [100%]

============================== 3 passed in 0.01s ===============================
```

Each test function is completely independent — `pytest` doesn't care what
order they're defined in, and (by design) each one should never depend on
another one having run first. This independence is what makes it safe to
run just one test by name while you're working on it:

```bash
python -m pytest test_calculator.py::test_add_zero -v
```
**Expected:** only that one test runs and is reported.

### Step 3 — Testing that a function correctly raises an exception

Some functions are *supposed* to raise an exception for bad input — Module
01's exception-handling lesson already covered `raise`/`try`/`except`;
testing that a function raises the *right* exception needs one new tool,
`pytest.raises`, used as a context manager (Module 01's `with` syntax):

```python
# calculator.py (add this)
def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
```

```python
# test_calculator.py
import pytest
from calculator import safe_divide


def test_safe_divide_normal_case():
    assert safe_divide(10, 2) == 5


def test_safe_divide_by_zero_raises_value_error():
    with pytest.raises(ValueError):
        safe_divide(10, 0)
```

Run `python -m pytest -v`. **Expected:** both pass.

**Line by line:** `with pytest.raises(ValueError):` — everything
indented inside this block is expected to raise a `ValueError` *somewhere*
inside it. If it does, `pytest.raises` catches that exception itself
(so it never propagates up and crashes the test) and the test passes.
**If the code inside the block does *not* raise a `ValueError`** — either
it raises nothing at all, or it raises some other, different exception
— `pytest.raises` itself raises a `Failed` error, and the test correctly
fails, because "the function was supposed to reject this input and
didn't" is exactly as real a bug as any wrong return value. You can
also check the exception's actual message, when that matters:

```python
def test_safe_divide_by_zero_message():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        safe_divide(10, 0)
```

`match=` takes a regular expression (Module 01, if you covered `re`
there — a plain substring like this one also works as a simple pattern)
checked against the exception's own string message — use this when the
*specific wording* of the error matters to your test, not just that
*some* `ValueError` happened.

### Step 4 — A fixture, from scratch

Real code rarely tests pure, no-setup functions like `add`. Add a small,
QuestLog-flavored function to `calculator.py` — a stand-in for "some
setup this test needs before it can ask its real question":

```python
# calculator.py (add this below `add`)
class ShoppingCart:
    def __init__(self):
        self.items: list[str] = []

    def add_item(self, name: str) -> None:
        self.items.append(name)

    def total_items(self) -> int:
        return len(self.items)
```

Without a fixture, testing this means repeating the same setup line in
every single test:

```python
# test_calculator.py
from calculator import ShoppingCart


def test_new_cart_is_empty():
    cart = ShoppingCart()          # <- setup, copy-pasted
    assert cart.total_items() == 0


def test_adding_one_item():
    cart = ShoppingCart()          # <- the exact same setup, again
    cart.add_item("Healing Potion")
    assert cart.total_items() == 1
```

Two tests, one line of real setup each — tolerable here, but imagine ten
tests, and the setup being five lines instead of one (spawning a
database connection, or an authenticated user, both of which this
module's real tests need). A **fixture** moves that setup into one place:

```python
# test_calculator.py
import pytest
from calculator import ShoppingCart


@pytest.fixture
def empty_cart():
    """A fixture -- a function decorated with @pytest.fixture. Its
    return value is what gets handed to any test that asks for it."""
    return ShoppingCart()


def test_new_cart_is_empty(empty_cart):
    assert empty_cart.total_items() == 0


def test_adding_one_item(empty_cart):
    empty_cart.add_item("Healing Potion")
    assert empty_cart.total_items() == 1
```

Run `python -m pytest -v`:
**Expected:** both tests pass, exactly as before.

**Line by line, the part that looks like magic:** `test_new_cart_is_empty`
takes a parameter named `empty_cart`. Nowhere in this file does anything
call `empty_cart()` and pass the result in — and yet, somehow, the
parameter really is a fresh `ShoppingCart` instance every time. Here is
exactly what `pytest` does, with no magic left unexplained: **before
calling any test function, `pytest` looks at that function's parameter
names. For each one, it searches for a `@pytest.fixture`-decorated
function with that exact name** (checked in this file, and in any
`conftest.py` — see Step 5 — visible from this file's location). It
calls *that* function, takes its return value, and passes it as the
argument with the matching name. This is the entire mechanism, start to
finish — no more, no less. `pytest` calls this **dependency injection**
(the same term Module 05, Lesson 04 used for FastAPI's own `Depends` —
not a coincidence; FastAPI's dependency system was directly inspired by
exactly this pytest feature, and this module's own
`backend/tests/conftest.py` fixtures (Lesson 05) will make that
connection completely concrete).

**Crucially: a fresh `ShoppingCart()` is created for *each* test that
asks for `empty_cart`**, not one shared instance reused across both — so
one test's changes (`add_item`) can never leak into another test and
silently affect its result. This "fresh, isolated setup, guaranteed,
every single time" property is a fixture's entire value.

### Step 5 — Cleanup: the part of a fixture that runs *after* the test

Some setup needs to be undone afterward — closing a file, disconnecting
from a database. A fixture does this with `yield` instead of `return`:

```python
@pytest.fixture
def cart_with_logging():
    print("\n[setup] creating cart")
    cart = ShoppingCart()
    yield cart                      # <- the test runs here, using `cart`
    print("[teardown] cart is done")  # <- runs after the test finishes
```

Run `python -m pytest -v -s` (`-s` tells `pytest` to actually show
`print()` output, which it hides by default):

**Line by line:** everything before `yield` is **setup** — it runs
*before* the test body. The value after `yield` (`cart`) is exactly what
gets handed to the test, the same as a plain `return` would. Everything
*after* `yield` is **teardown** — and `pytest` guarantees it runs even if
the test itself raised an exception partway through, the exact same
"guaranteed cleanup no matter what" property Module 01's context managers
(`with` statements) and Module 06's `async with` session pattern both
rely on — a fixture using `yield` is, under the hood, working the same
way a context manager does.

### Step 6 — `conftest.py`: fixtures without an import

Create a new file, `conftest.py`, in the same folder, and move
`empty_cart` into it:

```python
# conftest.py
import pytest
from calculator import ShoppingCart


@pytest.fixture
def empty_cart():
    return ShoppingCart()
```

Delete the `empty_cart` fixture (and its `import pytest` line, if nothing
else in the file still needs it) from `test_calculator.py`, but leave the
two tests that use it exactly as they are — **no import of `empty_cart`
added anywhere in `test_calculator.py`.**

Run `python -m pytest -v` again. **Expected:** the exact same two tests
still pass, completely unchanged, despite `empty_cart` no longer living
in the same file at all.

**Why this works:** `pytest` automatically discovers a file literally
named `conftest.py` in the same folder as your tests (and in every parent
folder, all the way up), and treats every fixture defined there as
available to every test file in that folder *and every folder below it*
— with no import statement needed at all. This is the mechanism this
module's real `backend/tests/conftest.py` relies on entirely: every test
file under `backend/tests/` (`test_auth.py`, `test_quests.py`,
`test_security.py`) uses fixtures like `client` and `signup_and_login`
that are defined *only* in `conftest.py`, and none of those test files
import them — `pytest` finds them by name, automatically, exactly as you
just proved to yourself here.

### Step 7 — Fixture scope: how often does setup actually run?

By default, a fixture runs **fresh, once per test function** that asks
for it — you already saw this in Step 3 (`empty_cart` was a brand-new,
empty cart in *both* tests, never shared). Sometimes that's wasteful: if
setting something up is genuinely expensive (starting a real database
connection, say), running it fresh for every single one of hundreds of
tests adds up. `@pytest.fixture(scope="module")` changes this to "once
per test *file*," shared across every test in that file:

```python
@pytest.fixture(scope="module")
def expensive_setup():
    print("\n[setup] this only prints ONCE for this whole file")
    return "some expensive resource"
```

**A genuine trade-off, not a free win:** a `module`-scoped (or wider —
`session`-scoped, meaning "once for the entire test run") fixture is
faster, but anything it returns is now **shared** across multiple tests —
if one test mutates it, that change is visible to every later test that
asks for the same fixture in the same file, silently reintroducing the
exact "one test's leftover state affects another" bug fixtures exist to
prevent in the first place. This module's own `db_session` fixture
(`backend/tests/conftest.py`, covered fully in Lesson 06) is deliberately
**function**-scoped (`pytest`'s default — no `scope=` argument needed at
all) for exactly this reason: every single test gets a genuinely fresh,
empty database, at the cost of recreating it every time.

### Step 8 — Fixtures that return a function ("factory fixtures")

Sometimes one test needs the *same kind* of setup more than once, with
different arguments each time — this module's real `signup_and_login`
fixture (`backend/tests/conftest.py`) is exactly this: a test that checks
ownership isolation needs *two* separate logged-in users, not one.

```python
@pytest.fixture
def cart_factory():
    """Returns a FUNCTION, not a cart directly -- the test calls that
    function itself, as many times as it needs, with different arguments
    each time."""

    def _make_cart(*initial_items: str) -> ShoppingCart:
        cart = ShoppingCart()
        for item in initial_items:
            cart.add_item(item)
        return cart

    return _make_cart


def test_two_separately_stocked_carts(cart_factory):
    hero_cart = cart_factory("Sword", "Shield")
    villain_cart = cart_factory("Poison Vial")

    assert hero_cart.total_items() == 2
    assert villain_cart.total_items() == 1
```

**Line by line:** `cart_factory` itself is a completely ordinary
fixture — `pytest` calls it once per test, exactly like `empty_cart`.
What makes it a "factory" is simply *what it returns*: not a `ShoppingCart`
directly, but a function (`_make_cart`) that the test itself then calls,
by hand, as many times as it wants. This is plain Python — a function
that returns another function is nothing special on its own — the
"factory fixture" pattern is just this ordinary technique, applied to
something `pytest` happens to inject for you.

### An aside: helper function vs. fixture — when to use which

Not every piece of reusable test setup needs to be a fixture. This
module's `backend/tests/test_quests.py` has a plain function,
`_create_quest(client, headers, **overrides)`, that is **not** a fixture
at all — just an ordinary Python function that several tests call
directly. The distinction: reach for a **fixture** when `pytest` itself
needs to manage the setup/teardown lifecycle (especially anything using
`yield` for cleanup, or anything you want available to many test files
via `conftest.py` with zero imports); reach for a **plain helper
function** when it's just "a few lines I don't want to repeat" that don't
need any lifecycle management and are only used by one file — importing
or defining a plain function is simpler, and simpler is better when it's
sufficient.

### Coverage: how much of your real code did the tests actually run?

Install `pytest-cov` (already in this module's `requirements-dev.txt`)
and run:
```bash
python -m pytest --cov=calculator --cov-report=term-missing
```
**Expected output (abbreviated):**
```
Name            Stmts   Miss  Cover   Missing
---------------------------------------------
calculator.py       9      0   100%
---------------------------------------------
TOTAL               9      0   100%
```

**Line by line:** `--cov=calculator` tells `pytest-cov` which module to
measure. `Stmts` is the number of executable statements in that file;
`Miss` is how many of them **never ran at all** while the test suite
executed; `Cover` is the resulting percentage; `--cov-report=term-missing`
adds a `Missing` column naming the exact line numbers that never ran, so
you know precisely what to write a test for next. Coverage tells you
*where you have zero tests* — it cannot tell you whether the tests you
already wrote check the right thing (Lesson 01's "100% coverage is not
the goal" box).

## Common mistakes & gotchas

- **A test function that doesn't start with `test_` is silently
  skipped — no error at all.** `pytest` never tells you "I ignored
  `check_add_works`" — it simply never calls it, and a suite with a typo
  like this can go months with a "passing" test suite that's quietly
  missing a whole test. If a test you *know* you wrote isn't showing up
  in `pytest`'s output at all (not even as a failure), check its name
  first.
- **`fixture 'empty_cart' not found`.** Either the fixture's name is
  spelled differently than the test's parameter name (they must match
  *exactly*), or the fixture is defined in a file `pytest` can't see from
  where the test lives — a fixture in `conftest.py` is visible to test
  files in that same folder and below, never in a sibling folder or
  above it.
- **Forgetting `yield` needs to actually be reached.** If setup code
  *before* `yield` raises an exception, the fixture never hands anything
  to the test at all, and `pytest` reports the test as an **error**
  (distinct from a **failure** — an error means something went wrong
  before your test's own `assert`s even got a chance to run; a failure
  means an `assert` ran and didn't match).
- **Mutating a `module`- or `session`-scoped fixture's return value and
  being surprised a *later, unrelated* test sees the mutation.** This is
  the trade-off Step 6 named directly — if you need real isolation
  between tests, use the default (function) scope, even though it's
  slower.
- **Writing a fixture that itself depends on another fixture, and being
  surprised at the order things run in.** A fixture can take other
  fixtures as its own parameters, exactly like a test can — `pytest`
  resolves the whole chain automatically, running each one's setup
  before the fixture (or test) that asked for it. This module's real
  `client` fixture (`backend/tests/conftest.py`) does exactly this: it
  takes `db_session` as a parameter, so asking for `client` in a test
  transitively gets you a fresh database too, with zero extra code in
  the test itself.

## How this connects

Every fixture in this module's real `backend/tests/conftest.py`
(`db_session`, `client`, `signup_and_login`) is built from nothing more
than what this lesson just taught: `@pytest.fixture`, `yield` for
cleanup, and a factory fixture for `signup_and_login` (since ownership
tests need more than one logged-in user). Lesson 03 adds two more tools
— `@pytest.mark.parametrize` and mocking — on top of this same
foundation. Lesson 05 shows exactly how `client` (a fixture you now
understand completely) makes testing a real FastAPI endpoint possible at
all.

## Quick self-check

1. What two conditions must be true about a function's name and its file's name for `pytest` to discover and run it as a test?
2. What, precisely, does `assert some_value == expected_value` do if the two are equal — and if they're not?
3. Explain, in your own words and with no hand-waving, exactly how a test function that takes a fixture's name as a parameter ends up receiving that fixture's return value. What decorator makes a function a fixture at all?
4. What is the difference between the code before `yield` in a fixture and the code after it, and when does each part run?
5. Why does this module's real `db_session` fixture use the *default* (function) scope instead of a wider one like `module` or `session`, even though that means recreating the database schema for every single test?
