# Exercise 01 — Shell Scavenger Hunt

**Difficulty:** Very easy — this should be nearly impossible to fail if you
read [`lessons/01-shell-and-filesystem.md`](../../lessons/01-shell-and-filesystem.md) carefully.

**Concepts this exercise uses** (all taught in Lesson 01):
`pwd`, `mkdir`, `cd`, `touch`, `ls` (including `-la`), `echo` with `>` and
`>>`, `cat`, `cp`, `mv`, `rm` (including `-r`), wildcards (`*`), `echo $VAR`
for environment variables, and `wc -l` with a pipe (`|`).

## What to build

You're going to build a small folder structure entirely from the command
line — no File Explorer, no VS Code file browser, no clicking. Every single
step below must be done by typing a shell command in Git Bash.

Do this inside your `git-practice` folder from the lessons, but in a fresh
subfolder so it doesn't interfere with your Git history:

```bash
cd ~/git-practice
mkdir scavenger-hunt
cd scavenger-hunt
```

From here, complete every task below, in order. Keep your terminal open —
you'll paste your full command history into `solution/MY_COMMANDS.md` at
the end (see "What to submit").

1. Confirm where you are with the command that prints your current working directory.
2. Create three subfolders in one go: `alpha`, `beta`, `gamma`.
3. Inside `alpha`, create an empty file called `treasure.txt`.
4. Without opening an editor, write the exact text `X marks the spot` into `alpha/treasure.txt`.
5. Without opening an editor, *append* a second line to that same file: `Found by: <your name>`.
6. Print the full contents of `alpha/treasure.txt` to confirm both lines are there.
7. Copy `alpha/treasure.txt` into the `beta` folder, keeping the same filename.
8. Move (rename) the copy inside `beta` so it's now called `beta/clue.txt`.
9. Inside `gamma`, create four empty files: `a.log`, `b.log`, `c.txt`, `d.txt`.
10. Using a single `ls` command with a wildcard, list *only* the `.log` files inside `gamma`.
11. Delete both `.log` files inside `gamma` using a single command with a wildcard (not two separate `rm` commands).
12. Print the value of your `HOME` environment variable.
13. Using `ls -la` piped into `wc -l`, count how many entries are in your `scavenger-hunt` folder right now (top level only, not recursive).
14. Create a folder called `temporary-junk` with one file inside it, then delete the whole folder in a single command.

## Acceptance criteria

- [ ] `alpha/treasure.txt` exists and contains exactly two lines: `X marks the spot` and `Found by: <your name>`.
- [ ] `beta/clue.txt` exists with the same two-line content, and there is no leftover `beta/treasure.txt`.
- [ ] `gamma/` contains exactly `c.txt` and `d.txt` — the two `.log` files were deleted using a wildcard, not deleted one at a time.
- [ ] `temporary-junk` does not exist anywhere in `scavenger-hunt` by the end.
- [ ] You can state, for each step, which lesson concept it used.

## What to submit

Create `solution/MY_COMMANDS.md` inside *this exercise's folder structure*
(you'll be comparing against the reference `solution/` after you're done —
don't peek first) containing every command you actually ran, in order, one
per line, in a code block. When you ask for a review, paste this file or
point the AI at it.

## Hints

If you're stuck for more than a few minutes on any single step, here's
where to look before asking for a hint:

- Steps 1–3, 9: re-read the "Creating things" section of Lesson 01.
- Steps 4–6: re-read "Creating things" — specifically the `echo`, `>`, `>>`, and `cat` examples.
- Steps 7–8: re-read "Moving, copying, renaming, deleting."
- Steps 10–11: re-read "Wildcards" — note step 11 specifically asks for *one* command, not two.
- Step 12: re-read "Environment variables and PATH."
- Step 13: re-read "Pipes — connecting commands together."
- Step 14: combines "Creating things" with the `-r` flag from "Moving, copying, renaming, deleting."

If you've re-read the relevant section and are still stuck, ask your AI
session for a hint — it will start at Level 1 (a nudge, no direct answer)
per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
