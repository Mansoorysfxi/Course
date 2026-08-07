# Module 09 — Linux, Networking & Servers

**Phase:** 3 — DevOps & Deployment (opening module)
**Estimated time:** 18–24 hours (this module includes real hands-on time
on a Linux system — via WSL2 for most exercises, optionally a real VPS
for the capstone — budget more time than a pure-reading module)
**Verified against (August 2026):** Ubuntu **24.04 LTS** ("Noble Numbat")
as this course's standard target — see `lessons/00-setup.md` for why
24.04 was chosen over the newer Ubuntu **26.04 LTS** ("Resolute Raccoon,"
released April 23 2026) that also exists as of this writing; Hetzner
Cloud **CX22** (2 vCPU / 4 GB RAM / 40 GB NVMe, ≈$4.59/mo) as the named
concrete VPS example, confirmed via Hetzner's own pricing pages and
third-party trackers, August 2026; Nginx **1.30.4** (latest stable
release, July 15 2026) vs. the older **1.24.0** Ubuntu 24.04 ships in its
own `apt` repository — both discussed, see `lessons/06-nginx-and-reverse-proxies.md`;
OpenSSH `ssh-keygen`'s current best-practice default, **Ed25519** (the
default algorithm since OpenSSH 9.5, October 2023); `ufw`'s current
default policy and syntax on Ubuntu 24.04/26.04, unchanged in shape for
several years. Every fact above was checked with a live web search while
writing this module, not recalled from memory — see each lesson's own
header for the specific source and date.

## What this module is

Through Module 08, QuestLog has only ever run on **your own machine** —
`uvicorn app.main:app --reload` in one terminal, `npm run dev` in
another, both talking over `localhost`. That's normal and correct for
development, but it means QuestLog has never once been reachable by
anyone except you, on your own computer, while it happens to be running.
This module changes that: you'll learn enough real Linux system
administration and networking to take QuestLog's exact, unmodified
Module 08 codebase and run it, for real, on a server anyone on the
internet can reach — a **VPS (Virtual Private Server)**, a rented slice
of a real computer sitting in a data center somewhere, running Linux,
that is *not* your laptop and does not turn off when you close your lid.

This module deploys QuestLog **manually** — every command typed by hand,
every config file written and understood line by line, with **no**
Docker, **no** CI/CD pipeline, **no** managed platform automating any of
it away. That's deliberate, and the master plan for this course says so
explicitly: this is "the painful way, on purpose." Module 10 (Docker)
exists specifically to fix the pain you're about to feel firsthand —
copying files by hand, forgetting a firewall rule, restarting a crashed
process manually — and that fix will only feel like genuine relief if you
first feel the actual problem it solves. Module 11 (CI/CD, HTTPS, a real
domain) automates the manual deploy steps you do by hand here. Skipping
this module's pain and jumping straight to Docker is exactly the kind of
shortcut that produces engineers who can run `docker compose up` but
have no idea what's actually happening inside the container — this
course is trying to build the opposite kind of engineer.

**This module changes *where and how* QuestLog runs. It does not change
what QuestLog *does.*** Zero new features, zero new routes, zero new
database columns. The `project/questlog/backend/app/` and
`frontend/src/` folders are byte-for-byte identical to Module 08's. Every
new file this module adds lives in a new `project/questlog/deploy/`
folder, alongside the application, never mixed into it.

## What you'll be able to do after this module

- Explain what a Linux **process** is, inspect running processes with
  `ps`/`top`, and read a Unix **permissions** string (`rwxr-xr-x`) to say
  exactly who can do what to a file.
- Generate a real SSH key pair, explain *why* key-based authentication is
  more secure than a password (in terms of what an attacker would
  actually need to forge each one), and configure a Linux server to
  accept only key-based logins.
- Explain what `systemd` is, write a real **unit file** from scratch, and
  use it to make a program restart automatically after a crash or a
  server reboot — the Linux equivalent of a dedicated game server that
  respawns itself.
- Explain the difference between `localhost`, a private IP, and a public
  IP address; explain what a **port** is doing in practice; and reason
  correctly about which IP/port combination a given running program is
  actually reachable on.
- Configure a firewall with `ufw`, explaining exactly what "default deny
  incoming" means and why it's the correct default posture for a
  server exposed to the entire internet.
- Explain, in genuine mechanical detail (not just "it sits in front"),
  what a **reverse proxy** does and why virtually no production web app
  exposes its actual application server directly to the internet —
  including the single most common Nginx reverse-proxy configuration
  mistake almost everyone hits once.
