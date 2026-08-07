# Exercise 03 — Branch, Conflict, and a Real Pull Request (Independent)

**Difficulty:** Independent — this exercise describes the *goal state*, not
every command. You decide the exact sequence based on Lessons 04 and 05.

**Concepts this exercise uses:**
- From [`lessons/04-git-branching-and-merging.md`](../../lessons/04-git-branching-and-merging.md): `git branch`, `git switch` / `git switch -c`, merging, merge conflicts and conflict markers, `git branch -d`.
- From [`lessons/05-github-and-pull-requests.md`](../../lessons/05-github-and-pull-requests.md): `git remote add`, `git push -u`, opening/merging a Pull Request on GitHub, `git pull` to sync back down.

## What to build

Using your `recipe-box` repo from Exercise 02 (or a fresh repo if you'd
rather keep them separate — your choice, either is fine):

1. **Push `recipe-box` to a new GitHub repository** if you haven't already
   (same process as `git-practice` in Lesson 05, but for `recipe-box`).
2. **Create a branch** called `add-waffles` from `main`. On it, add a new
   file `waffles.md` with a fake waffle recipe (similar shape to
   `pancakes.md`). Commit it.
3. **Switch back to `main`** and create a *second* branch called
   `rename-pancakes-title`. On this branch, change the very first line of
   `pancakes.md` (its title heading) to something different — e.g. from
   `# Pancakes` to `# Fluffy Pancakes`. Commit it.
4. **Also on `main` itself** (not on either branch), change that exact same
   first line of `pancakes.md` to a *third*, different value — e.g.
   `# Grandma's Pancakes`. Commit this directly on `main`.
5. **Merge `add-waffles` into `main`.** This should merge cleanly (no
   conflict) since it only touches a new file. Confirm with `git log
   --oneline --graph`.
6. **Merge `rename-pancakes-title` into `main`.** Since `main` and this
   branch both changed the same line of `pancakes.md` differently, this
   *should* produce a real conflict. Resolve it by hand: open the file,
   remove the conflict markers, and decide on a final title (it can be
   any of the three versions, a combination, or something new — your
   call). Complete the merge with a commit.
7. **Push `main` to GitHub.**
8. **Open a real Pull Request** for one more small change: create a branch
   `add-license-note`, add a line to `README.md` noting the project has no
   license yet, push the branch, and open a PR on GitHub (via the website
   or `gh pr create --fill` if you installed GitHub CLI).
9. **Merge that Pull Request on GitHub's website**, then sync your local
   `main` with `git pull` and delete the now-merged local branch.

## Acceptance criteria

- [ ] `recipe-box` exists as a real GitHub repository with your full commit history pushed.
- [ ] `git log --oneline --graph` on `main` shows: a fast-forward-style merge for `add-waffles`, and a real two-parent merge commit for `rename-pancakes-title`'s conflicted merge.
- [ ] `pancakes.md`'s final title line contains **no leftover conflict markers** (`<<<<<<<`, `=======`, `>>>>>>>`) anywhere in the file.
- [ ] A Pull Request for `add-license-note` was opened and merged on GitHub itself (not just merged locally) — check that the PR shows as "Merged" on the repo's Pull Requests tab.
- [ ] Local `main` was pulled after the PR merge, and the now-merged local branches were deleted with `git branch -d`.

## What to submit

In `solution/MY_SUBMISSION.md` inside this exercise's folder, paste:
1. The full output of `git log --oneline --graph` on `main` at the end.
2. The final contents of `pancakes.md`.
3. The URL of the merged Pull Request on GitHub.

## Hints

- If step 6's merge doesn't actually produce a conflict, double-check that
  the exact same *line* was changed on both sides — Git only conflicts on
  overlapping changed lines, not merely "both branches touched this file."
  Re-read Lesson 04's explanation of when merges are automatic versus
  conflicting.
- If you're unsure whether your merge was a fast-forward or a real merge
  commit, `git log --oneline --graph` visually distinguishes them — a
  fast-forward shows as a straight line, a real merge shows as a diamond
  shape where two lines rejoin.
- If `git push` for step 7 is rejected because the remote has commits you
  don't have locally, that's `git pull`'s job (Lesson 05) before you push
  again — this can legitimately happen if you interacted with the GitHub
  web UI at any point.
- Stuck on the PR button/flow itself? Re-read Lesson 05's numbered
  "Pull Request workflow, end to end" section — it's the exact sequence
  step 8–9 asks you to repeat independently.
