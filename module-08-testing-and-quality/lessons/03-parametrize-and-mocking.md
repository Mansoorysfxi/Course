# Lesson 03 — Parametrize and Mocking

## What you'll learn

- How to run the *same* test logic against many different inputs with
  `@pytest.mark.parametrize`, instead of copy-pasting a test function
  once per input.
- What a **mock** actually is — from first principles, with no prior
  testing knowledge assumed — and the more general term **test double**
  it's one example of.
- How to use `unittest.mock.patch` to replace a real function or object,
  temporarily, for exactly the duration of one test.
- `pytest`'s own built-in `monkeypatch` fixture — a second way to do
  similar things, and when each is the better tool.
- Why you should mock the *boundary* of what you're testing, and almost
  never the thing you're actually trying to verify.

## Why this matters

Two real, everyday problems this lesson solves:

1. **"I need to test the same logic against ten different inputs, and
   copy-pasting the test ten times is obviously wrong."** `parametrize`
   is the direct fix — this module's real
   `backend/tests/test_auth.py::test_signup_rejects_invalid_input` and
   `backend/tests/test_quests.py::test_create_quest_rejects_invalid_input`
   both already use it, for exactly this reason.
2. **"My code depends on something slow, unreliable, or dangerous to run
   for real inside a test"** — the current date/time, a real email being
   sent, a real payment being charged, or (this module's own real
   example) real time actually passing so a JWT can genuinely expire.
   Mocking is how you test code that depends on such things *without*
   actually waiting an hour, sending a real email, or charging a real
   card, every single time your test suite runs.

## Prerequisites

Lesson 02 (fixtures, `conftest.py`) — mocking is often combined with
fixtures, and this lesson's examples assume you're comfortable with both
already.

## The concept, explained simply

### Parametrize, in one sentence

`@pytest.mark.parametrize` runs the exact same test function multiple
times, once per set of inputs you give it — think of it as a `for` loop
around a test, except each iteration is reported by `pytest` as its own,
separately pass/fail-able test.

### A mock, explained from scratch

Here is the game-dev analogy this lesson promised, worked all the way
through, no prior testing vocabulary assumed:

Imagine testing an Unreal Engine gameplay ability — "casting Fireball
costs 20 mana and deals damage equal to `PlayerLevel * 5`." To test this
properly, in isolation, you do **not** want to spin up a real player
controller connected to a real save file, a real network session, and a
real animation system just to check one number. Instead, you'd create a
**stand-in** object: something that *looks* like a player, as far as this
one ability cares (it has a `Level` property, a `Mana` property, a
`TakeDamage()` method you can check was called) — but is otherwise
completely fake, built by you, purely for this one test, with none of a
real player's actual complexity.

**A mock is exactly that stand-in, but for a function or object in your
Python (or JavaScript) code, instead of a game object.** More precisely,
a mock is a fake object that:

1. **Stands in for a real one**, wherever your code under test asks for
   it — your actual code never knows the difference.
