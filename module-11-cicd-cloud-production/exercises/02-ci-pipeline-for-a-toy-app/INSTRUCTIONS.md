# Exercise 02 — A Real CI Pipeline for a Toy App (Guided)

**Concepts this exercise uses (all taught in
[`lessons/02-github-actions-from-zero.md`](../../lessons/02-github-actions-from-zero.md)
and [`lessons/03-a-real-ci-pipeline-for-questlog.md`](../../lessons/03-a-real-ci-pipeline-for-questlog.md)):**
`.github/workflows/` file location, `on: push:`/`on: pull_request:`,
`jobs:`, `runs-on:`, `steps:`, `uses:` vs `run:`, `actions/checkout`,
`actions/setup-python`, `working-directory:`, `cache:`.

**Where to work:** `exercises/02-ci-pipeline-for-a-toy-app/starter/` — a
tiny, already-working FastAPI app (`app/main.py`) with a real, already-
passing pytest suite (`tests/test_main.py`). Confirm it works locally
first:
```bash
cd exercises/02-ci-pipeline-for-a-toy-app/starter
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -v
```
**Expected:** `3 passed`.

## Your task

Write `.github/workflows/ci.yml` **from scratch** (there is no workflow
file in `starter/` at all — you're writing one) that:

1. Triggers on every push to `main`, and every pull request targeting
   `main`.
2. Has exactly one job, `test`, running on `ubuntu-latest`.
3. Checks out the repo, sets up Python **3.14**, and installs BOTH
   `requirements.txt` and `requirements-dev.txt`.
4. Uses `actions/setup-python`'s own built-in `cache: "pip"` option.
5. Runs `python -m pytest -v`.

## Verify it yourself

Since this is a standalone exercise folder, actually seeing this run
requires treating `starter/` as its own tiny GitHub repo — see
[`lessons/00-setup.md`](../../lessons/00-setup.md)'s own "which repo does
this even run in" explanation for exactly how (a throwaway repo is fine
here; delete it afterward if you like). If you'd rather not push
anything for real right now, reading your own `.github/workflows/ci.yml`
back against this exercise's acceptance criteria, and against Lesson 02's
own worked examples, is a legitimate way to complete this exercise — the
same "understanding fully is enough, live execution is optional" framing
this whole module uses.

If you do push it for real:
```bash
cd exercises/02-ci-pipeline-for-a-toy-app/starter
git init && git add . && git commit -m "toy CI app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/toy-ci-app.git
git push -u origin main
```
**Expected:** a new run appears under that repo's **Actions** tab within
seconds, turns green, and expanding the "Run pytest" step's log shows the
exact same `3 passed` output you already saw locally.

## Acceptance criteria

- [ ] `.github/workflows/ci.yml` exists, with no syntax errors (GitHub
      itself will show a clear error banner in the Actions tab if the
      YAML is invalid).
- [ ] The workflow triggers on both `push` to `main` and `pull_request`
      targeting `main`.
- [ ] `actions/checkout@v7` and `actions/setup-python@v6` are both used,
      each with an explicit, pinned major version (never unpinned).
- [ ] Python is set to version `"3.14"`, matching this exercise's own
      local setup.
- [ ] The workflow installs both requirements files and runs
      `python -m pytest -v`.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 03's own `backend-tests` job is structurally almost identical to
what this exercise wants — same trigger shape, same
checkout/setup-python/install/test step order. The main difference: this
toy app has no `SECRET_KEY` or any other required environment variable
to set.

</details>

<details>
<summary>Hint 2</summary>

`pip install -r requirements.txt -r requirements-dev.txt` installs both
files in one command — `pip install -r` accepts more than one `-r` flag.

</details>

<details>
<summary>Hint 3</summary>

`cache-dependency-path:` under `actions/setup-python`'s own `with:` can
be a YAML list (one entry per line, using `|`) if you want the cache key
to depend on both requirements files' contents — see Lesson 03's own
`backend-tests` job for the exact syntax.

</details>

A reference solution is in `solution/`.
