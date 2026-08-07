# Lesson 01 — Linux Processes and Permissions

**Verified against (August 2026):** `ps`, `chmod`, `chown`, `sudo`, and
`apt` syntax shown here is standard POSIX/Debian-family behavior,
unchanged for many years and confirmed current against Ubuntu 24.04's
own manual pages (`man ps`, `man chmod`, `man sudo`, `man apt`) — this is
mature, stable Unix material, not a fast-moving area, so this lesson
notes that explicitly rather than manufacturing a false sense of
"verified this week" precision that wouldn't mean much here.

## What you'll learn

- What a **process** actually is on Linux, how it relates to the program
  you compiled or wrote, and how to inspect running processes with `ps`
  and `top`.
- What a **PID** is and why it matters for controlling a specific running
  program.
- The Linux **permissions** model: users, groups, the `rwx` bits, and how
  to read a permissions string like `-rwxr-xr-x` at a glance.
- `chmod` and `chown` — changing what a file allows and who owns it.
- `sudo` and the **root** user — what "administrator" actually means on
  Linux, and why running everything as root is a real, serious mistake.
- **Package managers**, specifically `apt` — what a package manager is
  for, and how it differs from `pip`/`npm`, which you already know.

## Why this matters

Every later lesson in this module assumes you can look at a running
Linux system and answer basic questions about it: "is my backend process
actually running?", "why can't this program read that file?", "why does
this command say 'permission denied'?" Once QuestLog's backend is
running on a real server (Lessons 07–08), it is a **process** like any
other, its files have **permissions** like any other, and you'll
routinely need `sudo` to manage it. None of the later material makes
sense without this foundation.

## Prerequisites

- `lessons/00-setup.md` — a working, `systemd`-enabled WSL2 Ubuntu shell.
- Module 00's shell basics (`cd`, `ls`, `pwd`) — this lesson builds
  directly on those, adding new commands rather than re-teaching the
  shell itself.

## The concept, explained simply

In Unreal, when you hit Play, the engine spins up a running **instance**
of your game — with its own memory, its own current state, distinct from
the `.uproject` file and source code sitting on disk. Stop it, and that
instance is gone; the source files on disk are untouched. A Linux
**process** is exactly this idea, generalized to every single running
program on the machine, not just games: it's one specific, currently-
executing instance of a program, with its own private memory, its own
current state, completely separate from the program's file on disk. You
can have the exact same program (say, `python`) running as five
completely independent processes at once, the same way you could run
five separate instances of the same compiled game executable — each one
its own process, unaware of the others' memory.

**Permissions** are the Linux equivalent of access specifiers in C++
(`public`/`protected`/`private`), but applied to *files* instead of class
members, and checked by the *operating system* instead of the compiler.
Just as `private` doesn't stop a determined enough person from getting at
your class's internals (via reflection, memory hacking, whatever), Linux
permissions aren't unbreakable security — they're the OS's normal,
everyday gatekeeper deciding which *user accounts* may read, write, or
execute a given file, checked on every single file access, by the kernel
itself.

## The details

### Processes: what they are, how to see them

Every time you type a command, or every time `systemd` starts a service
(Lesson 03), Linux creates a new process. Try it — run a command that
takes a few seconds, in one WSL2 terminal:

```bash
sleep 60
```

`sleep 60` does exactly one thing: waits 60 seconds, then exits. While
it's running, open a **second** WSL2 terminal window (`wsl -d Ubuntu`
again) and run:

```bash
ps aux | grep sleep
```

**Expected output (yours will have different numbers):**
```
yourname   4821  0.0  0.0   2892  1536 pts/0    S+   14:02   0:00 sleep 60
yourname   4830  0.0  0.0   6408  2176 pts/1    S+   14:02   0:00 grep --color=auto sleep
```

**Line by line, what `ps aux` shows for the first line:**
- `yourname` — the **user** who owns this process (whoever ran the
  command).
