# Module 01 — Python, Properly

**Phase:** 0 — Foundations & Environment
**Estimated time:** 14–20 hours over one to two weeks (this module is dense — see "A note on scope" below)
**Verified against:** Python 3.14.7 (current stable release, August 2026 — 3.13.15 also actively maintained), pip (bundled with the installer), VS Code Python extension (`ms-python.python`, actively updated monthly, ~2026.4–2026.5.x builds) alongside its companion Python Environments extension. Type-hint syntax verified against PEP 585 (built-in generics, e.g. `list[int]`, standard since Python 3.9) and PEP 604 (`X | None` union syntax, standard since Python 3.10). See `lessons/00-setup.md` and `lessons/09-type-hints.md` for exactly what was checked and when.

## What this module is

You told us you know "a little" Python. This module takes that little bit
and turns it into the real, professional-grade Python the rest of this
course assumes: functions done properly (including the gotchas that catch
even experienced developers), every core data structure and *why* you'd
choose one over another, what a `for` loop actually does underneath, real
object-oriented Python compared directly against the C++ you already know,
deliberate error handling, a working virtual-environment/package workflow,
file I/O and JSON, type hints, and — because they're needed for FastAPI
starting in Module 05 — decorators, context managers, and the async/await
model, each fully "opened up" rather than left as unexplained syntax.

In Unreal terms: Module 00 got your engine and source control installed.
This module is learning the actual scripting language properly — not just
enough to make something run, but enough to read, debug, and extend real
code confidently, the way you already can in C++.

## What you'll be able to do after this module

- Write functions correctly, including default arguments, `*args`/`**kwargs`, and understand exactly why the "mutable default argument" bug happens and how to avoid it.
- Choose the right data structure (list, tuple, set, dict) for a given problem, with real time-complexity intuition, not guesswork.
- Explain, mechanically, what `for` actually does under the hood, and use comprehensions and generators appropriately.
- Write real Python classes — dunder methods, inheritance vs. composition — and compare each choice directly against C++'s equivalent.
- Handle errors deliberately: `try`/`except`/`finally`, and your own custom exception hierarchies.
- Set up and use a virtual environment and `pip`/`requirements.txt` without confusion, and structure your own code as proper modules/packages.
- Read and write files, and persist data as JSON, handling the realistic failure modes (missing file, corrupted content).
- Add type hints using modern syntax, and understand what they do (and don't do) for you.
- Write your own decorators and context managers from scratch, and explain exactly what `@` and `with` do underneath.
- Explain the event loop and `async`/`await` using a direct analogy to a game loop, and know when async genuinely helps versus when it's pointless ceremony.
- Build and ship a real, working command-line tool with JSON persistence — your Module 01 capstone.

## Prerequisites

**Module 00, specifically:** shell comfort (navigating folders, running
commands, reading `PATH`/environment variable errors) and Git basics
(commit/branch, reading an error message systematically) are assumed
throughout this module with no re-teaching. If any of that feels shaky,
revisit Module 00 before starting here — this module's setup lesson
(`lessons/00-setup.md`) briefly re-verifies your shell but does not
re-teach it.

## Module structure

```
module-01-python-properly/
├── README.md                                        ← you are here
├── lessons/
│   ├── 00-setup.md                                  ← install Python, venv, pip, verify VS Code
│   ├── 01-variables-types-and-control-flow.md       ← brisk review: variables, types, if/while/for
│   ├── 02-functions-and-scope.md                    ← functions, scope, *args/**kwargs, gotchas
│   ├── 03-data-structures.md                        ← lists, tuples, sets, dicts, time complexity
│   ├── 04-comprehensions-generators-and-iterators.md← comprehensions, generators, what for really does
│   ├── 05-oop-classes-and-dunders.md                ← classes, dunders, inheritance vs. composition
│   ├── 06-error-handling.md                         ← exceptions, try/except/finally, custom exceptions
│   ├── 07-modules-packages-and-virtual-environments.md ← modules, packages, __init__.py, venv/pip deep dive
│   ├── 08-file-io-and-json.md                       ← reading/writing files, JSON persistence
│   ├── 09-type-hints.md                             ← modern type hint syntax
│   ├── 10-decorators-and-context-managers.md        ← full "open the hood" treatment
│   └── 11-async-await-fundamentals.md               ← event loop, explained like a game loop
├── exercises/
│   ├── 01-functions-and-data-structures/            ← very easy
│   ├── 02-comprehensions-generators-and-oop/         ← guided
│   ├── 03-errors-files-and-json/                     ← guided
│   ├── 04-modules-packages-and-venv/                 ← guided/independent
│   └── 05-decorators-context-managers-and-async/     ← independent
├── project/
│   └── BRIEF.md                                     ← QuestLog CLI capstone
└── CHECKLIST.md
```

Read the lessons in numeric order — later lessons assume earlier ones
without re-explaining. Do not skip `00-setup.md`, even if Python is already
installed on your machine — it ends with a "Verify your setup" section that
confirms your specific version, venv, and VS Code integration all actually
work together before you rely on them for eleven more lessons.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson
fully, answer its self-check questions, do the matching exercise without
peeking at the solution, then ask your AI session *"Review my solution for
exercise 0N"*. After all five exercises and the capstone are done, say
*"Check my module"* for the full module-end review — this is also the
first module where your `CHECKLIST.md` includes real spaced-repetition
questions pulled from Module 00.

## A note on scope

This module covers more ground than Module 00 — the master plan's own
curriculum for "Python, Properly" is deliberately dense, on the theory that
you already know *some* Python and need thorough revision plus several
genuinely new topics (decorators, context managers, async) rather than a
ground-up introduction. Lessons 01–03 move briskly since they're mostly
revision; expect to slow down considerably starting around Lesson 05
(OOP) through Lesson 11 (async) — that's intentional, and matches where
"a little Python" typically runs out.

## A note on the capstone

The Module 01 capstone (`project/BRIEF.md`) has you build the **QuestLog
CLI** — a standalone command-line quest tracker with JSON persistence. This
is a genuinely separate, throwaway codebase from the web-based **QuestLog**
app that begins in Module 04 (see [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md))
— nothing here carries forward as code. What carries forward is the
domain (quests, quest lines, priority, done/not-done) and, far more
importantly, real comfort with everything this module taught, exercised
together in one working program instead of eleven separate small examples.
