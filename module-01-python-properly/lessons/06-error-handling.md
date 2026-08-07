# Lesson 06 — Error Handling: Exceptions, try/except/finally, Custom Exceptions

## What you'll learn

- What an exception actually is, and how Python's error-handling model differs fundamentally from C++'s (and from checking return codes).
- `try`/`except`/`else`/`finally` — what each block is for, and the order they run in.
- Catching specific exception types vs. catching everything, and why specificity matters.
- How to deliberately raise your own exceptions with `raise`.
- How to define and use custom exception classes.

## Why this matters

You'll be reading Python tracebacks constantly (Module 00, Lesson 02, already taught you the systematic *reading* skill) — this lesson teaches the other half: deliberately catching, handling, and raising exceptions yourself, so your programs can respond to bad input or unexpected conditions gracefully instead of crashing, and so *other* code calling yours gets useful, specific errors instead of a generic failure. Your capstone reads/writes a JSON file from disk — file I/O is exactly the kind of operation that fails in the real world (missing file, corrupted content, permissions) and needs deliberate error handling, not an assumption that it always works.

## Prerequisites

Lessons 01–05. Custom exceptions are themselves classes, using inheritance from Lesson 05.

## The concept, explained simply

C++ has multiple, inconsistent ways of signaling "something went wrong": a return code you might forget to check, a null pointer, an actual C++ exception (used less consistently than in some other languages). Python picked one consistent mechanism for the entire language: when something goes wrong, an **exception** — an object describing what happened — is **raised**, which immediately stops normal execution and starts unwinding up through whichever functions are currently running, looking for code that says "I know how to handle this specific kind of problem." If nothing catches it anywhere up that chain, the program crashes and prints the traceback you already learned to read in Module 00. This is Python's *only* mechanism for signaling errors — there's no separate "check a return code" convention to also remember, which is simpler than C++'s mixed approaches but means you must consciously decide where exceptions should be caught.

## The details

### A crash, and then catching it

