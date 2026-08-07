# Lesson 02 — Reading Documentation and Error Messages Like a Professional

## What you'll learn

- A systematic method for reading an error message / stack trace instead of guessing or panicking.
- How to read unfamiliar documentation efficiently — what to look for and in what order.
- Where to look first when something breaks, in priority order.
- Why "just Google the error" is real advice, and how to do it well.

## Why this matters

This is arguably the single highest-leverage skill in this entire course.
You are going to hit errors constantly — not because you're bad at this,
but because *everyone* does, forever, at every skill level. The difference
between a beginner and a senior engineer is almost never "the senior
engineer doesn't get errors" — it's that the senior engineer has a fast,
calm, systematic process for reading the error and finding the fix, while
the beginner freezes, panics, or randomly changes things hoping it helps.
This lesson teaches you that process explicitly, up front, so you have it
before you need it.

This also maps directly onto something you already know: reading Unreal's
Output Log after a crash, or a C++ compiler error with a wall of template
errors. The skill of "find the actually relevant line in a wall of noisy
text" transfers directly.

## Prerequisites

Lesson 01 (Shell) — some examples below use the terminal.

## The concept, explained simply

An error message is not an attack on you. It is the program *trying to
help you* by telling you exactly what it expected versus what actually
happened, and usually exactly where. Treat every error message as a clue
handed to you for free, not an obstacle. The skill is knowing how to read
the clue.

A **stack trace** (also called a "traceback" in Python) is a list showing
*the chain of function calls* that were active at the moment something
went wrong — like a breadcrumb trail. If function A called function B,
which called function C, and C is where the error happened, the trace shows
all three, in order, so you can see *how execution got there*, not just
*where it ended up*.

## The details

### A systematic method (use this every single time)

**Step 1 — Read the last line first, not the first line.**
In almost every language (Python included, which you'll see constantly
starting in Module 01), the *most specific, most useful* information is at
the *bottom* of the error output, even though the error happened logically
"first" in the trace. Beginners often start reading top-to-bottom, get
overwhelmed by unfamiliar internal code, and give up before reaching the
useful part at the bottom.

**Step 2 — Identify the error type and message.**
The last line is usually structured as `SomeErrorType: a human-readable
description`. The type alone often tells you the category of problem before
you even read the description — e.g. (you'll meet these properly in Module
01):
- `NameError` → you used a name (variable/function) that doesn't exist (yet, or a typo).
- `TypeError` → you used a value of the wrong kind for what you're doing with it (e.g., adding a number to text).
- `FileNotFoundError` → exactly what it says — a path was wrong or the file doesn't exist.
- `SyntaxError` → the code isn't even valid — often a missing colon, bracket, or quote.

