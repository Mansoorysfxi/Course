# Lesson 03 — Data Structures: Lists, Tuples, Sets, and Dicts

## What you'll learn

- The four core built-in collection types — `list`, `tuple`, `set`, `dict` — what each is for and how they differ.
- Which operations are fast and which are slow on each one, and *why* (a beginner-friendly introduction to time complexity intuition).
- Common operations on each: adding, removing, checking membership, looping, slicing.
- When to reach for which structure, with concrete decision rules, not vague advice.

## Why this matters

Almost every real program is, underneath, a story about moving data between a handful of collection shapes. Picking the wrong one doesn't just look inelegant — it can make code hundreds or thousands of times slower once real data volumes show up, in ways that are invisible with 5 test items and very visible with 50,000. This lesson gives you the mental model to pick correctly from the start, the same instinct you already have in C++ about `std::vector` vs. `std::map` vs. `std::unordered_set`, just mapped onto Python's specific four built-ins.

## Prerequisites

Lessons 01–02 (variables/types, functions/scope) — several examples here use functions and truthiness.

## The concept, explained simply

Four boxes, four different shapes of the same basic idea ("hold multiple values"):

- **`list`** — an ordered, changeable sequence. Like a C++ `std::vector`: items have a position (index), you can add/remove/change them, duplicates are fine.
- **`tuple`** — an ordered, **unchangeable** (immutable) sequence. Like a `std::vector` you've permanently locked after building it — same ordered-by-position idea as a list, but once created, its contents can never change.
- **`set`** — an unordered collection of **unique** values, optimized for one specific question: "is X in here?" Like a C++ `std::unordered_set`.
- **`dict`** (dictionary) — an unordered collection of **key → value** pairs, optimized for "look up the value for this specific key, fast." Like a C++ `std::unordered_map`.

## The details

### Lists — ordered, mutable

```python
quests = ["Slay dragon", "Find amulet", "Rescue villager"]

print(quests[0])          # index 0 = first item
print(quests[-1])         # -1 = last item, a Python-specific convenience
print(quests[0:2])        # slice: items at index 0 and 1 (stop is exclusive)

quests.append("Deliver letter")     # add to the end
quests.insert(0, "Wake up")         # insert at a specific position
quests.remove("Find amulet")        # remove by value (first match)
print(quests)
print(len(quests))
```
**Run:** `python lesson03.py` → **Expected output:**
```
Slay dragon
Rescue villager
['Slay dragon', 'Find amulet']
['Wake up', 'Slay dragon', 'Rescue villager', 'Deliver letter']
4
```

