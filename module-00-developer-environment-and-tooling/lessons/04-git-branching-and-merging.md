# Lesson 04 — Branches, Merging, and Resolving Conflicts

## What you'll learn

- What a branch actually is under the hood (it's simpler than it sounds).
- How to create, switch between, and delete branches.
- How to merge one branch into another.
- What a merge conflict is, why it happens, and how to resolve one by hand.
- The difference between a fast-forward merge and a real merge commit.

## Why this matters

Real projects are never worked on as one single, straight-line history.
You'll want to try something risky without breaking what already works,
work on a feature while a teammate works on a different one, or maintain a
stable version while developing the next one. Branches are how Git lets
multiple timelines coexist and later recombine. Conflicts are not a sign of
failure — they happen on every real team, constantly — so learning to
resolve one calmly, by hand, once, removes a huge amount of future anxiety.

## Prerequisites

Lesson 03 (Git Fundamentals) — you need `init`, `add`, `commit`, `status`,
`log` and a mental model of the staging area.

## The concept, explained simply

Think of your commit history as a chain of snapshots, each pointing back to
the one before it — like a chain of savepoints. A **branch** is nothing
more than a movable label pointing at one specific commit in that chain.
When you make a new commit while a branch label is "checked out," Git
moves that label forward to point at the new commit. That's the entire
mechanism — branches aren't separate copies of your project, they're just
named pointers. This is why creating a branch in Git is instant and cheap,
unlike, say, duplicating an entire project folder.

`HEAD` is a special pointer that always tracks "which branch (and
therefore which commit) am I currently looking at" — it's how Git knows
what your working directory should currently contain.

A **merge** takes the changes introduced on one branch and combines them
into another. Most of the time this is automatic and painless — Git is
very good at combining non-overlapping changes. A **merge conflict**
happens specifically when the *same lines* of the *same file* were changed
differently on both branches, and Git genuinely cannot guess which version
you want — so it stops and asks you.

## The details

### Creating and switching branches

Continue in the `git-practice` repo from Lesson 03 (or `cd` back into it).

```bash
git branch
```
**Expected output:** `* main` — the `*` marks your current branch. Right
now there's only one.

Create a new branch:

```bash
git branch feature-greeting
git branch
```
**Expected output:** now both `feature-greeting` and `main` are listed, `*`
still on `main` — creating a branch does **not** switch you to it.

Switch to it:

```bash
git switch feature-greeting
git branch
```
**Expected output:** `*` has moved to `feature-greeting`. (`git switch` is
the modern command for changing branches; you'll also see `git checkout
<branch>` used for the same purpose in older tutorials and some tools —
they're equivalent for this use case, `switch` was introduced later
specifically to be less confusing than `checkout`, which historically did
several unrelated things.)

Shortcut — create *and* switch in one command:

```bash
git switch -c feature-goodbye
```
`-c` = "create." You're now on a brand new branch called `feature-goodbye`,
created from wherever `main` currently was.

### Making a commit on a branch

```bash
git switch feature-greeting
echo "Hello there!" > greeting.txt
git add greeting.txt
git commit -m "Add greeting file"
git log --oneline
```

**Expected output:** you'll see this new commit, plus the earlier commits
from Lesson 03 that came before the branch split off.

Now check `main`:

```bash
git switch main
ls
```
**Expected output:** `greeting.txt` is **not** here. This is the entire
point of branches — `main`'s working directory only reflects commits that
are actually part of `main`'s history. The file genuinely doesn't exist
from `main`'s point of view yet.

### Merging — the easy case (fast-forward)

```bash
git switch main
git merge feature-greeting
ls
```

**Expected output:** Git prints something like `Fast-forward` followed by
a file change summary, and `greeting.txt` now appears. Since `main` hadn't
moved at all since `feature-greeting` branched off, Git could just slide
`main`'s pointer forward to match — no real "combining" was needed. This is
called a **fast-forward merge**.

### Merging — when both sides changed (a real merge commit)

Let's create a scenario where both branches move forward independently, so
merging has actual work to do.

```bash
git switch main
echo "This project has a greeting feature." >> README.md
git add README.md
git commit -m "Document the greeting feature in README"

git switch feature-goodbye
echo "Goodbye!" > goodbye.txt
git add goodbye.txt
git commit -m "Add goodbye file"
```

Now both `main` and `feature-goodbye` have commits the other doesn't have.
Merge `feature-goodbye` into `main`:

```bash
git switch main
git merge feature-goodbye
```

**Expected output:** since the two branches changed *different* files
(`README.md` on one, `goodbye.txt` on the other), Git combines them
automatically and opens your editor for a merge commit message (it
pre-fills one — you can just save and close). You'll see something like
`Merge made by the 'recursive' strategy.` This time Git created a genuine
new **merge commit** — one with *two* parents (the tip of `main` and the
tip of `feature-goodbye`) — because the histories had actually diverged and
needed combining, not just sliding a pointer forward.

```bash
git log --oneline --graph
```
`--graph` draws a text-based diagram of the branch/merge structure — worth
running any time you want to visualize what happened.

### Creating (and resolving) a real merge conflict, on purpose

This is the part beginners fear most and the part this course wants you to
practice deliberately, in a safe throwaway repo, before it ever happens for
real and matters.

```bash
git switch main
echo "Welcome to Git Practice." > README.md
git add README.md
git commit -m "Rewrite README opening line (on main)"

git switch -c conflict-branch
echo "Hello and welcome to my Git Practice repo." > README.md
git add README.md
git commit -m "Rewrite README opening line (on conflict-branch)"
```

Both branches now changed the *very same line* of `README.md`, differently.
Try to merge:

```bash
git switch main
git merge conflict-branch
```

**Expected output:** Git refuses to auto-resolve, and prints something
like:
```
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

Open `README.md` in VS Code. It now contains **conflict markers** Git
inserted directly into the file:

```
<<<<<<< HEAD
Welcome to Git Practice.
=======
Hello and welcome to my Git Practice repo.
>>>>>>> conflict-branch
```

**What each marker means:**
- `<<<<<<< HEAD` — everything below this, down to the `=======`, is *your
  current branch's* version (`main`, since that's what `HEAD` points to
  right now).
