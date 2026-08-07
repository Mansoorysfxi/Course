# Lesson 00 — Setup: Installing Python, venv, and pip

## What you'll learn

- What Python actually is (the language vs. the interpreter that runs it) and why you need to install something at all.
- How to install Python on Windows, and which exact version to get.
- The difference between the `python` command and the `py` launcher on Windows, and why that distinction exists.
- What a virtual environment is, why every Python project needs its own, and how to create/activate one with `venv`.
- What `pip` is and how `requirements.txt` records a project's dependencies.
- How to confirm VS Code is ready to run and debug Python.
- How to verify every piece of this setup, and how to fix the most common failures.

## Why this matters

Module 00 got your shell, Git, and VS Code working — the tools every module in this course uses. This lesson does the same thing for Python specifically. Every lesson and exercise from here through the rest of Phase 0–2 assumes you can open a terminal, run `python something.py`, and have it actually work, using an isolated set of packages that won't quietly break some *other* Python project on your machine. Skipping this, or doing it sloppily, is the single most common reason beginners get mysterious "it works on the tutorial video but not for me" errors — almost always because of which Python, or which set of installed packages, actually ran.

In Unreal terms: this is the equivalent of making sure you have the right Engine version installed, and understanding that each project can pin its own Engine version and plugin set rather than every project on your machine being forced to share one global setup.

## Prerequisites

Module 00 in full — you need a working shell (Git Bash), VS Code, and to be comfortable navigating folders and running commands from Lesson 01 of that module.

## The concept, explained simply

**Python** is both a *language* (the rules for what `x = 5` or `def foo():` mean) and a *program* called the **interpreter** that reads your `.py` files and actually executes them, line by line, translating your code into action as it goes — unlike C++, which you *compile* ahead of time into a `.exe` and then run separately. There is no separate compile step for a normal Python script: you write it, and you run it directly with the interpreter. That's the single biggest workflow difference from Unreal C++ you'll feel immediately — no waiting for a build.

Installing "Python" means installing that interpreter program onto your machine, plus a standard library of pre-written code that ships with it (things like `json`, `os`, `math` — all covered in later lessons).

A **virtual environment** solves a specific problem: imagine Project A needs version 1.0 of some package, and Project B (started a year later) needs version 3.0 of the *same* package, and installing one globally on your machine would break the other. A virtual environment is a self-contained, disposable folder holding its own private copy of the Python interpreter's package list, isolated from every other project and from your system's global Python. You create one per project. This maps loosely to how each Unreal project can pin its own Engine version and plugin versions in `.uproject`, rather than your entire machine being forced onto one global Engine install.

**pip** is Python's package installer — the tool that downloads and installs those packages (other people's pre-written, reusable code) into whichever environment is currently active.

## The details

### Step 1 — Install Python from python.org

Do not install Python from the Microsoft Store. It works for very basic use, but it has known quirks with the `py` launcher (covered below) and with where packages get installed, which cause confusing problems later in this course. Install directly from the official source instead.

