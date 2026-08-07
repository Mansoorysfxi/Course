# Lesson 04 — Debugging Techniques

## What you'll learn

- A systematic way to approach *any* bug, test failure or not — a
  refinement of Module 00's "how to read a stack trace" skill, now
  specifically applied to test failures.
- `pytest`'s own debugging flags: `-x`, `--lf`, `-k`, and `--pdb`.
- How to use Python's built-in debugger (`pdb`) via `breakpoint()` — what
  it actually is, and the handful of commands that get you 90% of the
  value.
- How to attach VS Code's graphical debugger to a failing test, so you
  can inspect variables visually instead of typing debugger commands.
- The frontend equivalent: `console.log`, the `debugger` statement, and
  browser DevTools — plus Vitest-specific tools (`screen.debug()`).
- Why `print()` debugging is not shameful, and when it's genuinely the
  right tool anyway.

## Why this matters

Writing tests (Lessons 02–03) finds bugs. It does not, by itself, tell
you *why* the code is wrong or *where* exactly to fix it — that's a
separate skill, debugging, and it's one you'll use constantly whether or
not a formal test is even involved: a confusing error in the FastAPI
`/docs` UI, a React component rendering the wrong thing, a `curl`
response that doesn't match what you expected. This lesson is placed
here, in the middle of the testing module, deliberately: once you have
real tests, they become one of your *best* debugging tools — a failing
test is a small, reproducible, isolated reproduction of a bug, which is
exactly the hardest part of debugging (reliably reproducing the problem
at all) already solved for you.

## Prerequisites

Module 00, Lesson 02 ("Reading docs and errors") — this lesson assumes
you can already read a Python traceback's basic shape (which line failed,
what exception was raised) and builds directly on that, now inside the
context of a failing test.

## The concept, explained simply

Debugging, done systematically, is the same loop every time, no matter
the language or the bug:

1. **Reproduce it reliably.** If you can't make the bug happen on
   command, you can't check whether a fix actually worked. A failing test
   is the best possible form of this — running it is the reproduction.
2. **Narrow down where, exactly, things go wrong.** Not "somewhere in
   this 200-line file" — a specific line, a specific variable's actual
   value at a specific moment.
3. **Form a hypothesis** — a specific, falsifiable guess about *why*
   ("I think `owner_id` is `None` here because the fixture didn't set it").
4. **Check the hypothesis directly** — print the variable, or pause
   execution there and inspect it — rather than guessing again.
5. **Fix, then re-run the same reproduction** to confirm the fix actually
   worked, not just that the code "looks right" now.

Everything in this lesson is a tool for step 2 and step 4 — ways to see
what's *actually* happening inside running code, instead of only reading
the code and reasoning about what *should* happen (which is exactly how
bugs go unnoticed for a long time in the first place: the code looks
correct to the person who wrote it).

## The details

### `pytest`'s own debugging flags

Given a test suite with one failing test buried among many passing ones:

- **`pytest -x`** — stop at the **first** failure instead of running
  every remaining test. Useful when one early failure is likely causing
  a cascade of unrelated-looking later failures (e.g. a broken fixture
  that every other test also depends on).
- **`pytest --lf`** ("last failed") — re-run *only* the tests that failed
  last time. After fixing one thing, this lets you check "did that fix
  work" in a fraction of the time a full re-run would take, without
  losing track of which tests you were actually chasing.
- **`pytest -k "expression"`** — run only tests whose name matches
  `expression`. `pytest -k "quest and not delete"` runs every test with
  "quest" in its name, except ones that also contain "delete" — genuinely
  useful once a suite has dozens of tests and you want exactly the
  handful relevant to what you're currently debugging.
- **`pytest -v`** — shown throughout Lessons 02–03 already; always worth
  having on while debugging, so you see exactly which named test is
  running.

Try this against this module's own real backend suite:
```bash
cd module-08-testing-and-quality/project/questlog/backend
python -m pytest -k "another_users" -v
```
**Expected output:**
```
tests/test_quests.py::test_one_user_cannot_list_another_users_quests PASSED
tests/test_quests.py::test_one_user_cannot_get_another_users_quest_by_id PASSED
tests/test_quests.py::test_one_user_cannot_update_another_users_quest PASSED
tests/test_quests.py::test_one_user_cannot_delete_another_users_quest PASSED

====================== 4 passed, 27 deselected in ~4s =======================
```
Every one of this module's four real ownership-isolation tests (Lesson 06
covers what they check) has `another_users` somewhere in its name — `-k`
matched on that substring alone, out of all 31 tests in the suite, and
`pytest` tells you exactly how many it skipped (`27 deselected`) so you
know the filter did something, not that your test file failed to load at
all.

