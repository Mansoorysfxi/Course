# Lesson 01 — The Shell and the Filesystem

## What you'll learn

- What a "shell" actually is, and how it differs from a "terminal" and a "console."
- How to navigate your filesystem entirely with typed commands (no mouse).
- How to create, move, copy, rename, and delete files and folders from the command line.
- What environment variables are, and specifically what `PATH` is and why `command not found` errors happen.
- How to chain and redirect commands (pipes and redirection) at a beginner level.

## Why this matters

Every tool you'll use for the rest of this course — Python, Node.js, Git,
Docker, deployment tools — is operated primarily through a shell, not a
GUI. Professional developers live in the terminal because it's faster,
scriptable, and works identically on your laptop and on a remote server
with no screen at all (which is exactly what you'll be deploying to in
Phase 3). If you can't navigate a filesystem by typing, you can't do the
rest of this course efficiently — you'd be constantly context-switching to
File Explorer, which doesn't even work once you're on a remote Linux server
with no graphical interface.

## Prerequisites

Lesson 00 (Setup) — you need Git Bash installed and open.

## The concept, explained simply

A **shell** is a program that reads text you type, interprets it as a
command, runs it, and prints the result. That's it — it's a program whose
entire job is to run other programs based on typed instructions, the same
way Unreal's in-editor console (the one you open with the tilde key `~`
in-game, or the "Output Log" with command input) lets you type `stat fps`
or `travel MapName` and something happens. A **terminal** (sometimes called
a "console" or "terminal emulator") is the *window* that displays text and
lets you type — it's just the display/input surface. The shell is the
program running *inside* that window interpreting what you type. Git Bash
is both: it's a terminal window running a shell called **bash** (Bourne
Again SHell — the name is a historical joke, don't worry about it).

Your filesystem — the folders and files on your hard drive — normally you
navigate by double-clicking folders in File Explorer. The shell gives you
the exact same access, but via typed commands. Every command below is just
a program (yes, `cd`, `ls`, etc. are tiny built-in programs) that the shell
runs for you.

## The details

### The prompt, and where you are

Open Git Bash. You'll see something like:

```
User@YOUR-PC MINGW64 ~
$
```

That `~` is a **path** — it's telling you *where you currently are* in the
filesystem, the same way "you are here" works on a map. `~` is shorthand
for your **home directory** (on Windows, something like
`C:\Users\YourName`). Everything you type happens relative to "where you
currently are," called your **working directory** (or "current directory").

Type this and press Enter:

```bash
pwd
```

