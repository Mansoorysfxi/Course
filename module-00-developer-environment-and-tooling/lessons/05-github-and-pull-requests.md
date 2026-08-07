# Lesson 05 — GitHub, Remotes, and Pull Requests

## What you'll learn

- What a "remote" is, and how your local repo connects to one on GitHub.
- How to create a repository on GitHub and connect an existing local repo to it.
- `git push`, `git pull`, `git clone`, and `git fetch` — what each actually does.
- What a Pull Request (PR) is and why it exists as a workflow, not just a button.
- The full collaboration loop: branch → push → open PR → review → merge.

## Why this matters

Lessons 03–04 gave you a fully working *local* Git workflow. That's genuinely
useful on its own (backup, history, branching for yourself) — but the
version of Git you'll use professionally is almost always about
*collaborating with other people through a shared remote copy*, and GitHub
is the dominant place that happens. The Pull Request workflow specifically
is how nearly all modern software teams and open-source projects review and
integrate changes — you'll use this exact loop for the rest of this course
and in any real job.

## Prerequisites

Lesson 03 (Git Fundamentals), Lesson 04 (Branching & Merging), and Lesson 00
(a GitHub account, and Git Credential Manager available from installing Git
for Windows).

## The concept, explained simply

So far, every repository you've made has existed only on your machine. A
**remote** is just a name Git gives to a *URL pointing at another copy* of
the same repository — most commonly, one hosted on GitHub. Your local repo
and the GitHub copy are not automatically kept in sync; you explicitly
**push** (upload your commits to the remote) and **pull** (download commits
from the remote into your local copy) whenever you want to sync.

A **Pull Request** (PR) is GitHub's name for a very specific, very useful
request: *"I've made these commits on this branch — please review the diff,
and if it looks good, merge them into that branch."* It is literally a
structured, reviewable wrapper around the merge you already learned to do
by hand in Lesson 04 — GitHub does the merge on your behalf once someone
approves and clicks "Merge," but everything happening underneath is exactly
the Git you already know.

## The details

### Creating a repository on GitHub and connecting to it

There are two common starting points: a repo that already exists locally
(your `git-practice` from Lessons 03–04), or starting fresh from GitHub.
Do the first one now.

1. Go to `github.com`, click the `+` in the top right → **New repository**.
2. Name it `git-practice` (matching your local folder, though the name
   doesn't technically have to match).
3. **Do not** check "Add a README file" or add a `.gitignore`/license from
   GitHub's UI — you already have a repo with history locally, and
   starting the GitHub copy completely empty avoids an unnecessary conflict
   in this first connection.
4. Click **Create repository**. GitHub shows you a page with setup
   commands — you're about to run the "push an existing repository" block
   manually, understanding each line rather than blindly pasting it.

Back in Git Bash, inside your `git-practice` folder:

```bash
git remote add origin https://github.com/YOUR-USERNAME/git-practice.git
```

**Line by line:**
- `git remote add` — register a new remote.
- `origin` — the conventional name for "the main remote copy of this repo."
  It's just a label, not a keyword — you could name it anything, but
  literally everyone uses `origin` for the primary remote by convention.
- The URL — where GitHub is hosting this repo. Copy this exact URL from
  your new repo's GitHub page (it'll show your actual username).

Verify it registered:

```bash
git remote -v
```
**Expected output:** two lines, both showing `origin` and your URL — one
for `fetch`, one for `push` (they can differ in advanced setups; for you
right now, they'll be identical).

### Pushing your history up

```bash
git push -u origin main
```

**Line by line:**
- `push` — upload commits from your local branch to the remote.
- `-u` — short for `--set-upstream`: remembers that your local `main`
  should track `origin`'s `main` from now on, so future plain `git push` /
  `git pull` commands (with no arguments) know where to sync automatically.
- `origin main` — push to the remote named `origin`, specifically its
  `main` branch.

**Expected output:** progress lines about compressing/writing objects, then
something like `* [new branch] main -> main`, and possibly a **browser
window popping up** asking you to confirm/log in via GitHub — this is Git
Credential Manager (Lesson 00) authenticating you for the first time. Log
in and approve; it remembers you afterward.

Refresh the GitHub repo page in your browser. **Expected result:** your
`README.md` and full commit history are now visible on GitHub.

### `clone` — getting a copy of a remote repo you don't have locally yet

You won't need this for `git-practice` since you built it locally first,
but this is how you'd start from the *other* direction — say, joining an
existing project:

```bash
git clone https://github.com/some-org/some-project.git
```
This downloads the *entire* history (not just the latest snapshot) into a
new folder named after the project, and automatically sets up `origin` for
you. You'll use `git clone` for essentially every project you didn't
personally create from scratch, starting with real projects later in this
course.

### `pull` and `fetch` — syncing changes down

If someone else (or you, from another machine, or via the GitHub web
editor) added commits to the remote that you don't have locally yet:

```bash
git pull
```
This downloads new commits from `origin` and merges them into your current
branch in one step — mechanically, it's `git fetch` (download the new
commits, but don't touch your current branch yet) followed by `git merge`
(combine them in) — you already know exactly what that second half does
from Lesson 04, including that it can produce a conflict if you and the
remote both changed the same lines.

**Try it yourself:** on GitHub's web UI, edit `README.md` directly (GitHub
lets you edit files and commit right in the browser) and add a line, commit
it via the website. Then run `git pull` locally and watch the new line
appear in your local file — you just synced a change that never touched
your machine's shell until the `pull`.

