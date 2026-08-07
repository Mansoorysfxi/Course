# Lesson 03 — systemd and Services

**Verified against (August 2026), via live web search:** `systemd` unit
file syntax and directive names shown here (`[Unit]`, `[Service]`,
`[Install]`, `After=`, `Wants=`, `Type=`, `Restart=`, `WantedBy=`) are
confirmed current and unchanged against `systemd`'s own documentation and
multiple current (2026) guides — this is stable, mature infrastructure;
the specific detail double-checked for this lesson is that
`Restart=on-failure` remains the officially recommended restart policy
for long-running services (per `systemd`'s own docs), and that
`After=` controls *ordering only*, not an actual dependency — a
frequently-misunderstood distinction confirmed directly against current
guidance and called out explicitly below.

## What you'll learn

- What `systemd` is and the actual problem it solves.
- What a **unit file** is, and how to write one from scratch, line by
  line.
- The core `systemctl` commands: `start`, `stop`, `restart`, `status`,
  `enable`, `disable`.
- How to read a running service's logs with `journalctl`.
- How `Restart=` makes a crashed process come back automatically — and
  why that specific behavior is exactly what QuestLog's backend needs on
  a real server.

## Why this matters

Right now, running QuestLog's backend means typing
`uvicorn app.main:app --reload` in a terminal you have to keep open. Close
that terminal (or lose your SSH connection to a real server, or reboot
the machine) and the backend is gone until someone manually retypes that
command. That's fine for local development — it's completely unacceptable
for a real server nobody's watching around the clock. `systemd` is what
turns "a command someone has to remember to type" into "a **service**"
— something the operating system itself starts automatically on boot,
restarts automatically if it crashes, and lets you control with a
consistent set of commands, exactly like every other program already
running on the machine (including SSH's own server from Lesson 02).

## Prerequisites

- `lessons/00-setup.md`'s Step 3 — `systemd` must actually be enabled in
  your WSL2 Ubuntu instance, or none of this lesson's commands will work
  (confirm again now: `ps --pid 1 -o comm=` should print `systemd`).
- `lessons/01-linux-processes-and-permissions.md` — processes, `sudo`,
  file permissions, and `kill`/signals, all used directly below.

## The concept, explained simply

Think of `systemd` as the Linux equivalent of a **dedicated game server
host's process supervisor** — the layer that watches over your actual
game server executable and automatically relaunches it if it crashes,
rather than leaving a dead server silently offline until a human notices
and manually restarts it. `systemd` is Ubuntu's (and most modern Linux
distributions') **init system**: the very first process the kernel
starts at boot (always **PID 1**, per Lesson 01), responsible for
starting every other background program the system needs — networking,
SSH, logging, and any application you tell it about — in the right
order, and for supervising all of them for as long as the machine is
running. A **unit file** is a small, plain-text configuration file that
describes one specific thing `systemd` should manage — most relevantly
for this module, a **service**: one long-running program, like
QuestLog's Uvicorn process.

## The details

### Step 1 — A toy program worth supervising

Create a tiny, deliberately long-running Python script to practice on —
no FastAPI, no dependencies, just something that behaves like a "server"
for the purpose of this lesson: it runs forever, printing a heartbeat,
until something stops it.

```bash
mkdir -p ~/systemd-practice
nano ~/systemd-practice/heartbeat.py
```

```python
import time

count = 0
while True:
    count += 1
    print(f"heartbeat #{count}", flush=True)
    time.sleep(2)
```

**Line by line:** an infinite `while True` loop — this program never
exits on its own, exactly like a real web server waiting for requests
forever. `flush=True` forces `print` to write immediately instead of
Python's default output buffering, so `journalctl` (Step 4) shows each
line the moment it's printed, not in delayed batches — genuinely
necessary here because Python buffers stdout differently when it's not
attached to an interactive terminal (exactly the situation a
`systemd`-managed process is always in). `time.sleep(2)` pauses two
seconds between beats so the output is readable instead of scrolling
instantly.

Confirm it runs (then stop it with `Ctrl+C` — you're about to hand this
job to `systemd` instead):

```bash
python3 ~/systemd-practice/heartbeat.py
```
**Expected:** `heartbeat #1`, `heartbeat #2`, ... printing every 2
seconds, forever, until `Ctrl+C`.

### Step 2 — Write a real unit file

Unit files that manage system-wide services live in
`/etc/systemd/system/`. Create one:

```bash
sudo nano /etc/systemd/system/heartbeat.service
```

```ini
[Unit]
Description=Toy heartbeat service for Module 09 practice
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/yourname/systemd-practice/heartbeat.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

(Replace `yourname` with your actual username — `whoami` if unsure;
unit files need a full, **absolute** path, never `~`, since `systemd`
doesn't run this the way an interactive shell does and has no concept of
"your home directory" to expand `~` against.)

**Section by section, directive by directive:**

- **`[Unit]`** — general metadata and ordering, not specific to this
  being a *service* particularly.
  - `Description=` — a free-text label shown by `systemctl status` and
    in logs. Purely for humans; has no functional effect.
  - `After=network.target` — an **ordering** rule: if this unit starts at
    all, make sure basic networking is already up first. **This is not a
    dependency** — `After=` alone does not make `network.target` start
    *because of* this file; it only controls the order *if* both happen
    to be starting anyway (which, for a unit enabled via
    `WantedBy=multi-user.target` below, they will be, at every normal
    boot). QuestLog's real service (the capstone) additionally needs
    `After=postgresql.service`, since the backend talking to a database
    that isn't listening yet would just crash and restart-loop uselessly
    until Postgres caught up.
- **`[Service]`** — how to actually run and manage the program itself.
  - `Type=simple` — tells `systemd` "the command in `ExecStart` *is* the
    long-running process itself; don't wait for it to fork or signal
    readiness some other way" — the correct type for a plain, foreground
    long-running program like this script, or like Uvicorn.
  - `ExecStart=` — the **exact** command `systemd` runs to start this
    service. Must be an absolute path to the program (`/usr/bin/python3`
    — confirm yours with `which python3`) and an absolute path to the
    script.
  - `Restart=on-failure` — **the single most important line in this
    entire lesson.** If the process exits with a *non-zero* (failure)
    exit code, or is killed by a signal, `systemd` automatically starts
    it again. (`Restart=always` would also restart it even after a
    clean, intentional exit — `on-failure` is the generally-recommended
    choice for a service that should only come back from a genuine
    crash, not from someone deliberately stopping it, which
    `systemctl stop` still respects either way.)
  - `RestartSec=3` — wait 3 seconds before each restart attempt, instead
    of instantly — avoiding a tight crash-restart-crash loop from
    hammering the CPU or, for a real app, hammering a database connection
    that's already struggling.
- **`[Install]`** — controls what happens when this unit is **enabled**
  (Step 4).
  - `WantedBy=multi-user.target` — the standard choice for almost any
    server-side service: `multi-user.target` is the normal, fully-booted,
    everything-running state a real server reaches after startup
    (roughly equivalent to the old concept of "runlevel 3" on older Unix
    systems, for anyone who's encountered that term) — meaning "start
    this service automatically once the system has fully booted to its
    normal running state."

### Step 3 — Load, start, and inspect the service

Unit files aren't picked up automatically the instant you save them —
tell `systemd` to re-read its configuration:

```bash
sudo systemctl daemon-reload
```
**Expected:** no output at all on success — silence is success here.

Now start it:

```bash
sudo systemctl start heartbeat
```
**Expected:** no output (again, silence = success). Confirm it's
actually running:

```bash
sudo systemctl status heartbeat
```
**Expected output (abbreviated):**
```
● heartbeat.service - Toy heartbeat service for Module 09 practice
     Loaded: loaded (/etc/systemd/system/heartbeat.service; disabled; ...)
     Active: active (running) since ...; 5s ago
   Main PID: 8842 (python3)
      Tasks: 1
     Memory: 8.9M
        CPU: 15ms
     CGroup: /system.slice/heartbeat.service
             └─8842 /usr/bin/python3 /home/yourname/systemd-practice/heartbeat.py
```
The green `●` and `Active: active (running)` confirm success. Notice
**`Main PID: 8842`** — this is Lesson 01's PID concept again: `systemd`
is tracking this exact running process by its PID, the same identifier
`ps aux` would show you for it. `disabled` next to `Loaded:` means it
won't yet auto-start on boot — that's Step 5. Press `q` if this opened a
pager.

### Step 4 — Watch it crash and come back on its own

Prove `Restart=on-failure` actually works by killing the process
directly, bypassing `systemctl` entirely (simulating a real crash, not a
deliberate stop):

```bash
sudo systemctl status heartbeat   # note the Main PID number
sudo kill -9 <THAT_PID>
sleep 4
sudo systemctl status heartbeat
```

**Expected:** the second `status` call shows `Active: active (running)`
again, with a **different** `Main PID` than before, and
`Active: active (running) since ...` showing a very recent timestamp —
proof `systemd` genuinely noticed the process died and restarted it
automatically, entirely on its own, within the `RestartSec=3` window you
configured. This exact mechanism — "if the process dies unexpectedly,
bring it back within a few seconds" — is precisely why a real server
runs its backend as a `systemd` service instead of a bare terminal
command: no human has to notice and restart it.

**Try it yourself:** compare this against stopping it deliberately —
`sudo systemctl stop heartbeat`, then `sudo systemctl status heartbeat`.
Does it come back on its own this time? Why not, given
`Restart=on-failure`?

### Step 5 — `enable`, so it survives a reboot too

`start` runs it *now*; it says nothing about what happens after a
reboot. `enable` is the separate step that wires the `[Install]`
section's `WantedBy=` into actually happening at boot time:

```bash
sudo systemctl enable heartbeat
```
**Expected output:**
```
Created symlink /etc/systemd/system/multi-user.target.wants/heartbeat.service → /etc/systemd/system/heartbeat.service.
```
**What actually happened:** `enable` created a **symbolic link** (a
filesystem shortcut) inside `multi-user.target.wants/`, a folder
`systemd` checks every time it reaches that target (i.e., every normal
boot) for units it should start. This is the entire mechanism behind
"`WantedBy=multi-user.target` means start on boot" — there's no hidden
magic, just a symlink in a folder `systemd` scans. `disable` removes
exactly that same symlink and nothing else, leaving the actual unit file
untouched (confirm: `sudo systemctl disable heartbeat`, then
`ls /etc/systemd/system/multi-user.target.wants/ | grep heartbeat`
prints nothing).

### Step 6 — Reading logs with `journalctl`

Every service `systemd` manages has its stdout/stderr captured
automatically — no manual log file setup needed:

```bash
sudo systemctl enable --now heartbeat   # --now: enable AND start in one command
journalctl -u heartbeat -n 20
```
**Line by line:** `-u heartbeat` filters to just this one unit's logs
(`journalctl` with no arguments shows the *entire system's* combined
log, which is almost never what you want). `-n 20` shows only the most
recent 20 lines, instead of the entire history. **Expected:** a series of
lines like:
```
Aug 07 10:32:01 YOURHOST python3[9012]: heartbeat #1
Aug 07 10:32:03 YOURHOST python3[9012]: heartbeat #2
```
**Try it yourself:** run `journalctl -u heartbeat -f` (`-f` = "follow,"
like `tail -f` from any prior module that used it) and watch new
heartbeat lines appear live, in real time, without re-running the
command. `Ctrl+C` to stop following. This exact command, pointed at
QuestLog's own real service name, is how you'll watch the backend's own
logs live on the actual capstone server.

### Cleanup

```bash
sudo systemctl disable --now heartbeat
sudo rm /etc/systemd/system/heartbeat.service
sudo systemctl daemon-reload
```

## Common mistakes & gotchas

- **Editing a unit file, then running `systemctl restart`, and seeing no
  change at all.** You forgot `sudo systemctl daemon-reload` — `systemd`
  caches the unit files it already parsed and does **not** automatically
  notice a file changed on disk; every edit to a `.service` file needs a
  `daemon-reload` before it takes effect at all, even for a service
  that's already running.
- **`status` shows `Active: failed` immediately after `start`.** The
  command in `ExecStart` itself is failing — almost always a wrong
  absolute path (a relative path, a `~`, or a typo), a missing
  executable, or (for a real app like QuestLog) a missing environment
  variable the program needs to even start. `journalctl -u <name> -n 50`
  shows the actual error the program printed before dying — always check
  this first, rather than guessing.
- **Using `Type=simple` for a program that daemonizes itself (forks into
  the background and exits its original process immediately).**
  `systemd` would think the service already "exited" and, depending on
  `Restart=`, either mark it failed or restart-loop it, even though the
  real, forked-off process is still healthily running in the background.
  This lesson's heartbeat script and QuestLog's Uvicorn process are both
  correctly `Type=simple` because neither forks — they run directly in
  the foreground of the process `systemd` started, which is exactly what
  `Type=simple` expects.
- **Confusing `After=` with an actual dependency.** As this lesson's
  header states, `After=` only affects *ordering*, not whether the other
  unit starts at all. If a service genuinely cannot function without
  another one running (QuestLog's backend without Postgres), pairing
  `After=` with `Wants=` (a soft dependency — "try to start this too, but
  don't hard-fail if it can't") is the standard, current pattern; the
  capstone's real unit file (Lesson 07) uses exactly this pair.
- **Forgetting `enable` and being surprised the service is gone after a
  reboot.** `start` alone is temporary, for the current boot session
  only — a genuinely common point of confusion, since the service can
  run correctly for hours or days before a reboot finally reveals the
  missing `enable`.

## How this connects

Lesson 04 shifts from "how does a program run" to "how is a running
program actually reached over a network" — the natural next question
once QuestLog's backend is a properly supervised service instead of a
terminal command. Lessons 07–08 (the capstone) write a real unit file for
QuestLog's Uvicorn process, using every directive from this lesson,
plus the `Wants=`/`After=` pairing with `postgresql.service` mentioned
above.

## Quick self-check

1. What is `systemd`, and what specific problem does running QuestLog as
   a `systemd` service solve that `uvicorn app.main:app --reload` in a
   plain terminal doesn't?
2. What's the difference between `systemctl start` and
   `systemctl enable`, precisely — what does each one actually cause to
   happen, mechanically?
3. Why doesn't editing a `.service` file take effect until you run
   `sudo systemctl daemon-reload`?
4. What does `After=` actually guarantee, and — just as importantly —
   what does it *not* guarantee?
5. If `sudo systemctl status myservice` shows `Active: failed`
   immediately after starting it, what's the very first command you
   should run to find out why, and what is it actually showing you?