2. **Records how it was used** — a mock remembers every time it was
   called, and with what arguments, so your test can later *assert on
   that history* ("was `send_email` called exactly once, with this
   recipient?") — a real object usually can't tell you this about
   itself at all.
3. **Can be told what to return**, in advance, for whatever your test
   needs it to return — "when this mock's `.get_current_price()` method
   is called, always return `9.99`," regardless of what a real pricing
   API would actually say right now.

The broader, more formal term for "any fake stand-in used in a test" is
a **test double** — borrowed directly from the movie industry's "stunt
double." A **mock**, specifically, is one *kind* of test double — the
kind that specifically records how it was used, so you can assert on
that history afterward. (Other kinds of test double exist too — a
**stub** is a simpler double that just returns canned values with no
recording at all; a **fake** is a double with a real, working, but
simplified implementation, like an in-memory dictionary standing in for
a real database. This course's own tests, and Python's own
`unittest.mock` library, use the word "mock" loosely enough to cover most
of these — the important thing is the concept, not memorizing which exact
sub-term applies where.)

## The details

### `@pytest.mark.parametrize`, step by step

Continue from Lesson 02's scratch folder (or create a fresh one) with
`calculator.py`'s `add` function. Instead of three separate test
functions for three different inputs:

```python
# test_calculator.py
import pytest
from calculator import add


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 5),
        (-2, -3, -5),
        (5, 0, 5),
        (0, 0, 0),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

Run `python -m pytest -v`:

**Expected output:**
```
test_calculator.py::test_add[2-3-5] PASSED                              [ 25%]
test_calculator.py::test_add[-2--3--5] PASSED                           [ 50%]
test_calculator.py::test_add[5-0-5] PASSED                              [ 75%]
test_calculator.py::test_add[0-0-0] PASSED                             [100%]

============================== 4 passed in 0.01s ===============================
```

**Line by line:** `@pytest.mark.parametrize("a, b, expected", [...])` —
the first argument is a comma-separated string naming the parameters this
test function will receive; the second argument is a list of tuples,
each one supplying one full set of values for those parameters, one tuple
per test run. `pytest` calls `test_add` once per tuple, and — this is the
part worth noticing — reports each call as its own, individually
pass/fail-able test, with the actual input values shown right in the test
name (`test_add[2-3-5]`), so a single failing case among many is
immediately obvious, not buried inside one big test function with four
separate `assert` lines.

**Try it yourself:** change one tuple to `(2, 3, 999)` (deliberately
wrong) and re-run. Predict, before running, exactly which of the four
`test_add[...]` lines will report `FAILED` and which three will still
say `PASSED`. (This is the whole point of parametrize over one test with
four `assert`s: one wrong case fails *by itself*, without hiding whether
the other three still pass.)

This module's real `test_signup_rejects_invalid_input` in
`backend/tests/test_auth.py` uses the exact same mechanism against two
genuinely different *kinds* of bad input (a malformed email, and a
too-short password), both of which the backend should reject with the
same `422` status — one test function, run twice, each failure reported
separately.

### Your first mock: `unittest.mock.patch`

Add a function to `calculator.py` that depends on something outside your
control — the current date:

```python
# calculator.py
from datetime import date


def days_until_new_year(today: date | None = None) -> int:
    """Real-world default (today=None means "use the real current date")
    -- exactly the kind of function that's awkward to test naively,
    because the "right answer" depends on literally what day it is when
    the test happens to run."""
    if today is None:
        today = date.today()
    new_year = date(today.year + 1, 1, 1)
    return (new_year - today).days
```

Testing this "for real" (calling it with no arguments) would give a
different expected answer every single day you ran the test — exactly
the "deterministic" property Lesson 01 said a real test must have. A
mock fixes this by **replacing** `date.today` itself, temporarily, with
something that always returns one specific, known date:

```python
# test_calculator.py
from datetime import date
from unittest.mock import patch
from calculator import days_until_new_year


def test_days_until_new_year_from_christmas():
    fake_today = date(2026, 12, 25)
    with patch("calculator.date") as mock_date:
        mock_date.today.return_value = fake_today
        # `today.year + 1` etc. inside the real function still needs
        # `date(...)` itself to keep working normally -- see the note below.
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
        assert days_until_new_year() == 7
```

Run `python -m pytest -v`. **Expected:** `1 passed`, no matter what
today's real date is when you run it.

**Line by line, the part that trips everyone up at first:** `patch(
"calculator.date")` — note the target string is `"calculator.date"`, the
name **as `calculator.py` itself imported it** (`from datetime import
date`, at the top of that file), not `"datetime.date"`. This is the
single most common mocking mistake there is, worth its own callout
below. `with patch(...) as mock_date:` — for exactly the duration of this
`with` block, every place `calculator.py`'s code says `date`, it's really
using `mock_date` instead, a completely different object created by
`unittest.mock` that records every call made to it and lets you control
what those calls return. `mock_date.today.return_value = fake_today` sets
up rule 3 from this lesson's definition above: "when `.today()` gets
called on this mock, always return this specific, fixed date." The moment
this `with` block ends, `calculator.date` is automatically restored to
the real `datetime.date` — even if the test had failed partway through,
the same "guaranteed cleanup" property a fixture's `yield` gives you
(Lesson 02).

(The `side_effect` line above is a real wrinkle worth being honest about:
because this test mocks `date` itself, not just `date.today`, the *rest*
of `days_until_new_year`'s code — which also calls `date(today.year + 1,
1, 1)` to build the "next New Year" — would otherwise call the mock too,
and get back another mock object instead of a real date, breaking the
subtraction at the end. `side_effect` tells the mock "when called
directly (not through `.today()`), actually run this real function
instead." A simpler, usually better alternative — patching only the one
specific method you need, not the whole module — is one of this lesson's
"Common mistakes & gotchas" below.)

### The exact mock this module's real tests use: freezing time for a JWT

This module's real `backend/tests/test_security.py::test_expired_token_is_rejected`
needs to prove that a JWT rejects itself once its expiry time has passed
— without a real test ever waiting a real hour. Here's the relevant
piece, explained now that you understand every part of it:

```python
from datetime import datetime, timedelta, timezone
from unittest.mock import patch


def test_expired_token_is_rejected():
    frozen_now = datetime.now(timezone.utc) - timedelta(hours=2)

    class _FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return frozen_now if tz else frozen_now.replace(tzinfo=None)

    with patch("app.security.datetime", _FrozenDatetime):
        token = create_access_token(subject="user-123")
    # ... assert decoding this token now raises jwt.ExpiredSignatureError
```

**Line by line:** `_FrozenDatetime` is a small subclass of the real
`datetime` class, overriding only `.now()` to always return a moment two
hours in the past — everything else about a real `datetime` still works
normally on it, since it *is* a real `datetime` subclass, sidestepping
the `side_effect` wrinkle from the previous example entirely. `patch(
"app.security.datetime", _FrozenDatetime)` replaces the name `datetime`
**inside `app/security.py`** with this frozen version, for the duration
of the `with` block. `create_access_token` (Module 07's real function)
calls `datetime.now(timezone.utc)` internally to compute the token's
expiry — while the patch is active, it unknowingly uses the *frozen* two
hours slower `.now()`, so the resulting token's `exp` claim genuinely,
correctly encodes "already expired two hours ago" — no real waiting, no
real clock manipulation on your actual machine, and the test passes or
fails identically no matter what today's real date is.

### `pytest`'s own `monkeypatch` fixture

`pytest` ships a built-in fixture, `monkeypatch`, that does a similar job
to `unittest.mock.patch` for simpler cases — especially replacing a
single value or environment variable, with no need to build a whole
mock object:

```python
def test_days_until_new_year_with_monkeypatch(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return date(2026, 12, 25)

    monkeypatch.setattr("calculator.date", FixedDate)
    assert days_until_new_year() == 7
```

**When to reach for which:** `monkeypatch` (a fixture — automatically
undoes itself after the test, exactly like `patch`'s `with` block does,
just via `pytest`'s own fixture-teardown mechanism instead) tends to read
more simply for "replace this one attribute/environment variable with
this one value." `unittest.mock.patch`'s explicit `Mock`/`MagicMock`
objects (which `patch` gives you automatically, as in the first example
above) are the better tool when you specifically need to **assert on how
something was called** afterward — e.g. `mock_send_email.assert_called_once_with(
"hero@example.com")` — which `monkeypatch` alone doesn't give you.

### The most important rule: mock at the boundary, not the thing you're testing

A mock should replace something **outside** the code you're actually
trying to verify — the real current time, a real external API, a real
slow database call *you're not the one testing right now*. It should
almost never replace the actual function whose correctness is the
test's whole point. A test that mocks `add` itself while "testing"
`add` would always pass, checking nothing real at all — an extreme,
obviously-wrong example, but the same mistake shows up more subtly when
someone mocks too much of a system under test and ends up with a test
that can never fail no matter what the real code does.

## Common mistakes & gotchas

- **Patching the wrong path — the single most common mocking bug.**
  `patch("datetime.date")` (patching where `date` was *originally
  defined*) instead of `patch("calculator.date")` (patching where it's
  *used*) silently does nothing to `calculator.py`'s own already-imported
  reference. Remember: `from datetime import date` inside `calculator.py`
  creates a **new name**, `calculator.date`, pointing at the same object
  — `patch` needs to know exactly *which* name, in *which* namespace, to
  swap out, and that's always the one the code under test actually uses,
  not the one it originally came from.
- **Forgetting a mock exists at all, and being confused why a value is
  a strange `<MagicMock id=...>` object instead of the real thing.** If
  you see `MagicMock` anywhere in an error message or a printed value
  you didn't expect, some code path called a method on a mock that
  wasn't specifically told what to return, and `unittest.mock`'s default
  behavior — auto-generating a fresh, generic mock for literally any
  attribute or call you ask of it — kicked in silently.
- **Over-mocking.** A test that mocks five different things to check one
  line of real logic has probably drifted into testing "does my mock
  setup work" instead of "does my real code work." If a test needs that
  much mocking, it's often a sign the function under test is doing too
  many unrelated things at once — a design smell mocking makes visible,
  not a mocking problem to work around.
- **Mocking something and then never asserting on it.** `patch(...)`
  alone doesn't check anything — it just swaps an implementation. If your
  test's whole point is "was this called correctly," you still need an
  explicit `mock_thing.assert_called_once_with(...)` (or similar) — the
  patch on its own proves nothing.

## How this connects

Lesson 02's fixtures and this lesson's parametrize/mocking are the last
purely-Python-fundamentals pieces before this module gets concrete about
the actual application: Lesson 04 is a short, standalone lesson on
debugging technique (useful whether or not a test is involved at all);
Lesson 05 tests real FastAPI endpoints, using `httpx` instead of mocking
the HTTP layer at all (a deliberate choice explained there); Lesson 06
tests against a real, if temporary, database rather than mocking it out.
Frontend testing (Lesson 07) uses mocking constantly — `vi.mock` (this
module's real `ProtectedRoute.test.tsx` and `QuestListPage.test.tsx`) is
JavaScript/Vitest's direct equivalent of `unittest.mock.patch`, applied
to an entire module import instead of one attribute — the exact same
underlying idea you just learned here, in a new syntax.

## Quick self-check

1. What does `@pytest.mark.parametrize` actually do, mechanically, to a single test function? How does `pytest` report four parametrized cases if one of them fails?
2. In your own words, using the game-dev analogy or your own: what is a mock, and what's the difference between a mock and the broader term "test double"?
3. Why does `patch("calculator.date")` work while `patch("datetime.date")` would silently do nothing, for a test inside `test_calculator.py` testing a function defined in `calculator.py`?
4. What's the real, practical difference between `unittest.mock.patch` and `pytest`'s built-in `monkeypatch` fixture — when would you reach for one over the other?
5. Why is "mock the boundary, not the thing you're testing" an important rule, and what would go wrong with a test that mocked the exact function it claims to be testing?
