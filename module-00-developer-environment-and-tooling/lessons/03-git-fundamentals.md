# Lesson 03 — Git Fundamentals: Version Control From Zero

## What you'll learn

- What version control is and the actual problem it solves.
- What a Git repository is, and the three-area model: working directory, staging area, repository history.
- The core commands: `git init`, `git status`, `git add`, `git commit`, `git log`, `git diff`.
- What `.gitignore` is and why it exists.
- How to write a good commit message.

## Why this matters

Every professional codebase you will ever touch — at a job, in open source,
in your own future projects — uses version control, almost always Git. It's
not optional professional knowledge, it's foundational, the same way
knowing how to compile your project is foundational before you can talk
about gameplay code. You've likely used Perforce or Unreal's built-in
source control plugin — those solve the same *problem* (tracking changes,
enabling collaboration, allowing rollback) but Git's *model* for doing it
is different enough that this lesson starts from zero rather than assuming
the mapping is obvious.

## Prerequisites

Lesson 00 (Setup — Git installed and configured) and Lesson 01 (Shell — you
need `cd`, `ls`, `mkdir`, `cat`).

## The concept, explained simply

Imagine writing a long design document with no "undo" beyond one step, no
way to see what you changed since yesterday, and no way to combine edits
from two people without one of them just overwriting the other's work.
That's file editing without version control. Now imagine instead: every
time you reach a good stopping point, you save a labeled snapshot of the
*entire project* — not just the current state, but a whole timeline of
snapshots you can inspect, compare, or return to at will. That's what Git
gives you. Each snapshot is called a **commit**.

Unlike Perforce (which is **centralized** — there's one server holding the
"real" history, and your machine holds a working copy plus whatever you've
checked out), Git is **distributed** — your machine holds the *entire*
history of the project, identical to what's on GitHub or any other copy.
This is why Git works completely offline: you can commit, branch, and view
history with no internet connection at all. You only need a network
connection when you want to *sync* with someone else's copy (Lesson 05).

## The details

### The three areas

Every Git repository has three conceptual "areas" your files move through:

1. **Working directory** — the actual files on disk, as you see them in VS
   Code or File Explorer right now. Editing a file changes it here first.
2. **Staging area** (also called "the index") — a holding area where you
   put exactly the changes you want *included in your next commit*. This is
   Git's most distinctive idea versus other tools: you don't commit
   everything you've changed automatically — you explicitly choose what
   goes in, file by file or even chunk by chunk.
3. **Repository (the committed history)** — once you commit, the staged
   snapshot becomes a permanent, timestamped entry in the project's
   history, with an ID.

The flow is always: edit files (working directory) → `git add` (moves
changes into staging) → `git commit` (moves staged changes into permanent
history).

### Starting a repository

```bash
mkdir git-practice
cd git-practice
git init
```

**Expected output:** something like
`Initialized empty Git repository in /c/Users/YourName/git-practice/.git/`.

`git init` creates a hidden folder named `.git` inside `git-practice`. That
folder *is* the entire database of history, commits, branches — everything.
Deleting `.git` un-tracks the project entirely (the files remain, but all
history is gone) — it's the single most important folder in any Git
project and you should never manually edit its contents.

Check it's there (recall `-a` from Lesson 01):

```bash
ls -la
```

### Checking status — your most-used Git command

```bash
git status
```

**Expected output:**
```
On branch main

No commits yet

nothing to commit (working tree clean)
```

`git status` tells you, at any moment: what branch you're on (Lesson 04),
what's changed, what's staged, what isn't. You will run this command more
than any other Git command, constantly, as a sanity check — that's normal
and expected, not a sign you're doing something wrong.

### Your first commit

```bash
echo "# Git Practice" > README.md
git status
```

**Expected output:** Git now reports `README.md` as an **untracked file** —
it exists on disk but Git isn't watching it yet.

```bash
git add README.md
git status
```

**Expected output:** `README.md` moved to a section like "Changes to be
committed" — it's now staged.

```bash
git commit -m "Add initial README"
```

**Expected output:** something like
`[main (root-commit) a1b2c3d] Add initial README` followed by a file-change
summary. `-m` lets you supply the commit message inline; without it, Git
would open your configured editor (VS Code, per Lesson 00) for you to type
one.

**Line by line, what just happened:** `git add` copied the current content
of `README.md` into the staging area. `git commit` took *everything
currently staged* and sealed it into a permanent snapshot, tagged with your
configured name/email (Lesson 00), a timestamp, and the message you gave
it.

**Try it yourself:** run `git status` again right after committing.
Predict what it'll say before running it. (It should say "nothing to
commit, working tree clean" again — the commit consumed everything that
was staged.)

### Making more changes, and `git diff`

```bash
echo "This repo is for practicing Git." >> README.md
git status
```

**Expected output:** `README.md` now shows as "Changes not staged for
commit" — Git can tell the *file* changed because it's tracked, but you
haven't staged the new change yet. (Recall from Lesson 01: `>>` appends,
`>` overwrites — using `>>` here preserves the first line.)

