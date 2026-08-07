# Lesson 04 — Comprehensions, Generators, and What `for` Actually Does

## What you'll learn

- List, set, and dict comprehensions — a compact way to build a collection from another one.
- What an **iterator** and an **iterable** actually are, mechanically — the real answer to "what does `for` do under the hood."
- Generators and generator functions (`yield`) — how to produce a sequence of values lazily, one at a time, without building the whole thing in memory first.
- When to reach for a comprehension, when for a generator, and why the memory difference matters.

## Why this matters

You've used `for` since Lesson 01 as "run this block once per item." This lesson opens the hood on that "magic," per the master plan's rule about never leaving magic behavior unexplained. Understanding the real mechanism pays off directly: it explains why some things can be looped over and others can't, why a generator can represent an infinite sequence without ever running out of memory, and it's a direct prerequisite for async/await in Lesson 11, which reuses this exact same "pause and resume" mechanism.

## Prerequisites

Lessons 01–03 (control flow, functions, and the four core data structures — comprehensions build directly on lists/sets/dicts).

## The concept, explained simply

So far, `for item in some_list:` has just meant "do this once per item." Here's the real mechanism: any object that `for` can loop over is called an **iterable** — it has a way of producing an **iterator**, a separate small object whose entire job is to hand out one item at a time and remember where it left off, like a bookmark in a book. `for` doesn't magically "know" how to walk through a list, a set, a dict, a file, and a `range()` — all fundamentally different internal structures — instead, it asks each one for its iterator, then just repeatedly asks that iterator "what's next?" until it says "nothing left." Every collection type from Lesson 03 supports this same small, uniform interface, which is *why* one `for` keyword works identically on all of them despite them being built completely differently underneath.

## The details

### Comprehensions — a compact way to build a new collection

Before comprehensions, building a filtered/transformed list looks like this:

```python
levels = [3, 7, 12, 1, 20, 15]

high_levels = []
for lvl in levels:
    if lvl >= 10:
        high_levels.append(lvl)

print(high_levels)
```
**Run:** `python lesson04.py` → **Expected output:** `[12, 20, 15]`

A **list comprehension** expresses the exact same loop in one line:

```python
high_levels = [lvl for lvl in levels if lvl >= 10]
print(high_levels)
```
**Expected output:** `[12, 20, 15]` — identical result.

**Reading a comprehension, left to right:** `[` *expression* `for` *item* `in` *iterable* `if` *condition* `]`. Read it out loud as: "give me [`lvl`] for [each `lvl`] in [`levels`] if [`lvl >= 10`]." The `if` part is optional — leave it off entirely if you want every item, just transformed:

```python
doubled = [lvl * 2 for lvl in levels]
print(doubled)
```
**Expected output:** `[6, 14, 24, 2, 40, 30]`

**Set and dict comprehensions** work the same way, with different brackets:

```python
unique_tens = {lvl // 10 for lvl in levels}
print(unique_tens)

level_lookup = {f"player_{i}": lvl for i, lvl in enumerate(levels)}
print(level_lookup)
```
**Expected output:**
```
{0, 1, 2}
{'player_0': 3, 'player_1': 7, 'player_2': 12, 'player_3': 1, 'player_4': 20, 'player_5': 15}
```

`enumerate(levels)` is a built-in that pairs each item with its index, producing `(0, 3), (1, 7), (2, 12), ...` — genuinely useful any time you need both the position and the value in a loop, instead of manually tracking a counter the way you would in C++'s indexed `for`.

**When to use a comprehension vs. a plain loop:** comprehensions are idiomatic Python and preferred when the logic is a single, simple transform/filter — they're not "more advanced," they're just more compact and, once you're used to reading them, faster to understand at a glance. The moment the body needs multiple statements, side effects (like printing or writing a file per item), or gets hard to read on one line, use a plain `for` loop instead — readability wins over compactness every time. **Try it yourself:** rewrite the `high_levels` comprehension to also double each qualifying value in the same expression (hint: change the part *before* `for`), predict the output, then run it.

