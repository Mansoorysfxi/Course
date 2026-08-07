# Lesson 02 — Functions, Scope, and the Argument Gotchas That Bite Everyone

## What you'll learn

- How to define and call functions, with and without return values.
- Default arguments — and the single most common real bug Python beginners (and plenty of professionals) hit with them.
- `*args` and `**kwargs`: what they actually are under the hood, not just "how to use them."
- Scope: local vs. global vs. enclosing, and Python's specific rules for reading vs. reassigning variables from an outer scope.
- What a closure is, briefly, as groundwork for decorators in Lesson 10.

## Why this matters

This is the point the master plan calls out specifically as where "a little Python" tends to run out. Functions in Python look superficially like functions in any language, but several of their rules — mutable default arguments, flexible argument-passing via `*args`/`**kwargs`, and how variable scope actually resolves — are genuinely different from C++ and cause real, hard-to-spot bugs if you don't understand the mechanism underneath. This lesson goes slow here on purpose.

## Prerequisites

Lesson 01 (Variables, Types, Control Flow).

## The concept, explained simply

A function in Python is a named, reusable block of code — the same core idea as a C++ function. The differences that matter: Python function parameters have no declared type (any object can be passed, unless you add type hints — Lesson 09), you don't need a header declaration/prototype before use, and a function can accept a genuinely variable number of arguments in a way C++ can't do without templates or overloads. Think of a Python function like an Unreal Blueprint function node with untyped input pins that quietly accept whatever you plug in — flexible, but the responsibility for "did I plug in the right kind of thing" shifts from the compiler onto you (or, later, onto type hints + a checker tool).

## The details

### Defining and calling a function

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Aria")
print(message)
```
**Run:** `python lesson02.py` → **Expected output:** `Hello, Aria!`

**Line by line:**
- `def` — keyword that starts a function definition. `greet` is the name; `(name)` is its single parameter.
- The function body is indented (same indentation rule as `if`/`while` from Lesson 01).
- `return` sends a value back to the caller and immediately exits the function — any code after `return` inside that same call never runs. A function with no `return` statement at all implicitly returns `None`.
- `greet("Aria")` — calling the function, passing `"Aria"` as the argument that fills the `name` parameter.

### Multiple parameters, and returning multiple values

```python
def calculate_damage(base_damage, multiplier):
    total = base_damage * multiplier
    is_critical = multiplier > 1.5
    return total, is_critical

result, was_critical = calculate_damage(20, 2.0)
print(result, was_critical)
```
**Expected output:** `40.0 True`

`return total, is_critical` doesn't actually return "two things" — it packs them into a single **tuple** (a fixed, ordered pair of values — Lesson 03 covers tuples fully) and returns *that*. `result, was_critical = calculate_damage(...)` then **unpacks** that tuple back into two separate names in one line. This pattern — return a tuple, unpack it on the call site — is Python's standard way of "returning multiple values," something C++ needs `std::pair`/`std::tuple` or output parameters for.

### Default arguments — the easy, safe case

```python
def greet_player(name, greeting="Welcome"):
    return f"{greeting}, {name}!"

print(greet_player("Aria"))
print(greet_player("Bram", greeting="Hail"))
```
**Expected output:**
```
Welcome, Aria!
Hail, Bram!
```

A default argument (`greeting="Welcome"`) is used whenever the caller doesn't supply that argument. Calling with `greeting="Hail"` uses a **keyword argument** — passing by parameter *name* instead of position, which also means you could call `greet_player(greeting="Hail", name="Bram")` in either order, since naming the parameter removes any ambiguity about which value goes where.

### The mutable default argument trap — a genuinely famous Python gotcha

Here is the bug this lesson exists to prevent you from ever shipping:

```python
def add_quest(quest_name, quest_log=[]):
    quest_log.append(quest_name)
    return quest_log

print(add_quest("Slay the dragon"))
print(add_quest("Find the amulet"))
```

**What you'd probably predict:** two separate lists, each with one quest.
**Actual output:**
```
['Slay the dragon']
['Slay the dragon', 'Find the amulet']
```

**Why this happens:** a default argument's value is evaluated **exactly once** — at the moment Python reads the `def` statement, not every time the function is called. `quest_log=[]` creates *one single list object*, and every call that doesn't supply its own `quest_log` shares that *same* list, forever, for the lifetime of the program. The second call's `.append()` mutated the exact list the first call already returned and was still holding onto.

This specific bug has burned nearly every Python developer at least once, often in production, often as a mysterious "why does this list have old data in it from a completely different request" bug (this exact pattern shows up again with real stakes once you're writing FastAPI endpoints in Module 05 — a mutable default there can leak data between unrelated requests).

**The fix — the standard idiom, always use this for mutable defaults:**

```python
def add_quest(quest_name, quest_log=None):
    if quest_log is None:
        quest_log = []
    quest_log.append(quest_name)
    return quest_log

