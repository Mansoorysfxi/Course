# Module 01 — Checklist

Complete this after finishing all five exercises and the capstone project,
and after your module-end review ("Check my module"). Don't start Module 02
until every box below is checked and any remedial exercises from your
review are done.

## Self-assessment

Answer these honestly, in your own words (writing them down — e.g. in your
Module 00 `course-companion` repo's notes — is more valuable than answering
silently in your head):

- [ ] I can explain why `def f(items=[]):` is dangerous and what the correct fix is, without looking it up.
- [ ] I can explain, from memory, when to reach for a `list` vs. a `tuple` vs. a `set` vs. a `dict`, including the time-complexity reasoning, not just "they're different."
- [ ] I can explain what `for item in my_list:` actually does, in terms of `iter()`, `next()`, and `StopIteration`, without needing to re-read Lesson 04.
- [ ] I can explain the difference between inheritance and composition, and give a concrete example of when I'd choose one over the other — ideally using a game-dev example, not just the one from the lesson.
- [ ] I have written at least one custom exception class that inherits from another custom exception class (not directly from `Exception`), and can explain why that hierarchy is useful.
- [ ] I can create, activate, and use a `venv` in Git Bash without checking the lesson, and I understand what `pip freeze > requirements.txt` is actually capturing.
- [ ] I have handled both a missing file and malformed JSON gracefully in real code, with two different `except` blocks, not one generic catch-all.
- [ ] I can write a type hint for "a function returning a list of dicts, or `None`" using modern syntax, without reaching for `typing.List`/`typing.Optional`.
- [ ] I have written my own decorator from scratch (using `functools.wraps` and `*args, **kwargs`) and my own context manager (using `@contextmanager`), and can explain what each one is doing mechanically, not just that it works.
- [ ] I can explain, using the game-loop analogy, why `async`/`await` doesn't make CPU-bound code faster, only I/O-bound waiting more efficient.
- [ ] All five exercises were reviewed and scored 7/10 or higher (or revised until they were).
- [ ] The capstone (QuestLog CLI) runs, persists data correctly across restarts, and was reviewed.

## Spaced-repetition review questions from earlier modules

Module 01 is the first module where this section applies for real (Module
00 had none — there was no earlier material yet). These five questions are
pulled from Module 00's actual content — answer them from memory before
checking `module-00-developer-environment-and-tooling/lessons/` if you get
stuck. If any of these feel shaky, that's a real signal to briefly revisit
the relevant Module 00 lesson before moving on to Module 02, not just to
this module's own material.

1. What's the difference between Git and GitHub, in your own words? *(Module 00, Lesson 00)*
2. What does `PATH` actually do, and what's the first thing you should try when a freshly-installed command gives `command not found`? *(Module 00, Lesson 01)*
3. What do the three Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) each represent, and what must you do with them before completing a merge? *(Module 00, Lesson 04)*
4. Why did merging a Pull Request on GitHub's website not automatically update your local `main` branch — what command fixes that? *(Module 00, Lesson 05)*
5. When reading an unfamiliar error message or stack trace, do you start at the top or the bottom, and why? *(Module 00, Lesson 02)*

## Before you move on to Module 02

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your Module 01 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 02 README to see what's coming next.
