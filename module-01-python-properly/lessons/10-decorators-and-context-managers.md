# Lesson 10 — Decorators and Context Managers: Opening the Hood

## What you'll learn

- What a decorator actually is, mechanically — built entirely from closures (Lesson 02) and the fact that functions are ordinary values in Python.
- How to write your own decorator from scratch, step by step, until the `@` syntax stops looking like magic.
- `functools.wraps` and why it matters.
- Decorators that take their own arguments.
- What `with` actually does, mechanically — `__enter__`/`__exit__`, the dunder methods behind every context manager.
- How to write your own context manager, two ways: a class, and the shorter `@contextmanager` generator-based approach.

## Why this matters

The master plan flags this lesson specifically for "full open the hood" treatment, because both decorators and context managers look like magic syntax the first time you see them (`@something` above a function; `with something:` around a block), and both are used *constantly* starting in Module 05 — FastAPI's entire routing system is built on decorators (`@app.get("/quests")`), and database connections, file handling, and test setups all lean on context managers. If you understand the mechanism now, in Python's plain form, nothing in FastAPI later will feel like unexplained magic — it'll feel like a specific, recognizable application of exactly what you're about to build by hand.

## Prerequisites

Lesson 02 (closures — decorators are built directly on this), Lesson 04 (generators — the `@contextmanager` approach is built on `yield`), Lesson 05 (dunder methods), Lesson 06 (`try`/`finally`), Lesson 08 (`with open(...)` — you've already *used* a context manager, this lesson shows you what it actually is).

## The concept, explained simply

Two ideas, both true in Python and false in C++: **functions are values**, just like an `int` or a `str` — you can assign a function to a variable, pass it as an argument to another function, and `return` it from a function, with zero special syntax. And **a decorator is nothing more than a function that takes a function as input and returns a (usually new, wrapping) function as output** — the `@` syntax you'll see below is purely a shorter way to write an assignment you could write out by hand. A **context manager** is, underneath `with`, an object implementing two specific dunder methods that guarantee "run this setup code, then guarantee this cleanup code runs no matter what" — the exact guarantee `try`/`finally` (Lesson 06) gives you, packaged into something reusable so you don't hand-write `try`/`finally` at every single call site.

## The details

### Step 1 — functions are values (the prerequisite fact)

```python
def shout(text):
    return text.upper() + "!"

my_function = shout          # NOT calling it — no parentheses — just storing a reference to it
print(my_function("hello"))
print(shout is my_function)  # the exact same function object, two names
```
**Run:** `python lesson10.py` → **Expected output:**
```
HELLO!
True
```

No parentheses after `shout` means "the function itself," not "call it." `my_function` now points at the exact same function object `shout` does — same idea as two names pointing at the same list from Lesson 03, just for a function instead of a list.

### Step 2 — a function that takes a function, and returns a function

```python
def loud_version(original_function):
    def wrapper(text):
        result = original_function(text)
        return f">>> {result} <<<"
    return wrapper

shout_loudly = loud_version(shout)
print(shout_loudly("hello"))
```
**Expected output:** `>>> HELLO! <<<`

**Line by line:** `loud_version` takes a function (`original_function`) as its parameter, defines a brand new inner function `wrapper` that calls the original and does something extra with its result, then `return`s `wrapper` itself (not the result of calling it). `wrapper` is a **closure** over `original_function` — exactly Lesson 02's mechanism — it "remembers" which specific function was passed in, even after `loud_version` has finished running. `shout_loudly` now refers to `wrapper`, permanently wired to call `shout` internally.

This — a function wrapping another function, adding behavior before/after/around the original call — **is a decorator.** You just wrote one, with zero special syntax.

### Step 3 — the `@` syntax is just sugar for exactly this

```python
def loud_version(original_function):
    def wrapper(text):
        result = original_function(text)
        return f">>> {result} <<<"
    return wrapper

@loud_version
def shout(text):
    return text.upper() + "!"

print(shout("hello"))
```
**Expected output:** `>>> HELLO! <<<` — identical result to Step 2.

**What `@loud_version` directly above `def shout(text):` actually does, with zero exceptions or special cases:** it's precisely equivalent to writing

```python
def shout(text):
    return text.upper() + "!"
shout = loud_version(shout)
```

That's the entire mechanism. `@decorator_name` above a function definition means "immediately after defining this function, pass it into `decorator_name`, and rebind this same name to whatever `decorator_name` returns." Nothing about `@` is a separate language feature beyond this substitution — it's purely a more readable way to write "wrap this function and reassign the name," right at the point where the function is defined, instead of several lines away.

### A genuinely useful decorator — timing and logging a function call

```python
import time
import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        print(f"Calling {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} returned {result!r} in {elapsed:.6f}s")
        return result
    return wrapper

@log_calls
def calculate_damage(base_damage, multiplier=1.0):
    return base_damage * multiplier

calculate_damage(20, multiplier=1.5)
```
**Expected output (your exact timing will differ):**
```
Calling calculate_damage((20,), {'multiplier': 1.5})
calculate_damage returned 30.0 in 0.000002s
```

**Line by line — this is the general-purpose decorator shape you'll reuse constantly:**
- `def wrapper(*args, **kwargs):` — using Lesson 02's `*args`/`**kwargs` here is exactly why that lesson introduced them: a decorator usually has no idea, in advance, what parameters the function it's wrapping will have, so it must accept and forward *anything*.
- `func(*args, **kwargs)` — calls the original function, spreading whatever positional/keyword arguments were actually received straight through to it, unchanged (Lesson 02's "spread on the way out" mechanism).
- `@functools.wraps(func)` — a decorator *for your decorator's inner function*, from the standard library. Without it, `wrapper` would completely replace `func`'s identity — `calculate_damage.__name__` would print `"wrapper"` instead of `"calculate_damage"`, and its docstring/other metadata would be lost too, breaking introspection tools, debuggers, and documentation generators that rely on a function correctly reporting its own name. `functools.wraps` copies that metadata from `func` onto `wrapper` for you. **Always include this on any decorator you write** — it's a one-line addition with no downside.

**Try it yourself:** remove `@functools.wraps(func)` and add `print(calculate_damage.__name__)` after the decorated definition. Predict the output before running it. (It prints `wrapper`, not `calculate_damage` — proof of exactly what `functools.wraps` was protecting you from.)

### A decorator that takes its own arguments — one more layer

```python
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def announce_quest(name):
    print(f"New quest available: {name}")

announce_quest("Slay the Dragon")
```
**Expected output:**
```
New quest available: Slay the Dragon
New quest available: Slay the Dragon
New quest available: Slay the Dragon
```

**Why there are three nested functions here, not two:** `@repeat(times=3)` needs `repeat(times=3)` to itself evaluate to something usable as a decorator (i.e., a function that takes a function and returns a function) *before* `@` ever applies it. So `repeat` takes the decorator's own argument (`times`) and returns `decorator` — a real decorator, in exactly Step 2's shape, which has closed over `times` (another Lesson 02 closure) so `wrapper` can use it. This three-layer pattern — "a function that returns a decorator" — is the standard shape for any decorator that itself needs configuration, and you'll see this exact shape in FastAPI's own decorators later (e.g. route decorators that take a path string as an argument).

### `with` — what it actually does, mechanically

You already used this in Lesson 08:
```python
with open("quests.txt", "r") as file:
    contents = file.read()
```

Here's the exact, real mechanism — `with EXPRESSION as NAME: BODY` is equivalent, with no simplification, to:

```python
manager = EXPRESSION
NAME = manager.__enter__()
try:
    BODY
finally:
    manager.__exit__(exc_type, exc_value, traceback)
```

**Line by line of what that means:** any object usable after `with` is called a **context manager**, and it earns that status by implementing exactly two dunder methods: `__enter__` (called once, at the start — its return value becomes whatever `as NAME` binds to) and `__exit__` (called once, guaranteed, when the block ends — whether it ended normally *or* because an exception was raised and is propagating through). This is precisely Lesson 06's `try`/`finally` guarantee, just packaged as a reusable object instead of hand-written at every call site. `open()`'s return value implements exactly this pair — `__enter__` returns the file object itself (which is why `file.read()` works inside the block), and `__exit__` closes the file, unconditionally, which is the real reason Lesson 08 told you to always prefer `with` over manual `open()`/`.close()`.

### Writing your own context manager — the class-based way

```python
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {elapsed:.6f}s")
        return False   # False means: do NOT suppress any exception that occurred

with Timer():
    total = sum(range(1_000_000))
print(total)
```
**Expected output (timing varies):**
```
Elapsed: 0.021next-line-varies
499999500000
```

**Line by line:**
- `__enter__(self)` — runs at the top of the `with` block; returning `self` means `as X:` (not used here, but available) would bind to the `Timer` instance itself.
- `__exit__(self, exc_type, exc_value, traceback)` — runs at the end, always. If the block raised an exception, `exc_type`/`exc_value`/`traceback` describe it (all three are `None` if the block completed normally, with no exception); returning `False` (or nothing, which Python treats as `False`) lets any such exception continue propagating normally after `__exit__` finishes its cleanup — returning `True` would *suppress* the exception entirely, which is occasionally useful but easy to misuse (silently swallowing real errors), so treat suppressing as a deliberate, rare choice, not a default.

### Writing your own context manager — the shorter `@contextmanager` way

Writing a full class with two dunder methods is more ceremony than most simple cases need. The standard library gives you a generator-based shortcut, directly reusing Lesson 04's `yield` mechanism:

```python
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Elapsed: {elapsed:.6f}s")

with timer():
    total = sum(range(1_000_000))
```

**Line by line — this is genuinely satisfying once Lesson 04 has clicked:** `@contextmanager` (itself a decorator, from the standard library) transforms a generator function into something usable after `with`. Everything *before* the `yield` becomes the equivalent of `__enter__`'s body; the single `yield` is the point where control passes into the `with` block's body (whatever's `yield`ed becomes the `as NAME` value, if you use one); everything *after* `yield` — guaranteed to run via the surrounding `try`/`finally`, exactly Lesson 06's mechanism again — becomes the equivalent of `__exit__`'s cleanup. One function, reading top-to-bottom in the order things actually happen, instead of two separate dunder methods on a class — often clearer for simple setup/cleanup pairs.

### A genuinely useful context manager for your capstone — safe JSON file writing

Recall Lesson 08's note about crash-mid-write leaving a corrupted save file. Here's the pattern that avoids it, as a reusable context manager:

```python
import json
import os

@contextmanager
def safe_json_write(path):
    temp_path = path + ".tmp"
    with open(temp_path, "w") as f:
        yield f
    os.replace(temp_path, path)   # only runs if the `with` block completed with no exception

with safe_json_write("quests.json") as f:
    json.dump({"quests": []}, f, indent=2)
```

**Why this is safer:** all writing happens to a *temporary* file first. `os.replace(temp_path, path)` — which atomically swaps the temp file into place as the real filename — only runs if the inner `with open(temp_path, "w") as f: yield f` block completed without raising. If your program crashes *during* the `json.dump` call, `quests.json` (the real file) was never touched at all — you're left with a leftover `.tmp` file and an intact, untouched previous save, rather than a half-written, corrupted `quests.json`. This is a genuinely production-grade pattern, not a toy example — you're encouraged to use exactly this in your capstone's save logic.

## Common mistakes & gotchas

- **Forgetting `*args, **kwargs` in a decorator's inner `wrapper` function.** Without them, your decorator only works on functions with that exact specific parameter signature, breaking the moment you apply it to anything else. Always accept and forward `*args, **kwargs` unless you have a specific, deliberate reason not to.
- **Forgetting `@functools.wraps(func)`.** Silently breaks `__name__`, docstrings, and anything introspecting the decorated function — a subtle bug that often only surfaces much later (e.g., in confusing debugger output, or a framework that relies on the function's real name).
- **Confusing the three-layer "decorator that takes arguments" pattern's nesting order.** `repeat(times) -> decorator(func) -> wrapper(*args, **kwargs)` — each layer exists for a specific reason (the decorator's own config, then the actual function being wrapped, then the eventual call) — write it out layer by layer rather than trying to collapse it prematurely.
- **Writing a context manager's `__exit__` (or the code after `yield` in the generator form) without a `try`/`finally`, and having cleanup code skipped when the block raises.** Wrap the risky part in `try`/`finally` inside your context manager itself if the cleanup absolutely must run even when something inside the `with` block fails.
- **Returning `True` from `__exit__` without meaning to, accidentally swallowing real exceptions.** Only return `True` (or use `return` with no value is `False`/falsy, which is correct default behavior) when you deliberately intend to suppress a specific, expected exception type — checking `exc_type` first.

## How this connects

Decorators and context managers are two of the most "it looked like magic until I saw the mechanism" topics in Python, and you've now built both from scratch. Lesson 11 (Async/Await) reuses the *exact same* pause/resume mechanism from `yield`-based generators (already familiar from `@contextmanager` above) to explain what `await` actually does. Module 05 (FastAPI) uses decorators as its primary routing syntax (`@app.get("/quests")`) and context managers for managing database sessions — both will look immediately familiar rather than magical. Your capstone is encouraged to use a decorator (e.g., logging each command the CLI runs) and the safe-write context manager shown above.

## Quick self-check

1. What two facts about Python make decorators possible at all?
2. Write out, in your own words, exactly what `@my_decorator` above a function definition is shorthand for.
3. Why does a decorator's inner `wrapper` function almost always need `*args, **kwargs`?
4. What are `__enter__` and `__exit__`, and what guarantee do they provide that's identical to `try`/`finally`?
5. In the `@contextmanager` generator style, what does the code *before* `yield` correspond to, and what does the code *after* it correspond to?
