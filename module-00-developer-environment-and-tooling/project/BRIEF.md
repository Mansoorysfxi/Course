# Module 00 Capstone — Your Course Companion Repo

## What this is

Unlike the three exercises (which used throwaway practice repos), this
capstone has you build a real repository you'll actually keep using: a
personal space to track notes, questions, and reflections as you go through
the rest of this course. It combines every skill from this module into one
real piece of infrastructure instead of one more disposable practice
exercise.

## Concepts this project uses

Everything from Lessons 00–05: shell navigation and file creation, Git
init/add/commit/status/diff/log, `.gitignore`, branching, merging (a real
one, not necessarily a conflicted one this time — that was Exercise 03's
job), remotes, push/pull, and at least one real Pull Request.

## What to build

1. **Create a new repository** called `course-companion` (or a name of your
   choice) — either starting locally with `git init` and connecting it to a
   new GitHub repo, or creating it on GitHub first and cloning it. Either
   direction is acceptable; you've now practiced both in Lessons 03–05.

2. **Set up this structure inside it:**
   ```
   course-companion/
   ├── README.md
   ├── .gitignore
   └── notes/
       └── module-00.md
   ```
   `README.md` should briefly describe what this repo is for (in your own
   words). `.gitignore` should at minimum ignore `.log` files and any
   editor-specific junk files you know about (e.g. nothing required beyond
   `*.log` for now — you don't have real build artifacts yet, but the habit
   of setting this up on day one matters).

3. **Write `notes/module-00.md`** — a genuine reflection, not filler. Include:
   - One thing about Git's model that surprised you or didn't match what
     you expected coming from Perforce/Unreal source control.
   - In your own words: what a merge conflict actually is and why it
     happens (no copy-pasting from the lesson — if you can't say it
     yourself, that's a sign to re-read Lesson 04).
   - One open question you still have, if any.

4. **Commit this in at least three separate, well-messaged commits** (e.g.,
   one for the initial structure, one for the README content, one for the
   notes file) — not one giant commit dumping everything in at once.

5. **Do this final step on a branch, not directly on `main`:** create a
   branch called `module-00-reflection`, and on it, add a second file,
   `notes/module-00-checklist.md`, containing a copy of this module's
   `CHECKLIST.md` self-assessment answers (see the module's `CHECKLIST.md`
   — do that first if you haven't). Commit it, push the branch, and open +
   merge a real Pull Request into `main` on GitHub.

6. **End state:** `main`, both locally and on GitHub, contains everything
   from steps 2–5, fully merged, with your local copy pulled up to date.

## Acceptance criteria

- [ ] The repo exists on GitHub with a clean, sensible commit history (check with `git log --oneline`).
- [ ] `.gitignore` is present and was committed before any file it would have caught was ever staged.
- [ ] `notes/module-00.md` contains genuine, specific reflection — not a restatement of the lesson text.
- [ ] At least one real Pull Request was opened and merged on GitHub for this project (visible on the repo's Pull Requests tab as "Merged").
- [ ] Local `main` is fully synced with GitHub's `main` (`git status` shows clean, `git log` matches what's on GitHub).

## What to submit for review

When you say "check my module," point the AI at (or paste) `git log
--oneline --graph` and the contents of `notes/module-00.md`. The AI will
grade this per [GRADING_PROTOCOL.md](../../GRADING_PROTOCOL.md) as part of
the full module-end review, alongside re-checking Exercises 01–03.

## Why this project, specifically

Real developer note-taking/reflection habits, kept in version control from
day one, are themselves a genuinely good professional practice — this
isn't just an exercise pretending to be useful, it's meant to actually be
useful. You're encouraged to keep adding a `notes/module-XX.md` file to
this same repo as you complete future modules, giving you your own running
record of the course independent of `PROGRESS.md` (which the AI maintains
for grading purposes — this one is just for you).
