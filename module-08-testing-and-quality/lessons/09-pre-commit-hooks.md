# Lesson 09 — Pre-commit Hooks

**Verified against (August 2026), by actually installing and running it:**
`pre-commit` framework **4.6.1** (`https://pypi.org/pypi/pre-commit/json`);
hook repositories `pre-commit/pre-commit-hooks` **v6.0.0** and
`astral-sh/ruff-pre-commit` **v0.16.1** (matching this backend's own
pinned `ruff==0.16.1`).

## What you'll learn

- What a **Git hook** is, in general, and specifically what "pre-commit"
  means as a moment in Git's own commit process.
- What the `pre-commit` **framework** is (a specific tool with that
  name, distinct from the general concept "a hook that runs before a
  commit") and how it's configured via `.pre-commit-config.yaml`.
- How to read and understand this module's own real, working
  `.pre-commit-config.yaml` line by line — including a deliberate design
  choice (running the frontend's own already-installed tools directly,
  rather than a more commonly seen alternative) explained honestly.
- How to actually run every hook by hand, and what a real, failing hook
  run looks like versus a clean one.

## Why this matters

Lesson 08's linter/formatter, and this module's own test suites
(Lessons 02–07), are all genuinely useful — but only if someone actually
runs them. A human who forgets, is in a hurry, or simply doesn't know a
check exists will commit code that skips it, every time, eventually. A
**pre-commit hook** removes the "remembering" step entirely: the checks
run automatically, every single time anyone tries to commit, and a
failing check can block that commit until it's fixed — turning "please
remember to run the tests" from a hopeful request into an enforced,
automatic gate.

## Prerequisites

Lesson 08 (ruff, prettier) and this module's real test suites (Lessons
02–07) — this lesson wires up tools you've already used by hand, so you
should already be comfortable running each one manually before
automating it.

## The concept, explained simply

Think of a pre-commit hook the way you'd think about an automatic build
validation step some game engines run before letting you check code into
a shared repository — a step that compiles the project and runs a quick
smoke test *automatically*, refusing the check-in outright if either
fails, specifically so a broken build never even reaches a teammate's
machine in the first place. A **Git hook**, generally, is exactly this
idea applied to Git itself: a script Git runs automatically at a specific
moment in its own workflow (Module 00's Git lessons covered `commit`,
`branch`, `merge` — a hook is a script that runs *around* one of those
moments, not a Git command you type yourself). "**pre-commit**" names
the specific moment: right after you type `git commit`, but *before* Git
actually creates the commit — giving a hook script the chance to inspect
what's about to be committed and, if it decides to, refuse.

**"pre-commit" (the framework) is a separate, specific tool** — installed
via `pip` (Lesson 00), configured via a `.pre-commit-config.yaml` file —
that manages *writing* that Git hook script for you, and running a whole
list of separate, independent checks (**hooks**, in this framework's own
vocabulary — a slightly different, more specific use of the word than
"Git hook" in general) each time it fires, instead of you hand-writing
one giant, hard-to-maintain shell script yourself.

## The details

### Installing the actual Git hook

```bash
cd module-08-testing-and-quality/project/questlog
pre-commit install
```

**Expected:** `pre-commit installed at .git/hooks/pre-commit`. **Line by
line:** this writes one small script into `.git/hooks/pre-commit` — a
location Git itself checks and automatically runs, with zero further
configuration, every single time you run `git commit` from anywhere
inside this repository. That tiny script's whole job is: read
`.pre-commit-config.yaml`, and run every hook it lists.

### Reading this module's real `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.1
    hooks:
      - id: ruff-check
        name: ruff check (backend)
        args: [--fix]
        files: ^backend/
      - id: ruff-format
        name: ruff format (backend)
        files: ^backend/

  - repo: local
    hooks:
      - id: prettier
        name: prettier --check (frontend)
        entry: npm --prefix frontend run format:check
        language: system
        files: ^frontend/src/.*\.(ts|tsx)$
        pass_filenames: false
      - id: oxlint
        name: oxlint (frontend)
        entry: npm --prefix frontend run lint
        language: system
        files: ^frontend/src/.*\.(ts|tsx)$
        pass_filenames: false
      - id: pytest
        name: pytest (backend)
        entry: bash -c "cd backend && python -m pytest -q"
        language: system
        files: ^backend/
        pass_filenames: false