### The Pull Request workflow, end to end

This is the workflow you'll repeat for the rest of this course and, likely,
your career. Practice it now on your own repo, where there's no risk.

1. **Branch for the new work** (never work directly on `main` for anything
   beyond trivial personal projects — Lesson 04 covers why):
   ```bash
   git switch -c add-license-note
   echo "This project has no formal license yet." >> README.md
   git add README.md
   git commit -m "Note that no license is set yet"
   ```
2. **Push the branch** (note: *not* `main` this time):
   ```bash
   git push -u origin add-license-note
   ```
3. **Open the Pull Request.** GitHub's response to that push usually
   includes a direct URL to open a PR. Alternatively, go to your repo on
   GitHub — it shows a banner "`add-license-note` had recent pushes" with
   a **Compare & pull request** button. Click it. You'll see:
   - **Base branch** — what you want to merge *into* (should be `main`).
   - **Compare branch** — your new branch (`add-license-note`).
   - A diff, exactly like `git diff`/`git log` would show, rendered nicely.
   - A title (pre-filled from your commit message) and a description box —
     explain *why*, for whoever reviews it (even if that's future-you).
4. **Click "Create pull request."**
5. **Review it** — on a real team, someone else looks at the diff and
   comments or approves. Solo, you're both author and reviewer — still
   worth actually re-reading the diff on the PR page before merging, as a
   habit.
6. **Merge it.** Click **Merge pull request** → **Confirm merge**. GitHub
   performs the equivalent of `git merge add-license-note` on its own
   server copy of `main`.
7. **Delete the branch** (GitHub offers a button right after merging) — its
   commits are safely preserved inside `main`'s history now; the branch
   label itself has served its purpose.
8. **Sync your local machine:**
   ```bash
   git switch main
   git pull
   ```
   Your local `main` now has the merged commit too, and you can safely
   delete your local copy of the now-merged branch:
   ```bash
   git branch -d add-license-note
   ```

### Why bother with a PR instead of just pushing straight to `main`?

For a solo repo, technically nothing stops you from committing directly to
`main` and skipping all of this. The PR workflow exists because on any team
of more than one person, you need: a checkpoint for review before code
lands, a record of *why* a change was made (the PR description/discussion),
a way to run automated checks before allowing a merge (you'll wire this up
yourself in Module 11 — CI/CD), and a clean way to know exactly what will
change *before* it changes anything. Practicing it solo now means the
workflow itself is already muscle memory before you're doing it under any
real pressure or with a real reviewer.

### `gh` shortcut (optional)

If you installed GitHub CLI in Lesson 00, the entire "open a PR" step can be
done from the terminal instead of the browser:

```bash
gh pr create --fill
```
`--fill` auto-uses your latest commit's message/description instead of
prompting you interactively. This opens the same PR you'd have made via the
website — `gh` is just a terminal-based alternative interface to the same
GitHub features, not a different system.

## Common mistakes & gotchas

- **Pushing before committing.** `git push` only sends commits that already
  exist locally. If `git status` shows uncommitted changes, `push` won't
  include them — commit first.
- **Forgetting `-u` on the first push of a new branch**, then being
  confused why plain `git push` later says it doesn't know what to push to.
  Fix: either use `-u` the first time, or Git's error message itself tells
  you the exact full command to run instead.
- **Opening a PR against the wrong base branch.** Always check the "base"
  dropdown on GitHub's PR creation screen — it defaults sensibly most of
  the time, but double-check, especially once you're working across more
  than two branches.
- **Merging a PR on GitHub and then being confused that your local `main`
  doesn't have the change.** The merge happened on GitHub's server copy —
  your local machine needs its own explicit `git pull` to catch up. This
  trips up almost everyone at first.
- **Force-pushing without understanding it.** Not covered in this lesson on
  purpose — it's a more advanced, riskier operation (it can rewrite shared
  history) that this course will introduce deliberately later, with proper
  warnings, rather than casually now.

## How this connects

This closes the loop on the entire Module 00 Git arc: local commits (Lesson
03) → branches and merging (Lesson 04) → sharing that history with a remote
and collaborating through Pull Requests (this lesson). This exact
branch → push → PR → merge → pull loop is what you'll use for every
exercise submission structure, every module's capstone if you choose to
track it on GitHub, and any real collaborative project for the rest of your
career.

## Quick self-check

1. What is a "remote," mechanically — what is Git actually storing when you `git remote add origin <url>`?
2. What's the difference between `git fetch` and `git pull`?
3. Why did merging a PR on GitHub's website not automatically update your local `main`?
4. Put the full collaboration loop in order: merge, push, open PR, branch, commit.
5. Name one concrete reason a team would want PRs instead of everyone pushing straight to `main`.