### `breakpoint()` and `pdb`: pausing code mid-run

Python has a built-in debugger, **`pdb`** ("Python DeBugger"). The
easiest way to use it: write the word `breakpoint()` as its own line,
anywhere in your code (application code, or test code — it works
identically in both):

```python
def test_ownership_debug_example(client, signup_and_login):
    import asyncio

    async def _inner():
        headers = await signup_and_login(client, "hero@example.com", "sword-and-shield")
        breakpoint()  # <- execution pauses here
        response = await client.get("/api/quests", headers=headers)
        assert response.status_code == 200

    asyncio.get_event_loop().run_until_complete(_inner())
```

Run `pytest -s` (the `-s` flag is required — without it, `pytest`
captures/hides output in a way that breaks the interactive debugger
prompt). When execution reaches `breakpoint()`, you get an interactive
prompt, right inside your terminal:

```
(Pdb)
```

**The handful of commands that get you almost everything:**
- `headers` (type any variable name, then Enter) — prints its current
  value, exactly like Python's own REPL.
- `n` ("next") — run the current line, then pause again on the next one.
- `s` ("step") — like `n`, but if the current line calls a function, step
  *into* that function instead of running it as one opaque unit.
- `c` ("continue") — stop pausing; run normally until the next
  `breakpoint()` (if any) or the program ends.
- `l` ("list") — show the source code around your current position, so
  you're not debugging blind.
- `q` ("quit") — abort entirely.

**Remove every `breakpoint()` call before committing** — this is
important enough to repeat: a `breakpoint()` left in code that runs in
CI (Module 11) or in a colleague's environment will hang that run
forever, waiting for an interactive terminal that isn't there.
`lessons/09-pre-commit-hooks.md`'s `ruff` configuration can be extended
with a rule (`T100`) that specifically catches a forgotten `breakpoint()`
before it's committed — worth knowing exists, even though this module's
own `pyproject.toml` doesn't enable it by default.

### `pytest --pdb`: drop into the debugger automatically, exactly where a test failed

Instead of manually placing `breakpoint()`, `pytest --pdb` automatically
opens a `pdb` prompt **at the exact moment any test fails** — right where
the failing `assert` (or exception) happened, with every local variable
at that point still inspectable:

```bash
python -m pytest --pdb -k "test_that_is_currently_failing"
```

This is often the single fastest way to understand *why* a specific test
failure happened: no need to guess where to add a `breakpoint()` at all —
`pytest` drops you exactly at the point of failure automatically.

### VS Code's graphical debugger

Everything `pdb` does with typed commands, VS Code's built-in debugger
does with clicks and a visual variable inspector — genuinely nicer for
complex objects (a whole `Quest` Pydantic model, say) that are awkward to
read as one line of `pdb` text output.

1. Open the **Testing** panel (the flask icon in VS Code's left sidebar)
   — it auto-discovers `pytest` tests once `python.testing.pytestEnabled`
   is set (VS Code's Python extension typically detects this
   automatically once it sees `pytest` installed in your active venv).
2. Click in the left margin, on the exact line you want to pause at, to
   set a **breakpoint** (a small red dot appears) — the graphical
   equivalent of writing `breakpoint()` yourself, with the advantage that
   you never accidentally commit it, since it lives in VS Code's own
   state, not your source file.
3. Right-click the test in the Testing panel and choose **Debug Test**
   (instead of **Run Test**).
4. Execution pauses at your breakpoint. VS Code's **Variables** panel
   (usually bottom-left while debugging) shows every local variable's
   current value, live, updating as you step — the **Debug Console** at
   the bottom lets you type any expression and see its value, exactly
   like `pdb`'s prompt, but with autocomplete.
5. The small floating toolbar that appears gives you **Step Over**
   (`pdb`'s `n`), **Step Into** (`pdb`'s `s`), and **Continue** (`pdb`'s
   `c`) as clickable buttons.

**Try it yourself:** set a breakpoint on the `assert response.status_code
== 200` line inside `backend/tests/test_quests.py::test_create_quest`,
debug that one test, and use the Variables panel to inspect
`response.json()` before the assertion runs — confirm the actual shape
matches what the test expects, the same "check your hypothesis directly"
step this lesson's five-step loop names.

### Debugging on the frontend

The exact same five-step loop applies — only the specific tools change.

**`console.log`** — JavaScript/TypeScript's `print()` equivalent. Inside
a component, or a test:
```tsx
console.log("quest value right before render:", quest);
```
Shows up in your terminal (when running under Vitest/Node) or your
browser's DevTools Console (Module 02's term — right-click any page →
"Inspect" → the "Console" tab) when running the real app in a real
browser.