print(add_quest("Slay the dragon"))
print(add_quest("Find the amulet"))
```
**Expected output:**
```
['Slay the dragon']
['Find the amulet']
```

**Why this fixes it:** `None` is immutable and shared safely — there's no "the same `None` got mutated" problem, because `None` can't be mutated at all. Each call that doesn't pass its own `quest_log` now creates a **brand-new** empty list, freshly, every single time, inside the function body where `if quest_log is None:` catches the "nothing was passed" case.

**The rule to memorize:** never use a mutable object (`[]`, `{}`, `set()`, or any custom object) directly as a default argument value. Use `None` as the default and create the real mutable value inside the function body instead.

**Try it yourself:** predict what happens if you use `quest_log=()` (an empty tuple — immutable) instead of `quest_log=[]`, and try to `.append()` to it. (It'll raise `AttributeError: 'tuple' object has no attribute 'append'` — tuples don't support `.append()` at all, which is one of several reasons Lesson 03 distinguishes lists from tuples by mutability, not just syntax.)

### `*args` — accepting any number of positional arguments

```python
def total_damage(*hits):
    print(type(hits))
    return sum(hits)

print(total_damage(10, 25, 7))
print(total_damage(5))
print(total_damage())
```
**Expected output:**
```
<class 'tuple'>
42
5
0
```

**What `*args` actually is:** the single `*` before a parameter name tells Python "collect *any* number of extra positional arguments the caller supplies, and pack them into a tuple with this name." `hits` inside the function is a completely ordinary tuple — you can loop over it, index it, pass it to `sum()`, anything a tuple supports. The name `args` is just convention (you could call it `hits`, as above, or anything else) — the `*` is what matters mechanically, not the specific word `args`.

### `**kwargs` — accepting any number of keyword arguments

```python
def describe_quest(**details):
    print(type(details))
    for key, value in details.items():
        print(f"  {key}: {value}")

describe_quest(name="Slay the Dragon", difficulty="Hard", reward=500)
```
**Expected output:**
```
<class 'dict'>
  name: Slay the Dragon
  difficulty: Hard
  reward: 500
```

**What `**kwargs` actually is:** two `*` characters before a parameter name collects *any* number of extra keyword arguments into a **dict** (dictionary — a name→value mapping, covered fully in Lesson 03) with this name. `details` is an ordinary dict; `.items()` gives you each key/value pair, which the `for` loop unpacks directly into `key` and `value` — this is the same tuple-unpacking idea from `return total, is_critical` above, just automatic per pair.

### Combining regular parameters, `*args`, and `**kwargs`

```python
def log_action(action, *extra_args, **extra_kwargs):
    print(f"Action: {action}")
    print(f"Extra positional: {extra_args}")
    print(f"Extra keyword: {extra_kwargs}")

log_action("attack", "goblin", "sword", critical=True, damage=15)
```
**Expected output:**
```
Action: attack
Extra positional: ('goblin', 'sword')
Extra keyword: {'critical': True, 'damage': 15}
```

The order is fixed: named/positional parameters first, then `*args`, then `**kwargs` — Python enforces this order in the function definition; writing them in a different order is a `SyntaxError`. You'll see this exact `*args, **kwargs` combination constantly once you reach decorators (Lesson 10) and FastAPI (Module 05) — it's the standard way to write a function that can "forward" arbitrary arguments through to something else without knowing in advance what they'll be.

**Try it yourself:** call `log_action("defend")` with no extra arguments at all, and predict the output for `extra_args`/`extra_kwargs` before running it. (They print as `()` and `{}` — empty, not `None` — `*args`/`**kwargs` always produce a real tuple/dict, even an empty one, never `None`.)

### Unpacking *into* a call with `*` and `**`

The same `*`/`**` syntax works in reverse, at the call site, to spread an existing list/dict *into* separate arguments:

```python
stats = [10, 2.5]
print(calculate_damage(*stats))

quest_info = {"base_damage": 20, "multiplier": 3.0}
print(calculate_damage(**quest_info))
```
**Expected output:**
```
(25.0, True)
(60.0, True)
```

`*stats` spreads the two-item list into two separate positional arguments (`10` and `2.5`), exactly as if you'd written `calculate_damage(10, 2.5)`. `**quest_info` spreads the dict into keyword arguments matching each parameter's name (`base_damage=20, multiplier=3.0`). This "collect on the way in, spread on the way out" symmetry is why `*`/`**` are used both in function definitions and in function calls.

### Scope — where a name is visible

```python
player_level = 5   # module-level (often loosely called "global") scope

def level_up():
    player_level = 6   # this creates a NEW local variable, it does NOT change the outer one
    print("Inside function:", player_level)

