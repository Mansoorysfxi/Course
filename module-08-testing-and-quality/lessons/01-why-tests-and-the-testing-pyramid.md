# Lesson 01 — Why Tests Exist, and the Testing Pyramid

## What you'll learn

- What an **automated test** actually is, precisely, and how it differs
  from "I ran the app and clicked around."
- Why professional software teams write tests at all — the real problems
  this solves, not just "best practice" as an unexamined slogan.
- The **testing pyramid**: the three broad categories of automated test
  (**unit**, **integration**, **end-to-end**), what each one actually
  checks, how fast/slow and how reliable each tends to be, and roughly
  how many of each a healthy project has.
- Where QuestLog's own upcoming tests (Lessons 02–07) will land on that
  pyramid, and why.

## Why this matters

You already know, from every module so far, the feeling of "did I just
break something?" after changing a file. Through Module 07, the honest
answer has always been: run the app, click through it by hand, and hope
you remembered every place that could have broken. Module 07's own
`README.md` even says this outright — every route was "exercised with
`curl` and FastAPI's `/docs`... while building this module," a real, but
entirely manual, verification process that has to be redone, by a human,
every single time.

That does not scale, and it gets worse — not better — the longer a
project lives. A change to `app/repository.py`'s `get_quest` function
(Module 07) could silently break quest ownership isolation, and a human
re-clicking through the app might never think to try logging in as a
*second* account and checking whether it can see the first account's
quests, because that scenario simply doesn't occur to them today. A test
that already does exactly that, written once, checks it forever, in
milliseconds, every single time, without ever forgetting.

## Prerequisites

Modules 01 (Python functions, `assert`), 05 (FastAPI routes), 06
(databases), and 07 (auth, ownership) — this lesson uses QuestLog's real
signup/login/quest code as its running examples throughout, so you should
already understand what that code does, even though you haven't tested
it yet.

## The concept, explained simply

**An automated test is a small program that runs another piece of your
program, and checks — with code, not with your eyes — whether the result
was correct.** That's the entire definition. Nothing about "testing" is
more mysterious than that.