### Iterables and iterators — the real mechanism

```python
numbers = [10, 20, 30]

iterator = iter(numbers)
print(type(iterator))

print(next(iterator))
print(next(iterator))
print(next(iterator))
print(next(iterator))   # this one raises StopIteration
```
**Expected output:**
```
<class 'list_iterator'>
10
20
30
```
...then a crash on the fourth call:
```
StopIteration
```

**Line by line — this is the actual mechanism behind every `for` loop you've written:**
- `iter(numbers)` calls the list's built-in `__iter__` method (a **dunder method** — "double underscore," covered fully in Lesson 05 — you'll recognize this exact naming pattern there) and gets back a fresh iterator object. The list itself is the **iterable** — it knows *how to produce* an iterator, but isn't one itself.
- `next(iterator)` calls the iterator's `__next__` method, which hands back the next item and internally advances its own bookmark by one position.
- Once there's nothing left, `__next__` raises a special exception, `StopIteration`, instead of returning a value — this exception is the standard, expected *signal* that iteration is done, not a bug.

**What `for item in numbers:` is actually doing**, spelled out with the pieces you just met — this is genuinely, mechanically what happens, just hidden behind the keyword:

```python
iterator = iter(numbers)
while True:
    try:
        item = next(iterator)
    except StopIteration:
        break
    print(item)
```
**Expected output:** `10`, `20`, `30`, each on its own line — identical behavior to `for item in numbers: print(item)`.

This is not a simplification for teaching purposes — this *is*, essentially, the CPython interpreter's actual translation of a `for` loop. `for` is syntactic sugar (a more convenient syntax for something you could write out longhand yourself) over exactly this `iter()` + repeated `next()` + catch `StopIteration` pattern. Now you know precisely why some things work with `for` and others raise `TypeError: 'X' object is not iterable` — it's a factual question of whether that object implements `__iter__` at all, not a vague rule to memorize.

**Try it yourself:** run `iter(5)` directly (not inside a `for`) and read the error. (`TypeError: 'int' object is not iterable` — plain numbers have no `__iter__`, so they can never be looped over directly, which is exactly why `range(5)` exists as a separate, genuinely iterable object standing in for "the numbers 0 through 4.")

### Generators — producing values lazily, one at a time

A **generator function** looks almost exactly like a normal function, with one difference: it uses `yield` instead of (or alongside) `return`.

```python
def countdown(n):
    print("Starting countdown")
    while n > 0:
        yield n
        n -= 1
    print("Done")

cd = countdown(3)
print(type(cd))
print(next(cd))
print(next(cd))
print(next(cd))
```
**Expected output:**
```
<class 'generator'>
Starting countdown
3
2
1
```

**What's actually happening — this is the important part:** calling `countdown(3)` does **not** run any of the function's code yet — it immediately returns a **generator object** (which is, itself, already an iterator — it has `__next__` built in automatically). Only when you call `next(cd)` for the first time does the function body actually start running, up to the first `yield`, where it **pauses**, hands back `n`'s current value, and — critically — **remembers exactly where it was**, including all of its local variables. The next call to `next(cd)` doesn't restart the function from the top; it **resumes** right after that `yield`, continues the `while` loop, and pauses again at the next `yield`. Notice `"Starting countdown"` only printed once, on the *first* `next()` call, not when `countdown(3)` was called — proof the function body genuinely hadn't started yet.

This "pause, remember everything, resume later, exactly where you left off" mechanism is precisely what makes `async`/`await` possible in Lesson 11 — `async def` functions use this exact same underlying pause/resume capability, just triggered by `await` instead of `yield`, and driven by an event loop instead of manual `next()` calls. If this section makes sense, Lesson 11 will click far faster.

You almost never call `next()` on a generator manually in real code — you loop over it, exactly like any other iterable:

