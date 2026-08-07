# Lesson 01 — The Problem Containers Solve, Containers vs. VMs, and Your First Real Container

**Verified against (August 2026):** this lesson's core technical claims
(what a Linux namespace and cgroup actually are, how a container differs
from a VM) are stable kernel/OS concepts, not fast-moving version-specific
facts — no single "current version" to pin here. The specific commands
and their output were run against Docker Desktop 4.85.0 / Docker Engine
(Lesson 00's verified versions) while writing this lesson.

## What you'll learn

- The concrete, real problem containers were built to solve — "works on
  my machine" — and why Module 09's manual deploy makes that problem
  viscerally obvious.
- The actual, non-magical mechanism that makes a container a container:
  Linux namespaces and cgroups, explained at a conceptual level.
- The real, structural difference between a container and a virtual
  machine — not just "containers are lighter," but *why* they're
  lighter.
- How to run, inspect, and clean up a real container: `docker run`,
  `docker ps`, `docker logs`, `docker exec`, `docker stop`, `docker rm`.

## Why this matters

Every remaining lesson in this module builds directly on the mental
model this lesson establishes. If "a container is just a really small
VM" is your working model, several things later in this module (why
containers start in milliseconds, why they can share one kernel, why a
`Dockerfile`'s layers work the way they do) will feel like arbitrary
trivia instead of consequences of one underlying idea. Get the real
model right here, once, and the rest of this module is mostly "applying
this one idea to a new situation."

## Prerequisites

- **Lesson 00**, completed and verified — `docker run hello-world`
  working is this lesson's starting point.
- **Module 09** — this lesson repeatedly compares against the manual
  deploy work you did there; if that module feels distant, skim
  `module-09-linux-networking-servers/lessons/07-deploying-questlog-part1-server-and-backend.md`'s
  Phase 5-8 (getting QuestLog's code and dependencies onto a fresh
  server) as a refresher.
- **Module 01's Python venv lesson** — this lesson's "why isolation
  matters" reasoning is the same reasoning a venv solves for Python
  packages, one level up (a whole OS-level environment, not just a
  package installation).

## The concept, explained simply

### The problem: "works on my machine"

Picture this exact, real scenario from Module 09: you installed
PostgreSQL on a fresh Ubuntu server, and Ubuntu's `apt` package manager
gave you version **16.x** — one version older than the PostgreSQL
**18.x** this course's `backend/` has been developed and tested against
locally the whole time (Module 09, Lesson 07's own header calls this out
explicitly). Nothing broke, because QuestLog's schema happens to use no
version-specific Postgres feature — but that was luck, not a guarantee.
Now imagine a different, equally real scenario: your teammate's machine
has Python 3.11 installed globally, yours has 3.14, and a library one of
you added behaves subtly differently between the two. Or: the exact
`npm` package versions in your `package-lock.json` resolved differently
on your teammate's machine because of some tiny difference in their
global npm config. Every one of these is the same underlying disease,
usually summarized as **"works on my machine"** (and, implicitly,
"...so I don't know why it doesn't work on yours, or on the server").

The actual root cause, every time, is the same: your code was never
really running in isolation — it was always running *alongside*,
*inside*, and *dependent on* whatever else happened to already be
installed on that one specific machine, in whatever specific versions
happened to already be there. A **container** is a way to package your
application together with the *exact* runtime and libraries it needs, as
one self-contained, portable unit, so "the same container image" really
does mean "the exact same bits," running identically, whether it's on
your laptop, your teammate's laptop, or a production server.

**Game-dev analogy:** a container image is like a packaged, complete
build of your game — engine binaries, content, the exact runtime
libraries it links against — versus shipping raw source code and hoping
the target machine happens to have the right compiler version, the right
SDK, the right dependencies already installed. One is guaranteed to
behave identically anywhere it runs; the other is a gamble on the target
environment matching yours closely enough. A **container**, specifically
(the *running* thing, as opposed to the packaged image sitting on disk)
is like one running instance of that packaged build — the same way one
compiled dedicated-server build can be launched as many separate,
simultaneously-running game-server instances, each isolated from the
others, all sharing the same underlying hardware.

### Containers vs. virtual machines: the real difference

The most common wrong mental model is "a container is just a smaller,
faster VM." Here's the actual structural difference:

```
   A VIRTUAL MACHINE                    A CONTAINER

  ┌─────────────────────┐             ┌─────────────────────┐
  │   Your Application   │             │   Your Application   │
  ├─────────────────────┤             ├─────────────────────┤
  │  Guest OS (full!)     │             │ (no guest OS at all)  │
  │  - own kernel          │             │                        │
  │  - own drivers          │             │                        │
  ├─────────────────────────┤         ├───────────────────────────┤
  │      Hypervisor           │         │      Container Engine        │
  │  (emulates hardware)       │         │  (namespaces + cgroups)        │
  ├─────────────────────────────┤     ├─────────────────────────────────┤
  │       Host OS                  │     │            Host OS                    │
  │       (one real kernel)           │     │       (one real kernel — SHARED)      │
  ├─────────────────────────────────────┤ ├───────────────────────────────────────┤
  │          Physical hardware              │ │          Physical hardware                │
  └─────────────────────────────────────────┘ └─────────────────────────────────────────┘
```

A **virtual machine** runs a complete, separate guest operating system —
its own kernel, its own drivers, all of it — on top of a **hypervisor**,
a program whose job is emulating real computer hardware convincingly
enough that a full, independent OS can boot and run on top of it,
believing it has a real, dedicated machine underneath it. This is
genuinely heavyweight: booting a VM means booting an entire second OS
from scratch, and every VM on a machine needs its own complete copy of
that OS's kernel and system files, each consuming real memory and disk
space, independently of every other VM on the same physical box.

A **container** runs no separate OS at all. It is, mechanically, just an
**ordinary process**, running directly on the host machine's *one real
kernel* — the exact same kernel every other process on that machine
(including other containers) is also using. What makes it "isolated"
from every other process on the machine isn't a separate kernel; it's
two specific Linux kernel features working together:

- **Namespaces** give a process its own, private *view* of some global
  system resource, without that resource actually being duplicated.
  There's a namespace for process IDs (a containerized process might see
  itself as PID 1, with no idea any other process on the machine even
  exists), one for network interfaces (a container gets what looks like
  its own private network stack), one for the filesystem's mount points
  (a container sees what looks like its own, complete root filesystem,
  built from the container image, even though the real, physical disk
  underneath is shared with everything else on the host).
