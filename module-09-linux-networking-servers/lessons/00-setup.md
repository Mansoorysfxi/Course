# Lesson 00 — Setup: A Real Linux Environment, and (Optionally) a Real Server

**Verified against (August 2026), via live web search — see each bullet
for the source:**

| Fact | Verified value | Source |
|---|---|---|
| Current Ubuntu LTS releases | **24.04 LTS "Noble Numbat"** (April 2024, supported to 2029 with ESM) and **26.04 LTS "Resolute Raccoon"** (released April 23, 2026) both exist and are current | Canonical's own release announcement and `ubuntu.com/about/release-cycle` |
| This course's chosen target | **Ubuntu 24.04 LTS** — see "Why 24.04, not the newer 26.04" below | — |
| A concrete, currently-cheap VPS example | **Hetzner Cloud, plan CX22** — 2 shared vCPU, 4 GB RAM, 40 GB NVMe SSD, ≈€4.35/mo (≈$4.59/mo) | Hetzner's own pricing pages and third-party trackers (`vpsfor.dev`, `bestusavps.com`), cross-checked August 2026 |
| Windows SSH client | `ssh.exe`, part of **OpenSSH Client**, built into Windows 10 (since build 1809) and Windows 11 by default | Microsoft Learn, `learn.microsoft.com/windows-server/administration/openssh` |
| WSL2 `systemd` support | Officially supported since WSL version **0.67.6** (September 2022); enabled via `/etc/wsl.conf` | Microsoft's WSL documentation and the original Windows Command Line devblog announcement |

Prices change; provider names are not an endorsement, they're this
module's one concrete, currently-real example so the module isn't vague.
Any Ubuntu-based VPS from any provider (DigitalOcean, Vultr, Linode/
Akamai, and others all sell a similarly-priced small Ubuntu box) works
identically for everything this module teaches — the commands you'll run
are standard Ubuntu/Nginx/systemd commands, not anything specific to
Hetzner.

## Do you need to pay for a VPS to do this module?

**No, not to read the lessons or do Exercises 01–05.** Every one of those
uses a **WSL2 Ubuntu instance** running locally on your own Windows
machine — completely free, and you almost certainly already have it from
earlier modules. **Yes, if you want to literally execute the capstone**
(`project/BRIEF.md` — deploying QuestLog somewhere reachable from outside
your own machine) **for real.** The entire point of a capstone deploy is
putting QuestLog on a machine that isn't yours, reachable by anyone with
its IP address — WSL2 cannot do that (it lives inside your own Windows
machine, behind your home router's own private network, exactly like the
private-vs-public IP distinction Lesson 04 explains). If you'd rather not
spend money right now, read Lessons 07–08 and `project/BRIEF.md`
carefully anyway — they're written as a complete, honest, followable
runbook you can come back and execute later, whenever you do rent a box.

## What you'll learn

- How to confirm WSL2 is installed and working (re-verifying Module 00's
  setup, per Rule 8 — never assume an earlier module's tool is still
  configured).
- How to enable `systemd` inside your WSL2 Ubuntu instance specifically —
  it is **not** on by default, and this module's `systemd` lesson and
  exercise genuinely need it.
- How to confirm Windows' built-in SSH client works, so Lesson 02's key
  generation and later, real, remote logins work from a plain PowerShell
  or Windows Terminal window — no extra software to install.
- If you're choosing to rent a real VPS: what a reasonable, currently-
  cheap choice looks like, and the handful of account-level decisions
  (region, OS image, SSH key) every provider's signup flow asks for.

## Why this matters

Every lesson from here on assumes you have a real, working Linux shell
to type commands into — not a mental simulation, an actual `bash` prompt
where `ls`, `ps`, `chmod`, and eventually `systemctl` and `ufw` really
run and really do something. Module 00 already got you a Linux
environment (WSL2) for tools like Git Bash; this lesson goes one step
further and turns on the one WSL2 feature (`systemd`) that was off by
default because most day-to-day coding doesn't need it — this module
specifically does.

## Prerequisites

- **Module 00** — WSL2 installed, a terminal you're comfortable in. This
  lesson re-verifies WSL2 works rather than teaches installing it from
  scratch; if `wsl --version` below fails entirely, go back to Module
  00's own setup lesson first.