1. Go to `https://www.python.org/downloads/` in your browser.
2. Click the big "Download Python 3.14.x" button (the site auto-detects Windows and offers the current stable release). **Verified for this lesson, August 2026: the current stable release is Python 3.14.7** (with Python 3.13.15 also actively maintained as the previous feature line, if you ever need it for compatibility with an older tool — you don't for this course). By the time you install, you'll likely see a slightly newer patch version (e.g. 3.14.8) — that's fine, this course doesn't depend on a specific patch release within the 3.14.x line.
3. Run the installer (`python-3.14.7-amd64.exe` or similar). On the very first screen:
   - **Check the box "Add python.exe to PATH"** at the bottom. This is the single most important checkbox in this entire lesson — skipping it is the #1 cause of `python: command not found` later. ("PATH" is the environment variable from Module 00 Lesson 01 that the shell searches to find programs by name.)
   - Click **"Install Now"** (the default/recommended option is fine — you don't need to customize anything for this course).
4. Let it finish, then close the installer.

### Step 2 — Understand `python` vs. `py` on Windows

Once installed, you actually have **two** ways to run Python from Git Bash:

- `python` — runs whichever Python the shell finds first by searching `PATH`, exactly like any other command (Module 00, Lesson 01).
- `py` — the **Python Launcher for Windows**, a small separate program that ships with the python.org installer specifically to solve "I have more than one Python version installed, which one actually runs?" `py` looks at all your installed python.org Python versions and picks the most recent one by default, and lets you target a specific one explicitly (e.g. `py -3.13`) without touching `PATH` at all.

For this course, with a single fresh install, `python` and `py` will behave identically — either works. This lesson standardizes on **`python`** for all commands, because it's the same command name Mac/Linux developers use (Module 00 already set you up to think "commands should transfer across operating systems" with Git Bash). If you ever install a second Python version later and `python` starts resolving to the wrong one, `py -3.14` is your escape hatch — see Troubleshooting below.

### Step 3 — Verify the interpreter and pip

Close and reopen Git Bash (PATH changes only apply to new terminal windows — you learned this the hard way, if at all, in Module 00).

```bash
python --version
```
**Expected output:** `Python 3.14.7` (or a newer 3.14.x patch).

```bash
pip --version
```
**Expected output:** something like `pip 25.x from C:\Users\YourName\AppData\...\site-packages\pip (python 3.14)`. `pip` is installed automatically alongside Python by the python.org installer — you don't install it separately.

### Step 4 — Create your first virtual environment

Pick (or create) a practice folder:

```bash
mkdir ~/python-practice
cd ~/python-practice
python -m venv .venv
```

**Line by line:**
- `python -m venv` — run the standard library module named `venv` as a program (`-m` means "run this installed module directly," rather than importing it from within another script).
- `.venv` — the name and location of the new environment. This exact name (a folder called `.venv`, with a leading dot) is the overwhelming community convention — VS Code's Python extension specifically looks for a folder with this name automatically. It's just a folder; nothing magic about the name itself except convention and tooling defaults.

**What just happened:** a new folder `.venv/` was created containing its own private copy of the Python interpreter (well — on Windows, small stub executables that point back at your real install, to save disk space) and its own empty package list, completely separate from any other project's `.venv`.

```bash
ls .venv
```
**Expected output:** folders including `Scripts/`, `Lib/`, and a file `pyvenv.cfg`. (On Mac/Linux this folder is called `bin/` instead of `Scripts/` — you'll see this exact name difference matter in a moment, and again if you ever work cross-platform.)

### Step 5 — Activate it (and understand what "activating" actually does)

```bash
source .venv/Scripts/activate
```

**Expected output:** your prompt changes to show `(.venv)` at the start, e.g. `(.venv) User@YOUR-PC MINGW64 ~/python-practice`.

**What "activating" actually does, mechanically:** it temporarily rewrites your current terminal session's `PATH` (Module 00, Lesson 01) so that `.venv/Scripts/` is searched *first* — meaning `python` and `pip` now resolve to the copies *inside* `.venv`, not your global install. It also sets an environment variable (`VIRTUAL_ENV`) some tools check. That `(.venv)` prefix in your prompt is Git Bash's way of reminding you an environment is active — it's easy to forget, and "why isn't my installed package being found" is very often "I'm not actually inside the venv I thought I was."

**A note specific to this course's shell:** the exact activation command differs by shell. Git Bash on Windows (what this course uses) needs `source .venv/Scripts/activate` — note the `Scripts` folder, with a capital S, and the fact that you `source` it. If you ever see a tutorial written for Mac/Linux bash, it'll say `source .venv/bin/activate` (`bin` instead of `Scripts`) — same idea, different folder name because that's just how Python's installer lays out files per OS. If you ever use plain Windows Command Prompt or PowerShell instead of Git Bash (this course doesn't, but you may encounter it at a job), the commands are `.venv\Scripts\activate.bat` and `.venv\Scripts\Activate.ps1` respectively — different syntax, same underlying idea.

Confirm it worked:

```bash
which python
```
**Expected output:** a path *inside* your project folder, ending in `.venv/Scripts/python`, not a global location like `/c/Users/YourName/AppData/Local/Programs/Python/...`. If you see the global path, activation didn't take — see Troubleshooting.

To leave the environment later:

```bash
deactivate
```
**Expected output:** the `(.venv)` prefix disappears from your prompt.

### Step 6 — Install a package with pip, and freeze it into requirements.txt

With `.venv` still active, install a small real package to see the whole loop:

```bash
pip install requests
```
**Expected output:** several lines ending in something like `Successfully installed requests-2.x.x ... `. `requests` is a widely-used real-world package for making HTTP calls (you'll meet HTTP properly in Module 02 — for now, it's just a convenient, real example package).

Now record exactly what's installed, so anyone else (including future-you, on a different machine) can recreate this exact environment:

```bash
pip freeze > requirements.txt
cat requirements.txt
```
**Expected output:** one or more lines like `requests==2.x.x` plus its own dependencies (packages `requests` itself needed), each pinned to an exact version. `pip freeze` prints every package currently installed *in the active environment*, in the exact `name==version` format `pip install -r` expects back.

To recreate this environment from scratch on another machine (or after deleting `.venv` to start clean):

```bash
pip install -r requirements.txt
```
`-r` means "read package names from this file instead of the command line." This is the exact mechanism that makes a Python project's dependencies reproducible — commit `requirements.txt` to Git (Module 00's skills), but **never commit `.venv/` itself** (it's large, platform-specific, and entirely regenerable from `requirements.txt` — this is exactly the kind of folder `.gitignore`, from Module 00 Lesson 03, exists for).

**A note on alternatives:** you'll sometimes hear about `pip-tools`, `Poetry`, or `uv` — newer tools that manage dependencies with extra features (lock files, faster installs, more precise reproducibility). They're genuinely good and increasingly popular in 2026, but this course deliberately sticks to the plain standard-library combination of `venv` + `pip` + `requirements.txt` throughout, because it's universal, requires no extra install, and teaches you the underlying mechanism every fancier tool is still built on top of. If you land at a job using Poetry or `uv`, everything you learn here about *why* isolation and pinning matter transfers directly — only the exact commands differ.

Clean up your practice package before moving on (optional, but tidy):

```bash
pip uninstall requests -y
pip freeze > requirements.txt
```

### Step 7 — Confirm VS Code's Python support

1. Open VS Code.
2. Go to the Extensions view (the four-squares icon on the left sidebar, or `Ctrl+Shift+X`).
3. Search for **Python** (publisher: Microsoft, extension ID `ms-python.python`). If it's not installed, click **Install**. Verified for this lesson (August 2026): the extension ships frequent monthly-ish updates (recent versions in the `2026.x` range) and now works alongside a companion **Python Environments** extension that Microsoft has been rolling environment/interpreter management into — VS Code will typically prompt you to install that companion extension automatically the first time you open a `.py` file. Accept that prompt.
4. Open your `python-practice` folder in VS Code (`File → Open Folder…`).
5. Open any `.py` file (create one if needed — see Verify your setup below). Look at the bottom-right status bar: it should show a Python version/interpreter name. Click it to see a list of detected interpreters — you should be able to pick the `.venv` one for this folder specifically (`.venv/Scripts/python.exe`), which is exactly why the `.venv` naming convention from Step 4 matters — VS Code looks for that name automatically.

## Verify your setup

Run each command in a **fresh** Git Bash window, inside `~/python-practice`, with `.venv` **not yet activated** (a clean starting point), then follow along:

```bash
python --version
```
**Expected:** `Python 3.14.7` (or newer 3.14.x).

```bash
cd ~/python-practice
source .venv/Scripts/activate
which python
```
**Expected:** the prompt shows `(.venv)`, and `which python` points inside `.venv/Scripts/`.

```bash
cat > hello.py << 'EOF'
print("Setup verified.")
EOF
python hello.py
```
**Expected output:** exactly `Setup verified.` printed to the terminal. (Recall the heredoc syntax, `<<'EOF' ... EOF`, from Module 00 Lesson 03 — it's writing these two lines into a new file called `hello.py` without opening an editor.)

```bash
pip --version
```
**Expected:** a version line mentioning `(python 3.14)` at the end, confirming `pip` matches the active venv's Python, not some other global install.

Open `hello.py` in VS Code and confirm: no red squiggly underlines, and the status bar in the bottom right shows an interpreter path containing `.venv`.

If every one of the above matches, your Python setup is ready for the rest of this module.

## Common mistakes & gotchas

- **`python: command not found` right after installing.** Almost always the "Add python.exe to PATH" checkbox was missed during install, or you're still using a terminal window opened *before* installing (PATH only reloads in new windows — same rule as Module 00). Fix: close every terminal completely, open a fresh one; if still broken, rerun the installer and confirm the checkbox, or use `py` instead, which python.org's installer registers separately from `PATH`.
- **`python` runs, but the version is way older than expected (e.g. `Python 2.7`).** This means some *other* Python (often one bundled with another tool, or a leftover old install) is earlier in `PATH` than your new one. Run `which python` to see exactly which file is running, and `where python` (works in Git Bash too, it's a Windows builtin) to list *every* `python.exe` PATH can find, in search order. The fix is either reordering PATH (advanced, not needed for this course) or simply always using `py` instead of `python`, since `py` ignores PATH entirely and always finds the newest python.org install.
- **You installed a package, but the script says `ModuleNotFoundError` anyway.** Check whether your venv is actually active (`(.venv)` in the prompt, or `which python` pointing inside `.venv`). It's very easy to `pip install` in one terminal tab with the venv active, then run your script in a *different* tab where you never activated it.
- **`source .venv/Scripts/activate` fails with "No such file or directory" in Git Bash.** Double-check capitalization and the folder name — on Windows it's `Scripts` (capital S), not `bin`. If you're following a Mac/Linux tutorial verbatim, it'll say `bin` and simply won't exist on your machine.
- **Multiple Python versions installed over time, and you're not sure which is "active."** Run `py --list` (or `py -0`) to see every python.org version installed and which one is the current default. This is exactly the scenario the `py` launcher exists for — don't try to solve version confusion by manually editing PATH.
- **Committing `.venv/` to Git by accident.** It's large (often 20+ MB), platform-specific, and fully regenerable from `requirements.txt`. Add a `.gitignore` (Module 00, Lesson 03) containing a line `.venv/` *before* your first commit in any Python project — exactly the same "set it up before you need it" lesson from Module 00's `.gitignore` exercise.

## How this connects

Every remaining lesson in this module assumes a working Python interpreter and, starting with Lesson 07 (Modules, Packages, and Virtual Environments), assumes you already understand *why* `venv` and `pip` exist — this lesson is the hands-on version of that concept; Lesson 07 goes deeper into modules/packages themselves. The capstone project (`project/BRIEF.md`) is built and run entirely inside a venv you set up exactly this way. Starting in Module 05 (FastAPI), every backend project in this course begins with these exact same three commands: `python -m venv .venv`, activate, `pip install -r requirements.txt`.

## Quick self-check

1. What's the difference between the Python *language* and the Python *interpreter*?
2. Why does each project get its own virtual environment instead of installing packages globally once?
3. What does "activating" a virtual environment actually change, mechanically?
4. On this course's shell (Git Bash on Windows), what's the exact command to activate a venv named `.venv`, and how does that differ from the Mac/Linux version?
5. What's the difference between `pip install requests` and `pip install -r requirements.txt`?
