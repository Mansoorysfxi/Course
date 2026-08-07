# Exercise 02 — Build a Git Repo From Scratch (Guided)

**Difficulty:** Guided — more independent than Exercise 01, but the steps
are still spelled out. You decide the exact commit messages and some file
content yourself.

**Concepts this exercise uses** (all taught in [`lessons/03-git-fundamentals.md`](../../lessons/03-git-fundamentals.md)):
`git init`, `git status`, `git add`, `git commit -m`, `git log` /
`git log --oneline`, `git diff`, `.gitignore`, and writing a good commit
message.

## What to build

A small repository for a fake project called **"recipe-box"** — a plain
text collection of recipes. You'll create it, track it with Git properly
from the start (including correctly *avoiding* committing a file that
shouldn't be tracked), and build up a real, readable commit history.

1. Create a new folder called `recipe-box` (not inside `git-practice` —
   this is a separate, standalone repo) and initialize it as a Git
   repository.
2. Confirm you're starting on a branch called `main` (Lesson 00's config
   should make this automatic — if it says `master` instead, go fix your
   `git config --global init.defaultBranch` setting from Lesson 00 before
   continuing).
3. Create a file `README.md` with at least a title and one sentence
   describing the (fake) project. Stage and commit it with a message
   that follows the "why, not just what" guidance from Lesson 03.
4. Create a file `pancakes.md` containing a short fake recipe (ingredients
   + steps, doesn't need to be real or good). Stage and commit it
   separately from the README — this should be its own commit, not bundled
   into the previous one.
5. Create a file `notes-to-self.log` with any throwaway text in it — this
   is meant to represent a debug/scratch file that should **never** be
   committed.
6. *Before* that log file ever gets staged, create a `.gitignore` file that
   ignores all `.log` files. Commit `.gitignore` on its own.
7. Confirm (using `git status`) that `notes-to-self.log` does not show up as
   untracked after the `.gitignore` commit.
8. Edit `pancakes.md` to add a second recipe's worth of content to the same
   file (e.g., a "tip" section or a variation). Before staging it, run
   `git diff` and actually read the output. Then stage and commit this
   change with an appropriately descriptive message.
9. Run `git log --oneline` and confirm you see exactly four commits, in a
   sensible order, each with a message that would make sense to someone
   who never saw the diff.

## Acceptance criteria

- [ ] The repo was initialized with `main` as the starting branch (verify with `git branch`).
- [ ] Exactly four commits exist, each doing one coherent thing (README, pancakes, gitignore, pancakes update) — not, for example, everything squashed into one commit, and not the `.gitignore` bundled in with another file's commit.
- [ ] `notes-to-self.log` exists on disk but was never staged or committed, and `git status` confirms it's ignored, not just "you happened to not run `git add` on it."
- [ ] Each commit message explains intent, not just filenames (e.g. not just "update files").
- [ ] `git log --oneline` output is included in what you submit for review.

## What to submit

Run `git log` (full form, not `--oneline`) and copy its full output, plus
the final contents of `.gitignore`, into a file called
`solution/MY_SUBMISSION.md` inside this exercise's folder. Also paste the
output of your `git diff` from step 8 (the diff itself, not just that you
ran it) — this proves you actually looked at it before committing, which is
the real point of that step.

## Hints

- If `notes-to-self.log` keeps showing up in `git status` after you write
  `.gitignore`, double check: did you write `*.log` (matches any `.log`
  file) or literally `notes-to-self.log` only? Both work for this exercise,
  but re-read Lesson 03's `.gitignore` section on *why* the wildcard version
  is usually preferred.
- If you accidentally `git add`-ed the log file *before* writing
  `.gitignore`, adding it to `.gitignore` afterward won't undo the staging.
  Re-read the "Common mistakes" section of Lesson 03 about `.gitignore`
  being forward-looking only, and use `git restore --staged
  notes-to-self.log` to un-stage it (this specific command wasn't taught
  yet in detail — it's fine to look up what it does, per Lesson 02's
  method, since it's a small escape hatch, not a core concept this exercise
  is testing).
- Stuck on writing a "why not what" commit message? Look again at the
  concrete good/bad examples in Lesson 03's "Writing good commit messages"
  section and model yours the same way.
