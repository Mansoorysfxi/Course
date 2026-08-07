# Module 01 Capstone — QuestLog CLI

## What this is

A real, runnable command-line quest tracker with JSON file persistence —
your own program, not another guided exercise. This is the **QuestLog
CLI**: a standalone tool, its own small codebase, that establishes the
"quests, quest lines, priority, done/not-done" domain the rest of this
course's running project (the web-based **QuestLog** app, starting in
Module 04 — see [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md)) will
reuse conceptually. **This capstone is not the same codebase as that later
app** — it's a fresh, separate, purely local CLI tool, built entirely with
what you've learned in this module. Nothing here carries forward as code;
what carries forward is the domain (the idea of a "quest" with a name,
priority, and completion state) and, more importantly, your comfort with
every Python fundamental this module taught.

## Concepts this project uses, and where each was taught

Every concept below has a dedicated lesson section — nothing here requires
anything not explicitly covered in this module (per the master plan's Rule
1: no exercise or project may need untaught material):

| Concept | Taught in |
|---|---|
| Variables, `if`/`elif`/`else`, `while` loops, f-strings, string methods (`.strip()`/`.split()`) | [Lesson 01](../lessons/01-variables-types-and-control-flow.md) |
| Functions, default arguments, `*args`/`**kwargs` | [Lesson 02](../lessons/02-functions-and-scope.md) |
| Lists, dicts, sets, and choosing between them | [Lesson 03](../lessons/03-data-structures.md) |
| List comprehensions (for filtering quests) | [Lesson 04](../lessons/04-comprehensions-generators-and-iterators.md) |
| Classes, `__init__`, `__repr__`, `__eq__`, composition | [Lesson 05](../lessons/05-oop-classes-and-dunders.md) |
| Custom exceptions, `try`/`except`/`finally` | [Lesson 06](../lessons/06-error-handling.md) |
| Packages, `__init__.py`, relative imports, `if __name__ == "__main__":` | [Lesson 07](../lessons/07-modules-packages-and-virtual-environments.md) |
| File I/O, `json.dump`/`json.load`, handling `FileNotFoundError`/`JSONDecodeError` | [Lesson 08](../lessons/08-file-io-and-json.md) |
| Type hints on every function/class (`list[...]`, `dict[...]`, `X \| None`) | [Lesson 09](../lessons/09-type-hints.md) |
| A decorator (command logging) and a context manager (safe JSON writes) | [Lesson 10](../lessons/10-decorators-and-context-managers.md) |