- **Cgroups** (control groups) limit and measure *how much* of the
  host's real, shared resources — CPU time, memory, disk I/O — a given
  process (or group of processes) is allowed to actually consume, so one
  container hogging resources can't starve everything else on the same
  machine.

Put together: a container is a completely ordinary process that has been
made to *believe* it's alone on the machine (namespaces) and that has
been *capped* in how much of the machine it can actually use (cgroups).
No emulated hardware, no second kernel to boot, no hypervisor in the
picture at all. This is exactly why a container starts in a fraction of
a second (it's just starting a process — there's no OS to boot) and why
you can run dozens of containers on a machine that could maybe run two
or three full VMs — they're all sharing the one, real kernel underneath,
each just wearing a namespace-shaped blindfold about the others'
existence.

**Where does Docker Desktop's own "Linux VM under the hood" (Lesson 00)
fit into this?** Windows doesn't run a Linux kernel natively at all —
there is no Windows kernel feature equivalent to Linux's own namespaces/
cgroups for Docker to use directly. So on Windows, Docker Desktop uses
WSL2's own lightweight Linux VM as the *one* real Linux kernel every
container you run actually shares — genuinely one VM, not one VM per
container. Every container you start is a real, namespaced,
cgroup-limited Linux process, sharing that one WSL2 kernel, exactly the
way multiple containers would share one real kernel on a bare-metal
Linux server. On native Linux (a real Ubuntu server, like the ones
Module 09 deployed to), there's no VM in the picture at all — containers
run directly on that server's own kernel.