- `4821` — the **PID (Process ID)**: a unique number the kernel assigns
  to every running process, the moment it starts. No two processes
  running at the same time ever share a PID. This is how you tell Linux
  *exactly which* running instance you mean when you want to inspect or
  stop one — the same way an Unreal `AActor*` pointer unambiguously
  identifies one specific spawned actor even if ten identical Blueprint
  instances exist in the level at once.
- `0.0` (twice) — percentage of CPU and memory currently used.
- `S+` — the process's current **state** (`S` = sleeping/waiting, the
  `+` means it's in the foreground of its terminal). A process that's
  actively using the CPU right now shows `R` (running); Lesson 03
  revisits process states when a `systemd` service misbehaves.
- `sleep 60` — the actual command line that started this process.

`ps aux`'s flags: `a` = show processes for all users, not just yours; `u`
= show the more detailed, human-readable columns above; `x` = also show
processes not attached to a terminal at all (like most `systemd`
services). The `| grep sleep` part is Module 00's pipe operator, filtering
`ps aux`'s full output (which lists *every* process on the system — try
running plain `ps aux` with nothing piped, and scroll) down to just the
line(s) containing "sleep".

**Try it yourself:** while `sleep 60` is still running in your first
terminal, run `ps aux | grep sleep` again from the second terminal a few
times, a couple seconds apart. What (if anything) about the output
changes between runs, and why does the PID specifically *never* change
between them?

### Stopping a process by PID: `kill`

