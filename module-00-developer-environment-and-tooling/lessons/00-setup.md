# Lesson 00 — Setup: Installing Your Toolkit

## What you'll learn

- What each core tool does and why you need it (VS Code, Git, a GitHub account, GitHub CLI).
- How to install all of them on Windows.
- How to tell Git who you are and configure its defaults.
- How to verify every piece of your setup actually works, with exact commands and exact expected output.
- What to do when a step doesn't go as expected (troubleshooting).

## Why this matters

Every exercise, in every module, for the rest of this course, assumes these
tools are installed and working. In game development terms, this is your
engine install + IDE + source control client. Get it right once, carefully,
and you never think about it again. Get it wrong, and every future lesson
becomes twice as hard because you're debugging your environment instead of
learning the actual concept.

## Prerequisites

None — this is the very first thing in the course.

## The concept, explained simply

You're installing four things:

1. **VS Code** — a text editor built specifically for writing code. Think of
   it as Notepad's extremely capable older sibling: it understands
   programming languages (colors your code, catches typos, autocompletes),
   runs commands, and has a plugin ecosystem (Unreal has a similar idea with
   editor plugins/extensions). This is where you'll write every line of code
   in this course.
2. **Git** — a program that tracks the history of changes to your files, so
   you can save checkpoints, go back to any previous checkpoint, and combine
   changes made by different people (or by you, on different days). If
   you've used Perforce or Unreal's built-in revision control, Git solves
   the same core problem — "what changed, when, and can I get it back" — but
   it works completely differently under the hood, which Lessons 03–05 cover.
3. **A GitHub account** — GitHub is a website that hosts Git repositories
   ("repos" — a repo is just a project folder that Git is tracking) online,
   so you can back them up, share them, and collaborate. Git itself doesn't
   need GitHub to work — GitHub is one popular *place* to put your Git
   repos, the way Dropbox is one popular place to put files, but the files
   would still exist without it.
4. **GitHub CLI (`gh`)** — a command-line tool that lets you interact with
   GitHub (create repos, open Pull Requests, etc.) without leaving the
   terminal. Optional but genuinely useful, and this course uses it
   occasionally.

Installing Git for Windows also gives you **Git Bash**, a terminal program
that understands the same commands Linux/Mac developers use ("bash" is the
name of that command language — Lesson 01 explains this properly). We use
Git Bash as the default shell for this whole course because it's what ships
with Git, it's what real teams commonly use on Windows day-to-day for coding
work, and it means the commands you learn here transfer directly to Mac,
Linux, and cloud servers later in the course (Modules 09–11 use real Linux
servers). Windows-specific alternatives (PowerShell) or a full Linux
environment (WSL2) exist and get their moment later — Module 10 explains
exactly when you'll want WSL2, for Docker.

## The details

### Step 1 — Install VS Code

1. Go to `https://code.visualstudio.com/` in your browser.
2. Click the download button for Windows (it should auto-detect your OS).
3. Run the installer (`VSCodeUserSetup-x64-*.exe`). Accept the license,
   keep the default install location.
4. On the "Select Additional Tasks" screen, make sure these boxes are
   checked (they usually are by default):
   - **Add "Open with Code" action to Windows Explorer file context menu**
   - **Add "Open with Code" action to Windows Explorer directory context menu**
   - **Add to PATH** — this is important; it means you can type `code` in a
     terminal to open VS Code. ("PATH" is explained fully in Lesson 01 — for
     now, just make sure this box is checked.)
5. Finish the install and launch VS Code once to confirm it opens.

At the time this lesson was written and verified (August 2026), the current
stable release was **VS Code 1.132**. VS Code auto-updates itself, so by the
time you install it you'll likely have a newer version — that's fine, this
course doesn't depend on a specific VS Code version. If you want to check
your installed version at any time: open VS Code → `Help` menu → `About`.

### Step 2 — Install Git for Windows (this also gives you Git Bash)