## The details

### Running your first real container

`docker run hello-world` (Lesson 00) proved the plumbing works, but it's
not a container you can actually poke at — it prints one message and
exits immediately. Let's run something that keeps running, so you can
inspect it while it's alive:

```bash
docker run --detach --name my-first-nginx --publish 8081:80 nginx:alpine
```

**Line by line:**
- `docker run` — create and start a new container from an image.
- `--detach` (short form `-d`) — run this container in the background,
  returning your terminal prompt immediately, instead of attaching to
  its output and blocking your terminal until it exits.
- `--name my-first-nginx` — gives this specific container a
  human-readable name, instead of Docker's own randomly generated one
  (something like `wonderful_turing`) — makes every later command in
  this lesson easier to read.
- `--publish 8081:80` (short form `-p`) — maps port `8081` on your own
  machine to port `80` *inside* the container. Lesson 04 explains
  exactly why this mapping is necessary at all (short version: the
  container has its own, private network namespace — Lesson 04 — so
  nothing outside it can reach port 80 *inside* it without an explicit
  mapping like this one).
- `nginx:alpine` — the image to run: Nginx (a real web server — Module
  09, Lesson 06 covered what it does), the `alpine` tag specifically
  (a small Linux distribution commonly used as a container base — more
  on tags and base images in Lesson 02).

**Expected output:** the first time, several lines of `Pulling from
library/nginx` as Docker downloads the image's layers, ending in a long
hexadecimal string (the new container's ID) printed on its own line.

Confirm it's actually running:

```bash
docker ps
```

**Expected output**, one row:
```
CONTAINER ID   IMAGE          COMMAND                  ...   STATUS         PORTS                  NAMES
a1b2c3d4e5f6   nginx:alpine   "/docker-entrypoint.…"   ...   Up 5 seconds   0.0.0.0:8081->80/tcp   my-first-nginx
```

Now actually talk to it, from your own machine, over the port you
published:

```bash
curl http://localhost:8081
```

**Expected:** an HTML page starting with `<!DOCTYPE html>` and containing
`Welcome to nginx!` — this exact, real web server, packaged inside this
exact container image, is genuinely serving a real HTTP response, on a
port your own machine's browser could open right now.

### Looking inside a running container

```bash
docker logs my-first-nginx
```
**Expected:** Nginx's own startup log lines, plus one new access-log line
recording the `curl` request you just made — proof this is a real,
logging web server process, not a static file being served by magic.

```bash
docker exec -it my-first-nginx sh
```
**Line by line:** `docker exec` runs an *additional* command inside an
*already-running* container (as opposed to `docker run`, which starts a
brand-new container) — `-it` combines two flags (`--interactive`,
keeping stdin open, and `--tty`, allocating a proper interactive
terminal) so you get a real, usable interactive shell, not a command
that runs once and immediately exits. `sh` is the actual command being
run inside the container — Alpine-based images (like this one) don't
include `bash` by default, only the smaller, more limited `sh`.

**Expected:** your prompt changes to something like `/ #` — you are now,
genuinely, inside this container's own, isolated filesystem. Try:

```sh
ps aux
```
**Expected:** a very short process list — just Nginx's own master and
worker processes, and this `sh` shell itself. **This is the namespaces
concept from this lesson's "concept" section, directly observable**: from
inside this container, there is no sign at all that your host machine
(or Docker Desktop, or any other container) has any other process
running anywhere — this container's process-ID namespace shows it only
itself, exactly as the concept section described.

```sh
exit
```
Leaves the container's shell and returns you to your own machine's
normal prompt (the container itself keeps running in the background —
`exit`ing an `exec`'d shell doesn't stop the container, only that one
additional command inside it).

### Stopping and removing a container

```bash
docker stop my-first-nginx
docker ps -a
```
**Expected:** `docker ps` (no `-a`) now shows nothing — `docker ps -a`
(all containers, including stopped ones) still shows `my-first-nginx`,
now with a `STATUS` of `Exited (0)` (or a different, nonzero code if it
was stopped in an unusual way — Nginx's own graceful-shutdown exit code
here is `0`).

```bash
docker rm my-first-nginx
docker ps -a
```
**Expected:** `my-first-nginx` no longer appears at all — `docker stop`
merely stops the process; `docker rm` actually deletes the stopped
container's own small, writable layer (Lesson 02 explains layers in
full). The *image* (`nginx:alpine`) is untouched by either command —
confirm with `docker images`, which still lists it, ready to `docker
run` again instantly, with no re-download needed.