Now stop that `sleep 60` early, from the *second* terminal, using the
PID you saw above (yours will differ from this example's `4821`):

```bash
kill 4821
```

**Expected:** switch back to the first terminal — it returns to your
prompt immediately, instead of waiting out the rest of the 60 seconds.
`kill`, despite its name, doesn't have to be violent — by default it
sends a polite request (a **signal** called `SIGTERM`, "please terminate
yourself when convenient") that a well-behaved program can catch and use
to shut down cleanly (save state, close files, etc.) before exiting.
`kill -9 <PID>` sends `SIGKILL` instead — an immediate, un-catchable,
un-ignorable termination, useful only when a process is well and truly
stuck and won't respond to the polite version. This exact distinction
matters again in Lesson 03: `systemd` sends `SIGTERM` first when stopping
a service, and only escalates to `SIGKILL` if the process doesn't exit
within a timeout.

### `top` — watching everything at once

`ps aux` is a single snapshot. `top` is a live, continuously refreshing
view of every process, sorted by CPU usage by default:

```bash
top
```

**Expected:** a full-screen, auto-refreshing table. The top few lines
summarize overall CPU/memory usage; below that is a live, sortable
process list — the closest Linux equivalent to Windows' Task Manager
"Details" tab. Press `q` to quit back to your prompt.

**Try it yourself:** with `top` open, open a third terminal and run
`sleep 30 &` (the trailing `&` runs it in the **background**, so that
terminal gets its prompt back immediately instead of waiting). Watch it
briefly appear in `top`'s list, then disappear again once the 30 seconds
elapse.

### Permissions: reading `ls -l`'s output

Run this inside your WSL2 home directory:

```bash
cd ~
touch example.txt
ls -l example.txt
```

**Expected output (your username/date will differ):**
```
-rw-r--r-- 1 yourname yourname 0 Aug  7 10:00 example.txt
```

**Breaking down `-rw-r--r--` character by character:**
- **Position 1** (`-`): file *type* — `-` means a plain file, `d` would
  mean a directory, `l` would mean a symbolic link (a shortcut).
- **Positions 2–4** (`rw-`): permissions for the file's **owner**
  (`r` = read, `w` = write, `-` = no execute permission here).
- **Positions 5–7** (`r--`): permissions for the file's **group** (a
  named set of users — every user belongs to at least one).
- **Positions 8–10** (`r--`): permissions for **everyone else** on the
  system.

So `-rw-r--r--` reads as: "a plain file; the owner can read and write it;
the owner's group can only read it; everyone else can only read it. No
one can execute it." Then `1 yourname yourname` shows a link count
(ignore this for now) followed by the file's **owner** and **group**,
both `yourname` here because that's who created it.

**What "execute" means for a file vs. a directory** is a genuinely
common point of confusion: for a plain file, the execute bit means "this
file may be run as a program/script." For a **directory**, execute
instead means "you may `cd` into this directory or access files inside
it by name" — a directory's *read* bit only lets you *list* its
contents (`ls`), while its *execute* bit is what actually lets you enter
it or open a specific file inside it whose name you already know. This
is why you'll occasionally see a directory permission like `drwx------`
(only the owner can enter it at all) even though its contents show up
fine to that owner in `ls`.

### `chmod` — changing permissions

Make `example.txt` executable for its owner only:

```bash
chmod u+x example.txt
ls -l example.txt
```

**Expected:**
```
-rwxr--r-- 1 yourname yourname 0 Aug  7 10:00 example.txt
```

**Line by line:** `chmod` (change mode) takes a target (`u` = user/owner,
`g` = group, `o` = others, `a` = all three) plus an operation (`+` = add,
`-` = remove, `=` = set exactly) plus which permission (`r`, `w`, `x`).
`u+x` reads as "add execute for the owner." You'll also very commonly see
**numeric** (octal) mode, which this module's `systemd`/deploy lessons
use directly — each `rwx` triplet maps to one digit, adding up `r=4`,
`w=2`, `x=1`:

```bash
chmod 644 example.txt
ls -l example.txt
```
**Expected:** back to `-rw-r--r--` — `6` = `4+2` = `rw-` (owner), `4` =
`r--` (group), `4` = `r--` (others). `chmod 600 example.txt` would give
`-rw-------` — owner-only read/write, no access for anyone else at all;
you'll use exactly this mode on a real server for anything holding a
secret (an SSH private key, a `.env` file with a database password —
Lesson 02 and the capstone both do this for real).

**Try it yourself:** predict what `chmod 755 example.txt` produces as an
`ls -l` string *before* running it, then check.

### `chown` — changing ownership

`chown` changes who owns a file — you'll use this on a real server
because your app's files need to be owned by a dedicated, non-root
service account (the capstone creates one), not by whatever admin user
you happened to log in as:

```bash
sudo chown yourname:yourname example.txt
```
(Replace `yourname` with your actual username — check it with `whoami`
if unsure.) This one is a no-op here since you already own the file —
the syntax (`chown newowner:newgroup path`) is what matters; the
capstone runs this for real against files owned by `root` that a
dedicated `questlog` service account needs to run.

### `sudo` and the root user

Linux has one special user, **`root`** (UID — user ID — `0`), that
bypasses the permission checks above entirely — root can read, write, or
delete literally any file on the system, and configure anything about
the machine itself. This is necessary (someone has to be able to install
system software, manage other users' accounts, configure the firewall)
but also genuinely dangerous: a typo while logged in *as* root has no
safety net at all. `sudo` ("superuser do") is the standard, safer
alternative: instead of logging in as root directly, you log in as your
normal, permission-limited user, and prefix any *specific command* that
genuinely needs root's power with `sudo`, re-entering your own password
to confirm:

```bash
sudo whoami
```
**Expected:** `root` — for that one command only, you ran as root; your
normal shell prompt is still your regular user immediately afterward.
This "elevate for one command, then drop back down" pattern is why
almost every command this module uses that touches system-level state
(`apt install`, editing `/etc/` files, managing `systemd` services,
configuring `ufw`) is prefixed with `sudo` — and why a command failing
with `Permission denied` (with no `sudo`) is one of the single most
common errors you'll hit from here through the rest of this module.

### Package managers: `apt`

You already know two package managers deeply: `pip` (Module 01, Python
packages) and `npm` (Module 03, JavaScript packages). Both install
*libraries your own code imports*, scoped to one project. **`apt`**
("Advanced Package Tool") is Ubuntu/Debian's **system-level** package
manager: it installs entire *programs* (Nginx, PostgreSQL, `nano`) for
the whole machine to use, tracks which files belong to which installed
program, and knows how to cleanly remove them again. Two commands you'll
run constantly from here on:

```bash
sudo apt update
```
**Expected output (abbreviated):** several lines like
`Get:1 http://archive.ubuntu.com/ubuntu noble InRelease [...]`, ending in
something like `Reading package lists... Done`. **Line by line:** this
does **not** install or upgrade anything yet — it downloads the current
*list* of available packages and their latest versions from Ubuntu's
package servers, so `apt` knows what's currently available. Skipping
this before installing something can mean installing a stale, out-of-
date version, or `apt` not finding a package at all.

```bash
sudo apt install -y nano
```
**Expected output (abbreviated):** `nano` is already the newest version
(if Lesson 00 already had you install it), or a short download-and-
install sequence ending in `Setting up nano (...) ...`. **Line by line:**
`install` is the subcommand; `-y` auto-answers "yes" to apt's "Do you
want to continue? [Y/n]" confirmation prompt (safe here because you
already know exactly what you're installing); `nano` is the package
name. Lessons 03–08 use `sudo apt install` repeatedly — PostgreSQL,
Nginx, and every other system-level program this module needs all
install this exact way.

## Common mistakes & gotchas

- **`Permission denied` on a command that touches system files or
  services.** Missing `sudo`. This is overwhelmingly the most common
  error beginners hit in this entire module — if a command's own
  documentation shows `sudo` in front of it and you left it off, this is
  the result.
- **`sudo: command not found` after a fresh `apt install` of something
  that should have added a command.** `apt update` wasn't run first (or
  wasn't run recently), so `apt` tried to install from a stale package
  list and may have silently failed to find the right version, or the
  install itself genuinely failed a few lines up in output you scrolled
  past — always check for `E:` lines in `apt`'s output, which mark real
  errors.
- **Confusing a process's PID with the number of CPU cores, or with a
  port number** — these are three completely unrelated numbers that all
  happen to be small integers. A PID identifies one running program
  instance; Lesson 04 introduces ports, a completely separate concept
  (which network "door" a program is listening on).
- **Expecting `chmod +x somefile.py` alone to let you run it with just
  `somefile.py`.** Making a script executable is necessary but not
  sufficient on its own for `./somefile.py` (note the `./`) to work
  without it — you also need a correct **shebang** line
  (`#!/usr/bin/env python3`) at the very top of the file telling the
  kernel which interpreter to run it with. Without a shebang, `./file.py`
  fails even with execute permission set; running it explicitly as
  `python3 somefile.py` sidesteps needing execute permission or a
  shebang at all, because you're not asking the kernel to execute the
  file directly.
- **Running literally everything with `sudo` "just in case it fixes the
  error."** This is a real, common bad habit, not just a style nitpick:
  files created as root become owned by root, and a normal user then
  can't modify or even delete them without *also* using `sudo` from then
  on — a self-inflicted mess this lesson's `chown` section exists partly
  to let you clean up. Use `sudo` only for the specific commands that
  genuinely need it (installing packages, managing services, editing
  files under `/etc/`), never as a reflexive fix for an unrelated error.

## How this connects

Lesson 02 uses everything here immediately: SSH keys are files, and
their permissions (a private key must be `600`, readable by no one but
its owner, or SSH will flatly refuse to use it) are enforced exactly the
way this lesson just explained. Lesson 03's `systemd` services run as a
specific *user* (this lesson's concept) and their unit files live in
directories with specific permissions. The capstone (Lessons 07–08)
creates a dedicated, non-root `questlog` user specifically so the app's
own process never runs with root's unlimited power — a real security
practice this lesson's "why running everything as root is a mistake"
point sets up directly.

## Quick self-check

1. What is a PID, and why can two completely different commands never share one at the same time?
2. Given `-rwxr-x---`, who can execute this file, and who can't read it at all?
3. What does the execute permission bit mean for a *directory*, as opposed to a plain file — and why is that different from what you might guess?
4. Why is running every command as `root` (instead of using `sudo` selectively) a genuinely bad habit, not just poor style?
5. What's the difference between what `pip`/`npm` install versus what `apt` installs?
