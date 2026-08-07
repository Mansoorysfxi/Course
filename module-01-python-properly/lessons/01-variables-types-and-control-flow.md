# Lesson 01 — Variables, Types, and Control Flow (A Fast Review)

## What you'll learn

- How Python variables differ from C++ variables (no declared type, no manual memory management).
- Python's core built-in types: `int`, `float`, `str`, `bool`, `None`, and how Python decides a variable's type at runtime.
- How arithmetic, comparison, and boolean operators work, including a few Python-specific gotchas.
- `if`/`elif`/`else`, `while`, and a first look at `for` (covered in full, "what actually happens," in Lesson 04).
- What "truthiness" means — which values Python treats as false in a boolean context.
- f-strings, the standard way to build formatted text.

## Why this matters

You said you know "a little" Python — this lesson is that refresher, moving quickly, so Lesson 02 onward can slow down at exactly the point where "a little Python" usually runs out: functions done properly, real data structures, and OOP. If any single line in this lesson is genuinely new to you, that's fine — but if most of it feels obvious, that's the intended experience; skim, run the snippets to confirm they behave as you expect, and move on.

## Prerequisites

Lesson 00 (Setup) — a working Python interpreter and a venv you know how to activate.

## The concept, explained simply

In C++, you write `int health = 100;` — you tell the compiler *up front* what type `health` is, and that's fixed forever (barring a cast). Python variables don't work that way. Python is **dynamically typed**: a variable is just a name that currently *points at* some value, and that value carries its own type — the name itself has no fixed type at all. You can write `health = 100` (an `int`) and, on the very next line, `health = "full"` (a `str`) — Python won't stop you. This is powerful and dangerous in equal measure: powerful because you write less boilerplate, dangerous because a typo or logic error that C++'s compiler would catch at compile time might not show up until the exact line that breaks at runtime. (Lesson 09, Type Hints, is Python's modern answer to getting some of that C++-style safety back, opt-in, without giving up dynamic typing's convenience.)

## The details

Open your `python-practice` venv from Lesson 00 (`source .venv/Scripts/activate`) and create a new file for this lesson's snippets, e.g. `lesson01.py`, that you edit and re-run as you go: `python lesson01.py`.

### Variables and basic types

```python
health = 100          # int
stamina = 75.5        # float
player_name = "Aria"  # str (text)
is_alive = True       # bool
current_quest = None  # None — "no value," Python's equivalent of a null/empty state

print(type(health))
print(type(player_name))
print(type(current_quest))
```

**Run it:** `python lesson01.py`
**Expected output:**
```
<class 'int'>
<class 'str'>
<class 'NoneType'>
```

**Line by line:** each `=` creates (or reassigns) a name to point at a value. `type(x)` asks Python, at that exact moment, what kind of value `x` currently holds — there's no separate compile-time type to ask about, because there isn't a compile step at all (Lesson 00). `None` is Python's single, specific "this variable deliberately holds no value" — comparable to a null pointer in C++, but it's a real, distinct value/type (`NoneType`), not "the absence of memory."

**Try it yourself:** add a line `health = "one hundred"` right after the first assignment, then `print(type(health))` again. Predict the output before running it. (It'll print `<class 'str'>` — Python happily let you change `health`'s type mid-program. In real code this is usually a *bug waiting to happen*, not a feature you should lean on.)

### Arithmetic and a genuine Python gotcha: integer vs. float division

```python
print(10 + 3)    # 13
print(10 - 3)    # 7
print(10 * 3)    # 30
print(10 / 3)    # 3.3333333333333335
print(10 // 3)   # 3
print(10 % 3)    # 1
print(10 ** 2)   # 100
```

**Line by line:**
- `/` always produces a `float`, even for two `int`s that divide evenly (`10 / 2` gives `5.0`, not `5`) — this is different from C++, where `int / int` truncates.
- `//` is **floor division** — divide, then round down to the nearest whole number, discarding the remainder. `10 // 3` is `3`.
- `%` is the **modulo** operator — the remainder left over after floor division. `10 % 3` is `1` because `3 × 3 = 9`, remainder `1`.
- `**` is exponentiation — `10 ** 2` is 100. C++ has no equivalent operator; you'd call `pow()`.

**Try it yourself:** predict `-7 // 2` before running it. (It's `-4`, not `-3` — floor division rounds *toward negative infinity*, not toward zero, which surprises people coming from C++'s truncating integer division.)

### Comparison and boolean operators

```python
print(5 == 5)     # True
print(5 != 3)     # True
print(5 > 3 and 2 < 4)   # True
print(5 > 3 or 2 > 4)    # True
print(not True)          # False
```