- Explain what a **load balancer** is and when one becomes necessary,
  conceptually, without having set one up (this module's scope).
- Take QuestLog's exact Module 08 codebase and deploy it, by hand, to a
  real (or realistically-described) Ubuntu server: PostgreSQL installed
  and configured, the FastAPI backend running as a supervised `systemd`
  service, the React frontend built and served as static files, Nginx
  reverse-proxying the API and serving the frontend from one public IP
  address, and `ufw` allowing only the traffic that deployment actually
  needs.

## Prerequisites

- **Module 08 in full** — this module deploys that exact codebase
  unchanged. If your own Module 08 solution differs from the reference
  in `module-08-testing-and-quality/project/questlog/`, use the
  reference copy (already brought forward into this module's own
  `project/questlog/`) so this module's instructions match exactly.
- **Module 06's PostgreSQL lesson** — you'll install and configure
  Postgres again here, this time on Linux instead of Windows, and the
  underlying concepts (roles, databases, `psql`) are identical.
- **Module 07's CORS lesson** — this module's deployment removes the
  need for CORS entirely (frontend and backend become same-origin behind
  Nginx), and understanding *why* that removes the need requires
  remembering what CORS was solving in the first place.
- Comfort with a command-line shell (Module 00) — this module lives
  almost entirely in a terminal.

## A real VPS is optional for reading; required only to execute the capstone live

Every lesson in this module is written as real instructions you could
run, right now, against a real Ubuntu server — not a simulation. You do
**not** need to have already paid for a VPS to read and understand this
module; every lesson explains the concept fully and shows exact commands
and expected output either way. A small VPS (Hetzner's CX22, ≈$4.59/mo
at the time of writing, or an equivalent ~$4–6/mo box from any other
provider — see `lessons/00-setup.md`) is only required at the point you
want to **literally execute** the capstone deploy in `project/BRIEF.md`
against a real, internet-reachable server. Exercises 01–04 (Linux
processes/permissions, SSH, `systemd`, `ufw`) can all be done for free,
right now, inside a WSL2 Ubuntu instance on your own Windows machine —
`lessons/00-setup.md` sets that up. Only the capstone deploy genuinely
needs a real remote machine, because the entire point is reaching it from
outside your own network.

## Module structure

```
module-09-linux-networking-servers/
├── README.md                                              ← you are here
├── lessons/
│   ├── 00-setup.md                                        ← WSL2 Ubuntu + a real VPS (optional) + SSH client verification
│   ├── 01-linux-processes-and-permissions.md
│   ├── 02-ssh-and-key-based-auth.md
│   ├── 03-systemd-and-services.md
│   ├── 04-networking-ports-and-ips.md
│   ├── 05-firewalls-with-ufw.md
│   ├── 06-nginx-and-reverse-proxies.md
│   ├── 07-deploying-questlog-part1-server-and-backend.md   ← capstone walkthrough, part 1
│   └── 08-deploying-questlog-part2-frontend-and-going-live.md ← capstone walkthrough, part 2
├── exercises/
│   ├── 01-linux-processes-and-permissions/                ← easy — WSL2, almost impossible to fail if Lesson 01 was read
│   ├── 02-ssh-key-based-login/                             ← guided — WSL2's own SSH server as the practice target
│   ├── 03-systemd-toy-service/                              ← guided, leaning independent — WSL2 (systemd-enabled)
│   ├── 04-ufw-firewall-rules/                                 ← independent — WSL2
│   └── 05-nginx-reverse-proxy/                                 ← independent — WSL2, proxies a real toy backend
├── project/
│   ├── BRIEF.md                                                 ← the capstone: deploy QuestLog to a real (or real-if-you-choose) VPS
│   └── questlog/                                                 ← QuestLog, copied forward from Module 08, app code byte-identical
│       ├── frontend/                                               ← unchanged
│       ├── backend/                                                 ← unchanged
│       └── deploy/                                                   ← NEW this module: systemd unit, Nginx config, runbook, .env template
└── CHECKLIST.md
```

Read the lessons in order. Lessons 01–03 cover Linux itself (processes,
permissions, SSH, `systemd`); Lesson 04 shifts to networking concepts;
Lessons 05–06 cover the two pieces of network-facing infrastructure
(`ufw`, Nginx) every deploy needs; Lessons 07–08 are the capstone
walkthrough itself, applying everything to QuestLog specifically.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without
looking at its solution, ask for a review, revise if needed, then move
on. Once all five exercises are done, work through `project/BRIEF.md` —
this module's capstone is unusually hands-on-a-real-machine rather than
hands-on-more-code, and it is genuinely fine (expected, even) if it takes
longer and involves more troubleshooting than any capstone before it.
That friction is the point — see "What this module is," above.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's `project/questlog/`
is Module 08's finished, tested QuestLog, copied forward with its
application code **completely unchanged** — `backend/app/`,
`frontend/src/`, both test suites, `ruff`/`prettier`/`pre-commit`, all
identical, byte for byte, to Module 08's. The only addition is a new
`project/questlog/deploy/` folder holding this module's own new
artifacts: a `systemd` unit file, an Nginx site config, a `.env`
production template, and a written runbook — deployment infrastructure
that sits *alongside* the application, exactly the way it would in any
real repository that deploys manually.
