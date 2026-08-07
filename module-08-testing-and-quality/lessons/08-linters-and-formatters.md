# Lesson 08 — Linters and Formatters

**Verified against (August 2026):** `ruff` **0.16.1**
(`https://pypi.org/pypi/ruff/json`), `prettier` **3.9.6**
(`https://www.npmjs.com/package/prettier`) — both confirmed by actually
installing them and reading back the resolved version (Lesson 00).

## What you'll learn

- What a **linter** is and what a **formatter** is, precisely, and why
  they're two genuinely different tools even though people often mention
  them together.
- Why this course uses `ruff` for Python (and *not* older, still-common
  tools like `flake8`/`black`/`isort` separately) and `prettier` for
  JS/TS.
- How to configure `ruff`'s rule set deliberately and narrowly, instead
  of turning on everything.
- How to actually run both tools against this module's real capstone
  code, and read what each one reports.
- The real, specific bugs and style issues `ruff` found in Module 07's
  own, previously "finished" backend code the first time it was ever
  run against it — a genuine, honest example, not a hypothetical.

## Why this matters

Every module through Module 07 wrote real, working code with no
automated style or correctness checking beyond "does it run, and does it
produce the right answer" (which tests, Lessons 02–07, now check). A
linter catches a different, complementary category of problem: code
that *runs fine* but is subtly wrong in a way that hasn't caused a
failure *yet* (an unused import silently shadowing a real bug, a
bare `except:` swallowing an error that should have been visible), or
code that's simply inconsistent in style across a growing team/codebase,
making every file slightly harder to read than it needs to be. A
formatter solves a narrower, more mundane problem: ending arguments about
whether a line should have one space or two after a comma, forever, by
having a tool decide, consistently, so no human ever has to.

## Prerequisites

Lesson 00 (both tools installed and verified) — this lesson explains what
they actually do and why; Lesson 00 already covered how to install them.

## The concept, explained simply

Think of the difference between a linter and a formatter the way you'd
think about the difference between **code review comments about actual
bugs or bad patterns** versus **auto-formatting a source file's
whitespace/braces to match a team's style guide**. A senior engineer
reviewing your pull request might say "this variable is never used,
delete it" (a linter's job) or "you're catching every exception here with
no specific type, which will hide real bugs" (also a linter's job) — both
are judgments about whether the code is *correct or well-structured*.
That same reviewer would almost never comment "please add a space after
this comma" — that's exactly the kind of purely cosmetic, zero-judgment
change a formatter handles automatically, instantly, so no human's
attention is ever spent on it at all.

**A linter reads your code and looks for problems** — real bugs,
suspicious patterns, deprecated syntax, style inconsistencies — and
reports them (optionally fixing some automatically). **A formatter
rewrites your code's whitespace, quote style, line breaks, and similar
purely cosmetic details** into one consistent shape, with zero opinion
about whether the code's actual *logic* is correct.

## The details

### `ruff`: one tool, two jobs

Historically, a Python project needing this module's exact capability
set (linting + import sorting + formatting) would install three or four
separate tools: `flake8` (linting), `isort` (import sorting), `black`
(formatting), and often `pyupgrade` (flagging old syntax with a newer
equivalent) — each with its own config, its own separate command, and
its own speed (all four together, on a large codebase, noticeably slower
than what's coming next). **`ruff`**, written in Rust rather than Python,
replaces all four with one single, extremely fast tool and one
configuration section — confirmed via Astral's (ruff's maintainer) own
current documentation as the reasoning behind the project's design.

**Two separate subcommands, two separate jobs, deliberately not merged
into one:**
```bash
ruff check .        # the LINTER -- finds problems, some auto-fixable
ruff format .       # the FORMATTER -- rewrites style, no judgment calls
```

Run both, right now, against this module's real backend:
```bash
cd module-08-testing-and-quality/project/questlog/backend
ruff check app tests
ruff format --check app tests
```
**Expected:** `All checks passed!` and `N files already formatted` — this
module's own capstone code is already clean, because (see this lesson's
final section) it was made clean, deliberately, as part of writing this
module.

