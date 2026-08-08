# Lesson 02 — GitHub Actions From Zero

**Verified against (August 2026), via GitHub's own Marketplace/release
pages and documentation:** `actions/checkout@v7`,
`actions/setup-python@v6`, `actions/setup-node@v6` all confirmed current
major versions. Node.js 24 became GitHub Actions' own default runtime for
JavaScript-based actions on June 2, 2026 (Node 20 support for actions
ends September 16, 2026) — irrelevant to the *app* versions this course
runs (this course already uses Node 24 for QuestLog itself, per Module
10), but relevant to which `actions/*` action versions are current, since
older major versions of these actions targeted the older runtime.

## What you'll learn

- What GitHub Actions actually is, and the exact vocabulary it uses:
  workflow, job, step, runner, action.
- Every major piece of workflow YAML syntax this course uses: `on:`,
  `jobs:`, `runs-on:`, `steps:`, `uses:` vs. `run:`, `with:`, `env:`,
  `needs:`, `if:`, `permissions:`, and secrets.
- How to write, push, and watch a real workflow run for the very first
  time.
- How caching in CI works, and why it matters.

## Why this matters

Lesson 01 established *why* automation matters. This lesson is the exact
syntax that turns "I want this to happen automatically" into something
GitHub will actually run. Every later lesson in this module builds
directly on the syntax here — Lesson 03 uses it to run QuestLog's real
tests; Lesson 08's capstone workflow is built entirely from these same
pieces, just more of them.

## Prerequisites

- **Lesson 01** — the *why*, established first.
- **Lesson 00-setup.md** — a GitHub account, and (if you want to run
  anything for real right now) a real, empty GitHub repository to push
  to.
- Basic YAML familiarity is helpful but not assumed — this lesson
  explains YAML's own rules (indentation-based nesting, lists, key-value
  pairs) as they come up.

## The concept, explained simply

**GitHub Actions** is GitHub's own built-in build-farm-as-a-service —
exactly Lesson 01's automated build farm analogy, except you don't have
to buy, rack, or maintain any of the actual machines. You write one text
file describing what should happen and when; GitHub provides a fresh,
disposable virtual machine (called a **runner**) every single time that
"when" condition is met, runs exactly what you described on it, and then
throws that machine away. A **workflow** is one such text file (one
overall automated process, like "test and deploy this app"). A workflow
is made of one or more **jobs** (each job gets its OWN fresh runner,
which is why two jobs can't casually share files unless you explicitly
tell them to). Each job is made of an ordered list of **steps**, run one
after another, on that same runner. A step is either a **action** — a
pre-built, reusable piece of automation someone else already wrote and
published (`uses:`) — or a **raw shell command** you write yourself
(`run:`).

## The details

### Where a workflow file lives, and the absolute minimum that runs

Every workflow file lives at `.github/workflows/<any-name>.yml`, at the
root of a repository. GitHub scans that exact folder automatically —
nothing else registers a file as a workflow.

Create this exact file (assuming you're treating some folder as its own
repo root, per Lesson 00-setup.md's own explanation):

**File: `.github/workflows/hello.yml`**
```yaml
name: Hello CI

on:
  push:
    branches: [main]

jobs:
  say-hello:
    runs-on: ubuntu-latest
    steps:
      - name: Print a greeting
        run: echo "Hello from a GitHub Actions runner!"
```

Line by line:
- `name: Hello CI` — the workflow's own display name, shown in GitHub's
  **Actions** tab. Purely cosmetic; has zero effect on what actually runs.
- `on:` — the **trigger** section: what event(s) cause this workflow to
  run at all. `push: branches: [main]` means "run this every time a
  commit is pushed to the `main` branch specifically" — a push to any
  other branch would NOT trigger this workflow, because only `main` is
  listed.
- `jobs:` — every workflow has at least one job. `say-hello` here is just
  this job's own internal ID (used later if another job needs to
  reference it via `needs:` — see below); it can be almost any short
  string.
- `runs-on: ubuntu-latest` — which kind of runner GitHub should give this
  job: a fresh Ubuntu Linux virtual machine, the current latest version
  GitHub maintains (`windows-latest` and `macos-latest` also exist; this
  course uses `ubuntu-latest` throughout — Linux runners are faster to
  start and free-tier-cheaper for a public repo, and this course's own
  Dockerfiles already target Linux anyway).
- `steps:` — a YAML **list** (each entry starts with `- `) run in order,
  top to bottom, on that one runner.
- `- name: Print a greeting` — a human-readable label for this one step,
  shown in the run's own log output. Optional, but real projects always
  include it — an unlabeled step just shows its raw command instead,
  which gets unreadable fast in a workflow with many steps.
- `run: echo "..."` — a literal shell command, run exactly as if you'd
  typed it into a terminal on that fresh Ubuntu machine.

