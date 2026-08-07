# Module 00 — Developer Environment & Tooling

**Phase:** 0 — Foundations & Environment
**Estimated time:** 8–12 hours over your first week
**Verified against:** Git for Windows 2.55.0.3, VS Code 1.132, GitHub CLI (gh) 2.96.0 — all current as of August 2026. Versions change fast; the setup lesson tells you how to check what's actually current when you install.

## What this module is

Before you write a single line of "real" code in this course, you need the
tools every professional developer uses daily to write, run, save, and share
code. In Unreal Engine terms: this is the equivalent of getting the engine
installed, Visual Studio configured, Perforce or Git set up, and knowing your
way around the editor's file browser and output log — before you ever open a
Blueprint. Skipping this module would be like trying to learn gameplay
scripting without knowing how to open the project.

None of this is "AI" or "full stack" specific — it's the ground floor every
other module stands on.

## What you'll be able to do after this module

- Use a command-line shell (Git Bash) confidently: navigate folders, create/move/delete files, understand environment variables and `PATH`.
- Explain what version control is and why every professional codebase uses it.
- Use Git for the full local workflow: `init`, `add`, `commit`, `branch`, `merge` — including resolving a merge conflict by hand.
- Push code to GitHub, open a Pull Request, and merge it — the same workflow used at real companies and in open source.
- Read an error message or a stack trace systematically instead of panicking or guessing.
- Read unfamiliar documentation efficiently and know what to search for when you're stuck.

## Prerequisites

None. This is the first module. You need a Windows machine with permission
to install software (admin rights) and an internet connection.

## Module structure

```
module-00-developer-environment-and-tooling/
├── README.md                          ← you are here
├── lessons/
│   ├── 00-setup.md                    ← install everything, verify it works
│   ├── 01-shell-and-filesystem.md     ← what a shell is, navigating via CLI
│   ├── 02-reading-docs-and-errors.md  ← how to read docs & stack traces
│   ├── 03-git-fundamentals.md         ← version control, init/add/commit
│   ├── 04-git-branching-and-merging.md← branches, merges, conflicts
│   └── 05-github-and-pull-requests.md ← remotes, push/pull, PRs
├── exercises/
│   ├── 01-shell-scavenger-hunt/
│   ├── 02-git-basics-repo/
│   └── 03-branch-merge-conflict/
├── project/
│   └── BRIEF.md                       ← Course Companion Repo capstone
└── CHECKLIST.md
```

Read the lessons in numeric order — each one assumes everything before it.
Do not skip `00-setup.md` even if you think you already have some of this
installed; it ends with a "Verify your setup" section you should actually
run.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson fully,
answer its self-check questions, do the matching exercise without peeking at
the solution, then ask your AI session *"Review my solution for exercise
0N"*. After all three exercises and the capstone project are done, say
*"Check my module"* for the full module-end review.

## A note on the capstone

The Module 00 capstone (`project/BRIEF.md`) has you build a real GitHub
repository you'll actually use to track your own notes as you go through
this course — so it's not a throwaway exercise, it's infrastructure you keep.