**The `debugger` statement** — JavaScript's own `breakpoint()`. Placed
anywhere in your code, it pauses execution *if and only if* browser
DevTools (or Node's own inspector) are already open and attached —
otherwise it's silently skipped, unlike Python's `breakpoint()`, which
always pauses. In a real browser: open DevTools **before** triggering the
code path that hits `debugger`, and execution will pause there, with the
same kind of variable inspector, step-over/step-into controls, and a
live console VS Code's Python debugger gives you.

**`screen.debug()`** — React Testing Library's own, test-specific tool.
Inside any Vitest test using `render(...)` (Lesson 07), calling
```tsx
screen.debug();
```
prints the *entire current state* of the fake DOM (jsdom, Lesson 00) to
your terminal, formatted and indented — invaluable when a query like
`screen.getByText("Quest Board")` fails with "unable to find element,"
because it shows you exactly what *did* render, so you can see the actual
text/structure your query should have matched instead of guessing blind.

**React DevTools** — a real browser extension (for Chrome/Firefox) that
adds "Components" and "Profiler" tabs to DevTools, letting you inspect a
running React app's actual component tree, each component's current
props and state, live — the closest frontend equivalent to VS Code's
Variables panel, but for React's own concepts specifically rather than
plain JavaScript variables. Not needed for this module's own tests
(jsdom has no real browser to install an extension into), but essential
once you're debugging the *real*, running app (`npm run dev`) rather than
a test.

### `print()` debugging is not shameful

Every technique above is more *powerful* than a well-placed `print()` —
but "powerful" isn't always "faster in this specific moment." For a
quick, one-off "what is this value, right now" check, adding
`print(f"DEBUG: quest_line={quest_line!r}")`, running the test with
`pytest -s` (needed for the same reason as the `breakpoint()` example —
`pytest` hides output by default), and deleting the line once you've
learned what you needed, is a completely legitimate, fast technique —
professional engineers use it constantly, alongside the more structured
tools above, not instead of ever learning them. The real skill is
knowing which tool fits the moment: a `print()` for a quick one-shot
check; `pytest --pdb` or a real breakpoint when you need to explore
several related variables interactively, or step through several lines
of confusing control flow one at a time.

## Common mistakes & gotchas

- **`breakpoint()` (or a VS Code test-debug session) that seems to "hang
  forever."** Usually means `-s` wasn't passed to `pytest` (output/input
  capture is still active, so the interactive prompt exists but you can't
  see or type into it), or — for async test code specifically — the
  breakpoint is inside a coroutine that never actually got awaited, so
  execution never truly reached that line at all.
- **Forgetting a `breakpoint()` or `debugger` statement and committing
  it.** Covered above — always search your diff (`git diff`, Module 00)
  for the literal words `breakpoint()` and `debugger` before committing.
- **Using `print()` inside application code (not test code) and
  forgetting to remove it before a real deploy.** A stray `print()`
  inside `app/repository.py`, say, will still run in production, slowing
  things down and cluttering real logs — Module 07's own
  `lessons/11-secrets-config-and-logging.md` covers Python's `logging`
  module as the correct, permanent alternative for anything that should
  stay in the code long-term; `print()`/`console.log`/`breakpoint()` are
  all meant to be temporary, deleted once the immediate question is
  answered.
- **Debugging by only reading the code, over and over, without ever
  actually running anything to check a specific value.** This is the
  single most time-wasting anti-pattern in debugging — if you've reread
  the same ten lines three times without a new idea, stop reading and
  start printing/breakpointing an actual value instead.

## How this connects

This lesson's five-step loop and tools apply to *everything* from here
on — Lessons 05–06's FastAPI/database tests, Lesson 07's frontend tests,
and every exercise in this module, all the way through the rest of the
course. Debugging is not a "testing topic" specifically; it's placed here
because a module about tests is the natural place to also formalize a
skill you've already been doing informally, ad hoc, since Module 00.

## Quick self-check

1. What are the five steps of this lesson's debugging loop, in order, and which step does a failing test satisfy automatically, compared to a bug found by manually clicking through the app?
2. What does `pytest --lf` do, and when is it faster than a normal `pytest -v` run?
3. What is the one flag you must pass to `pytest` for `breakpoint()` (or a debug `print()`) to actually show its output/prompt, and why does `pytest` hide it by default otherwise?
4. What is the difference between Python's `breakpoint()` and JavaScript's `debugger` statement, specifically regarding whether they pause execution unconditionally?
5. Name one situation where a quick `print()` is genuinely the right tool, and one situation where `pytest --pdb` or VS Code's graphical debugger would serve you better. What makes the difference?
