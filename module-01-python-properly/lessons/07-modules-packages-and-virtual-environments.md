# Lesson 07 — Modules, Packages, Imports, and Why Isolation Matters

## What you'll learn

- What a **module** is (spoiler: every `.py` file already is one) and what a **package** adds on top of that.
- `import`, `from ... import ...`, and `as` — the different ways to bring code from one file into another.
- What `__init__.py` does, and whether you still need it in modern Python.
- How Python actually finds a module when you `import` it (the module search path).
- The `if __name__ == "__main__":` pattern, and why it exists.
- A deeper look at *why* virtual environments and `requirements.txt` (introduced hands-on in Lesson 00) matter, now that you understand imports.

## Why this matters

Every project beyond a single throwaway script needs to be split across multiple files — your capstone alone will have at least a couple of files (e.g., the data model, and the command-line interface driving it). This lesson is what makes that possible and predictable: how Python locates and loads code across files, and how to organize related files into a proper package rather than a pile of loosely related scripts. It's also where Lesson 00's `venv`/`pip` setup gets its full justification, now that you understand what "importing a package" really means.

## Prerequisites

Lesson 00 (Setup — you already have a venv and have used `pip`/`requirements.txt` once). Lessons 01–06 for general comfort, though this lesson doesn't build directly on any single one of them.

## The concept, explained simply

A **module** is just a single Python file — nothing more. The moment you save a file called `quest_utils.py`, you have a module named `quest_utils`, whether or not you ever intended it as one. A **package** is a *folder* of related modules, grouped together and given its own name, so you can `import` the whole group as one unit — analogous to how an Unreal plugin bundles several related classes/assets under one plugin name rather than shipping loose files. `import` is the mechanism for pulling code defined in one module into another, so you don't have to copy-paste it or cram your entire program into one giant file.

## The details

### Your first import — using the standard library

Python ships with a large **standard library** — modules that come pre-installed with every Python install, no `pip install` needed (you've already used one implicitly: `sys`, in Lesson 04).

```python
import math

print(math.sqrt(144))
print(math.pi)
```
**Run:** `python lesson07.py` → **Expected output:**
```
12.0
3.141592653589793
```

`import math` makes the entire `math` module available under the name `math` — every function/value inside it (`sqrt`, `pi`, and many more) is accessed with a `math.` prefix. This prefixing is deliberate: it avoids ambiguity about *where* `sqrt` came from if you ever import multiple modules that happen to define something with the same name.

### `from ... import ...` — pulling out specific names

```python
from math import sqrt, pi

print(sqrt(144))
print(pi)
```
**Expected output:** identical to above, but now `sqrt` and `pi` are used *without* the `math.` prefix — they've been imported directly into your file's own namespace.

**Trade-off:** `import math` is more verbose per use but always unambiguous about origin; `from math import sqrt` is shorter but risks silently colliding with a same-named thing you define yourself later in the same file (your own `pi = 3` would then shadow the imported one, an easy source of confusion). This course generally prefers `import module_name` and using the `module_name.thing` prefix for third-party/less-obvious names, and reserves `from ... import ...` for very common, unambiguous cases.

### `as` — renaming an import

```python
import math as m

print(m.sqrt(144))
```
Used constantly in real-world code for long or awkward names — you'll see this exact pattern with third-party libraries starting in later modules (e.g. `import numpy as np` is a near-universal convention in data/AI code you'll meet in Phase 4). It doesn't change what's imported, only the local name you refer to it by.

### Splitting your own code across files — your first custom module

Create two files in the same folder:

`quest_utils.py`:
```python
def format_quest(name, reward_gold):
    return f"{name} (rewards {reward_gold} gold)"

DIFFICULTY_LEVELS = ["Trivial", "Easy", "Medium", "Hard", "Legendary"]
```

`lesson07_main.py`:
```python
import quest_utils

print(quest_utils.format_quest("Slay the Dragon", 500))
print(quest_utils.DIFFICULTY_LEVELS)
```
**Run:** `python lesson07_main.py` → **Expected output:**
```
Slay the Dragon (rewards 500 gold)
['Trivial', 'Easy', 'Medium', 'Hard', 'Legendary']
```

`import quest_utils` works with **no special setup at all** here specifically because `quest_utils.py` sits in the *same folder* you're running `lesson07_main.py` from — Python automatically looks in the current script's own folder first (more on the full search order below). Notice `quest_utils` is *just a name* referring to the file `quest_utils.py` — the `.py` extension is never written in the `import` statement itself.

### How Python actually finds a module — the search path

```python
import sys
print(sys.path)
```
**Expected output:** a list of folder paths, in order — something like:
```
['/c/Users/YourName/python-practice', '/c/Users/YourName/AppData/.../python314.zip', ..., '/c/Users/YourName/python-practice/.venv/Lib/site-packages']
```

**What this actually is:** the exact, ordered list of folders Python searches, top to bottom, when you write `import something` — stopping at the *first* match it finds, exactly the same "search a list in order, stop at first match" idea as `PATH` from Module 00, just for Python modules instead of terminal programs. It always includes: the running script's own folder (first — which is why `quest_utils` above just worked), the standard library's location, and — critically, connecting directly back to Lesson 00 — your active virtual environment's `site-packages` folder, which is *where `pip install` actually puts things*. This is the real mechanism behind "activate the right venv before running your script" from Lesson 00: if the wrong (or no) venv is active, `sys.path` won't include the folder holding whatever you `pip install`-ed, and `import` fails with `ModuleNotFoundError`, even though the package is genuinely installed *somewhere* on your machine.