1. Go to `https://git-scm.com/install/windows` in your browser.
2. Download the 64-bit installer (the site auto-selects the right one; the
   version verified for this lesson is **2.55.0.3**, released July 2026 —
   you'll likely get something slightly newer, which is fine).
3. Run the installer. The defaults are sensible for almost every option, but
   pay attention to these screens:
   - **Select Components:** leave the defaults checked. Optionally check
     "Windows Explorer integration → Git Bash Here" if you want a
     right-click shortcut to open Git Bash in any folder (recommended).
   - **Choosing the default editor used by Git:** select "Use Visual Studio
     Code as Git's default editor" if it's offered — this means when Git
     ever needs you to type a message in an editor, it'll open VS Code
     instead of an unfamiliar terminal editor.
   - **Adjusting the name of the initial branch in new repositories:**
     choose **"Override the default branch name for new repositories"** and
     type `main`. (Lesson 03 explains exactly what a "branch" is — for now,
     just set this so your repos start with a branch called `main`, which is
     the modern standard GitHub itself uses.)
   - **Adjusting your PATH environment:** choose the recommended middle
     option, **"Git from the command line and also from 3rd-party
     software."**
   - **Choosing the SSH executable:** use the bundled OpenSSH (default).
   - Everything else: keep the defaults.
4. Finish the install.

### Step 3 — Open Git Bash and confirm it launches

Right-click on your Desktop or inside any folder in File Explorer → "Git
Bash Here" (if you enabled that option), or find "Git Bash" in your Start
Menu. A dark terminal window should open showing a prompt that looks
something like:

```
User@YOUR-PC MINGW64 ~
$
```

That `$` is where you type commands. Leave this open — Lesson 01 uses it
immediately.

### Step 4 — Tell Git who you are

Git stamps every "checkpoint" you save (called a **commit** — Lesson 03
explains this in full) with a name and email. This has nothing to do with
logging in anywhere yet — it's just metadata Git attaches locally. In Git
Bash, type each of these lines and press Enter (replace with your own name
and the email you plan to use for GitHub):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**Line by line:**
- `git` — runs the Git program.
- `config` — the subcommand for reading/writing Git's settings.
- `--global` — apply this setting for every repository on this computer, not
  just one project. (The opposite would be a per-repository setting, which
  you won't need yet.)
- `user.name` / `user.email` — the specific settings being written.
- `"Your Name"` — the value, in quotes because it contains a space.

Nothing will print out if these succeed — silence means success. This is a
recurring pattern in command-line tools: many commands only speak up when
something goes *wrong*. That's different from, say, Unreal's editor, which
constantly gives you visual feedback — you'll get used to it.

### Step 5 — Set your default branch name globally (belt-and-suspenders)

You already set this during the installer in Step 2, but let's set it
explicitly via config too, so it's not dependent on remembering an installer
checkbox:

```bash
git config --global init.defaultBranch main
```

This tells Git: whenever I run `git init` to start tracking a new project,
name the first branch `main` (instead of Git's old historical default,
`master`). This setting has existed since Git version 2.28 (released 2020)
and is now the standard practically everyone uses, matching what GitHub
itself defaults to when you create a repo on the website.

### Step 6 — Create a GitHub account

1. Go to `https://github.com/` and click "Sign up."
2. Pick a professional-looking username — you may put this on a resume
   later. Avoid anything embarrassing or hard to say out loud.
3. Verify your email address (GitHub will send a confirmation link/code).

### Step 7 — Connect Git Bash to your GitHub account

You need Git (running on your machine) to be able to prove to GitHub's
servers that commands like "push my code" are actually coming from you.
There are two common ways to do this: HTTPS with a credential helper, or
SSH keys. This course uses **HTTPS with GitHub's credential manager**,
because Git for Windows bundles Git Credential Manager (GCM) automatically,
which makes this the lowest-friction option for a beginner — it pops up a
browser login window the first time you need to authenticate, then
remembers you.

You don't need to do anything to install GCM — it ships with Git for
Windows from Step 2. You'll see it in action the first time you `git push`
to a real GitHub repository, in Lesson 05 / Exercise 03. There's nothing to
verify yet in isolation; it activates on first use.

### Step 8 — Install GitHub CLI (`gh`) (recommended, not strictly required)

1. Go to `https://cli.github.com/` and download the Windows installer.
2. Run it, accepting defaults. The version verified for this lesson was
   **2.96.0** (July 2026) — again, you'll likely get something newer.
3. Close and reopen Git Bash (so it picks up the updated PATH), then
   authenticate:

```bash
gh auth login
```

This starts an interactive prompt. Choose:
- `GitHub.com`
- `HTTPS`
- `Y` to authenticate Git with your GitHub credentials
- `Login with a web browser` — it'll give you a one-time code, open your
  browser, ask you to paste the code and approve.

## Verify your setup

Run each command below in Git Bash and compare against the expected output
shape (your exact version numbers will differ — that's fine, the point is
that a real version number prints instead of an error).

```bash
code --version
```
**Expected:** three lines — a version number (e.g. `1.132.0`), a commit
hash, and an architecture (e.g. `x64`). If you get
`command not found`, VS Code's PATH entry didn't get added — see
Troubleshooting below.

```bash
git --version
```
**Expected:** a single line like `git version 2.55.0.windows.3`.

```bash
git config --global user.name
git config --global user.email
```
**Expected:** your name on the first command, your email on the second.
If either prints nothing, redo Step 4.

```bash
git config --global init.defaultBranch
```
**Expected:** `main`.

```bash
gh --version
```
**Expected:** something like `gh version 2.96.0 (2026-07-02)`. If you skipped
Step 8, this will fail with `command not found` — that's fine, `gh` is
optional. If you *did* install it and see `command not found`, close and
fully reopen Git Bash first (PATH changes only apply to new terminal
windows).

```bash
gh auth status
```
(Only if you installed `gh`.) **Expected:** output including
`Logged in to github.com account <your-username>`.

If every command above prints what's expected, your environment is ready.

## Common mistakes & gotchas

- **`code: command not found` in Git Bash.** Almost always means "Add to
  PATH" wasn't checked during VS Code install, or you opened Git Bash
  *before* installing VS Code and it's using a stale PATH. Fix: close every
  open terminal window completely and open a fresh Git Bash. If it's still
  missing, reinstall VS Code and confirm the "Add to PATH" checkbox.
- **`git: command not found`.** Same category of issue — reopen the
  terminal first; if that doesn't fix it, the Git installer likely didn't
  add Git to PATH (Step 2 → "Adjusting your PATH environment" — reinstall
  and pick the recommended option).
- **Commit author shows the wrong name/email later.** You set `user.name`/
  `user.email` after already making commits, or you set it without
  `--global` inside a repo that then overrides it. Fix: rerun Step 4's
  commands; for already-made commits it's a separate (more advanced) fix
  you don't need yet.
- **A browser window doesn't pop up during `git push` or `gh auth login`.**
  Check if it opened in a background window or a different browser than
  your default. Corporate/locked-down machines sometimes block this flow —
  if so, `gh auth login` also offers a manual "paste this code" flow that
  doesn't require an auto-launched browser.
- **Confusing "Git" and "GitHub."** Git is the tool on your computer that
  tracks history. GitHub is a website/service that stores copies of Git
  repositories online and adds collaboration features (Pull Requests,
  issues, etc.). You can use Git with zero internet connection and never
  touch GitHub. This distinction matters constantly in Lessons 03–05.

## How this connects

Every remaining lesson in this module — and every exercise in this entire
course — assumes this setup is done. Lesson 01 immediately puts your new
Git Bash terminal to work. Lessons 03–05 put Git and GitHub to work. Later
modules (09, 10) revisit your environment to add Linux server access and
Docker — but the Git/VS Code/GitHub foundation you just built never changes.

## Quick self-check

1. What's the difference between Git and GitHub, in your own words?
2. Which file/setting did you change to make new repositories start on a
   branch called `main` instead of `master`?
3. If you typed `git --version` in a brand-new terminal and got
   `command not found`, what's the first thing you'd try?
4. Why does this course use Git Bash instead of PowerShell or Command
   Prompt as the default shell?