**Expected output:** something like `/c/Users/YourName` — `pwd` stands for
"print working directory." Notice it's shown Linux-style (forward slashes,
`/c/` instead of `C:\`) — Git Bash translates Windows paths into this
Linux-style format internally, which is one reason commands you learn here
transfer directly to Mac/Linux/servers later.

### Listing what's around you

```bash
ls
```

**Expected output:** a list of files/folders in your current directory —
compare it against what File Explorer shows you for the same folder; it
should match.

**Try it yourself:** run `ls -la` and compare the output to plain `ls`.
Before running it, predict: what do you think the extra letters `l` and `a`
might do? (Answer: `-l` = "long format," showing permissions, size, and
modified date per item; `-a` = "all," including hidden files — files/folders
whose name starts with a dot, like `.git`, which are hidden from normal
`ls` and from File Explorer by default.)

### Moving around: `cd`

```bash
cd Desktop
pwd
```

**Expected output:** your path now ends in `.../Desktop`. `cd` stands for
"change directory." You just moved from your home directory into
`Desktop`, a subfolder of it — this is a **relative path** (relative to
where you already were).

Go back:

```bash
cd ..
pwd
```

**Expected output:** you're back in your home directory. `..` always means
"the parent of the current folder" — one level up. This works no matter how
deep you are.

**Try it yourself:** from your home directory, predict what `cd ../..`
would do before running it, then try it. (It moves up two levels — each
`..` separated by `/` is one more level up.)

Two more special shortcuts:

```bash
cd ~     # jump straight to your home directory, from anywhere
cd /c    # jump to the root of your C: drive (an absolute path)
```

The difference between `Desktop` (relative — depends on where you started)
and `/c/Users/YourName/Desktop` (**absolute** — always means the same
folder no matter where you ran it from) matters a lot once you start
writing scripts and config files that reference paths.

### Creating things

```bash
mkdir shell-practice
cd shell-practice
```

`mkdir` = "make directory." You just created a new folder and moved into
it. Now create a file:

```bash
touch notes.txt
ls
```

**Expected output:** `notes.txt` appears in the listing. `touch` is a
slightly odd name for what it does here — historically it just updates a
file's "last modified" timestamp, but if the file doesn't exist yet, that
forces it to be created empty first. It's the fastest way to make an empty
file from the command line.

Put some actual content into it without opening an editor:

```bash
echo "hello from the shell" > notes.txt
cat notes.txt
```

**Expected output:** `hello from the shell` printed by `cat`.

**Line by line:**
- `echo "hello from the shell"` — prints that exact text to the screen (try
  it alone, with no `>`, to see this).
- `>` — this is **redirection**. Instead of letting `echo`'s output go to
  your screen, it redirects it *into* a file, overwriting whatever was
  there. If `notes.txt` didn't exist, `>` creates it.
- `cat notes.txt` — `cat` (short for "concatenate") prints a file's
  contents to the screen. It's the fastest way to peek inside a small text
  file without opening an editor.

**Try it yourself:** run `echo "second line" >> notes.txt` (note: two `>`
characters this time) then `cat notes.txt` again. Predict the result before
running it. (`>>` *appends* instead of overwriting — you should see both
lines now.)

### Moving, copying, renaming, deleting

```bash
cp notes.txt notes-backup.txt
ls
```
`cp` = copy. You now have two files with the same content.

```bash
mv notes-backup.txt archive.txt
ls
```
`mv` = move — but it's *also* how you rename things, since "rename" is just
"move to a new name in the same place." No separate `rename` command exists
in bash for this reason.

```bash
rm archive.txt
ls
```
`rm` = remove/delete. **There is no undo and no Recycle Bin for this.** This
is one of the biggest differences from File Explorer — deleting via `rm` is
permanent immediately. Always double check the filename before pressing
Enter on an `rm` command, especially ones using wildcards (see below).

To delete a whole folder (not just a file):

```bash
cd ..
mkdir throwaway-folder
rm -r throwaway-folder
```
`-r` means "recursive" — delete this folder *and everything inside it*.
Without `-r`, plain `rm` refuses to delete folders at all, as a safety
check.

### Wildcards

```bash
cd shell-practice
touch report1.txt report2.txt report3.txt image.png
ls *.txt
```
**Expected output:** only the three `.txt` files listed, not `image.png`.
`*` means "match anything." `*.txt` means "anything, followed by `.txt`" —
this pattern (called a **glob**) works with most commands, including `rm`
— meaning `rm *.txt` would delete all three text files at once. Be
deliberately careful with wildcards and `rm` together; there's no confirmation
prompt.

### Environment variables and `PATH`

An **environment variable** is a named piece of text data that the shell
(and every program it launches) can read — think of it as a small set of
global settings available to every program you run, similar to how project
settings in Unreal are available to every system in the game rather than
being passed around by hand everywhere.

See one:

```bash
echo $HOME
```
**Expected output:** your home directory path. The `$` before a name means
"substitute the *value* of this variable here" rather than the literal text
`HOME`.

The single most important environment variable for a developer is `PATH`.
View it:

```bash
echo $PATH
```

**Expected output:** a long line of folder paths separated by colons (`:`).
This is the answer to a question you'll ask constantly: **"how does the
shell know what program to run when I type a name like `git` or `code`?"**
When you type a command, the shell searches every folder listed in `PATH`,
in order, looking for a program with that name. The moment it finds one, it
runs it and stops looking.

This explains the single most common beginner error in this entire course:

```
bash: some-command: command not found
```

This means: *the shell searched every folder in `PATH` and found nothing
named `some-command`.* The fix is always one of:
1. The program genuinely isn't installed — install it.
2. It's installed, but its folder was never added to `PATH` — you need to
   add it (Lesson 00's troubleshooting section covers this for VS Code/Git
   specifically).
3. It's installed and *is* in `PATH`, but you opened this terminal *before*
   installing it — `PATH` is loaded once when the terminal starts.
   Fix: close the terminal completely and open a new one.

**Try it yourself:** run `echo $PATH` and count how many folders are listed
(split by `:`). Then run `which git` — this tells you the *exact* folder
bash found `git` in, i.e., which entry in `PATH` matched.

### Pipes — connecting commands together

A **pipe**, written `|`, takes the output of one command and feeds it in as
the *input* of the next command, instead of printing it to the screen.

```bash
ls -la | wc -l
```
`wc -l` counts lines of input ("word count, lines mode"). Piped together,
this counts how many files/folders are in your current directory
(including the header line `ls -la` prints, so it's off by one/two, but you
get the idea of chaining). You'll use pipes constantly once you get into
logs and command output filtering in later modules — this is just the
introduction.

## Common mistakes & gotchas

- **Typing Windows-style paths (`C:\Users\...`) into Git Bash.** Bash uses
  forward slashes (`/c/Users/...`). Backslash has a special meaning in bash
  (it's an "escape character"), so pasting a Windows path directly often
  breaks. Git Bash is usually smart enough to auto-convert simple cases, but
  when it's not, convert `C:\Users\Name` to `/c/Users/Name` by hand.
- **Spaces in folder/file names without quotes.** `cd My Folder` breaks
  because bash thinks `My` and `Folder` are two separate arguments. Fix:
  quote it — `cd "My Folder"`. This is a very common early error.
- **Case sensitivity confusion.** Git itself is case-sensitive about
  filenames even though Windows' filesystem often isn't. `Notes.txt` and
  `notes.txt` can look "the same" to Windows but are different files to
  Git — this causes confusing bugs later; the fix is just to be consistent
  about casing.
- **Using `rm -r` carelessly.** Always run `ls` first inside a folder you're
  about to `rm -r`, to double check what's actually in there.
- **Forgetting that `PATH` only reloads when you open a new terminal.**
  If you install something and it's "not found," the very first
  troubleshooting step is always: close every terminal window, open a fresh
  one, try again.

## How this connects

Every command you learned here — `cd`, `ls`, `mkdir`, `cat`, `rm`, pipes —
is exactly what you'll use to move around Git repositories (Lessons 03–05),
run Python scripts (Module 01), start servers (Module 05 onward), and
eventually operate a real remote Linux server with no GUI at all (Module
09). `PATH` specifically comes back constantly — every "command not found"
error you'll ever hit in this course traces back to the concept from this
lesson.

## Quick self-check

1. What's the difference between a terminal and a shell?
2. What does `cd ..` do, and how is that different from `cd ~`?
3. You run `some-tool --version` and get `command not found` — name two
   different root causes and how you'd check which one it is.
4. What does the `>` operator do differently from `>>`?
5. If `ls` shows `data.txt` but not `.env`, why not, and what flag would
   show it?
