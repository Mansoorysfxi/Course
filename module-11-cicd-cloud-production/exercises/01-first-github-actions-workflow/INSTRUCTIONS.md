# Exercise 01 — Your First GitHub Actions Workflow (Easy)

**Concepts this exercise uses (all taught in
[`lessons/02-github-actions-from-zero.md`](../../lessons/02-github-actions-from-zero.md)'s
"Where a workflow file lives, and the absolute minimum that runs"
section):** `.github/workflows/` file location, `name:`, `on: push:`,
`jobs:`, `runs-on:`, `steps:`, `run:`.

This exercise is deliberately almost impossible to fail if you read
Lesson 02 — it asks you to reproduce, with one small twist, the exact
"Hello CI" example that lesson already walked through in full.

## Your task

Create a brand-new, empty GitHub repository (any name — `hello-actions`
is a reasonable choice), and, inside it, a file at
`.github/workflows/hello.yml` that:

1. Is named (via `name:`) anything you like.
2. Triggers on every push to `main`.
3. Has exactly one job, running on `ubuntu-latest`.
4. Has one step that prints a message **that includes your own GitHub
   username** (not the exact text from Lesson 02's own example — this
   small twist is the only thing this exercise adds beyond directly
   copying that lesson's own worked example).

## Verify it yourself

```bash
mkdir hello-actions && cd hello-actions
git init
mkdir -p .github/workflows
# create hello.yml as described above
git add .
git commit -m "First GitHub Actions workflow"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hello-actions.git
git push -u origin main
```
Open `https://github.com/YOUR_USERNAME/hello-actions/actions` in a
browser. **Expected:** a new run appears within a few seconds, turns
green, and expanding its one step's log shows your message, with your
own real username in it.

## Acceptance criteria

- [ ] The workflow file lives at exactly `.github/workflows/hello.yml`
      (or any filename inside that exact folder).
- [ ] `on: push: branches: [main]` (or an equivalent that genuinely
      triggers on a push to `main`).
- [ ] The one step's printed message includes your own GitHub username.
- [ ] You can point to the exact run in your own repo's Actions tab and
      show the message printed in its log.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 02's own `hello.yml` example is, almost word for word, this
exercise's own answer — the only change needed is the message text
itself.

</details>

<details>
<summary>Hint 2</summary>

If the Actions tab shows nothing at all after pushing, double-check the
file genuinely lives at `.github/workflows/...` at your repo's root, not
nested one folder deeper by accident — Lesson 00-setup.md's own "Common
mistakes" section covers exactly this.

</details>

There is no `starter/`/`solution/` folder for this exercise — it's short
enough, and personal enough (your own username, your own new repo), that
writing it entirely from Lesson 02's own worked example is the intended
path. Ask for a review by sharing a link to your own repo's Actions tab
and the exact YAML you wrote.