```

**Line by line, top to bottom:**

- **`repos:`** — a list of hook *sources*. Each `repo:` names an actual
  Git repository containing one or more hooks' definitions —
  `pre-commit` downloads (and caches) each one the first time it's used.
- **`rev: v6.0.0`** — pins an *exact* version of that hook repository,
  the same "never let an unpinned dependency silently change under you"
  discipline Module 01's `requirements.txt` and this module's own
  `requirements-dev.txt`/`package.json` versions already practice.
- **`pre-commit/pre-commit-hooks`'s four hooks** — small, generic,
  language-agnostic checks: `trailing-whitespace` and `end-of-file-fixer`
  both auto-fix genuinely trivial issues (a stray space at a line's end;
  a file not ending in exactly one newline character — POSIX convention,
  and the reason `git diff` sometimes shows a confusing "\ No newline at
  end of file" marker on files that lack it). `check-yaml` parses every
  YAML file (including this very config file) to catch a syntax error
  before it causes a confusing failure elsewhere. `check-added-large-files`
  refuses to let an accidentally-huge file (a stray database dump, a
  build artifact) get committed at all — exactly the kind of stray
  artifact this course's own `HANDOVER.md` has had to manually clean up
  more than once.
- **`astral-sh/ruff-pre-commit`'s two hooks** — `ruff-check`/`ruff-format`,
  Lesson 08's exact two tools, run automatically. `args: [--fix]` on
  `ruff-check` means it auto-fixes anything it safely can (import
  ordering, `UP017`-style modernizations) rather than only reporting.
  **Order matters** (Lesson 08's own gotcha, restated here as policy):
  `ruff-check` runs before `ruff-format`, so a lint fix that changes code
  shape gets formatted afterward, not the reverse. `files: ^backend/`
  restricts both hooks to files whose path starts with `backend/` — this
  config file lives one level *above* both `backend/` and `frontend/`,
  covering the whole `project/questlog/` folder, so this restriction
  keeps Python-specific hooks from ever being asked to lint a
  `.tsx` file.
- **The `local` hooks — a deliberate departure from a more commonly seen
  pattern, explained honestly:** many real projects wire up `prettier`
  via a repository named `pre-commit/mirrors-prettier`, which — like
  `ruff-pre-commit` above — downloads and manages its own, separate,
  isolated copy of `prettier` for `pre-commit` to run. This project uses
  `repo: local` with `language: system` instead, for one concrete reason:
  this frontend *already* has its own exact, pinned `prettier` version
  installed via `npm` (Lesson 00, `frontend/package.json`) — a second,
  separately-managed copy inside `pre-commit`'s own cache would be one
  more place a version could quietly drift out of sync with the one
  actually used everywhere else (`npm run format`, CI, a developer's own
  terminal). `language: system` tells `pre-commit` "don't manage any
  environment for this hook at all — just run this exact shell command,
  using whatever's already on `PATH`/already installed." `entry: npm
  --prefix frontend run format:check` runs this exact project's own
  `package.json` script (Lesson 00) from whatever folder `pre-commit`
  happens to invoke hooks from. `pass_filenames: false` — normally,
  `pre-commit` appends the list of changed files matching `files:` onto
  the end of `entry`'s command; this hook's own npm script (`prettier
  --check .`) already checks the whole `frontend/` folder itself, so
  those extra filename arguments would be unwanted noise, not useful
  filtering.
- **The `pytest` hook** — genuinely running this module's entire real
  backend test suite (Lessons 02–06) on every single commit that touches
  `backend/`. **A real, worth-stating-honestly trade-off:** many
  production teams deliberately *don't* run a full test suite inside a
  pre-commit hook, specifically because pre-commit hooks are meant to
  stay fast (a hook that takes over a few seconds starts tempting people
  to skip it, via `git commit --no-verify` — Module 00's Git vocabulary —
  defeating the whole point), preferring to run the full suite in CI
  (Module 11) instead, and keeping pre-commit itself limited to fast
  linting/formatting checks. This module includes it anyway, partly
  because this module's own suite is small enough to stay fast (about 15
  seconds — check for yourself: `cd backend && python -m pytest -q`) and
  partly because seeing a real, working example of "yes, you genuinely
  can wire your whole test suite into a hook" is worth more, pedagogically,
  than only describing the trade-off in words. On a much larger, slower
  real-world test suite, moving this specific hook to CI-only would be
  the right call — know that this is a choice, not a universal rule.

### Running every hook by hand, without committing anything

```bash
pre-commit run --all-files
```

**Expected, on a clean run (verified for real while writing this
lesson):**
```
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
ruff check (backend).....................................................Passed
ruff format (backend)....................................................Passed
prettier --check (frontend)..............................................Passed
oxlint (frontend)........................................................Passed
pytest (backend).........................................................Passed
```

**What a real, failing run looks like — also verified for real while
writing this lesson**, the very first time this exact config ran against
this exact codebase (before the fixes Lesson 08 already described):
```
trim trailing whitespace.................................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing backend/alembic/versions/....py