Push this file to a real repo (Lesson 00-setup.md's Step 1), open that
repo's **Actions** tab in a browser. **Expected:** within a few seconds,
a new run named "Hello CI" appears, its status icon turns from a spinning
yellow dot to a green checkmark, and clicking into it, then into the
`say-hello` job, then expanding the "Print a greeting" step, shows:
```
Hello from a GitHub Actions runner!
```

**Try it yourself:** change the `echo` message and push again. **Predict,
before pushing,** exactly how many seconds you'll wait before the new run
appears in the Actions tab, then time it for real.

### Every job starts from nothing — `actions/checkout`

The runner GitHub hands you is **completely empty** — it does not
already have your repository's code on it, even though the workflow that
triggered it lives inside that repository. This surprises almost
everyone the first time. `actions/checkout` is the official action that
fixes this — it's the very first step in almost every real job that
exists:

```yaml
steps:
  - name: Check out the repo
    uses: actions/checkout@v7
```

`uses:` (instead of `run:`) means "run this pre-built action" rather
than a raw shell command. `actions/checkout@v7` names the action
(`actions/checkout`, an action GitHub itself publishes and maintains) and
pins an exact version (`@v7`, the current major version as of this
lesson's own header). **Always pin a version** — `@v7`, never just
`actions/checkout` with no version at all — for the exact same reason
Module 05 onward pinned exact package versions in `requirements.txt`:
reproducibility. An action's maintainer could publish a breaking `v8`
tomorrow; pinning `@v7` means your workflow keeps working exactly as
written until you deliberately choose to upgrade.

### Setting up a language runtime: `actions/setup-python` / `actions/setup-node`

A fresh Ubuntu runner has *some* tools preinstalled, but rarely the exact
version your project needs. `actions/setup-python` and
`actions/setup-node` install a specific, chosen version:

```yaml
steps:
  - uses: actions/checkout@v7
  - uses: actions/setup-python@v6
    with:
      python-version: "3.14"
```
`with:` passes named inputs to an action — every action documents its
own accepted `with:` keys (this is the action's own equivalent of a
function's named parameters). `python-version: "3.14"` here matches
QuestLog's own backend Python version exactly (Module 10's
`backend/Dockerfile`) — **always match your CI's runtime version to your
actual app's version**; a mismatch is a real, common source of "works in
CI, breaks in production" (or the reverse) bugs.

### Running real commands: `working-directory`

QuestLog's backend and frontend each live in their own subfolder
(`backend/`, `frontend/`). A step's `working-directory:` changes which
folder a `run:` command executes from, without needing `cd` inside the
command itself:
```yaml
steps:
  - uses: actions/checkout@v7
  - uses: actions/setup-python@v6
    with:
      python-version: "3.14"
  - name: Install dependencies
    working-directory: backend
    run: pip install -r requirements.txt
```

### Environment variables and secrets

A step (or a whole job) can set environment variables a `run:` command
sees, exactly like a normal shell:
```yaml
  - name: Run pytest
    working-directory: backend
    env:
      SECRET_KEY: ci-test-secret-key-do-not-use-in-production
    run: python -m pytest -v
```
For a value that's genuinely secret (a real Sentry DSN, a real deploy
hook URL — never something you'd want visible in a public log or a
fork's pull request), GitHub Actions has **secrets**: values you enter
once, in a repo's own **Settings → Secrets and variables → Actions**
page, that a workflow can read but a workflow's own *log output* will
always show as `***` even if a `run:` command accidentally tries to
print one directly:
```yaml
  - name: Trigger a deploy
    run: curl "${{ secrets.RENDER_BACKEND_DEPLOY_HOOK }}"
```
`${{ ... }}` is GitHub Actions' own **expression syntax** — anything
inside those double-curly-braces gets evaluated and substituted before
the step actually runs. `secrets.RENDER_BACKEND_DEPLOY_HOOK` reads a
secret named exactly `RENDER_BACKEND_DEPLOY_HOOK` from that repo's own
Settings page. A secret referenced but never actually set simply
resolves to an empty string — GitHub Actions doesn't error at parse time
for a missing secret, only (usually) when whatever command tries to use
that now-empty value fails on its own.

**One secret always exists automatically, in every workflow, with no
setup at all:** `secrets.GITHUB_TOKEN` — a short-lived credential GitHub
itself generates fresh for every single run and revokes the moment that
run ends, scoped (via the `permissions:` key, next section) to exactly
that one repository. Lesson 03/Lesson 08 use this to push Docker images
to GitHub's own Container Registry with no separate account or password
needed at all.

### `permissions:` — least privilege, explicitly

```yaml
jobs:
  build:
    permissions:
      contents: read
      packages: write
```
By default, `GITHUB_TOKEN`'s exact permissions depend on a repository's
own (or organization's own) settings — sometimes broad, sometimes
already fairly locked down. Writing `permissions:` explicitly, naming
exactly what a job needs (here: read the repo's own code, write to this
repo's own package registry) and nothing more, is current best practice
regardless of a repo's default — the same "least privilege" principle
Module 07's auth lesson already taught for API access, applied here to a
CI job's own credentials.

### Jobs run in parallel unless you say otherwise — `needs:`

```yaml
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps: [...]

  frontend-tests:
    runs-on: ubuntu-latest
    steps: [...]

  build-images:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    steps: [...]
```
With no `needs:` at all, `backend-tests` and `frontend-tests` start at
the same time, on two separate runners, and run independently — faster
overall than running everything in one long sequential list. `needs:
[backend-tests, frontend-tests]` on `build-images` means: wait until
BOTH named jobs finish successfully before starting this one at all. If
either named job fails, `build-images` is **skipped entirely** by
default — exactly the mechanism that makes "tests run → image builds"
a real, enforced order, not just a suggestion.

### `if:` — conditionally running a job or step

```yaml
  build-images:
    needs: [backend-tests, frontend-tests]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```
`github.event_name` and `github.ref` are two of many built-in **context**
values GitHub Actions exposes automatically (no secret or setup needed) —
respectively, which kind of event triggered this run (`push`,
`pull_request`, etc.) and which exact branch/ref triggered it. This
specific condition means "only actually build and push images for a real
push to `main` — never for a pull request," which is exactly the
behavior Lesson 01 described: a pull request should run tests (to
provide feedback before merging) but never build/deploy anything on its
own.

### Caching — why your second run is faster than your first

```yaml
  - uses: actions/setup-python@v6
    with:
      python-version: "3.14"
      cache: "pip"
      cache-dependency-path: backend/requirements.txt
```
Without caching, every single run re-downloads every dependency from
scratch, every time — slow, and, for a busy project, a real amount of
wasted network traffic. `cache: "pip"` tells `actions/setup-python` to
save pip's own downloaded packages after a successful run, keyed on a
hash of the file(s) named in `cache-dependency-path` — the next run, if
that exact file hasn't changed, restores the cached packages instead of
re-downloading them. `actions/setup-node` has the exact same `cache:`
option for `npm`. This is conceptually identical to Module 10's own
Docker layer caching (Lesson 02 of that module) — different mechanism,
same underlying idea: don't redo expensive work that didn't need to
change.

### A quick note on matrix builds (mentioned, not used by this course)

You may see `strategy: matrix:` in real workflows — it runs the *same*
job multiple times, once per combination of listed values (e.g., testing
against Python 3.12, 3.13, AND 3.14 in one workflow). QuestLog's own CI
(Lesson 03) doesn't need this — it targets exactly one pinned Python and
Node version, matching its own Dockerfiles exactly — but recognizing
`strategy: matrix:` in someone else's workflow is worth being able to do.

## Common mistakes & gotchas

- **Forgetting `actions/checkout` entirely**, then being confused why a
  later step says a file "does not exist" — the runner never had your
  repository's files in the first place.
- **YAML indentation errors.** YAML uses indentation (spaces, never tabs)
  to express nesting — a step accidentally indented one space differently
  than its siblings either becomes invalid YAML (GitHub shows a clear
  parse error before even attempting to run anything) or, worse, silently
  changes *which* job or step it belongs to. Use a consistent 2-space
  indent throughout, exactly like every example in this lesson.
- **A workflow that "does nothing" because of the trigger, not a bug in
  the steps.** If `on: push: branches: [main]` and you push to a
  different branch, or open a PR without also listing `pull_request:`,
  the workflow correctly never runs at all — check the Actions tab's own
  "why didn't this run" reasoning (GitHub often explains this directly)
  before assuming your YAML syntax itself is broken.
- **Assuming two jobs share files just because they're in the same
  workflow.** Job 1 building something and Job 2 needing that exact
  output requires either combining them into one job, or using GitHub
  Actions' own **artifacts** mechanism (upload in one job, download in
  another) — this course's own pipeline (Lesson 08) avoids this entirely
  by pushing a Docker image to a registry between jobs instead, which
  naturally works this same way: the registry itself is the shared
  storage.
- **A secret that "isn't working"** almost always means either a typo in
  its exact name (secret names are case-sensitive) between the repo's
  Settings page and the `secrets.NAME` expression, or the secret was
  added to the wrong scope (an *environment*-scoped secret, if your repo
  uses GitHub Environments, is invisible to a job that doesn't specify
  that environment) — this course's own workflows use only plain,
  repository-level secrets, the simplest case.

## How this connects

Lesson 03 takes every piece of syntax from this lesson and applies it for
real: two actual jobs running QuestLog's actual backend and frontend test
suites. Lesson 08's capstone workflow adds the `build-and-push-images`
and `deploy` jobs on top of that, using `needs:`, `if:`, and secrets
exactly as introduced here.

## Quick self-check

1. What's the difference between a workflow, a job, and a step?
2. Why does almost every real job's very first step use
   `actions/checkout`?
3. What does `needs: [backend-tests, frontend-tests]` actually guarantee,
   and what happens to that job if one of those two named jobs fails?
4. What is `secrets.GITHUB_TOKEN`, specifically — where does it come
   from, and how long does it live?
5. Why does `cache: "pip"` (or `cache: "npm"`) make a SECOND run of a
   workflow faster than the first, specifically — what's actually being
   reused, and what determines whether it's still valid to reuse?