**Line by line:**
- `quests[0]` — indexing starts at `0`, exactly like C++ arrays/vectors.
- `quests[-1]` — negative indices count from the end; `-1` is always the last item. C++ has no direct equivalent — you'd write `.back()` or `v[v.size()-1]`.
- `quests[0:2]` — a **slice**: `start:stop`, where `stop` is exclusive (same "stop before this index" rule as `range()` from Lesson 01). This returns a *new* list, leaving `quests` unchanged.
- `.append(x)` adds to the end. `.insert(i, x)` adds at position `i`, shifting everything after it. `.remove(x)` deletes the *first* item equal to `x` (raises `ValueError` if `x` isn't present at all — worth wrapping in error handling, Lesson 06, in real code).
- `len(quests)` — the number of items. `len()` is a built-in function that works on all four collection types in this lesson, not a list-specific method.

**Mutability in action — the part that trips people up:**

```python
quests_backup = quests          # this does NOT copy the list
quests_backup.append("Surprise quest")
print(quests)                   # the "original" changed too!
```
**Expected output:** `quests` now *also* contains `"Surprise quest"`, even though you only modified `quests_backup`.

**Why:** `quests_backup = quests` doesn't create a second list — it makes `quests_backup` a second name pointing at the *exact same* list object in memory, the same way two C++ pointers can point at the same object. Mutating through either name mutates the one shared object. To get an actual independent copy:

```python
quests_backup = quests.copy()   # or: list(quests), or quests[:]
```

### Tuples — ordered, immutable

```python
coordinates = (10, 25)
print(coordinates[0])

coordinates[0] = 99   # this line raises an error — see below
```
**Expected output:** `10`, then a crash:
```
TypeError: 'tuple' object does not support item assignment
```

**Why use a tuple instead of a one-item list here?** Immutability is a *feature*, not a limitation, when the data genuinely shouldn't change after creation — coordinates, an RGB color, a fixed record like `(quest_id, quest_name)`. It also communicates intent to anyone reading the code: "this is a fixed little bundle, not a growing collection." Recall from Lesson 02: `return total, is_critical` returns a tuple for exactly this reason — a small, fixed, ordered bundle of results.

You've already seen tuple **unpacking**:
```python
x, y = coordinates
print(x, y)
```
**Expected output:** `10 25`

### Sets — unordered, unique, fast membership checks

```python
seen_quest_ids = set()
seen_quest_ids.add(101)
seen_quest_ids.add(102)
seen_quest_ids.add(101)   # duplicate — silently has no effect
print(seen_quest_ids)
print(101 in seen_quest_ids)
print(999 in seen_quest_ids)
```
**Expected output (order of set printing may vary — sets are unordered):**
```
{101, 102}
True
False
```

**Line by line:** `set()` creates an empty set (note: `{}` alone creates an empty **dict**, not a set — a genuine Python quirk; an empty set must be written `set()`). `.add()` inserts a value; adding a value already present does nothing (sets enforce uniqueness automatically — there's no error, no duplicate). `in` checks membership.

**Why `in` on a set matters so much:** this is the entire reason sets exist. Checking `x in seen_quest_ids` is (on average) **O(1)** — "constant time," meaning it takes roughly the same tiny amount of work whether the set has 10 items or 10 million. Checking `x in some_list` is **O(n)** — Python has to potentially check every single item, one by one, until it finds a match or reaches the end, so the work grows linearly with the list's size. For a small list this difference is invisible; for "has this ID already been processed" checks running thousands of times over thousands of items, it's the difference between a program that feels instant and one that visibly hangs.

Sets also support the classic set-theory operations, useful surprisingly often:

```python
completed = {101, 102, 103}
available = {102, 103, 104, 105}

print(completed & available)   # intersection: in both
print(completed | available)   # union: in either
print(available - completed)   # difference: in available, not completed
```
**Expected output:**
```
{102, 103}
{101, 102, 103, 104, 105}
{104, 105}
```

### Dicts — key → value lookups, fast by key

```python
quest_rewards = {
    "slay_dragon": 500,
    "find_amulet": 200,
    "rescue_villager": 150,
}

print(quest_rewards["slay_dragon"])
quest_rewards["deliver_letter"] = 50     # add a new key
quest_rewards["find_amulet"] = 250       # update an existing key
print(quest_rewards)

print("slay_dragon" in quest_rewards)    # checks KEYS by default
print(quest_rewards.get("nonexistent", 0))   # safe lookup with a default
```
**Expected output:**
```
500
{'slay_dragon': 500, 'find_amulet': 250, 'rescue_villager': 150, 'deliver_letter': 50}
True
0
```

**Line by line:**
- `quest_rewards["slay_dragon"]` — direct key lookup. If the key doesn't exist, this raises `KeyError` (Lesson 06 covers catching this properly).
- `quest_rewards["deliver_letter"] = 50` — assigning to a key that doesn't exist yet *creates* it; assigning to an existing key *overwrites* it. There's no separate "insert" vs. "update" method needed for the common case.
- `.get(key, default)` — the safe alternative to `[key]`: returns the value if the key exists, or the given default (here `0`) if it doesn't, *without* raising an error. Prefer `.get()` whenever "the key might not be there" is a real possibility you want to handle gracefully rather than crash on.
- `in` on a dict checks **keys**, not values, by default.

**Why dict lookups are fast, mechanically:** a dict is built on a **hash table** — a data structure that runs each key through a hash function (a calculation that turns the key into a number) to figure out roughly where in memory to look, rather than scanning every entry one by one. This is why `quest_rewards["slay_dragon"]` is also, like set membership, roughly **O(1)** on average — regardless of whether the dict has 5 entries or 5 million. This is the exact same underlying idea as C++'s `std::unordered_map`, and it's *why* dict keys must be **hashable** — which is also why you can't use a `list` as a dict key (lists are mutable, and Python requires hashable, effectively-immutable objects as keys) but *can* use a `tuple`.

Looping over a dict:

```python
for quest, reward in quest_rewards.items():
    print(f"{quest}: {reward} gold")
```
`.items()` gives you each key/value pair as a tuple, which the `for` loop unpacks — the exact same pattern from `**kwargs` in Lesson 02, because `**kwargs` *is* a dict. `.keys()` and `.values()` give you just one side if that's all you need.

### Time complexity intuition — a beginner-friendly summary table

You don't need to memorize formal Big-O notation for this course, but you do need the *intuition*: some operations are "always fast no matter how big the collection is," and some are "get slower the bigger the collection gets."

| Operation | `list` | `set` | `dict` |
|---|---|---|---|
| Check membership (`x in collection`) | Slow — checks items one by one, gets worse as the list grows | Fast — roughly constant time regardless of size | Fast, by key — roughly constant time regardless of size |
| Add one item | Fast at the end (`.append`), slow at the start/middle (`.insert(0, x)` shifts everything) | Fast | Fast |
| Access by position/order | Fast (`my_list[i]`) | Not supported — sets have no order or index | Not supported by position — only by key |
| Preserves insertion order | Yes | No (conceptually unordered, though modern CPython happens to preserve set iteration in some cases — don't rely on it) | Yes (guaranteed since Python 3.7) |
| Allows duplicates | Yes | No — automatically deduplicated | Keys: no. Values: yes. |

**The practical decision rule:**
- Need order, duplicates allowed, and mostly append/loop-through behavior? → **list**.
- Need a small, fixed, never-changing bundle of values? → **tuple**.
- Need "have I seen this before" / "give me only the unique ones" / fast membership checks, and don't care about order? → **set**.
- Need to look things up by a meaningful name/ID rather than position? → **dict**.

**Try it yourself:** you'll build a small timing experiment for this exact intuition in Exercise 01 — for now, just predict: if you had 100,000 quest IDs and needed to repeatedly check "has this ID already been completed?", would you reach for a `list` or a `set`, and why?

## Common mistakes & gotchas

- **Assuming `my_list_copy = my_list` makes a copy.** It doesn't — both names point at the same list. Use `.copy()`, `list(x)`, or `x[:]` for an actual independent copy.
- **Writing `{}` expecting an empty set.** `{}` is an empty **dict**. Use `set()` for an empty set.
- **Using `quest_rewards[key]` when the key might not exist, and not handling the resulting `KeyError`.** Use `.get(key, default)` when "missing" is an expected, normal case, and save `try`/`except KeyError` (Lesson 06) for when a missing key represents a genuine bug you want to know about loudly.
- **Trying to use a `list` as a dict key or a set element.** Both require hashable (effectively immutable) elements — you'll get `TypeError: unhashable type: 'list'`. Use a `tuple` instead if you need a fixed multi-value key.
- **Assuming a `set` or plain `dict` iteration preserves the order you'd expect from a list.** Dicts have guaranteed insertion order since Python 3.7 (a real, documented guarantee you can rely on), but sets remain conceptually unordered — don't write code whose correctness depends on set iteration order.
- **Repeatedly checking membership against a growing `list` in a loop, without realizing it's quietly O(n²) overall.** This is the single most common "why is my script suddenly slow with real data" bug beginners write — converting the list to a `set` first (if duplicates/order don't matter for that check) is often a one-line fix.

## How this connects

Lesson 04 builds comprehensions directly on top of lists/dicts/sets — the same collections, a more compact way to build them. Lesson 05 (OOP) uses lists and dicts constantly as the data an object holds internally (your capstone's `QuestManager` holds its quests in exactly one of these structures — you'll decide which, and justify it, in the capstone). Error handling (Lesson 06) covers `KeyError`/`IndexError` properly. This lesson's time-complexity intuition comes back explicitly once you're dealing with real data volumes from a database (Module 06) — the same "list scan vs. hash lookup vs. index" reasoning is exactly why database indexes exist.

## Quick self-check

1. Why is `x in my_set` fast regardless of the set's size, while `x in my_list` gets slower as the list grows?
2. What's the difference between a `list` and a `tuple`, and give one concrete reason to prefer a tuple even though a list could technically hold the same values.
3. What does `quests_backup = quests` actually do, and how is that different from `quests_backup = quests.copy()`?
4. Why can't you use a `list` as a dictionary key, and what would you use instead if you needed a multi-value key?
5. When would you reach for `.get(key, default)` instead of `my_dict[key]`?