fix end of files.........................................................Failed
- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing backend/alembic/README
Fixing frontend/public/favicon.svg

ruff check (backend).....................................................Failed
- hook id: ruff-check
- files were modified by this hook

Found 12 errors (12 fixed, 0 remaining).

ruff format (backend)....................................................Failed
- hook id: ruff-format
- files were modified by this hook

2 files reformatted, 18 files left unchanged
```

**The exact right response to this, every time:** several hooks *fixed*
what they found automatically (notice "exit code: 1" and "files were
modified by this hook" together — this specific combination means "I
found something and changed it for you, I did not just complain") — the
correct next step is `git add` the now-fixed files and run `pre-commit
run --all-files` (or just `git commit` again) a second time, which should
now show every hook passing, since there's nothing left to fix.

## Common mistakes & gotchas

- **`pre-commit install` fails with "not a git repository."** Covered in
  Lesson 00 — `pre-commit install` needs a real `.git` folder to write
  its hook script into.
- **A hook "fails" the first time purely because it auto-fixed
  something, then you commit again without re-staging the fix.** The
  fixed file exists on disk, but Git only commits what's actually
  **staged** (Module 00) — always `git add` again after any hook reports
  "files were modified," before retrying the commit.
- **Bypassing a failing hook with `git commit --no-verify`, as a habit
  rather than a rare, deliberate exception.** This flag genuinely exists
  for real emergencies (a hook itself is broken and blocking an urgent
  fix) — using it routinely defeats the entire purpose of having hooks
  at all, and is exactly the failure mode Module 07's course generation
  process (this very course!) was explicitly told never to reach for
  without the user's explicit request, for the same underlying reason:
  skipping an enforced check should always be a visible, deliberate
  choice, never a silent default.
- **A hook that's slow enough that people start dreading `git commit`.**
  This lesson's own honest note about the `pytest` hook applies broadly —
  if a hook regularly takes more than a few seconds, seriously consider
  whether it belongs in a pre-commit hook at all, versus in CI (Module 11)
  only.
- **Forgetting hooks only run against files that are part of a commit
  (or, with `--all-files`, literally everything) — not "the whole
  project, always."** A normal `git commit` (without `--all-files`) only
  runs each hook's `files:` pattern against files that are actually
  staged for that specific commit — genuinely fast, because most commits
  touch only a handful of files.

## How this connects

This lesson closes the loop this whole module has been building: Lessons
02–07 gave you real, working tests; Lesson 08 gave you real linting and
formatting; this lesson makes *all of it* run automatically, every
single time, with no human required to remember any of it. This is also
this module's last new concept before the capstone (`project/BRIEF.md`)
asks you to confirm all of it — tests, linting, formatting, and this
exact `.pre-commit-config.yaml` — works together, for real, against the
whole, finished QuestLog application.

## Quick self-check

1. What is the difference between "a Git hook" (the general concept) and "pre-commit" (the specific framework this lesson installs)?
2. What does `rev: v0.16.1` in this module's `.pre-commit-config.yaml` actually pin, and why does that matter for a team of more than one person?
3. Why does this project's `.pre-commit-config.yaml` use `repo: local` with `language: system` for `prettier` and `oxlint`, instead of a dedicated mirror repository the way it does for `ruff`?
4. When a hook reports "Failed... files were modified by this hook," what two things must you do before your commit will actually succeed?
5. What is the real, honest trade-off this lesson names about including a full `pytest` run inside a pre-commit hook, and under what condition would moving it to CI-only be the better call?