level_up()
print("Outside function:", player_level)
```
**Expected output:**
```
Inside function: 6
Outside function: 5
```

**What's happening:** any name *assigned to* inside a function is, by default, **local** to that function — it exists only for the duration of that call and shadows (temporarily hides) any same-named variable outside, rather than modifying it. This is different from some languages' block scoping (where an `if`/`for` block doesn't create a new scope) — in Python, a *function* is a scope boundary, but `if`/`for`/`while` blocks are **not**: a variable created inside an `if` block is visible after the block ends, as long as you're still in the same function or module.

**Reading** an outer variable (without reassigning it) works fine with no special syntax:

```python
player_level = 5

def show_level():
    print("Current level:", player_level)   # just reading — no problem

show_level()
```
**Expected output:** `Current level: 5`

The rule is specifically about **assignment**: Python decides, when it reads your function's code, that any name you assign to anywhere in that function is local for the *entire* function body — even before the line that assigns it. This causes a specific, confusing error if you try to read a global variable and then reassign it later in the same function without declaring your intent:

```python
player_level = 5

def broken_level_up():
    print(player_level)   # UnboundLocalError happens here, not on the next line
    player_level = player_level + 1

broken_level_up()
```
**Expected output:** an `UnboundLocalError`, because Python already decided `player_level` is local to `broken_level_up` (due to the assignment on the next line), so the `print` on the *first* line tries to read a local variable that doesn't have a value yet.

**The fix, when you genuinely need to modify a module-level variable from inside a function:** the `global` keyword.

```python
player_level = 5

def level_up_properly():
    global player_level
    player_level += 1

level_up_properly()
print(player_level)
```
**Expected output:** `6`

**Use `global` sparingly.** Functions that silently reach out and mutate variables outside themselves are harder to reason about and test — you'll see far more idiomatic Python (and this course's own capstone) pass values in as parameters and return new values out, rather than relying on `global`. It's shown here so you recognize it and understand the `UnboundLocalError` when you hit it, not as a pattern to reach for by default.

### A brief look at closures (full use case arrives in Lesson 10)

```python
def make_multiplier(factor):
    def multiply(value):
        return value * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(10))
print(triple(10))
```
**Expected output:**
```
20
30
```

`multiply` is defined *inside* `make_multiplier` and refers to `factor`, a variable from its **enclosing** scope (the function it's nested in — a third scope category alongside local and global). Even after `make_multiplier` has finished running and returned, the inner `multiply` function "remembers" the specific `factor` value it was created with — `double` remembers `2`, `triple` remembers `3`, permanently. This remembering is called a **closure**. It looks like a curiosity right now; Lesson 10 (Decorators) is built entirely on top of this exact mechanism, so recognizing the shape of it now pays off directly there.

## Common mistakes & gotchas

- **Using `[]` or `{}` as a default argument.** Covered above at length — use `None` and create the mutable value inside the function body instead.
- **`UnboundLocalError: local variable '...' referenced before assignment`.** You read a variable, then assigned to the same name later in the same function, without `global` — Python decided the whole function treats that name as local. Fix: either rename one of them, pass it as a parameter, or use `global` if you genuinely need to modify the outer one.
- **Forgetting that Python has no function overloading by parameter type.** You can't define `def greet(name: str)` and a separate `def greet(name: int)` the way C++ overloads by signature — the second `def greet` simply replaces the first entirely. Default arguments, `*args`/`**kwargs`, or explicit type checks inside one function are Python's answers to "handle different call shapes."
- **Putting `*args`/`**kwargs` in the wrong order in a `def`.** Regular parameters, then `*args`, then keyword-only params if any, then `**kwargs` — anything else is a `SyntaxError`.
- **Assuming a function without `return` returns nothing at all.** It returns `None` specifically — `x = my_function_with_no_return()` gives `x` the actual value `None`, which can itself cause a later `AttributeError`/`TypeError` if you try to use `x` as if it were something else.

## How this connects

Every exercise and every remaining lesson defines and calls functions constantly — this is the last lesson that explains function mechanics from scratch. Lesson 03 (Data Structures) needs the mutable-default-argument lesson directly, since `list`/`dict` are exactly the mutable types that trap. Lesson 10 (Decorators) is a direct continuation of the closures shown here — a decorator *is* a function that takes a function and returns a new function, closing over it, which will look immediately familiar after this lesson.

## Quick self-check

1. Why does `def add_quest(quest_name, quest_log=[]):` cause quests from *previous, unrelated calls* to show up unexpectedly? What's the fix?
2. What real data type does `*args` collect into inside the function body? What about `**kwargs`?
3. What's the difference between reading an outer-scope variable inside a function versus assigning to a same-named variable inside that function?
4. When would you need the `global` keyword, and why should you use it sparingly?
5. In `make_multiplier`, why does `double(10)` still return `20` even though `make_multiplier`'s call already finished running?