**Deliberately not used: `async`/`await` (Lesson 11).** This tool has no
genuine I/O-bound waiting to overlap — it reads/writes one small local file
and reads keyboard input, both effectively instant on any modern machine.
Forcing `async def` onto this code would add ceremony with zero real
benefit, which is exactly the judgment call Lesson 11 itself warns
against ("async gives you overlap during waiting, never simultaneous CPU
computation" — there's no meaningful wait here to overlap). You'll use
`async`/`await` for real starting in Module 05, once there's a real web
server juggling real concurrent requests.

## What to build

### 1. Project setup

Following Lesson 00 and Lesson 07's exact conventions:

```bash
mkdir ~/questlog-cli
cd ~/questlog-cli
python -m venv .venv
source .venv/Scripts/activate
```

This project needs **no third-party packages** — everything it uses
(`json`, `os`, `time`, `functools`, `contextlib`) is in Python's standard
library. Still create `requirements.txt` (even if empty, or with a comment
noting "no dependencies") — the habit of having one from day one matters
more than its contents on any single project.

### 2. Package structure

```
questlog-cli/
├── requirements.txt
├── main.py
└── questlog/
    ├── __init__.py
    ├── models.py        ← Quest class
    ├── exceptions.py    ← custom exception hierarchy
    ├── manager.py       ← QuestManager class + safe JSON persistence
    ├── decorators.py    ← the @log_command decorator
    └── cli.py           ← the interactive command loop
```

### 3. `questlog/models.py` — the `Quest` class

A `Quest` needs, at minimum: `name: str`, `priority: str` (e.g. `"low"`,
`"medium"`, `"high"` — validate it's one of these three, raising a custom
exception otherwise), `quest_line: str | None` (optional grouping — `None`
if this quest isn't part of one), and `is_complete: bool` (defaults to
`False`). Give it a proper `__repr__` (Lesson 05's pattern) and an
`__eq__` comparing `name` and `quest_line` (two quests with the same name
in the same quest line are considered the same quest for this tool's
purposes). Every parameter and method needs a type hint (Lesson 09).

### 4. `questlog/exceptions.py` — your exception hierarchy

At minimum: a base `QuestLogError(Exception)`, plus
`QuestNotFoundError(QuestLogError)` (raised when a lookup by name fails)
and `InvalidPriorityError(QuestLogError)` (raised when `Quest` is given a
priority outside `"low"`/`"medium"`/`"high"`) — following Lesson 06's exact
pattern of a small, deliberate hierarchy rather than reusing generic
built-ins for domain-specific problems.

### 5. `questlog/manager.py` — the `QuestManager` class and persistence

`QuestManager` holds its quests internally (composition — Lesson 05) in
whichever data structure you can justify (a `list[Quest]`? a
`dict[str, Quest]` keyed by name for O(1) lookup? — Lesson 03's
time-complexity intuition should inform, and you should be able to explain,
whichever you pick). It needs at least:

- `add_quest(self, name, priority, quest_line=None) -> Quest`
- `complete_quest(self, name) -> None` — raises `QuestNotFoundError` if no
  quest with that name exists (Lesson 06's "raise your own exception
  instead of letting a raw `KeyError`/lookup failure propagate" pattern).
- `delete_quest(self, name) -> None` — same error-handling expectation.
- `list_quests(self, quest_line=None) -> list[Quest]` — returns all
  quests, or only those in a given quest line if provided, using a **list
  comprehension** (Lesson 04) for the filtering.
- `save(self, path) -> None` and a module-level or classmethod-style
  `load(path) -> QuestManager` (or similar) — persistence to/from JSON.
  **Use a context manager for the write path** — write a
  `@contextmanager`-based `safe_json_write(path)` (Lesson 10's exact
  pattern: write to a temporary file, then `os.replace()` it into place
  only once writing succeeds, so a crash mid-save can never corrupt your
  real save file). **Handle both realistic load failures** from Lesson 08:
  a missing file (start with an empty `QuestManager`, not an error) and
  malformed JSON (raise your own `QuestLogError` subclass, not a raw
  `json.JSONDecodeError`).

### 6. `questlog/decorators.py` — `@log_command`

A decorator (Lesson 10's exact pattern, using `functools.wraps` and
`*args, **kwargs`) that, applied to each command-handling function in
`cli.py`, logs — printed to the console, or appended to a small
`command_log.txt` file, your choice — which command ran, with what
arguments, and whether it succeeded or raised. This is the natural,
motivated use of a decorator this brief keeps referring to: an audit trail
of every action taken on your quest log, added in one line per command
function rather than duplicated logging code inside each one.

### 7. `questlog/cli.py` — the interactive command loop

A simple `input()`-based loop (no need for `argparse` or any other
unfamiliar module — plain `input()` plus `.strip()`/`.split()`, all from
Lesson 01, is enough) supporting at least: `add`, `list`, `complete
<name>`, `delete <name>`, `filter <quest_line>`, and `quit` (which saves
before exiting). Wrap command dispatch in `try`/`except QuestLogError` so a
mistyped quest name produces a friendly message instead of a crash
(Lesson 06's "catch at the boundary" pattern from Exercise 03).

### 8. `main.py` and `__init__.py`

`main.py` (top-level, outside the package) imports from `questlog` and
calls the CLI's entry point, guarded by `if __name__ == "__main__":`
(Lesson 07). `questlog/__init__.py` re-exports whatever you consider the
package's "public" pieces (at minimum `Quest` and `QuestManager`).

## Acceptance criteria

- [ ] Running `python main.py` starts an interactive loop; `add`, `list`, `complete`, `delete`, `filter`, and `quit` all work as described.
- [ ] Quests persist: add a few quests, `quit`, run `python main.py` again, `list` — the same quests are still there, loaded from the JSON file.
- [ ] Deleting or completing a quest name that doesn't exist prints a friendly error message (via a caught `QuestNotFoundError`) rather than crashing with a traceback.
- [ ] `Quest`'s priority validation actually rejects an invalid priority (e.g. `"urgent"`) with `InvalidPriorityError`, not a generic exception.
- [ ] The JSON save file, opened directly in a text editor, is valid, readable JSON matching what `list` shows.
- [ ] Killing the program (e.g. closing the terminal) mid-save should never leave a corrupted save file — you don't need to literally demonstrate a mid-crash, but your `save` implementation must visibly use the temp-file-then-`os.replace()` pattern, not a direct overwrite.
- [ ] Every function and method has type hints, using modern syntax (`list[...]`, `dict[...]`, `X | None` — Lesson 09).
- [ ] `@log_command` is applied to at least the `add`/`complete`/`delete` command handlers and visibly logs each call.
- [ ] The project has its own `.venv` (not submitted/committed) and a `requirements.txt` (even if it states there are no third-party dependencies).

## What to submit for review

When you're ready, tell your AI session *"Review my capstone for Module
01"* and point it at (or paste) your `questlog-cli/` project — specifically
`questlog/models.py`, `questlog/manager.py`, `questlog/decorators.py`,
`questlog/cli.py`, and a sample of your saved JSON file. The AI will grade
this per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md), the same
rubric used for every exercise, applied to the whole project as one
submission.

## Why this project, specifically

Every module in this course ends with something that forces you to combine
everything just taught into one coherent, working thing, rather than
leaving each concept isolated in its own five-line example forever. A CLI
task tracker is small enough to actually finish in a reasonable amount of
time, but genuinely touches almost everything: real classes with real
relationships (composition, not just one lonely `Quest` class), real
persistence with real failure modes (a missing file, a corrupted file), and
a decorator/context manager pair with an actual motivation behind each one
rather than existing just to check a box. The domain itself — quests,
quest lines, priority, done/not-done — is deliberately simple (per
[`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md)) so that everything hard
about this capstone is the *Python*, not the business logic; you'll meet
this exact domain again, in a completely different codebase and technology
stack, starting in Module 04.