**Try it yourself:** run `docker run --rm -d --name second-nginx -p 8082:80 nginx:alpine`
— note the new `--rm` flag. Stop it with `docker stop second-nginx`, then
immediately run `docker ps -a` again. **Predict, before running it**,
whether `second-nginx` will still appear in that list — then check.
(`--rm` tells Docker to automatically remove the container the moment it
stops, skipping the separate `docker rm` step entirely — useful for
short-lived, throwaway containers you never intend to inspect after the
fact.)

## Common mistakes & gotchas

- **`docker: Error response from daemon: Conflict. The container name
  "/my-first-nginx" is already in use`.** You already have a (possibly
  stopped) container with that exact name — `docker rm my-first-nginx`
  first, or pick a different `--name`.
- **`curl: (7) Failed to connect to localhost port 8081` even though
  `docker ps` shows the container `Up`.** Double-check the `-p` mapping
  actually matches — `-p 8081:80` means *host* port 8081 maps to
  *container* port 80; `curl`ing port 80 directly on your own machine
  (instead of 8081) will fail, because nothing is actually listening on
  your own machine's port 80 at all — only inside the container.
- **Forgetting `-d` and wondering why your terminal "hangs."** Without
  `--detach`, `docker run` attaches to the container's own console
  output and blocks your terminal for as long as the container keeps
  running — exactly correct behavior for a container whose whole job is
  running in the foreground, but disorienting the first time. `Ctrl+C`
  stops it (and, without `--rm`, leaves a stopped container behind, same
  as `docker stop` would).
- **Confusing `docker stop` with `docker rm`.** `stop` pauses the
  process; the container (and anything written to its own writable
  layer) still exists, and `docker start my-first-nginx` would resume it
  exactly where it left off. `rm` actually deletes it. This distinction
  matters a lot once Lesson 05 introduces volumes — data written *inside*
  a container but *not* in a volume is lost the moment that specific
  container (not just the image) is removed.

## How this connects

Every container this whole module runs — `hello-world` in Lesson 00,
`nginx:alpine` here, and eventually QuestLog's own backend and frontend
containers in Lessons 07-08 — is exactly the same underlying mechanism:
an isolated, cgroup-limited, namespaced Linux process, started from a
packaged image. Lesson 02 explains where that image itself actually
comes from: a `Dockerfile`, and the layered, cacheable build process that
turns it into a runnable image.

## Quick self-check

1. In your own words, what specifically makes a container "isolated,"
   mechanically — name both kernel features involved and what each one
   is responsible for.
2. Why does a container start dramatically faster than a virtual
   machine, in terms of what each one does (or doesn't) have to do at
   startup?
3. When you ran `ps aux` inside the `my-first-nginx` container via
   `docker exec`, why did it show so few processes, given that your host
   machine was almost certainly running dozens of other processes at
   that exact moment?
4. What's the difference between `docker stop` and `docker rm`, and
   which one actually deletes the container?
5. On Windows, what real Linux kernel are your containers actually
   sharing, given that Windows itself has no native equivalent to Linux
   namespaces/cgroups?