- No new programming-language tooling is required this module — no new
  Python packages, no new npm packages. This module is entirely about
  the operating system and the network underneath the code you already
  know how to write.

## The concept, explained simply

Think of the difference between **WSL2** and a **real VPS** the way
you'd think about the difference between **Play-in-Editor (PIE)** and a
**dedicated build running on a real server** in Unreal: PIE runs inside
your own editor, on your own machine, and is perfect for iterating fast
— but nobody outside your machine can connect to it, because it was
never built to be reached from anywhere else. A real dedicated server
build, running on an actual machine with its own network address, is
what a player anywhere in the world can actually connect to. WSL2 is
this module's "PIE": a completely real Ubuntu Linux system, running real
`bash`, real `systemd`, real `ufw` — everything you'll learn behaves
identically — but it lives inside your Windows machine's own private
network, invisible to the outside internet by design. A VPS is the
"real dedicated server build": the exact same Ubuntu, the exact same
commands, but sitting on a machine with a public IP address anyone can
reach.

## The details

### Step 1 — Re-verify WSL2 itself

Open PowerShell (not WSL — plain Windows PowerShell) and run:

```powershell
wsl --version
```

**Expected output (versions will differ slightly, that's fine):**
```
WSL version: 2.x.x.x
Kernel version: 5.15.x.x
WSLg version: 1.0.x
MSRDC version: 1.2.x
Direct3D version: 1.611.x
DXCore version: 10.0.x
Windows version: 10.0.26200.x
```

If this command isn't recognized at all, WSL was never installed —
return to `module-00-developer-environment-and-tooling/lessons/`'s own
setup lesson before continuing here.

**Try it yourself:** run `wsl -l -v` (list installed distros and their
WSL version). You should see `Ubuntu` listed with `VERSION` showing `2`.
If it shows `1`, run `wsl --set-version Ubuntu 2` and wait for it to
convert (this can take several minutes) — every command in this module
assumes WSL**2**, not WSL1, because only WSL2 runs a real Linux kernel
capable of `systemd`.

### Step 2 — Enter your Ubuntu shell

```powershell
wsl -d Ubuntu
```

**Expected:** your prompt changes to something like
`yourname@YOURPC:~$` — you are now inside a real Ubuntu Linux system.
Confirm which Ubuntu version:

```bash
lsb_release -a
```

**Expected output (abbreviated):**
```
Distributor ID: Ubuntu
Description:    Ubuntu 24.04.x LTS
Release:        24.04
Codename:       noble
```

**If yours shows a different version** (e.g. `22.04`), that's fine for
everything except a few exact `apt` package version numbers this module
mentions — the commands themselves are identical across recent Ubuntu
LTS releases. If you'd like to match this module exactly, Microsoft
Store's "Ubuntu 24.04 LTS" app installs this specific version
side-by-side with any existing `Ubuntu` distro.

### Step 3 — Enable `systemd` in WSL2

By default, WSL2's Ubuntu does **not** run `systemd` as its process
manager (WSL historically used a much lighter, non-`systemd` init
process to start faster) — but real Ubuntu servers, including every VPS
you'd ever rent, always run `systemd`, and Lesson 03 and Exercise 03
genuinely need it here too. Turn it on:

```bash
sudo nano /etc/wsl.conf
```

(`nano` is a simple terminal text editor — Module 00 introduced it
alongside VS Code; if the file doesn't exist yet, `nano` creates it.) Add
exactly these lines:

```ini
[boot]
systemd=true
```

Save and exit (`Ctrl+O`, `Enter`, then `Ctrl+X` in `nano`). Back in
**PowerShell** (not inside WSL — this restart command has to run from
Windows):

```powershell
wsl --shutdown
```

**Expected:** no output, and after a few seconds every open WSL window
closes (this fully restarts the Linux VM WSL2 runs, which is required
for `/etc/wsl.conf` changes to take effect — editing this file while WSL
is still running has no effect until the next start). Reopen your Ubuntu
shell (`wsl -d Ubuntu`) and confirm:

```bash
ps --pid 1 -o comm=
```

**Expected:** `systemd` — meaning PID 1 (Lesson 01 explains exactly what
this means) is now `systemd` itself, not the lightweight `init` process
WSL2 used before. If this instead prints something like `init`,
`/etc/wsl.conf` wasn't picked up — re-check Step 3's file for typos
(`[boot]` on its own line, `systemd=true` beneath it, no stray
indentation) and re-run `wsl --shutdown`.

### Step 4 — Confirm Windows' built-in SSH client

Windows 10 (build 1809+) and Windows 11 both ship a real OpenSSH client
already installed — no download needed. Confirm, from **PowerShell**:

```powershell
ssh -V
```

**Expected output (version numbers will vary):**
```
OpenSSH_for_Windows_9.x, LibreSSL 3.x.x
```

**If this says "ssh is not recognized"** (rare on a current Windows 11
install, but possible on a heavily locked-down machine): open
**Settings → System → Optional Features**, search for "OpenSSH Client,"
and install it — it's a Windows feature, not a separate download from
the internet.

### Step 5 — Decide about a real VPS now, or later

If you want to execute this module's capstone live right away, this is
the point to actually create one. This module doesn't require any one
specific provider — the steps in Lessons 07–08 are written to work
against any fresh Ubuntu 24.04 server from any host. As one concrete,
currently-priced example (verified August 2026, prices change — check
the provider's own pricing page before paying):

**Hetzner Cloud, plan CX22:** 2 shared vCPU, 4 GB RAM, 40 GB NVMe SSD,
20 TB traffic included, ≈€4.35/mo (≈$4.59/mo, billed hourly if you
destroy it early — a few hours of testing costs a fraction of a cent).
Signup flow, in outline (every provider's flow looks roughly like this):

1. Create an account, add a payment method.
2. "Create Server" / "Create Droplet" (wording varies by provider).
3. **Image:** choose **Ubuntu 24.04 LTS** (to match this module exactly
   — see "Why 24.04" below).
4. **Type/plan:** the cheapest general-purpose tier (CX22 on Hetzner, or
   the equivalent "Basic"/entry tier elsewhere).
5. **Authentication:** choose **SSH key**, not a root password, and
   paste in the *public* key Lesson 02 has you generate. (If your
   provider's UI forces you to pick this before you've read Lesson 02,
   it's fine to generate the key first — Lesson 02 comes right after
   this setup lesson, before the capstone needs a server at all.)
6. **Region:** whichever is geographically closest to you — it only
   affects latency, nothing this module teaches depends on which one.
7. Create it. The provider emails or displays the server's **public IP
   address** — write it down; every capstone command in Lessons 07–08
   refers to it as `<YOUR_SERVER_IP>`.

**You do not need to do this right now.** Nothing until `project/BRIEF.md`
requires a running server to exist.

## Why 24.04, not the newer 26.04

Ubuntu 26.04 LTS ("Resolute Raccoon") is real and current — it was
released April 23, 2026, a few months before this lesson was written,
and every major cloud provider already offers it as an image. This
course still standardizes on **24.04 LTS** for three concrete reasons,
consistent with Rule 7's instruction to verify and then make an honest,
stated choice rather than default to "newest":

1. **Maturity of the ecosystem around it.** 24.04 has been in general
   use for over two years by the time of this writing; the overwhelming
   majority of tutorials, Stack Overflow answers, and `apt` package
   combinations you'll encounter while troubleshooting a real problem
   are written against it. 26.04, being a few months old, has far less
   of that accumulated real-world troubleshooting history yet.
2. **This course's earlier modules already assume it.** Module 06's
   PostgreSQL setup lesson and other Linux-adjacent references were
   written and verified against 24.04-era package versions.
3. **The commands themselves don't meaningfully differ.** Every command
   in this module (`apt`, `systemctl`, `ufw`, `ssh-keygen`) works
   identically on 26.04. If you already have (or end up with) a 26.04
   server, nothing in this module should require translation — this is
   stated here for honesty, not because it would break anything.

If you specifically want to practice on 26.04 instead, that's a
completely reasonable choice — just expect exact package version numbers
quoted in later lessons (e.g. Nginx's `apt` version) to differ slightly.

## Verify your setup

Run every command below, inside your WSL2 Ubuntu shell unless marked
otherwise, and confirm your output matches:

```powershell
# In PowerShell:
wsl --version
```
**Expected:** version info, no error (Step 1).

```powershell
ssh -V
```
**Expected:** an `OpenSSH_for_Windows_...` line (Step 4).

```bash
# In WSL2 Ubuntu:
lsb_release -a
```
**Expected:** `Description: Ubuntu 24.04.x LTS` (or your chosen version — Step 2).

```bash
ps --pid 1 -o comm=
```
**Expected:** `systemd` (Step 3 — this is the one most learners get wrong
the first time; if it says anything else, `/etc/wsl.conf` wasn't applied).

```bash
systemctl status
```
**Expected:** a screen starting with `● YOURHOST` and `State: running`
(press `q` to exit the pager). If this errors with `System has not been
booted with systemd as init system`, Step 3 didn't take effect — go back
and re-check it.

If every command above matches, you have a real, `systemd`-enabled Linux
shell and a working SSH client, and you're ready for Lesson 01.

## Common mistakes & gotchas

- **`ps --pid 1 -o comm=` still shows `init`, not `systemd`, after editing
  `/etc/wsl.conf`.** The single most common cause: `wsl --shutdown` was
  run from *inside* a WSL terminal instead of from PowerShell/Command
  Prompt. `wsl --shutdown` has to come from the Windows side, because
  it's shutting down the entire WSL2 virtual machine your Linux shell is
  running inside — a command run from inside that VM can't shut down the
  VM it's currently running in (the same reason you can't uninstall an
  app in Unreal's editor from a Blueprint that app is currently running).
- **`/etc/wsl.conf` edits "don't matter" even after a proper
  `wsl --shutdown`.** Check for a stray typo — `[boot]` must be alone on
  its own line, exactly as written, and `systemd=true` must be
  underneath it, not on the same line. INI-format files like this are
  whitespace- and section-header-sensitive.
- **`sudo nano /etc/wsl.conf` says "command not found" for `nano`.** A
  minimal WSL Ubuntu image occasionally lacks it. Install it:
  `sudo apt update && sudo apt install -y nano` (Lesson 01 explains
  exactly what `apt` and `sudo` are doing here, if either is unfamiliar
  — for now, just run it).
- **PowerShell's `ssh -V` opens Git Bash's SSH instead of Windows'
  built-in one, or vice versa, and behaves unexpectedly.** If you
  installed Git for Windows (Module 00), it bundles its *own* copy of
  OpenSSH, and depending on your `PATH` order, `ssh` might resolve to
  that copy instead of `C:\Windows\System32\OpenSSH\ssh.exe`. Both work
  fine for this module — check which one you're using with (PowerShell):
  `Get-Command ssh` — and don't be surprised if the version number in
  Step 4 doesn't exactly match "OpenSSH_for_Windows" if Git's copy came
  first on `PATH`. Either is acceptable; this module's commands are
  standard OpenSSH syntax, not specific to one bundling of it.
- **A newly created VPS ignores the SSH key you pasted in and only
  offers a password (or none at all).** Some providers only apply an
  uploaded SSH key at *first boot*/creation time — if you added the key
  to your account *after* creating the server, it may not have been
  injected into it. Destroy and recreate the server (a fresh $4–6/mo box
  costs essentially nothing to redo within the first few minutes) with
  the key already selected during creation, or use the provider's
  console/rescue-mode SSH-key-injection tool if it has one.

## How this connects

Lesson 01 starts using this exact WSL2 shell immediately — every `ps`,
`chmod`, and `ls -l` command in that lesson runs here. The `systemd` you
just turned on is what Lesson 03 and Exercise 03 use to run a real
service. The SSH client you just confirmed is what Lesson 02 uses to
generate a key pair and what the capstone (Lessons 07–08) uses to
actually log into a real remote server, if you choose to rent one.

## Quick self-check

1. What's the practical difference between WSL2 and a real VPS, in terms
   of what each one is reachable *from*?
2. Why does `wsl --shutdown` have to be run from PowerShell instead of
   from inside the WSL2 Ubuntu shell itself?
3. Why doesn't WSL2 run `systemd` by default, and what file turns it on?
4. Why does this course standardize on Ubuntu 24.04 LTS instead of the
   newer 26.04 LTS, even though both are current, supported releases as
   of this writing?
5. Is a real VPS required to complete Exercises 01–05 in this module? Which part of this module does genuinely require one?