Python spells its boolean operators as the actual words `and`, `or`, `not` — not `&&`, `||`, `!` like C++. (`&`, `|`, `!` do exist in Python but mean something different — bitwise operations and, for `!`, nothing at all as a standalone operator — so don't reach for C++ muscle memory here.)

### Truthiness — what counts as "false" without being the literal `False`

```python
values_to_check = [0, 1, "", "hello", None, [], [1, 2], 0.0]
for v in values_to_check:
    print(v, "->", bool(v))
```
**Expected output:**
```
0 -> False
1 -> True
 -> False
hello -> True
None -> False
[] -> False
[1, 2] -> True
0.0 -> False
```

(`[]` is an empty **list** — a data structure covered fully in Lesson 03; for now, just notice it behaves like `False` when empty.)

**The rule:** `0`, `0.0`, `""` (empty string), `None`, and empty collections (`[]`, `{}`, etc.) are all "falsy" — they behave as `False` in a boolean context (like an `if` condition) even though they aren't literally the value `False`. Everything else is "truthy." This matters constantly in real code: `if my_list:` is idiomatic Python for "if this list has anything in it," and is preferred over the more verbose `if len(my_list) > 0:`.

### `if` / `elif` / `else`

```python
health = 35

if health <= 0:
    print("Defeated")
elif health < 25:
    print("Critical — heal now")
elif health < 60:
    print("Wounded")
else:
    print("Healthy")
```
**Expected output:** `Wounded`.

**Line by line:** Python has no curly braces for blocks — **indentation itself defines the block**. Everything indented under `if health <= 0:` belongs to that branch. This is not a style preference, it's the actual syntax: inconsistent indentation is a `SyntaxError` or (worse) silently changes what your code does. The convention, and what this course uses throughout, is **4 spaces per indent level** — never tabs, never a mix. Each condition is checked top to bottom; the first one that's `True` runs its block, and the rest are skipped entirely — `elif` (Python's word for "else if") lets you chain more than two branches without deeply nesting `if`s inside `else`s the way you might in C++.

**Try it yourself:** change `health` to `-5`, predict the output, then run it. Then change it to `60` exactly, predict again (pay attention to `<` vs `<=`), then run it.

### `while` loops

```python
countdown = 3
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Go!")
```
**Expected output:**
```
3
2
1
Go!
```

`countdown -= 1` is shorthand for `countdown = countdown - 1` — Python supports `+=`, `-=`, `*=`, `/=`, etc., same as C++. **Important Python-specific gap:** Python has **no `++` or `--` operators at all** — `countdown++` is a `SyntaxError`. Always write `countdown += 1`.

A `while` loop with no way for its condition to eventually become `False` runs forever — an infinite loop, exactly as dangerous as in any language. If you ever get stuck in one while testing, `Ctrl+C` in the terminal interrupts the running script.

### A first look at `for` (full treatment in Lesson 04)

```python
for i in range(5):
    print(i)
```
**Expected output:** `0`, `1`, `2`, `3`, `4`, each on its own line.

`range(5)` produces the sequence `0, 1, 2, 3, 4` — five numbers, starting at `0`, stopping *before* `5`. This is the most common beginner off-by-one surprise in Python: `range(5)` is **not** `1, 2, 3, 4, 5`. Python's `for` doesn't work anything like C++'s three-part `for (int i = 0; i < 5; i++)` — there's no manual counter, no manual increment, no condition you write yourself. You're about to see exactly why, and what `for` is actually doing underneath, in Lesson 04 — for now, just use it to mean "run this block once for each item in this sequence."

### f-strings — building text with variables inside it

```python
name = "Aria"
level = 12
print(f"{name} is level {level}.")
```
**Expected output:** `Aria is level 12.`

The `f` immediately before the opening quote marks this as an **f-string** ("formatted string literal"). Anything inside `{curly braces}` inside an f-string is evaluated as a real Python expression and substituted into the text — not just variable names, but any expression:

```python
print(f"Next level in {(level + 1) * 10} XP.")
```
**Expected output:** `Next level in 130 XP.`

f-strings are the standard, idiomatic way to build formatted text in modern Python — prefer them over older techniques you might see in older code/tutorials (`"%s" % name`, or `"{}".format(name)`), which still work but are considered legacy style.

## Common mistakes & gotchas

- **`IndentationError` or code running in the wrong branch.** Almost always mixed tabs/spaces, or an editor auto-indenting inconsistently. VS Code's Python extension (Lesson 00) defaults to 4 spaces and shows whitespace characters if you ask it to — trust it over eyeballing.
- **Using `=` when you meant `==`.** `if health = 100:` is actually a `SyntaxError` in Python (unlike some languages where it silently compiles and does the wrong thing) — Python refuses to let you assign inside a condition this way, which is a real safety net over C++.
- **Expecting `range(5)` to include `5`.** It doesn't — `range(start, stop)` always stops *before* `stop`. `range(5)` is shorthand for `range(0, 5)`.
- **Trying `count++` or `count--`.** Not valid Python — use `count += 1` / `count -= 1`.
- **Forgetting Python's `and`/`or`/`not` are words, not symbols.** `&&`/`||`/`!` either error or (worse, with `&`/`|`) silently do something different (bitwise operations) rather than the boolean logic you intended.
- **Assuming `10 / 2` gives an `int`.** It gives `5.0` — a `float`. Use `//` if you specifically want integer (floor) division.

## How this connects

Lesson 02 immediately builds on this: functions are where "a little Python" tends to plateau, so it slows down considerably starting there — default arguments, `*args`/`**kwargs`, and scope rules that behave differently from C++'s block scoping. Lesson 04 comes back to `for` specifically and opens the hood on what it's actually doing. Everything here — variables, `if`, `while`, f-strings — is used in literally every subsequent lesson and the capstone, without further explanation, so make sure the self-check below is genuinely comfortable before moving on.

## Quick self-check

1. Why can a Python variable "change type" partway through a program, and why is that both convenient and risky?
2. What does `10 // 3` evaluate to, and how is that different from `10 / 3`?
3. Name three values Python treats as "falsy" that are not the literal value `False`.
4. Why is `range(5)` five numbers starting at `0` rather than five numbers ending at `5`?
5. What actually defines a block of code in Python, if not curly braces?