- `=======` — the dividing line between the two versions.
- `>>>>>>> conflict-branch` — everything above this, up from `=======`, is
  the *incoming branch's* version.

**To resolve it:** decide what the file should actually say, delete the
three marker lines (`<<<<<<<`, `=======`, `>>>>>>>`) entirely, and leave
only the final text you want. For example, edit the file so it just
contains:

```
Hello and welcome to my Git Practice repo.
```

(You can keep one side, the other, a combination, or something new
entirely — Git has no opinion here, this decision is entirely yours.)

Then tell Git the conflict is resolved:

```bash
git add README.md
git status
```
**Expected output:** `README.md` now shows as staged, and status should say
something like "All conflicts fixed but you are still merging." Complete
the merge:

```bash
git commit -m "Merge conflict-branch, resolve README opening line"
```

No `-m` message is pre-filled as cleanly here since it was a conflicted
merge — but you can still supply your own with `-m` as usual.

```bash
git log --oneline --graph
```
Confirm the merge commit exists and both parent lines are present.

### Deleting a branch you no longer need

```bash
git branch -d feature-goodbye
```
`-d` deletes a branch *only if* it's already fully merged somewhere,
protecting you from silently losing unmerged commits. (There's a `-D`
force-delete for when you're certain, but that's outside this lesson's
scope — you don't need it yet.)

## Common mistakes & gotchas

- **Panicking mid-conflict and running `git merge --abort`.** This is
  actually a legitimate escape hatch — it cancels the merge and returns you
  to exactly how things were before you started — but new learners
  sometimes use it out of panic and then feel stuck. It's fine to abort and
  retry; it's not a failure state.
- **Leaving conflict markers in the file by accident.** If you forget to
  delete `<<<<<<<`/`=======`/`>>>>>>>` and just `git add` + commit anyway,
  the file now contains broken, literal marker text as real content. Always
  open the file and read it fully after a conflict, before staging it.
- **Forgetting which branch you're on before making changes.** Always
  `git status` (it shows the current branch at the top) or `git branch`
  before starting new work, especially after switching around during
  practice like this lesson.
- **Confusing a fast-forward merge with a "real" merge.** Both are valid
  and correct — fast-forward just means there was nothing to actually
  combine. Don't be confused if `--graph` looks like a straight line for
  some merges and a diamond shape for others; both are expected.
- **Trying to switch branches with uncommitted changes that would be
  overwritten.** Git will refuse and print a warning rather than silently
  losing your work — that's Git protecting you, not a bug. Commit or stash
  your work first (stashing is outside this lesson's scope — for now,
  commit before switching).

## How this connects

Branches and merge conflicts are the backbone of how *any* real
collaboration happens in Git — including the Pull Request workflow in
Lesson 05, where a Pull Request is essentially "please merge my branch into
yours, here's a preview of the diff, and here's where any conflicts would
be." Every module from here on that has you touch a shared or evolving
codebase will have you branch for new work rather than committing straight
to `main`.

## Quick self-check

1. What is a branch, mechanically — what is Git actually storing when you create one?
2. What's the difference between a fast-forward merge and a merge commit with two parents?
3. What do the three conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) each represent?
4. After resolving a conflict by editing the file, what two commands do you run to finish the merge?
5. Why does Git refuse to switch branches if you have uncommitted changes that would be overwritten?