### Choosing a rule set deliberately, not `ALL`

`ruff` supports hundreds of individual rules, grouped into named
categories (`E`/`F` for the classic `pycodestyle`/`Pyflakes` checks,
`I` for import sorting, `UP` for "this syntax is outdated, here's the
modern equivalent," `B` for `flake8-bugbear`'s catalog of common real
bugs, and many more). `ruff` even supports one special code, `ALL`, that
enables literally every rule it has. **This module's own
`backend/pyproject.toml` deliberately does not use `ALL`** — Astral's own
documentation explicitly recommends against it for exactly the reason
this course cares about: `ALL` silently enables *new* rules automatically
every time you upgrade `ruff` to a newer version, which can suddenly
introduce a wave of new warnings you never opted into, unrelated to
whatever you were actually working on that day.

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

**Line by line:** `select = [...]`, not `extend-select` (ruff's docs'
own recommended distinction) — an explicit, complete list of exactly
which categories are on, easy to read at a glance, with new `ruff`
versions never silently adding more without you choosing to. `E`/`F` —
the long-standing `pycodestyle`/`Pyflakes` basics (unused imports, unused
variables, obviously malformed code). `I` — import sorting/grouping
(standard library, then third-party, then your own project's imports,
each group alphabetized) — this is *why* `ruff check --fix` reordered
several of this module's own imports (see below). `UP` — "pyupgrade"
style modernization (e.g. `Union[str, None]` → `str | None`, a real,
current Python syntax improvement this rule flags automatically). `B` —
`flake8-bugbear`'s specific catalog of patterns that are *usually* real
bugs, not just style (e.g. `B904`, covered directly below).

### `ruff format`: opinionated, and deliberately non-configurable in most ways

```toml
[tool.ruff.format]
quote_style = "double"
```

`ruff format` is intentionally a much smaller surface of choice than
`ruff check` — by design, closely compatible with `black`'s own output
shape (the formatter it was built to be a faster drop-in replacement
for), specifically so teams already using `black` could switch with
almost no actual code changes. `quote_style = "double"` is one of the
few genuine choices left: always use `"double quotes"`, never `'single
quotes'`, for consistency — matching this project's own frontend
`prettier` convention (below), so switching between backend and frontend
code never requires a mental style-switch.

### `prettier`: JavaScript/TypeScript's formatter

```bash
cd ../frontend
npx prettier --check .     # report only, changes nothing
npx prettier --write .     # actually rewrite files
```

This project's `.prettierrc.json`:
```json
{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```
**Line by line:** `semi: true` — always end a statement with a semicolon
(JavaScript technically allows omitting them in most cases via
"automatic semicolon insertion," a genuinely confusing, edge-case-prone
feature Module 03 didn't cover in depth — always writing them explicitly
sidesteps the whole issue). `singleQuote: false` — double quotes, the
same choice this module's `ruff format` config makes for Python, for the
same "one consistent convention across the whole stack" reason.
`trailingComma: "all"` — add a trailing comma after the *last* item in a
multi-line list/object/function-call argument list, which keeps future
diffs smaller (adding a new last item becomes a one-line diff, not a
two-line diff that also touches the previously-last item to add a
comma to it). `printWidth: 100`/`tabWidth: 2` — matches this project's
existing line-length convention (also `100`, on the Python side's `ruff`
config) and this project's existing 2-space indentation (Module 04's
own convention throughout).