See exactly what changed, before staging it:

```bash
git diff
```

**Expected output:** a diff view — lines starting with `+` are additions,
`-` are removals, shown in the context of surrounding unchanged lines. This
is one of Git's most valuable features: you can review *exactly* what
you're about to commit before you commit it.

```bash
git add README.md
git commit -m "Explain the purpose of this repo in the README"
```

### Viewing history

```bash
git log
```

**Expected output:** your two commits, newest first, each showing a long ID
(a **commit hash** — a unique fingerprint of that exact snapshot, computed
from its content), author, date, and message.

**Try it yourself:** run `git log --oneline` and compare the output format
to plain `git log`. Predict what `--oneline` might abbreviate before
running it.

### Staging multiple files, and staging *some* changes

```bash
touch notes.txt ideas.txt
git status
```
Two untracked files show up.

```bash
git add .
git status
```
`.` means "everything in the current directory and below." Both new files
are now staged. Commit them:

```bash
git commit -m "Add notes and ideas files"
```

### `.gitignore` — telling Git what to never track

Not every file in a project folder belongs in version control. Examples
you'll meet constantly starting in Module 01: virtual environment folders,
compiled output, dependency folders (`node_modules/` in JavaScript
projects), secret API keys, OS-generated junk files (like macOS's
`.DS_Store` or Windows' `Thumbs.db`). Committing these bloats your history
with regenerable/irrelevant files and can leak secrets.

```bash
echo "some log output" > debug.log
cat > .gitignore << 'EOF'
*.log
EOF
git status
```

**Expected output:** `debug.log` does **not** appear as untracked, even
though it exists in the folder — because `.gitignore` told Git to ignore
any file matching `*.log`. `.gitignore` is created the same way as any
file — it's just a plain text file, one pattern per line, that Git reads
automatically.

**Line by line of the command that created it:**
- `cat > .gitignore << 'EOF' ... EOF` — this is a **heredoc**, a way to
  write multiple lines of text into a file from the shell without an
  editor. Everything between the two `EOF` markers becomes the file's
  content. You don't need to memorize this syntax right now — VS Code
  editing a file directly works just as well, this is just a fast
  shell-only way to do it for short files.

Now add `.gitignore` itself to the repo (the ignore-rules file should be
tracked, even though the things it *lists* aren't):

```bash
git add .gitignore
git commit -m "Add .gitignore for log files"
```

### Writing good commit messages

A commit message should describe **why**, not just restate **what** (the
diff already shows *what*). Weak: `fix stuff`, `updates`, `asdf`. Strong:
`Fix crash when order has no items` (a bug fix — explains the symptom
fixed), `Add .gitignore for log files` (an infrastructure change — explains
purpose). Convention widely used in the industry: start with a capitalized,
imperative verb — "Add," "Fix," "Remove," "Refactor" — as if finishing the
sentence "This commit will...". Keep the first line under about 50–72
characters; if you need more explanation, leave a blank line after the
first line and write a longer explanation below it.

## Common mistakes & gotchas

- **Forgetting `git add` before `git commit`.** Committing only saves
  what's *staged*. If you edit a file after staging it but before
  committing, the newer edit isn't included unless you `git add` again.
  `git status` before every commit avoids this.
- **Running `git commit` with no `-m` and no message, then being dropped
  into an unfamiliar editor.** If VS Code opens asking for a commit
  message: type your message on the first line, save, and close the tab —
  Git is waiting for that file to be saved and closed.
- **Committing secrets or huge generated folders because `.gitignore`
  wasn't set up first.** Once something is committed, removing it from the
  *current* files isn't enough — it still exists in history. It's much
  easier to set up `.gitignore` *before* your first commit than to clean up
  after. (Exercise 02 has you practice this deliberately, safely.)
- **Confusing "staged" with "committed."** Staging is temporary and easy to
  undo (`git restore --staged <file>`); committing creates a permanent
  history entry. `git status` always tells you which state a file is in.
- **Thinking `.gitignore` retroactively removes already-tracked files.**
  It only prevents *new*, currently-untracked files from being picked up.
  A file Git is already tracking keeps being tracked even if it later
  matches a `.gitignore` pattern, until you explicitly untrack it.

## How this connects

This lesson gave you the entire *local*, single-timeline Git workflow.
Lesson 04 introduces **branches** — multiple parallel timelines within the
same repository — and what happens when two timelines both changed the
same part of a file (a **merge conflict**). Lesson 05 connects your local
repository to GitHub so this history can be backed up, shared, and
collaborated on. Exercise 02 in this module has you build and commit to a
real repo using exactly the commands from this lesson.

## Quick self-check

1. What are the three areas a change passes through, in order, from editing a file to it being permanently in history?
2. What's the difference between `git add` and `git commit`?
3. Why does Git work completely offline, unlike Perforce?
4. If you create `secrets.env` and don't want it ever tracked, what do you do, and *when* should you do it relative to your first commit involving that file?
5. What makes a commit message like "Fix crash when order has no items" better than "fix stuff"?
