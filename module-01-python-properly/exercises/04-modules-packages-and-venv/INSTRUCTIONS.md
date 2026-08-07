# Exercise 04 — A Real Package, a Real Venv (Guided / Independent)

**Difficulty:** Guided/independent — the target structure is specified
exactly, but you build it entirely from scratch this time, including the
terminal commands, the way Module 00's Exercises 02–03 had you build a real
repo from scratch rather than filling in a skeleton.

**Concepts this exercise uses:**
- From [`lessons/07-modules-packages-and-virtual-environments.md`](../../lessons/07-modules-packages-and-virtual-environments.md): packages, `__init__.py`, relative imports, `sys.path`, `if __name__ == "__main__":`.
- From [`lessons/00-setup.md`](../../lessons/00-setup.md): `python -m venv`, activation in Git Bash, `pip install`, `pip freeze > requirements.txt`.
- From [`lessons/09-type-hints.md`](../../lessons/09-type-hints.md): hinting every function/method you write here, using the modern `list[...]`/`dict[...]`/`X | None` syntax.

## What to build

Unlike Exercises 01–03, there's no `starter/` skeleton to fill in — you're
building a small, real, isolated Python project from nothing, the same way
you built `recipe-box` from nothing in Module 00. Do all of this in a fresh
folder, e.g. `~/questpkg-project` (outside this course repo is fine, or
inside your own `solution/` copy here if you'd rather keep it self-contained
— either is fine, since this exercise isn't graded on *where* it lives).

1. **Create the project folder and set up a venv, per Lesson 00:**
   ```bash
   mkdir ~/questpkg-project
   cd ~/questpkg-project
   python -m venv .venv
   source .venv/Scripts/activate
   ```
2. **Install one real package and freeze it,** exactly rehearsing Lesson
   00's mechanics (this package won't actually be *used* by your code below
   — it's here purely so you practice the install → freeze → reproduce
   loop on something real):
   ```bash
   pip install requests
   pip freeze > requirements.txt
   cat requirements.txt
   ```
3. **Build this package structure** inside the project folder:
   ```
   questpkg-project/
   ├── .venv/                (not committed/submitted — see below)
   ├── requirements.txt
   ├── main.py
   └── questpkg/
       ├── __init__.py
       ├── models.py
       └── formatting.py
   ```
4. **`questpkg/models.py`** — define a `Quest` class with type-hinted
   attributes (`name: str`, `difficulty: str`, `reward_gold: int`,
   `is_complete: bool = False`) and a type-hinted `__init__`. Every
   parameter and the return type of every method (including `__init__ ->
   None`) must be hinted, per Lesson 09.
5. **`questpkg/formatting.py`** — `from .models import Quest` (a relative
   import, per Lesson 07), then define `format_quest(quest: Quest) -> str`
   that returns a readable one-line description of a quest. Add an
   `if __name__ == "__main__":` block at the bottom that builds one sample
   `Quest` and prints `format_quest(...)`'s result — so this file works
   both as an importable module *and* a standalone demo script, per Lesson
   07's exact pattern. **A genuine gotcha you'll hit here:** running
   `python questpkg/formatting.py` directly produces
   `ImportError: attempted relative import with no known parent package` —
   a relative import (`.models`) only works when Python knows the file is
   being run *as part of a package*, which a direct file path doesn't
   convey. The fix (and the standard, correct way to run any file inside a
   package directly) is to use the `-m` flag you already met in Lesson 00
   for `venv`, applied here to a dotted module path instead, run from the
   project's top-level folder:
   ```bash
   python -m questpkg.formatting
   ```
   This tells Python "run `formatting` specifically as a module inside the
   `questpkg` package," which correctly establishes the package context
   relative imports need.
6. **`questpkg/__init__.py`** — re-export `Quest` at the package's top
   level, so `from questpkg import Quest` works directly (Lesson 07's
   `from .models import Quest` pattern).
7. **`main.py`** (top-level, outside the package) — `from questpkg import
   Quest`, `from questpkg.formatting import format_quest`, create a couple
   of `Quest` instances, print each one's formatted description, all inside
   an `if __name__ == "__main__":` guard.
8. **Run it and confirm it works:**
   ```bash
   python main.py
   ```

## Acceptance criteria

- [ ] The exact folder structure above exists, with `__init__.py` present in `questpkg/` and re-exporting `Quest`.
- [ ] Every function/method you wrote has type hints on every parameter and its return type, using modern syntax (`list[...]`, `dict[...]`, `X | None` — not `typing.List`/`Optional` from before Python 3.9/3.10, per Lesson 09).
- [ ] `python main.py`, run from the project's top-level folder, prints sensible output with no errors.
- [ ] `python -m questpkg.formatting`, run from the project's top-level folder, also works and prints its own demo output — proving both the `if __name__ == "__main__":` guard and the relative import are working correctly together (Lesson 07).
- [ ] `requirements.txt` exists and contains a line like `requests==2.x.x` (an exact version pinned, from `pip freeze`).
- [ ] `.venv/` itself is **not** part of what you submit (it's large, regenerable, and per Lesson 00 should never be committed to version control) — only submit/describe the files above it.

## What to submit

Create a file `solution/MY_SUBMISSION.md` (in *this* exercise's folder,
i.e. `exercises/04-modules-packages-and-venv/solution/MY_SUBMISSION.md`)
containing:
1. The exact sequence of terminal commands you ran, from `mkdir` through `python main.py`.
2. The full contents of `requirements.txt`.
3. The output of running `python main.py`.
4. The output of running `python -m questpkg.formatting`.

Point your AI session at that file (or paste it) and say *"Review my
solution for Exercise 04."*

## Hints

- Stuck on `__init__.py`'s re-export? Re-read Lesson 07's package example
  — `from .models import Quest` inside `questpkg/__init__.py` is exactly
  the line you need, adapted to your own class.
- Stuck on hinting `format_quest`'s `quest` parameter with your own class?
  Lesson 09's "Hinting your own classes" section shows this directly — once
  `formatting.py` has `from .models import Quest` at the top, just write
  `quest: Quest` in the signature like any other hint.
- Got `ImportError: attempted relative import with no known parent
  package`? That's the exact, expected gotcha this exercise calls out
  above — you ran `python questpkg/formatting.py` directly instead of
  `python -m questpkg.formatting` from the project root. This isn't a bug
  in your code; it's a real, common Python behavior worth recognizing by
  name the first time you hit it, rather than being confused by it in a
  real project later.
- Stuck on why `pip freeze` inside a fresh venv shows more than just
  `requests`? `requests` itself depends on a few smaller packages (e.g.
  `certifi`, `charset-normalizer`, `idna`, `urllib3`) — `pip freeze` lists
  every installed package, direct or transitive, exactly as Lesson 00
  described.
- If you've re-read the relevant sections and are still stuck, ask your AI
  session for a Level 1 hint per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
