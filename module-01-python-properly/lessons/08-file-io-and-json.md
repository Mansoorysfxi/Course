# Lesson 08 — File I/O and JSON

## What you'll learn

- How to open, read, write, and append to files, and why `with` is the standard way to do it (a first taste of context managers, opened fully in Lesson 10).
- Text modes (`"r"`, `"w"`, `"a"`) and what each actually does to the file.
- What JSON is, why it became the near-universal data interchange format, and how it maps onto Python's own data structures.
- `json.dump`/`json.load` (files) vs. `json.dumps`/`json.loads` (strings), and exactly when to use which.
- Handling the realistic failure modes of file + JSON work: missing files and malformed content.

## Why this matters

Your capstone's entire reason for existing beyond one running session is **persistence** — quests need to still be there after you close and reopen the program, which means writing them to a file and reading them back. JSON is the format you'll use for that, and it's also the format virtually every web API you'll build or call for the rest of this course (starting Module 02) speaks natively. Getting comfortable with file I/O + JSON now, including its realistic failure modes, pays off immediately in the capstone and constantly for the rest of the course.

## Prerequisites

Lesson 03 (data structures — JSON maps directly onto lists/dicts), Lesson 06 (error handling — reading files and parsing JSON are exactly the operations that realistically fail and need `try`/`except`).

## The concept, explained simply

A file on disk is just a sequence of bytes; Python's file-handling functions let you treat a text file as something you can read line-by-line or all at once, and write to, from your running program. **JSON** (JavaScript Object Notation, despite the name having nothing Python-specific or even necessarily anything to do with running JavaScript) is a plain-text format for representing structured data — numbers, strings, booleans, lists, and key/value objects — using a syntax that maps almost one-to-one onto Python's own `list`/`dict`/`str`/`int`/`float`/`bool`/`None`. It became the dominant data interchange format on the web (displacing older, more verbose alternatives like XML) specifically because it's compact, human-readable, and trivially easy for almost every programming language to parse.

## The details

### Opening, writing, and reading a file — the basic mechanics

```python
file = open("quests.txt", "w")
file.write("Slay the Dragon\n")
file.write("Find the Amulet\n")
file.close()
```
**Run:** `python lesson08.py`, then check the result: `cat quests.txt` (Module 00, Lesson 01) → **Expected output:**
```
Slay the Dragon
Find the Amulet
```