Compare this to something you already know from game development: an
Unreal Engine **automation test** (or, in a from-scratch engine, a
regression test you'd write to check that `TakeDamage(50)` really does
reduce an Actor's health by exactly 50, not 49 or 51). You don't run the
whole game and watch the health bar with your own eyes every time you
touch the damage code — you write a small function that spawns an Actor,
calls `TakeDamage(50)`, and asserts `Health == InitialHealth - 50`. Run
that function a thousand times a day, in a fraction of a second each
time, and you'd never notice the cost. That's a **unit test** — a test of
one small piece, in isolation, checked automatically.

Now compare it to something bigger: playtesting a full level from the
main menu through to the level's completion screen, confirming every
system (save data, quest triggers, UI) worked together correctly. A human
playtester does this by hand, and it's slow — but a testing tool that
launches the actual game and drives it through the same steps
automatically is an **end-to-end test**. It's slower and more fragile
(a UI layout change can break it even though the actual game logic is
fine) than the health-bar unit test, but it catches a different category
of bug: the ones that only show up when real systems interact.

Everything in this lesson is really just naming and organizing the space
*between* those two extremes.

## The details

### What, precisely, makes a test "automated"

Three properties, all required:

1. **It runs code, not a human.** No person reads a checklist and clicks
   buttons — a program calls a function, or sends a request, or renders
   a component.
2. **It checks the result with code.** An `assert` statement (Python), or
   `expect(...).toBe(...)` (JavaScript/Vitest) — a line of code that
   raises an error if the actual result doesn't match the expected one.
   No human looks at the screen and judges "does that look right."
3. **It reports pass or fail, unambiguously, every time, without a
   human's judgment involved.** Running the same test twice against the
   same code produces the same result twice — this property has a name,
   **deterministic**, and it matters enough that Lesson 03 spends real
   time on the ways `async`/randomness/the current date/time can quietly
   break it.

A `curl` command you type by hand and read the JSON reply from — like
every prior module's own "Verify your setup" sections have you do — is
**not** an automated test by this definition, even though it's genuinely
useful. It fails property 1 (a human ran it) and, usually, property 2 (a
human read the output and judged it, rather than code comparing it to an
expected value).

### The three real problems tests solve

**1. Regression prevention.** A **regression** is a bug where something
that used to work stops working, because of a change made somewhere else,
often in code the person making the change didn't even think was related.
Module 07's `app/repository.py`'s `get_quest` combines an id check *and*
an owner check in one `WHERE` clause specifically to prevent one category
of bug (IDOR — Module 07, Lesson 07) — a test that creates two users and
asserts the second one gets a `404` on the first one's quest catches, and
keeps catching, any future change (even by a completely different
person, working on a completely different feature) that accidentally
loosens that check.

**2. Confidence to change code at all.** Software that's never touched
again doesn't need tests. Software that's actively developed — which is
every real, useful piece of software — needs to change: new features,
bug fixes, refactors (Module 01's term for restructuring code without
changing its behavior). A large, thorough test suite is what makes a
refactor *safe*: change the internals, run the tests, and if they all
still pass, you have real, checked evidence — not a hope — that the
externally visible behavior didn't change either.

**3. Specification, in an executable, unambiguous form.** A test that
says "logging in with the wrong password returns `401`, not `200`" is a
*requirement*, written in a form a computer can check, forever. Compare
this to a requirement written only in a design document or a comment: a
document can go stale (nobody updates it when the code changes); a test
that goes stale **fails**, loudly, the moment the code stops matching it.

### The testing pyramid

```
        /\
       /  \        End-to-end (E2E) tests
      /----\       fewest, slowest, most realistic
     /      \
    /--------\     Integration tests
   /          \    more of these, medium speed
  /------------\
 /              \  Unit tests
/________________\ most of these, fastest, most isolated
```

This is a **shape**, not a strict rule enforced by any tool — it's a
description of what a *healthy* test suite tends to look like, based on
decades of real teams' experience with the trade-off each layer makes.

**Unit tests** — test one small, isolated piece of code (often a single
function or class) with nothing real around it. In this module,
`tests/test_security.py`'s tests of `hash_password`/`verify_password`/
`create_access_token` are unit tests: no HTTP request, no database, no
FastAPI app — just plain Python functions, called directly, checked
directly.
- *Fast*: milliseconds each; a whole suite of hundreds can run in seconds.
- *Isolated*: a failure points at almost exactly one function.
- *Cheap to write, cheap to run constantly* — so you write the *most* of
  these.
- *Weakness*: proves the pieces work individually, says nothing about
  whether they work correctly *together*.

**Integration tests** — test several real pieces working together. This
module's `tests/test_auth.py` and `tests/test_quests.py` are integration
tests: a real HTTP request goes through FastAPI's real routing, a real
`Depends` dependency chain (Module 05/07), and a real (if temporary)
database, all genuinely integrated, not each mocked out individually.
- *Slower than unit tests* (a database round-trip, even an in-memory one,
  costs more than calling a plain function) but still fast enough to run
  constantly — this module's entire 31-test backend suite runs in about
  15 seconds.
- *Catches a category of bug unit tests structurally cannot*: two pieces
  that each work fine alone but disagree about the shape of data passed
  between them, for instance.
- You write *fewer* of these than unit tests — not because they're less
  valuable, but because each one naturally exercises more code at once,
  so you need fewer to reach the same coverage.

**End-to-end (E2E) tests** — drive the *entire*, real, running system,
usually through the same interface a real user uses: a real browser,
clicking real buttons, against a real (if test-specific) backend and
database, start to finish. QuestLog doesn't have any E2E tests in this
module (see this lesson's "How this connects" section for exactly why,
honestly) — a real E2E test for QuestLog would launch a real browser
(via a tool like Playwright — not covered in this module, mentioned here
only so the term isn't a total mystery later), navigate to the login
page, type a real password, click real buttons, and confirm a new quest
genuinely appears on screen.
- *Slowest*: seconds per test, not milliseconds — a real browser has to
  actually start, actually render, actually wait for real (if fast)
  network round-trips.
- *Most realistic*: closest to "a real person actually did this and it
  worked," because almost nothing is faked.
- *Most fragile*: a purely cosmetic change (moving a button, renaming a
  CSS class a test happened to search for) can break an E2E test with
  zero change to the app's actual correctness — this fragility is *why*
  the pyramid has the fewest of these at the top, not because they're
  less valuable per test, but because each one costs more to write and
  more to keep passing through unrelated changes.

### Where this module's own tests land, and why

| File | Pyramid layer | What makes it that layer |
|---|---|---|
| `backend/tests/test_security.py` | Unit | Calls plain Python functions (`hash_password`, `create_access_token`) directly — no HTTP, no database. |
| `backend/tests/test_auth.py`, `test_quests.py` | Integration | Real HTTP requests, through the real FastAPI app, into a real (temporary) database — several real layers, genuinely combined. |
| `frontend/src/components/QuestForm.test.tsx`, `ProtectedRoute.test.tsx`, `QuestCard.test.tsx` | Unit (mostly) | Each renders exactly one component in isolation — QuestForm.test.tsx never touches a real backend at all. |
| `frontend/src/pages/QuestListPage.test.tsx` | Unit/small integration | Renders one page, but the page itself combines several smaller pieces (filtering, sorting, three rendering states) — see `lessons/07-frontend-testing-with-vitest-and-rtl.md`'s note on this file's deliberate use of a **mock** (Lesson 03 defines this term from scratch) to keep it a unit test despite testing a whole page. |

Notice there is no strict, universal line between "unit" and
"integration" — reasonable engineers draw it slightly differently. What
matters is the *shape*: mostly fast, isolated tests; a meaningful but
smaller number of tests that check real pieces working together; and
(not present in this module, but real in a production system) a small
number of full, realistic, slow end-to-end checks.

## Common mistakes & gotchas

- **"We don't have time to write tests."** This inverts the real
  trade-off: tests cost time up front and save (usually much more) time
  later, every time they catch a regression before a user does. The
  honest cost/benefit question is never "tests vs. no tests," it's
  "spend an hour now, or spend an unknown amount of time later debugging
  a bug in production, plus the cost of that bug actually happening to a
  real user first."
- **Treating "100% code coverage" (Lesson 02's term — every line of code
  ran at least once during the test suite) as the goal.** Coverage
  measures whether a line *ran*, not whether its result was *checked*
  correctly. A test that calls a function and asserts nothing about the
  result gives that function 100% coverage while checking literally
  nothing. Coverage is a useful tool for finding code with *zero* tests;
  it is a bad tool for judging whether existing tests are actually good.
- **Writing only end-to-end tests because "that's what real users do."**
  This inverts the pyramid — a project with mostly E2E tests is typically
  slow to run (minutes, not seconds) and brittle (a small, unrelated
  change breaks several tests at once), which in practice makes teams
  start skipping test runs entirely, defeating the entire point.
- **Confusing "a test failed" with "the code is definitely wrong."** A
  test can itself be wrong — testing the wrong expected value, or
  depending on something non-deterministic (the current time, a
  particular ordering, real network access). Lesson 02's fixtures and
  Lesson 03's mocking exist specifically to make tests deterministic and
  independent of things outside your control.

## How this connects

Everything from Lesson 02 onward is this lesson's pyramid made concrete
in actual, running code: Lessons 02–03 build up pytest fundamentals
(fixtures, parametrize, mocking) mostly through unit-test examples;
Lessons 05–06 write real integration tests against QuestLog's own FastAPI
app and database; Lesson 07 does the same for the frontend. This module
deliberately does **not** cover end-to-end testing with a real browser
(tools like Playwright or Cypress) — that's a genuinely separate skill
with its own setup, and Rule 1 of this course means introducing it
properly, not as a rushed afterthought, would need its own dedicated
lesson this module's curriculum doesn't call for. What you now know is
enough to recognize the term and the trade-off when you meet it later in
your career.

## Quick self-check

1. What are the three properties that make a test "automated," and which of them does typing a `curl` command by hand and reading the output fail?
2. In your own words, what is a "regression," and why is a test suite specifically good at preventing them compared to manual testing?
3. Draw (or describe) the testing pyramid's three layers, and give one real trade-off (speed vs. realism, or similar) between the bottom and top layers.
4. Why is `tests/test_security.py` a unit test while `tests/test_auth.py` is an integration test, given both are in the same `backend/tests/` folder and both use `pytest`?
5. Why is "100% code coverage" a bad primary goal for a test suite, even though coverage itself is a useful measurement?
