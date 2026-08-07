# Lesson 09 — Type Hints: Getting Some of C++'s Safety Back

## What you'll learn

- What type hints are, and — importantly — what they are *not* (they don't change how your program runs).
- The modern syntax: hinting variables, function parameters, and return values.
- Built-in generic collection hints (`list[int]`, `dict[str, int]`) — the current, modern syntax — versus the older `typing.List[int]` style, and why the modern syntax exists.
- `Optional`/`| None`, `Union`/`|`, and hinting your own classes.
- How a type checker (briefly, conceptually) uses hints to catch bugs before you ever run the code — the actual payoff.

## Why this matters

You come from C++, where the compiler refuses to build if you pass a `string` where an `int` is expected. Python's dynamic typing (Lesson 01) gave that up for flexibility — but modern Python has a real, widely-used answer for getting a meaningful chunk of that safety back, *without* giving up dynamic typing at runtime: type hints, checked by a separate tool, not by the interpreter itself. This isn't a niche feature — starting with FastAPI in Module 05, type hints stop being optional style and become the literal mechanism the framework uses to validate incoming data and generate API documentation automatically. Getting comfortable with the syntax now, on familiar code, pays off directly there.

## Prerequisites

Lessons 01–05 (you're about to hint variables, functions, and your own classes).

## The concept, explained simply

A **type hint** is an annotation you add to your code — a variable, a function parameter, a return value — stating what type of value is *intended* to go there. Here's the crucial part: **Python itself does not enforce this at all when running your program.** You can write `def add(a: int, b: int) -> int:` and then call `add("hello", "world")`, and Python will happily try to run it (and, in this specific case, actually "succeed," because `+` on two strings concatenates them — a good example of exactly the kind of bug a type hint is meant to help catch *before* runtime, via a separate tool, rather than after). Type hints are read by external **type checkers** (the most common: Pylance, built into VS Code's Python extension from Lesson 00, and a standalone tool called mypy) that scan your code *without running it* and flag places where the hinted types don't line up — catching a category of bug at write-time that would otherwise only surface when that exact buggy line finally executes, possibly in production, possibly rarely.

## The details

### Hinting variables and function signatures

```python
player_name: str = "Aria"
player_level: int = 12
is_alive: bool = True

def calculate_damage(base_damage: int, multiplier: float) -> float:
    return base_damage * multiplier

print(calculate_damage(20, 1.5))
```
**Run:** `python lesson09.py` → **Expected output:** `30.0` — runs identically with or without the hints; they're purely informational to any tool reading the code (including, genuinely, other humans — this is a real benefit even with no checker running at all).

**Line by line:**
- `player_name: str = "Aria"` — the `: str` is the hint; it doesn't create or enforce anything at runtime, it just documents (in a machine-checkable way) that `player_name` is intended to always hold a string.
- `def calculate_damage(base_damage: int, multiplier: float) -> float:` — each parameter is hinted individually, and `-> float` (after the closing parenthesis, before the colon) hints the **return type**.

Open this exact file in VS Code (Lesson 00's Python extension gives you Pylance, a type checker, automatically) and try this deliberately broken call:

```python
print(calculate_damage("twenty", 1.5))
```

**Expected result:** VS Code shows a red squiggly underline under `"twenty"`, *without you ever running the file* — hovering over it explains the mismatch (`str` where `int` was expected). This is the actual payoff: a whole class of bugs caught while you're still typing, not after you've run the program and it's failed (or, worse, quietly done something wrong without crashing at all).

### Built-in generic collection hints — the current, modern syntax

```python
def total_reward(quests: list[dict[str, int]]) -> int:
    return sum(q["reward_gold"] for q in quests)

quests = [
    {"reward_gold": 100},
    {"reward_gold": 250},
]
print(total_reward(quests))
```
**Expected output:** `350`

**Verified for this lesson (August 2026):** `list[dict[str, int]]` — using Python's own built-in `list` and `dict` directly as generic types, with square brackets specifying what's *inside* them — is the current, standard, recommended syntax, and has been since **Python 3.9** (via [PEP 585](https://peps.python.org/pep-0585/)). `list[dict[str, int]]` reads as "a list, of dicts, where each dict has string keys and int values" — exactly matching the `quests` data above.

**You'll still encounter the older syntax in existing code/tutorials — recognize it, don't write new code with it:**
```python
from typing import List, Dict

def total_reward(quests: List[Dict[str, int]]) -> int:
    ...
```
Before Python 3.9, plain `list`/`dict` couldn't be subscripted with `[...]` for hinting purposes at all, so the `typing` module provided capitalized stand-ins (`List`, `Dict`, `Tuple`, and more) specifically to work around that limitation. Since Python 3.9 made the built-ins themselves subscriptable, these `typing` aliases are unnecessary for new code — and, verified for this lesson, they've been soft-deprecated since 3.9, emit deprecation warnings starting in Python 3.12, and are slated for removal in Python 3.14 (the version this course installs, per Lesson 00) — meaning `from typing import List` will increasingly show up as a discouraged pattern in linters/checkers. **This course always uses the modern, lowercase built-in syntax** (`list[...]`, `dict[...]`, `tuple[...]`, `set[...]`).

### `Optional` / `| None`, and `Union` / `|`

Sometimes a value is genuinely allowed to be either a real value *or* `None` (recall Lesson 01/02's use of `None` as "no value yet").

```python
def find_quest(quests: list[dict], name: str) -> dict | None:
    for quest in quests:
        if quest["name"] == name:
            return quest
    return None

result = find_quest([{"name": "Slay the Dragon"}], "Slay the Dragon")
print(result)

missing = find_quest([{"name": "Slay the Dragon"}], "Find the Amulet")
print(missing)
```
**Expected output:**
```
{'name': 'Slay the Dragon'}
None
```

`dict | None` reads as "either a dict, or `None`" — this `|` syntax (called a **union type**: the value could genuinely be one type *or* another) was introduced in Python 3.10 ([PEP 604](https://peps.python.org/pep-0604/)) and, verified for this lesson, is now the standard modern way to write this, alongside `list[...]`/`dict[...]` from PEP 585 above. You'll also see the older equivalent in existing code: `from typing import Optional` then `Optional[dict]` (specifically for "this or `None`") or `from typing import Union` then `Union[dict, str]` (for "this or that, more generally") — same relationship as `List`/`list`: the `typing` versions predate Python supporting the shorter syntax directly, and this course uses the modern `|` form throughout.

**Why this specific hint matters so much in practice:** a function hinted as returning `dict | None` is telling every caller, explicitly, "check for `None` before assuming you got a real dict" — exactly the kind of "does this key/value actually exist" question Lesson 03's `.get()` and Lesson 06's error handling exist to answer safely. A type checker will actually flag `result["name"]` as unsafe if `result`'s hinted type includes `None`, until you've narrowed it down (e.g., with `if result is not None:`) — genuinely catching the "forgot to handle the missing case" bug before runtime.

### Hinting your own classes

```python
class Quest:
    def __init__(self, name: str, reward_gold: int) -> None:
        self.name: str = name
        self.reward_gold: int = reward_gold

def describe(quest: Quest) -> str:
    return f"{quest.name}: {quest.reward_gold} gold"

q = Quest("Slay the Dragon", 500)
print(describe(q))
```
**Expected output:** `Slay the Dragon: 500 gold`

Your own classes work as hints exactly like built-in types — `quest: Quest` means "this parameter should be an instance of the `Quest` class." Note `__init__`'s return hint is `-> None`, since constructors never return a meaningful value (they always implicitly return `None`, per Lesson 02) — hinting this explicitly is a genuine, common convention, not required but expected in code that hints consistently.

## Common mistakes & gotchas

- **Believing a type hint prevents the "wrong" value from ever being passed at runtime.** It doesn't — hints are purely for tools (type checkers, IDEs) and human readers; Python itself never checks them while running. Passing a `str` where an `int` is hinted will not raise a `TypeError` from the hint itself — it'll only fail later, and only if the mismatched type actually causes a real problem somewhere downstream.
- **Writing `from typing import List, Dict` in new code out of old habit.** Use the built-in `list[...]`/`dict[...]` syntax instead — it's shorter, requires no import, and is the direction the language itself has moved (verified for this lesson: `typing.List`/`typing.Dict` are slated for removal in Python 3.14).
- **Forgetting `-> None` on functions/methods that don't return anything meaningful**, leaving their return type unhinted/ambiguous, especially `__init__`. Not a bug, just an inconsistency a type-hint-conscious codebase avoids.
- **Using `Optional[X]`/`X | None` and then not actually checking for `None` before using the value.** The hint documents the possibility; it's still your job to write the `if x is not None:` check — the hint just makes it possible for a type checker to *catch you* if you forget.
- **Over-hinting trivial local variables where the type is already obvious from the right-hand side** (e.g., `count: int = 0`). Not wrong, just usually unnecessary noise — hints earn their keep most on function signatures (parameters/return types) and class attributes, where the type genuinely isn't obvious from a glance, less so on an obvious local variable one line long.

## How this connects

Type hints are used lightly throughout every remaining lesson and exercise in this module (function signatures especially), and become load-bearing starting in Module 05: FastAPI reads your type hints at runtime (not just for a separate checker tool) to validate incoming request data automatically and generate interactive API documentation — the exact same `list[...]`/`dict[str, int]`/`X | None` syntax from this lesson, just put to direct, functional use rather than purely advisory use. Your capstone's `Quest`/`QuestManager` classes and their methods should be hinted throughout, following this lesson's conventions.

## Quick self-check

1. Does Python enforce type hints while a program is actually running? If not, what actually checks them, and when?
2. What's the modern way to hint "a list of strings," and what's the older, now-discouraged equivalent?
3. What does `dict | None` mean as a return type hint, and why does that matter to whoever calls that function?
4. Why does `__init__` typically get hinted with `-> None`?
5. Give one concrete example (not from this lesson) of a bug a type checker could catch before you ever run the code.
