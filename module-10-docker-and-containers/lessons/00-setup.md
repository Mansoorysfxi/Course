# Lesson 00 — Setup: Docker Desktop, WSL2, and Verifying Both Actually Work

**Verified against (August 2026), via live web search — see each row for
the source:**

| Fact | Verified value | Source |
|---|---|---|
| Current Docker Desktop version | **4.85.0**, released **August 3, 2026** | `docs.docker.com/desktop/release-notes/` (fetched directly) |
| Docker Compose CLI | `docker compose` (Compose **V2**, a Go-based plugin built directly into the Docker CLI/Desktop) is current and correct; the old standalone, hyphenated `docker-compose` (Compose **V1**, Python-based) is deprecated — Docker now only patches high-severity vulnerabilities/critical bugs in it | Docker's own blog ("Docker Compose: What's New, What's Changing, What's Next") and `docs.docker.com` |
| Compose file `version:` key | Obsolete/ignored since Compose V2's general availability (2022); Docker's own current documentation recommends removing it entirely | `docs.docker.com/reference/compose-file/legacy-versions/`, cross-checked against multiple 2026 sources |
| Windows requirement | Docker Desktop's WSL2 backend requires WSL2 itself (re-verified below) and hardware virtualization enabled in BIOS/UEFI; works on Windows 11 Home, Pro, Enterprise, and Education editions alike (the WSL2 backend removed the older Hyper-V-only Pro/Enterprise requirement) | Docker's own system requirements documentation, cross-checked August 2026 |
| WSL integration UI path | **Docker Desktop → Settings → Resources → WSL Integration** — a toggle for "Enable integration with my default WSL distro," plus a per-distro toggle list (e.g. `Ubuntu`) | Docker's own documentation and multiple current (2026) setup guides |

Every fact above was checked with a live web search or direct fetch of
Docker's own documentation while writing this lesson, not recalled from
memory — this is exactly the kind of fast-moving installation procedure
Rule 7 exists for: Docker Desktop ships new versions roughly monthly, and
its own settings UI has moved around across major versions before.

## What you'll learn

- What Docker Desktop actually is, and why this course installs it
  instead of "just Docker" directly on Windows.
- How to install Docker Desktop with the WSL2 backend, and exactly what
  "WSL2 backend" means (you already have WSL2 from Module 00/09 — this
  lesson re-verifies it, per Rule 8, rather than assuming it's still
  fine).
- How to turn on WSL integration for your Ubuntu distro specifically.
- How to verify, with exact commands and exact expected output, that
  Docker itself, Docker Compose, and the WSL2 integration are all
  genuinely working before Lesson 01 asks you to run anything.
- The specific, real failure modes this exact setup hits most often, and
  how to fix each one.

## Why this matters

Every single lesson and exercise from here on assumes a working `docker`
command and a working `docker compose` command in a terminal. Module 09
deployed QuestLog by hand, one `apt install`, one `systemctl`, one `psql`
command at a time — direct, real, and, as that module's own README puts
it, deliberately painful. Everything in this module packages that same
kind of work into portable, reproducible container images — but none of
that is possible without Docker itself actually installed and running
first. Get this exactly right now, once, and every later lesson in this
module just works.

## Prerequisites

- **Module 00** — WSL2 already installed (`wsl --version` should already
  succeed on your machine).
- **Module 09** — a working WSL2 Ubuntu distro, ideally the same one you
  used for that module's exercises. This lesson **does not assume it
  still works correctly** — Rule 8 is explicit that no earlier module's
  setup should be assumed to still be fine, and Step 1 below re-verifies
  it from scratch.
- Comfort with PowerShell and a Linux shell (both used throughout this
  lesson).
- Administrator access on your Windows machine (installing Docker
  Desktop requires it).

## The concept, explained simply

Recall Lesson 00's Unreal analogy from Module 09: WSL2 is like
Play-in-Editor (PIE) — a completely real Linux system, but living inside
your own machine, invisible from outside it. Docker takes that idea one
step further, inside that same Linux system: instead of one whole,
shared Ubuntu environment where every tool you install (Postgres, Nginx,
a specific Python version) permanently changes that one shared machine
the way Module 09's manual deploy did, Docker lets you spin up
completely isolated, disposable mini-environments — containers — each
with only the exact software one specific job needs, each throwaway,
each reproducible from a text file (a Dockerfile) instead of a
memory of "which commands did I run, in which order, six weeks ago?"

**Docker Desktop**, specifically, is the Windows (and macOS) packaging
of Docker: it runs the real Docker Engine (the background service that
actually builds images and runs containers) inside a small, dedicated
Linux VM under the hood, and gives you a `docker` command in PowerShell,
Command Prompt, or any WSL2 shell, that talks to it. On Windows, the
modern, recommended way to run that Linux VM is to reuse WSL2 itself —
this is what "WSL2 backend" means: Docker Desktop doesn't need its own,
separate virtualization technology, because WSL2 already provides a
real, lightweight Linux kernel Docker can run containers inside of
directly. This is also why Docker commands you type inside your Ubuntu
WSL2 shell and Docker commands you type inside plain Windows PowerShell
both work identically and see the same containers — they're both
talking to the exact same Docker Engine, just from two different
terminal front doors.