```python
def get_reward(rewards, quest_name):
    return rewards[quest_name]

quest_rewards = {"slay_dragon": 500}
print(get_reward(quest_rewards, "find_amulet"))
```
**Run:** `python lesson06.py` → **Expected output:** a crash:
```
Traceback (most recent call last):
  File "lesson06.py", line 5, in <module>
    print(get_reward(quest_rewards, "find_amulet"))
  File "lesson06.py", line 2, in get_reward
    return rewards[quest_name]
KeyError: 'find_amulet'
```
(Recall Module 00 Lesson 02's method: read the last line first — `KeyError: 'find_amulet'` — then find your own code in the trace.)

Now catch it instead of crashing:

```python
try:
    print(get_reward(quest_rewards, "find_amulet"))
except KeyError:
    print("That quest doesn't exist.")
```
**Expected output:** `That quest doesn't exist.` — the program kept running instead of crashing.

**Line by line:**
- `try:` — marks a block where you expect a *specific, anticipated* failure might occur.
- `except KeyError:` — if (and only if) a `KeyError` is raised anywhere inside the `try` block, this block runs instead of the program crashing. Any other exception type would **not** be caught here and would still propagate (continue unwinding) as normal.

### Catching the exception object itself, and catching multiple types

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Math problem: {e}")

try:
    value = quest_rewards["find_amulet"]
except (KeyError, TypeError) as e:
    print(f"Lookup problem: {type(e).__name__}: {e}")
```
**Expected output:**
```
Math problem: division by zero
Lookup problem: KeyError: 'find_amulet'
```

`as e` binds the actual exception *object* to a name so you can inspect it — `str(e)` (what `print` shows) gives its message, `type(e).__name__` gives the exception's class name as text. A tuple of types in `except (KeyError, TypeError):` catches either one with the same handling block — use this when multiple, genuinely different failure types deserve identical handling.

### Why catching *specific* exceptions matters — the danger of bare `except:`

```python
try:
    value = quest_rewards["find_amulet"]
    print(value.upper())   # a second, DIFFERENT bug: calling .upper() on an int
except:
    print("Something went wrong.")
```
**Expected output:** `Something went wrong.` — technically "works," but this is a real anti-pattern.

**Why this is dangerous:** a bare `except:` (no type at all) catches *literally everything* — including exceptions that indicate a genuine bug in your own code (like calling `.upper()` on a number, above, which would actually be an `AttributeError` from a completely different problem than a missing key), and even things like `KeyboardInterrupt` (the user pressing `Ctrl+C` to stop your program) or `SystemExit`. Swallowing all of these identically hides real bugs behind a generic, unhelpful message, and makes your own program impossible to stop cleanly. **The rule: always catch the most specific exception type(s) you actually expect and know how to handle.** If you must catch broadly (e.g., at the very top level of a program, to log an error before exiting cleanly), catch `Exception` specifically (which excludes `KeyboardInterrupt`/`SystemExit`, both of which inherit from a different base, `BaseException`) rather than a bare `except:`, and still log/print enough detail (`type(e).__name__`, `str(e)`) to actually diagnose it later.

### `else` and `finally` — the parts beginners forget exist

```python
def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Can't divide by zero.")
        return None
    else:
        print("Division succeeded.")
        return result
    finally:
        print("safe_divide finished running.")

print(safe_divide(10, 2))
print("---")
print(safe_divide(10, 0))
```
**Expected output:**
```
Division succeeded.
safe_divide finished running.
5.0
---
Can't divide by zero.
safe_divide finished running.
None
```

**Line by line:**
- `else:` (attached to a `try`, not an `if`) runs **only if the `try` block completed with no exception at all** — it's a place to put code that should run "on success," kept visually distinct from the `try` block itself so it's clear at a glance which lines are the risky ones actually being guarded, versus the ones that only make sense to run after they succeeded.
- `finally:` runs **unconditionally, no matter what** — whether the `try` succeeded, an exception was caught, or even if an exception was *not* caught and is actively propagating past this whole block. This makes `finally` the right place for cleanup that must always happen — most commonly, closing a file or releasing a resource (Lesson 08 revisits this exact pattern for file handling, and Lesson 10 shows how context managers automate it so you rarely need to write `finally` for this specific purpose by hand).

**Try it yourself:** remove the `return None` from the `except` block and predict whether `finally`'s print still runs before the function's overall failure propagates further. (It does — `finally` always runs, even when an exception is about to continue propagating past this function entirely.)

### Raising your own exceptions

```python
def complete_quest(quest, current_level):
    if quest["required_level"] > current_level:
        raise ValueError(
            f"Level {current_level} is too low for '{quest['name']}' "
            f"(requires level {quest['required_level']})"
        )
    print(f"Completed: {quest['name']}")

dragon_quest = {"name": "Slay the Dragon", "required_level": 20}

try:
    complete_quest(dragon_quest, 5)
except ValueError as e:
    print(f"Cannot complete quest: {e}")
```
**Expected output:** `Cannot complete quest: Level 5 is too low for 'Slay the Dragon' (requires level 20)`

`raise` deliberately triggers an exception — the same mechanism that runs automatically for built-in errors, now triggered by *your* code, for a condition *you've* decided is exceptional. `ValueError` is a sensible built-in choice here because the actual problem is "a value (the level) is inappropriate for this operation" — Python has several built-in exception types (`ValueError`, `TypeError`, `KeyError`, `IndexError`, `FileNotFoundError`, and more) that already mean something specific; reusing the right one instead of always inventing a custom one helps callers of your code recognize and handle familiar categories of failure.

### Custom exceptions — your own, specific error types

```python
class QuestError(Exception):
    """Base class for all quest-related errors in this program."""
    pass

class QuestNotFoundError(QuestError):
    def __init__(self, quest_name):
        self.quest_name = quest_name
        super().__init__(f"No quest named '{quest_name}' exists.")

class QuestAlreadyCompleteError(QuestError):
    def __init__(self, quest_name):
        self.quest_name = quest_name
        super().__init__(f"'{quest_name}' is already complete.")


def complete_quest(quests, quest_name):
    if quest_name not in quests:
        raise QuestNotFoundError(quest_name)
    if quests[quest_name]["is_complete"]:
        raise QuestAlreadyCompleteError(quest_name)
    quests[quest_name]["is_complete"] = True


quests = {"slay_dragon": {"is_complete": False}}

try:
    complete_quest(quests, "find_amulet")
except QuestNotFoundError as e:
    print(f"Not found: {e}")
except QuestAlreadyCompleteError as e:
    print(f"Already done: {e}")
```
**Expected output:** `Not found: No quest named 'find_amulet' exists.`

**Line by line:**
- `class QuestError(Exception):` — a custom exception is, mechanically, just a class (Lesson 05) that inherits from `Exception` (Python's general-purpose base class for "things you're expected to be able to catch and handle," as opposed to `BaseException`'s more severe subclasses like `SystemExit`). Inheriting from `Exception` is what makes `except QuestError:` and `isinstance(e, Exception)` work correctly.
- `QuestNotFoundError(QuestError)` and `QuestAlreadyCompleteError(QuestError)` both inherit from your own `QuestError`, not directly from `Exception` — this creates a small hierarchy: catching `except QuestError:` would catch *either* specific subtype, while catching `except QuestNotFoundError:` specifically catches only that one. This mirrors exactly how `except (KeyError, TypeError):` groups unrelated built-in types, except here the grouping is deliberate and structural, via inheritance, because these errors are conceptually related.
- `super().__init__(f"...")` — passes a human-readable message up to `Exception`'s own constructor, which is what makes `str(e)` / `print(e)` show something useful, exactly like calling any parent `__init__` from Lesson 05.

**Why bother with custom exceptions instead of always raising built-in `ValueError`s?** Specificity for *callers* of your code. Code that calls `complete_quest` can choose to catch `QuestNotFoundError` and `QuestAlreadyCompleteError` completely differently (e.g., one might suggest a different quest name, the other might just be a no-op with a friendly message) — impossible to do cleanly if both had merely raised a generic `ValueError` with different text, since catching by exception *type* is reliable and catching by parsing an error *message* is fragile and bad practice.

## Common mistakes & gotchas

- **Using a bare `except:` (or `except Exception:` without good reason) to make an error "go away."** This hides real bugs and produces unhelpful failures later. Catch the specific exception type(s) you actually expect and know how to handle.
- **Catching an exception broader than intended, accidentally hiding an unrelated bug.** E.g., wrapping a huge block of unrelated code in one `try: ... except Exception:` — if *any* line in that block fails for *any* reason, you get the same generic handling. Keep `try` blocks as small/specific as reasonably possible, wrapping just the risky operation.
- **Forgetting that `finally` runs even when you don't want cleanup to mask a real failure.** Code inside `finally` that itself might fail can suppress or replace the original exception's traceback in confusing ways — keep `finally` blocks simple (closing files, releasing locks), not complex logic.
- **Inventing a new custom exception type inheriting directly from `Exception` for every tiny thing, instead of reusing an appropriate built-in.** Not every error needs a custom type — reach for a custom exception (or hierarchy of them, as above) when callers genuinely need to distinguish and handle different failure categories differently; use plain built-ins (`ValueError`, `KeyError`, etc.) for one-off, ordinary validation failures.
- **Checking for a condition and then still letting the operation potentially fail anyway (a race between check and use).** Not a concern for this module's single-threaded scripts, but worth knowing the phrase "check, then use" can have gaps — you'll meet this properly once concurrency (Lesson 11, and later, real multi-request web servers) is on the table.

## How this connects

Lesson 08 (File I/O and JSON) is where this lesson's patterns get used constantly and for real — reading a file that might not exist, parsing JSON that might be malformed, both need exactly this `try`/`except` treatment, and it's exactly what your capstone's persistence layer needs to be genuinely robust rather than crashing on first real-world misuse. Lesson 10 (Context Managers) shows how Python automates the "always clean up, even on failure" pattern `finally` exists for, specifically for resources like open files.

## Quick self-check

1. What is an exception, mechanically, and how is Python's approach to signaling errors different from checking a return code?
2. Why is a bare `except:` considered dangerous, and what should you catch instead?
3. Put these in the order they can run for one `try` statement, and explain when each one runs: `except`, `else`, `finally`.
4. Why would you define your own `QuestNotFoundError` class instead of just raising a generic `ValueError` with a descriptive message?
5. If `QuestNotFoundError` and `QuestAlreadyCompleteError` both inherit from `QuestError`, what does `except QuestError:` catch that `except QuestNotFoundError:` alone would not?