**Line by line:**
- `open("quests.txt", "w")` — opens (creating it if it doesn't exist) a file for writing. `"w"` mode **truncates** the file first — if `quests.txt` already had content, it's gone the instant `open(..., "w")` runs, replaced entirely by whatever you write afterward. This returns a **file object** — not the file's contents, a handle you use to interact with it.
- `.write(text)` — writes exactly the given string, with **no automatic newline** — you must include `\n` yourself if you want each call on its own line, unlike `print()`, which adds one automatically.
- `.close()` — releases the file. **This matters more than it looks like:** until a file is closed, some of what you wrote may still be sitting in an internal buffer, not actually flushed to disk yet — and on some systems, other programs (or your own script if it tries to reopen the same file) may not see your changes, or may fail to open it at all, until it's closed. Forgetting to close a file is a real, if easy to overlook, bug.

**The problem with `open()`/`.close()` written by hand:** if anything raises an exception between `open()` and `.close()`, `.close()` never runs, leaking the open file. You already know the fix in principle from Lesson 06 — wrap it in `try`/`finally`. Python provides a cleaner, standard way to get that guarantee automatically:

```python
with open("quests.txt", "w") as file:
    file.write("Slay the Dragon\n")
    file.write("Find the Amulet\n")
# file is automatically, guaranteedly closed here — even if an exception happened above
```

**This is a context manager** (the `with` statement) — Lesson 10 opens the hood on exactly how `with` accomplishes this guarantee (it's built on two more dunder methods, `__enter__`/`__exit__`, in the same family as Lesson 04/05's dunders). For now, the rule: **always use `with open(...) as f:` to work with files, never bare `open()`/`.close()`.** This is the single strongest, most universal convention in this entire lesson — real Python code essentially never opens a file without `with`.

### Reading a file back

```python
with open("quests.txt", "r") as file:
    contents = file.read()
print(contents)
print("---")

with open("quests.txt", "r") as file:
    for line in file:
        print(f"Line: {line.strip()}")
```
**Expected output:**
```
Slay the Dragon
Find the Amulet

---
Line: Slay the Dragon
Line: Find the Amulet
```

**Line by line:**
- `"r"` mode — read (this is also the default if you omit the mode entirely, but writing it explicitly is clearer).
- `.read()` — returns the **entire** file's contents as one single string, including the newline characters. (Notice the blank line in the output above — that's the trailing `\n` from the file's last written line, plus `print()`'s own automatic newline.)
- Looping directly over a file object (`for line in file:`) — a file object is itself **iterable** (exactly Lesson 04's mechanism), producing one line at a time, each *including* its trailing `\n`. This is generally preferred over `.read()` for large files, because it reads and processes one line at a time rather than loading the entire file into memory at once — the same lazy-vs-eager tradeoff as generators vs. lists from Lesson 04.
- `.strip()` — a string method that removes leading/trailing whitespace (including that trailing `\n`) — used here purely so the printed output doesn't show an extra blank line per entry.

### Appending, instead of overwriting

```python
with open("quests.txt", "a") as file:
    file.write("Rescue the Villager\n")
```
`"a"` mode ("append") adds to the *end* of an existing file without touching what's already there — the file-I/O equivalent of the shell's `>>` from Module 00, versus `"w"` behaving like `>`.

### JSON — mapping Python data onto a universal text format

```python
import json

quest_data = {
    "name": "Slay the Dragon",
    "difficulty": "Hard",
    "reward_gold": 500,
    "is_complete": False,
    "tags": ["combat", "boss"],
}

json_text = json.dumps(quest_data, indent=2)
print(json_text)
print(type(json_text))
```
**Expected output:**
```
{
  "name": "Slay the Dragon",
  "difficulty": "Hard",
  "reward_gold": 500,
  "is_complete": false,
  "tags": [
    "combat",
    "boss"
  ]
}
<class 'str'>
```

**Line by line:**
- `json.dumps(...)` — "dump to a **s**tring": converts a Python object (here, a dict) into a JSON-formatted string. Note the trailing `s` — this is the *string* version, distinct from `json.dump` (no `s`) below, which writes *directly to a file*, a genuinely easy pair of names to mix up.
- `indent=2` — pretty-prints with 2-space indentation, purely for human readability; omit it for compact output (no difference in what the data *means*, only how it looks as text).
- Notice `False` (Python) became `false` (JSON) — JSON has its own literal spellings for booleans (`true`/`false`, lowercase) and `null` (JSON's `None`) — these are real, meaningful translations `json` performs for you, not typos.

**The full JSON ↔ Python type mapping you need:**

| Python | JSON |
|---|---|
| `dict` | object (`{...}`) |
| `list` | array (`[...]`) |
| `str` | string |
| `int` / `float` | number |
| `True` / `False` | `true` / `false` |
| `None` | `null` |

Notably **absent from JSON**: `tuple` and `set` have no JSON equivalent — `json.dumps` will silently convert a tuple into a JSON array (indistinguishable from a list once round-tripped) and will **raise an error** on a `set` (`TypeError: Object of type set is not JSON serializable`), because JSON has no concept of "unique, unordered collection." This is a real, practical constraint: whatever data structure you use *inside* your program, only these six JSON-representable shapes survive being saved to a file and loaded back.

### Writing JSON directly to a file, and reading it back

```python
with open("quest.json", "w") as file:
    json.dump(quest_data, file, indent=2)

with open("quest.json", "r") as file:
    loaded_data = json.load(file)

print(loaded_data)
print(type(loaded_data))
print(loaded_data["reward_gold"] + 100)
```
**Expected output:**
```
{'name': 'Slay the Dragon', 'difficulty': 'Hard', 'reward_gold': 500, 'is_complete': False, 'tags': ['combat', 'boss']}
<class 'dict'>
600
```

**Line by line:** `json.dump(data, file, ...)` (no `s`) writes JSON text *directly* into an already-open file object — equivalent to `file.write(json.dumps(data, ...))` but without needing the intermediate string. `json.load(file)` (no `s`) reads and parses an already-open file's JSON content directly into real Python objects — notice `loaded_data` is a genuine `dict`, not a string that merely *looks* like one, which is why `loaded_data["reward_gold"] + 100` works immediately as real arithmetic on a real `int`.

**The naming rule to memorize, since mixing these up is extremely common:** the ones **with** an `s` (`dumps`/`loads`) work with **s**trings; the ones **without** an `s` (`dump`/`load`) work directly with an already-open **file**.

### Handling realistic failures — a file that doesn't exist, and malformed JSON

```python
import json

def load_quests(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"No save file at {path} yet — starting fresh.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Save file at {path} is corrupted: {e}")
        return {}

quests = load_quests("does_not_exist.json")
print(quests)
```
**Expected output:**
```
No save file at does_not_exist.json yet — starting fresh.
{}
```

**Line by line:** `FileNotFoundError` (a built-in exception, from Lesson 06's world) is raised by `open()` itself when the path doesn't exist — completely normal and expected the *first time* a program runs, before it's ever saved anything, so handling it gracefully (return an empty starting state) rather than crashing is exactly the right behavior for a persistence layer. `json.JSONDecodeError` is raised by `json.load`/`json.loads` when the file's content exists but isn't valid JSON at all (e.g., it got manually edited and broken, or a previous write was interrupted partway through) — also a completely realistic failure for any program reading its own save file back, and exactly the kind of thing Rule-driven, "explain why" error handling (Lesson 06) exists to make deliberate rather than accidental.

**Try it yourself:** manually create a file `broken.json` containing just the text `{not valid json` (no closing brace, deliberately broken), then call `load_quests("broken.json")` against it. Predict which `except` branch fires before running it.

## Common mistakes & gotchas

- **Opening a file with `"w"` when you meant to read it, wiping out its contents by accident.** `"w"` truncates immediately on open, before you've even called `.write()` — double-check your mode character every time, especially against a real save file you care about.
- **Forgetting `with` and leaking an open file handle**, especially inside a function where an exception between `open()` and `.close()` would skip the close entirely. Always use `with open(...) as f:`.
- **Confusing `json.dump`/`json.load` (files) with `json.dumps`/`json.loads` (strings)**, e.g. calling `json.dump(data, "quest.json")` and getting a confusing error, because the second argument to `json.dump` must be an *already-open file object*, not a filename string.
- **Assuming a `set` or `tuple` will round-trip through JSON unchanged.** Sets raise an error entirely; tuples silently become plain lists — if your program logic depends on "this was specifically a tuple," JSON persistence alone won't preserve that distinction.
- **Not handling `FileNotFoundError` for a save file that legitimately hasn't been created yet.** The very first run of any program with file-based persistence hits exactly this case — treat it as a normal, expected condition (start with empty/default data), not an error to crash on.
- **Writing partial/corrupted JSON because a crash happened mid-write.** A more advanced but realistic issue: if your program crashes exactly while writing a save file, the file can be left half-written and invalid. This lesson's `json.JSONDecodeError` handling covers *reading* a corrupted file gracefully; Lesson 10's context manager section shows a safer *writing* pattern (write to a temporary file, then rename) that avoids ever leaving a half-written file in the first place — genuinely useful for your capstone's save logic.

## How this connects

This lesson is the direct backbone of your capstone's persistence layer — quests saved to and loaded from a `.json` file, using exactly the `try`/`except FileNotFoundError`/`except json.JSONDecodeError` pattern shown above. Lesson 10 (Decorators and Context Managers) revisits `with` specifically, opening the hood on *how* it guarantees cleanup, and shows a safer file-writing pattern building on this lesson's JSON handling. Module 02 (Web Fundamentals) and Module 05 (FastAPI) both rely on JSON as the universal format for data flowing over the internet — everything you just learned about the Python↔JSON mapping applies unchanged there.

## Quick self-check

1. Why should you always use `with open(...) as f:` instead of calling `open()`/`.close()` by hand?
2. What's the difference between opening a file in `"w"` mode versus `"a"` mode?
3. What's the naming rule that tells you when to use `json.dump` vs. `json.dumps`?
4. Name two Python data types that do *not* survive a round-trip through JSON unchanged, and explain what happens to each.
5. Why is handling `FileNotFoundError` when loading a save file a normal, expected case rather than a genuine error?