### Packages — a folder of modules, with `__init__.py`

A **package** groups multiple modules under one importable name. Create this structure:

```
questlog_pkg/
├── __init__.py
├── models.py
└── formatting.py
```

`questlog_pkg/models.py`:
```python
class Quest:
    def __init__(self, name):
        self.name = name
```

`questlog_pkg/formatting.py`:
```python
def format_name(name):
    return name.title()
```

`questlog_pkg/__init__.py` (can be completely empty, or can re-export things):
```python
from .models import Quest
```

Then, from a script *outside* `questlog_pkg/` (in the parent folder):
```python
from questlog_pkg import Quest
from questlog_pkg.formatting import format_name

q = Quest(format_name("slay the dragon"))
print(q.name)
```
**Expected output:** `Slay The Dragon`

**Line by line:**
- The folder `questlog_pkg/` becomes an importable package named `questlog_pkg` specifically *because* it contains an `__init__.py` file (historically — see the note below on modern Python).
- `from .models import Quest` inside `__init__.py` uses a **relative import** — the leading `.` means "from a module inside this same package," regardless of what the package itself is ultimately named or where it lives on disk. This line is what makes `from questlog_pkg import Quest` work directly, without callers needing to know it actually lives in `questlog_pkg/models.py` — `__init__.py` is choosing to "re-export" it at the package's top level, a common, deliberate convenience for whoever uses your package.
- `from questlog_pkg.formatting import format_name` reaches directly into a specific module *inside* the package, using dotted-path notation — this always works regardless of what `__init__.py` does or doesn't re-export.

**Do you still need `__init__.py` in modern Python?** Technically, no — Python 3.3+ supports "namespace packages," where a plain folder with no `__init__.py` at all can sometimes still be imported. In practice, for this course (and the overwhelming majority of real, non-trivial Python projects, including everything FastAPI-based starting Module 05), you should **still always include an explicit `__init__.py`** — even an empty one. It makes your intent unambiguous, avoids a category of confusing edge cases namespace packages can introduce, and is what virtually every real-world Python codebase and tutorial you'll encounter actually does. Treat "empty or re-exporting `__init__.py` in every package folder" as this course's standing convention.

### `if __name__ == "__main__":` — letting a file be both a module and a script

```python
# quest_utils.py (extended)
def format_quest(name, reward_gold):
    return f"{name} (rewards {reward_gold} gold)"

if __name__ == "__main__":
    print(format_quest("Test Quest", 1))
```

Run it directly: `python quest_utils.py` → **Expected output:** `Test Quest (rewards 1 gold)`

But `import quest_utils` from another file does **not** print anything — the block under `if __name__ == "__main__":` is skipped entirely.

**Why:** every module has a built-in variable, `__name__`, that Python sets automatically. When a file is run *directly* (`python quest_utils.py`), Python sets `__name__` to the literal string `"__main__"` for that file. When the exact same file is instead *imported* by another file, Python sets `__name__` to the module's actual name (`"quest_utils"`) — never `"__main__"`. This one `if` check is how a single file can serve double duty: reusable code that other files import cleanly (without unwanted side effects like a demo print statement firing), *and* a runnable script when executed directly for testing/demonstration. Your capstone's entry point script uses this exact pattern.

## Common mistakes & gotchas

- **`ModuleNotFoundError` for a package you're sure you installed.** Almost always: the wrong venv is active (or none at all) — recall Lesson 00's `which python`/`(.venv)` prompt check. `sys.path` (above) tells you definitively whether the environment you *think* is active actually is.
- **Naming your own file the same as a standard library or installed package (e.g., `random.py`, `json.py`).** Because the running script's own folder is searched *first*, your file can accidentally shadow a real standard-library module, causing baffling errors deep inside unrelated code that tried to `import random` and got your file instead. Avoid naming your own files after anything in the standard library.
- **Confusing a relative import's `.` with a filesystem path.** `from .models import Quest` has nothing to do with "the current directory" the way `.` means in the shell (Module 00) — it specifically means "relative to this package," a Python-import-system-only concept.
- **Forgetting `__init__.py` and being confused why a folder "isn't a package."** Add an empty `__init__.py` — per this lesson's stated convention, always include one, don't rely on namespace-package behavior.
- **Putting real logic directly at a module's top level (outside any function, with no `__name__ == "__main__"` guard) and being surprised it runs the instant the file is merely imported.** Anything not inside a function/class, at a module's top level, executes immediately the first time that module is imported *anywhere* — this is usually fine for constants (`DIFFICULTY_LEVELS` above) and dangerous for anything with real side effects (printing, opening files, making network calls).

## How this connects

This lesson is the conceptual deep-dive behind the exact commands you already ran hands-on in Lesson 00 (`python -m venv`, `pip install`, `pip freeze > requirements.txt`) — you now know *why* activating the right venv matters (`sys.path`), and *why* isolating packages per-project matters (two projects needing different, incompatible versions of the same package would otherwise collide in one shared `site-packages`). Your capstone project is structured as a small package using exactly the `__init__.py` + multiple `.py` files pattern shown here, with an `if __name__ == "__main__":` entry point.

## Quick self-check

1. What's the difference between a module and a package?
2. Why did `import quest_utils` work with zero configuration when the two files were in the same folder — what's actually happening?
3. What does `sys.path` represent, and how does it explain a `ModuleNotFoundError` for a package you're sure is installed?
4. What does the leading `.` mean in `from .models import Quest`, and how is that different from a shell path's `.`?
5. Why does `if __name__ == "__main__":` prevent code from running when a file is imported, but not when it's run directly?