**Step 3 — Find the line number that's actually *your* code.**
A trace often includes lines from libraries you didn't write. Scan for the
first (or last, depending on the language's ordering convention) line that
points at a file *you* created, and start your investigation there. That's
usually where the real mistake is, even if the error only *surfaced*
somewhere deep inside a library.

**Step 4 — Re-read that exact line and the few lines around it.**
Now that you know roughly what kind of mistake it is (from Step 2) and
exactly where (from Step 3), read that code slowly. Most errors are found
right here, once you're not scanning a wall of text anymore.

**Step 5 — If it's still not obvious, search the exact error message.**
Copy the error type + message (not your specific variable names/paths —
strip those out) and search it. Professional developers do this
constantly; it is not cheating, and it's explicitly part of this course's
process, not a substitute for it (see Rule 1 in the master plan — the
lessons teach the concept; searching is for "has someone hit this exact
wording before").

**A good search query:** `FastAPI "RequestValidationError" pydantic v2`
**A bad search query:** `my code doesn't work help`

Include the exact error type/class name in quotes, plus the library/tool
name and version if relevant, and strip out anything specific to your
project (your variable names, your file paths, your data).

**Step 6 — Check official docs before random blog posts, especially for anything version-specific.**
Search results skew toward old blog posts and outdated Stack Overflow
answers, because those accumulate the most votes/links over years — but
tools change. A five-year-old answer for a fast-moving library (React,
FastAPI, any AI API) can be actively wrong for the version you have
installed. Prefer, in this order: (1) the tool's own official docs site,
(2) the tool's official GitHub repository issues/discussions, (3) recent
(check the date!) Stack Overflow or blog content, (4) old content, treated
with suspicion.

### Worked example: reading a real Python traceback

You'll write actual code like this starting in Module 01 — for now, just
practice reading it as text.

```
Traceback (most recent call last):
  File "app.py", line 12, in <module>
    result = calculate_total(order)
  File "app.py", line 7, in calculate_total
    return order["price"] * order["quality"]
KeyError: 'quality'
```

Applying the method:
- **Step 1/2 (last line):** `KeyError: 'quality'` — a dictionary lookup
  failed because the key `'quality'` doesn't exist in it.
- **Step 3 (your code):** both frames are in `app.py`, which is your file —
  look at line 7, inside `calculate_total`.
- **Step 4 (re-read):** `order["quality"]` — is it possible the key is
  actually spelled `"quantity"`? That's almost certainly the bug: a typo, `quality`
  instead of `quantity`.
- You didn't need to search anything — the method alone found it. This is
  the common case: most errors are solvable with Steps 1–4 alone, and
  searching (Steps 5–6) is for the harder remainder.

### How to read unfamiliar documentation efficiently

You will constantly land on documentation pages for tools this course
introduces. A method, in order:

1. **Find the "Getting Started" / "Quickstart" page first**, not the full
   API reference. You want the smallest working example before anything
   else.
2. **Check the version.** Good docs show a version selector or state the
   version at the top. If a page doesn't mention a version and the tool
   changes fast, be suspicious — check the URL or a "last updated" date.
3. **Copy the smallest example and run it before reading further.** Reading
   docs passively teaches you much less than running the example and
   watching what happens, then changing one thing.
4. **Use the page's search / your browser's find-in-page (Ctrl+F)** rather
   than reading linearly, once you know roughly what you're looking for
   (e.g., "how do I set a timeout" → Ctrl+F "timeout").
5. **Check for a changelog / "what's new" page** when something that used
   to work stops working, or a tutorial you found online doesn't match what
   you're seeing — you may be on a newer (or older) version than the
   tutorial assumed.

## Common mistakes & gotchas

- **Reading top-to-bottom and giving up before the useful line at the
  bottom.** Covered above — retrain yourself to read bottom-up for
  tracebacks.
- **Searching your exact variable names or file paths.** This returns
  nothing useful, because no one else on the internet used your variable
  name. Generalize the query first.
- **Changing code randomly to "see if it helps" without forming a
  hypothesis.** This can accidentally "fix" something for the wrong reason,
  hiding the real bug until later. Always be able to state, in one
  sentence, *why* you think a change will fix the error before making it.
- **Trusting the first search result blindly.** Especially for fast-moving
  tools (anything in Phase 4 of this course), check the date and version
  the content is about.
- **Assuming an error is your fault when it might be an environment
  issue.** If literally nothing changed and something that worked
  yesterday now fails, check Lesson 01's `PATH`/environment concepts and
  your tool versions before assuming you introduced a logic bug.

## How this connects

You'll apply this method starting immediately — Module 00's own exercises
can produce Git errors, and essentially every module from here on produces
error messages of some kind. This lesson is the one you'll mentally return
to most often in the entire course, more than any single tool-specific
lesson.

## Quick self-check

1. When reading a Python traceback, do you start at the top or the bottom? Why?
2. What's wrong with searching your literal error text including your own variable names?
3. Give an example of a "good" search query for an error, versus a "bad" one.
4. Why should you prefer official docs over a blog post from several years ago for a fast-moving tool?
5. What should you be able to state *before* changing code to try to fix a bug?