**Notice `prettier` has no linting rules at all, and can't catch a bug**
— this project keeps `oxlint` (Module 04's own linter, already installed)
as the *linting* half of the frontend's tooling; `prettier` only ever
formats. This is the frontend mirroring the backend's linter/formatter
split exactly, just with two separate tools instead of `ruff`'s one tool
doing both jobs.

### A real, honest example: what `ruff` found in Module 07's own code

While writing this module, running `ruff check` against Module 07's
copied-forward backend for the very first time — code that had already
been through several rounds of careful, human writing across Modules
05–07 — found several genuine, if minor, issues, none of which any prior
module's manual `curl` testing could ever have caught, because none of
them changed the app's actual runtime behavior in a way manual testing
would notice:

- **Unsorted imports** in `app/main.py`, `app/routers/auth.py`, and
  `app/routers/quests.py` — each file had `from app import repository`
  positioned before other `from app...` imports alphabetically, purely
  a style inconsistency, auto-fixed instantly by `ruff check --fix`.
- **`UP017`** in `app/db_models.py` and `app/security.py` — both used
  `datetime.now(timezone.utc)`; `ruff` correctly flagged that modern
  Python (3.11+) added a `datetime.UTC` constant specifically to make
  this shorter and slightly clearer — `datetime.now(UTC)` — a genuine,
  small modernization, also auto-fixed.
- **`B904`** in `app/dependencies.py`'s `get_current_user` — the real,
  most substantive finding: an `except InvalidTokenError:` block that
  re-raised a *different* exception (`credentials_exception`) with no
  `from` clause at all, silently discarding Python's own exception-chain
  information about *why* the original error happened — genuinely useful
  for anyone reading a server log later trying to debug an unrelated
  problem, and a one-word fix (`raise credentials_exception from exc`).
- **Three `E501` (line too long)** in `app/repository.py`'s seed data —
  purely cosmetic, fixed by wrapping three long description strings
  across multiple lines.

None of these were "the app is broken" — every one of Module 07's real
tests (this module's own `backend/tests/`) already passed before any of
these fixes, and continued to pass identically afterward. That is
precisely a linter's actual value: catching real, if small, issues that
correctness testing alone has no reason to ever notice.

## Common mistakes & gotchas

- **Running `ruff format` before `ruff check --fix`, then being confused
  when `check` finds more to fix afterward.** Order matters, and this
  module's own `.pre-commit-config.yaml` (Lesson 09) deliberately runs
  `ruff-check` *before* `ruff-format` for exactly this reason: a lint fix
  (like reordering imports) can itself need re-formatting afterward; the
  reverse order risks the formatter "finishing" a file the linter is
  about to change again.
- **Treating a linter warning as something to silence rather than
  understand.** `ruff` (and most linters) let you disable a specific rule
  for one line with a comment (`# noqa: B904` for `ruff`) — genuinely
  useful for a rare, deliberate exception, but reaching for it as a
  first response to every warning defeats the entire point; understand
  *why* a rule exists before deciding it doesn't apply to your specific
  case.
- **Assuming `prettier`/`ruff format` changing a file means something is
  "wrong" with your code.** A formatter reformatting a file you just
  wrote is completely normal and expected the first time you run it
  against code written before the formatter was configured — it's not a
  verdict on your code's correctness, only its whitespace.
- **Not running the formatter/linter until right before a commit, and
  being surprised by a large, unfamiliar-looking diff.** Running
  `ruff format`/`npx prettier --write` frequently, right after writing
  new code, keeps each individual formatting change small and
  unsurprising — Lesson 09's pre-commit hooks make this automatic, so
  this specific gotcha mostly disappears once that's wired up.

## How this connects

This lesson's two tools are exactly what Lesson 09's `pre-commit`
configuration automates — instead of remembering to run `ruff check`/
`ruff format`/`prettier --check` by hand before every commit, Lesson 09
wires all three (plus this module's actual test suites) to run
automatically, every time.

## Quick self-check

1. What is the difference between a linter and a formatter, in one sentence each, and which of `ruff check`/`ruff format` is which?
2. Why does this course's `pyproject.toml` explicitly list `select = ["E", "F", "I", "UP", "B"]` instead of using ruff's `ALL`?
3. What real, specific bug (not just a style issue) did `ruff` find in Module 07's `app/dependencies.py`, and why does it matter for someone debugging a production issue later?
4. Why does this project's `.prettierrc.json` use the exact same `printWidth` (100) as the backend's `ruff` configuration?
5. Why does `prettier` have no linting rules at all, and what tool does this project rely on instead for catching real JS/TS problems?