## The details

### Step 1 — Re-verify WSL2 itself (never assume an earlier module's setup is still fine)

Open **PowerShell** (not WSL):

```powershell
wsl --version
```

**Expected output** (version numbers will differ slightly — what matters
is that this succeeds at all, with no "not recognized" error):
```
WSL version: 2.x.x.x
Kernel version: 5.15.x.x
WSLg version: 1.0.x
...
```

```powershell
wsl -l -v
```

**Expected:** a table listing `Ubuntu` (or whichever distro name Module
09 used) with a `VERSION` column showing `2`. If WSL itself is missing
or broken, stop here and revisit
`module-00-developer-environment-and-tooling/lessons/`'s own setup
lesson before continuing.

### Step 2 — Check virtualization is enabled (BIOS/UEFI)

Docker Desktop's WSL2 backend needs hardware virtualization turned on at
the BIOS/UEFI level — a setting entirely outside Windows itself, on the
motherboard's own firmware. Most machines ship with it already on, but
it's occasionally disabled by a system administrator's image or a BIOS
reset. Check from PowerShell:

```powershell
Get-ComputerInfo -Property "HyperVRequirementVirtualizationFirmwareEnabled"
```

**Expected:** `HyperVRequirementVirtualizationFirmwareEnabled : True`.
If this shows `False`, you'll need to reboot into your BIOS/UEFI setup
(the exact key varies by manufacturer — commonly `Del`, `F2`, or `F10`
during boot) and enable a setting usually named **Intel VT-x**, **AMD-V**,
or simply **Virtualization Technology**. This is the single most common
reason Docker Desktop fails to start at all on a machine that otherwise
looks correctly configured.

### Step 3 — Install Docker Desktop

Download Docker Desktop for Windows from `docker.com/products/docker-desktop/`
(the current version, per this lesson's header, is **4.85.0** — the
installer always fetches the current release regardless of this
lesson's exact number, so don't worry if yours differs slightly by the
time you read this; just note it here alongside this lesson's other
verified facts, per Rule 7). Run the installer. When prompted, **ensure
"Use WSL 2 instead of Hyper-V" is checked** — this is the default on a
current installer, but worth confirming explicitly since this is exactly
the setting this whole lesson is about. Accept the reboot it asks for if
one is needed.

After reboot, Docker Desktop should start automatically (a whale icon
appears in your system tray). If it doesn't, launch it from the Start
menu. The first launch can take a minute or two while it finishes
initializing its own internal Linux VM.

### Step 4 — Enable WSL integration for your Ubuntu distro

Open Docker Desktop's own window and navigate to:

**Settings → Resources → WSL Integration**

**Expected:** a toggle labeled "Enable integration with my default WSL
distro," and, below it, a per-distro list including your `Ubuntu`
install with its own toggle. Turn both on if they aren't already, then
click **Apply & Restart**.

**Why this step exists, specifically:** Docker Desktop's Engine runs
inside its *own* internal, hidden Linux VM by default — WSL integration
is what additionally makes the `docker` command available *inside* your
own, separate Ubuntu WSL2 distro too (the one Module 09 already set up
and enabled `systemd` inside), so every command in this module's lessons
works whether you're sitting in a plain PowerShell window or inside your
Ubuntu shell. Without this step, `docker` would work fine from
PowerShell/Command Prompt but say `command not found` inside your
Ubuntu WSL2 shell specifically.

### Step 5 — Confirm the Docker daemon is actually running

From **either** PowerShell or your WSL2 Ubuntu shell (pick whichever
you plan to use for the rest of this module — this course uses the WSL2
Ubuntu shell throughout, for consistency with Module 09):

```bash
docker info
```

**Expected:** a long block of output describing your Docker
installation — server version, number of containers, storage driver,
etc. — with no `Cannot connect to the Docker daemon` error anywhere near
the top. If you see that error specifically, Docker Desktop itself isn't
running yet — see this lesson's troubleshooting section.

## Verify your setup

Run every command below and confirm your output matches (all from your
WSL2 Ubuntu shell unless marked otherwise, matching this course's
convention since Module 09):

```bash
docker --version
```
**Expected:** something like `Docker version 28.x.x, build xxxxxxx`
(exact numbers will differ; what matters is no error).

```bash
docker compose version
```
**Expected:** `Docker Compose version v2.x.x`. **Note the space, not a
hyphen** — this course uses `docker compose` (Compose V2, built into
Docker CLI) throughout, never the old standalone `docker-compose`
binary. If typing `docker-compose` (hyphenated) on your machine still
happens to work, that's a separate, legacy binary some systems still
have installed alongside the current plugin — this course's own
commands never use it, and you shouldn't need it either.

```bash
docker run hello-world
```
**Expected**, the first time you run this (Docker has to download the
tiny `hello-world` image first):
```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```
This one command is a genuinely complete, real proof that every piece
works together: your `docker` CLI reached Docker Engine, Engine reached
Docker Hub (a **container registry** — Lesson 02 explains this term) over
the internet, downloaded a real container image, and successfully ran it
as a container. Run it a **second** time:

```bash
docker run hello-world
```
**Expected:** the exact same `Hello from Docker!` message, but **without**
the `Unable to find image` / `Pulling from library/hello-world` lines
this time — proof Docker cached the image locally the first time and
didn't need to download it again. This is your very first hands-on look
at a recurring theme this whole module returns to: Docker aggressively
caches anything it's already done, and reuses that cached result whenever
it safely can.

```bash
docker ps -a
```
**Expected:** a table with one row, showing the `hello-world` container
you just ran twice (or two rows, one per run — either is fine), each
with a `STATUS` of `Exited (0)` — a container whose one job was printing
that message and exiting; `Exited (0)` specifically means it finished
successfully (Lesson 01 explains exit codes and container lifecycle in
full).

If every command above matches, Docker Desktop, the WSL2 backend, WSL
integration, and Docker Compose are all confirmed working, and you're
ready for Lesson 01.

**Try it yourself:** in Docker Desktop's Settings → Resources → WSL
Integration, turn **off** the toggle for your specific Ubuntu distro
(leave the "Enable integration with my default WSL distro" master switch
alone), click Apply & Restart, then try `docker ps` again from inside
your WSL2 Ubuntu shell. **Predict, before doing this**, exactly what
error you'll see and why — then confirm, and turn the toggle back on
before continuing to Lesson 01.

## Common mistakes & gotchas

- **`Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
  Is the docker daemon running?`** — Docker Desktop itself isn't
  running. Check your system tray for the whale icon; if it's missing,
  launch Docker Desktop from the Start menu and wait for it to finish
  starting (the whale icon stops animating once it's ready).
- **`docker: command not found` inside your WSL2 Ubuntu shell, but
  `docker --version` works fine from PowerShell.** WSL integration
  (Step 4) isn't enabled for your specific distro — open Docker
  Desktop's Settings → Resources → WSL Integration and check that your
  distro's own toggle (not just the "default distro" toggle) is on,
  then Apply & Restart.
- **Docker Desktop won't start at all, or shows a virtualization-related
  error on launch.** Almost always Step 2 (BIOS virtualization) — go
  back and confirm `HyperVRequirementVirtualizationFirmwareEnabled` is
  `True`. A less common second cause: WSL2 itself needs updating —
  `wsl --update` from PowerShell, then `wsl --shutdown`, then try
  launching Docker Desktop again.
- **`docker run hello-world` hangs indefinitely trying to pull the
  image, with no error.** Almost always a network/firewall/proxy issue
  reaching Docker Hub specifically — if you're on a corporate or
  school network, check whether it blocks outbound Docker Hub traffic;
  a personal home network essentially never has this problem.
- **"Bind for 0.0.0.0:8000 failed: port is already allocated" (or
  similar), the first time this module's later lessons ask you to run a
  container publishing a port Module 09 also used.** Module 09's
  `uvicorn`, `npm run dev`, or a real Postgres/Nginx install may still
  be running in the background from that module's own work, holding
  onto the exact port (`8000`, `5173`, `5432`, `80`) a new container in
  *this* module now also wants. Find and stop the old process first:
  ```bash
  # Linux/WSL2 -- find whatever is listening on, e.g., port 8000:
  sudo ss -tlnp | grep 8000
  # Then stop that specific process (Module 09, Lesson 01, covers `kill` in full).
  ```
  This is a real, common gotcha specifically because this course keeps
  every module's `project/questlog/` around side by side — nothing
  automatically stops a previous module's long-running dev server for
  you.
- **`docker compose version` says `docker-compose: command not found`
  (hyphenated) — but `docker compose version` (space) works fine.**
  This is expected and correct on a current Docker Desktop install — the
  hyphenated binary is the old, separate, deprecated Compose V1, which a
  fresh Docker Desktop install has no reason to include at all. Every
  command in this module uses the space form; if you see a tutorial
  elsewhere using the hyphenated form, mentally translate it (nearly
  always a direct, one-for-one substitution — see Lesson 06 for the one
  or two real syntax differences that occasionally matter).

## How this connects

Every remaining lesson in this module assumes the exact setup this
lesson just verified: a working `docker` command, a working
`docker compose` command, and WSL integration enabled for the Ubuntu
distro this course has used since Module 00. Lesson 01 runs your first
real container beyond `hello-world` and explains, precisely, what a
container actually is under the hood.

## Quick self-check

1. What specifically does "Docker Desktop's WSL2 backend" mean — what is
   WSL2 actually providing to Docker Desktop, mechanically?
2. Why does WSL integration need to be enabled *per distro*, separately
   from Docker Desktop simply being installed and running?
3. If `docker run hello-world` succeeds the first time with a
   "Pulling from library/hello-world" message, but the second run shows
   no such message, what changed between the two runs, and where is
   that change stored?
4. Why might a container fail to start with a "port is already
   allocated" error specifically in this course, given how earlier
   modules' project code is kept around?
5. What's the difference between `docker-compose` (hyphenated) and
   `docker compose` (space), and which one does this course use, and why?