```python
for value in countdown(3):
    print(f"T-minus {value}")
```
**Expected output:**
```
Starting countdown
T-minus 3
T-minus 2
T-minus 1
Done
```

Generators can also be written compactly as **generator expressions** — comprehension syntax with `()` instead of `[]`:

```python
squares_list = [x * x for x in range(1000000)]        # builds ALL 1,000,000 values in memory, right now
squares_gen = (x * x for x in range(1000000))          # builds nothing yet — just remembers how to produce them
```

### Why the memory difference genuinely matters

```python
import sys

squares_list = [x * x for x in range(1000000)]
squares_gen = (x * x for x in range(1000000))

print(sys.getsizeof(squares_list))
print(sys.getsizeof(squares_gen))
```
**Expected output (exact numbers vary by Python build, but the shape is what matters):**
```
8448728
104
```

The list comprehension allocated space for all one million computed values immediately — several megabytes. The generator expression allocated a tiny, fixed-size object that merely *knows how* to produce those values, one at a time, on demand — regardless of whether the underlying sequence has 3 items or 3 billion. If you only ever need to process values one at a time (say, in a `for` loop that stops early, or feeds each value somewhere else without keeping them all around) a generator can be the difference between a script that runs fine and one that exhausts your machine's memory on large enough input. The cost: a generator can only be iterated through **once** — once exhausted, it's empty forever, unlike a list, which you can loop over repeatedly.

**Try it yourself:** create a generator expression, loop over it fully once with a `for` loop, then try looping over the *same* generator object a second time. Predict what you'll see before running it. (The second loop produces nothing at all — no error, it just immediately has zero items, because the generator has already been fully consumed and has no way to "rewind.")

## Common mistakes & gotchas

- **Trying to loop over an exhausted generator a second time and getting silently nothing, with no error.** Generators are single-use. If you need to iterate multiple times, use a list (or comprehension with `[]`) instead, or create a fresh generator each time you need one.
- **Nesting comprehensions until they're unreadable.** A comprehension inside a comprehension (e.g., flattening a list of lists) is valid Python but frequently a readability regression — if you have to read it twice to understand it, write it as a plain nested `for` loop instead.
- **Forgetting a generator function's body doesn't run until you start pulling values from it.** If a generator function has an important side effect (opening a file, printing a log line) at the very top, before any `yield`, that code only runs on the *first* `next()`/iteration, not at the moment the generator object is created — this surprises people who expect "calling the function" to mean "running the function."
- **Confusing `yield` with `return` in the same function.** A `return` statement inside a generator function doesn't return a value to the caller the normal way — it raises `StopIteration`, ending the generator (optionally with the returned value attached, an advanced detail you don't need yet).
- **Using a comprehension purely for its side effects (e.g., `[print(x) for x in items]`).** This works, but it's considered bad style — it builds and immediately throws away a list of `None`s just to trigger `print()` as a side effect. Use a plain `for` loop when you want side effects, and a comprehension only when you want the resulting collection itself.

## How this connects

You now understand the real mechanism behind every `for` loop written since Lesson 01, and you have the two idiomatic Python "give me a new collection from this one" tools (comprehensions for small/eager collections, generators for large/lazy ones). Lesson 05 (OOP) shows you how to make your *own* custom classes iterable by implementing `__iter__`/`__next__` yourself — the exact dunder methods `iter()`/`next()` called under the hood here. Lesson 11 (async/await) reuses generators' pause-and-resume mechanism directly — genuinely the same underlying CPython feature, extended to work with an event loop instead of manual `next()` calls.

## Quick self-check

1. In your own words, what does `for item in some_list:` actually do, in terms of `iter()`, `next()`, and `StopIteration`?
2. What's the difference, mechanically, between `[x*x for x in range(10)]` and `(x*x for x in range(10))`?
3. Why does calling a generator function not immediately run any of its code?
4. Give one concrete situation where a generator is clearly the better choice over a list, and explain why using a list there would be worse.
5. What happens if you try to iterate over a generator a second time after fully consuming it once?
