# Lesson 07 — Deploying QuestLog, Part 1: Server Prep, PostgreSQL, and the Backend as a Service

**Verified against (August 2026):** every command in this lesson is
standard Ubuntu 24.04 / PostgreSQL / `systemd` usage, cross-checked
against the same sources cited in Lessons 01–05 (Ubuntu's own package
repository data for PostgreSQL, `systemd`'s own documentation for the
two additional hardening directives introduced here). This lesson does
not introduce new tool versions beyond what earlier lessons already
verified — PostgreSQL's version installed via `apt` on Ubuntu 24.04 is
**16.x** (Ubuntu 24.04's default `postgresql` package at the time of
writing) — one version newer than the PostgreSQL 18.x this course's
Module 06/08 used locally; this lesson notes that explicitly, and it
doesn't matter for anything QuestLog's schema uses (no version-specific
Postgres feature is involved anywhere in this course).

## What you'll learn

- How to take a fresh Ubuntu server from "just created" to "hardened
  enough to keep running unattended," using nothing but Lessons 01–05.
- How to install and configure PostgreSQL on a real Linux server (as
  opposed to Module 06's local Windows install).
- How to run QuestLog's exact FastAPI backend as a real, supervised
  `systemd` service — combining Lesson 03's unit-file mechanics with a
  handful of new, explained hardening directives.
- How to verify each phase actually worked before moving to the next,
  rather than stacking unverified steps on top of each other.

## Why this matters

This is where every earlier lesson in this module stops being separate
topics and becomes one working system. Nothing in this lesson is new
*conceptually* — every single command is a direct application of
Lessons 01–05 — but doing it in the correct order, on a real machine,
against QuestLog's actual codebase, is a different skill than
understanding each piece in isolation. This lesson (backend + database)
and Lesson 08 (frontend + Nginx + going live) together are this
module's capstone in full.

## Prerequisites

- **Every lesson in this module so far** (00–06) — this lesson assumes
  you can generate an SSH key, read a permissions string, write a unit
  file, reason about bind addresses, and configure `ufw`, without
  re-explanation.
- **Module 06's PostgreSQL lesson** — creating roles/databases, `psql`
  basics — the mechanics are identical here, just on Linux instead of
  Windows.
- **Module 08's finished QuestLog** — this module's own
  `project/questlog/` (a byte-identical copy) is exactly what gets
  deployed.
- A target machine: either a real VPS (Lesson 00 — Hetzner CX22 or
  equivalent), or your WSL2 Ubuntu instance if you're working through
  this as a dry run without paying for a server yet (every command below
  works identically either way, except that "reachable from outside"
  claims obviously only mean something on a real VPS).

## The concept, explained simply

Deploying an application by hand is exactly the process of manually
recreating, on a strange new machine, every piece of setup your own
development machine already quietly has — an interpreter, a database, a
process to run your code, a way to reach it over a network — except this
time nothing is assumed to exist, and every single piece has to be
installed and wired together deliberately, by you, once. Every step
below answers exactly one question: "what does this specific fresh
machine not yet have that QuestLog needs to run?"

## The details

### Phase 1 — Log in, and immediately stop using the default account for everyday work

However you created your server, you were given one initial way to log
in — usually `root` directly, or a default provider-created user. Log in
once to confirm access:

```bash
ssh root@<YOUR_SERVER_IP>
```

**Expected:** a root shell prompt (`#`, conventionally, rather than `$`)
— this confirms Lesson 00/02's SSH key setup actually worked end to end
against a real remote machine. Immediately create a normal, non-root
user for everyday work — running everything as `root` directly violates
exactly the principle Lesson 01 explained:

```bash
adduser deploy
usermod -aG sudo deploy
```

**Line by line:** `adduser deploy` creates a new user account named
`deploy`, interactively prompting for a password (set a real one — this
account still needs `sudo`'s own password confirmation even after key
login is set up for SSH itself) and some optional profile fields you can
leave blank (press Enter through each). `usermod -aG sudo deploy` adds
`deploy` to the `sudo` group — the specific group whose members are
allowed to run `sudo` at all (without this, `deploy` could log in but
couldn't run any command needing elevated privileges).

Copy your SSH public key to this new user, so you can log in as `deploy`
directly, the same key-based way (repeating Lesson 02's Steps 1–3,
against this real account instead of `localhost`):

```bash
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

From your **own laptop**, in a **new** terminal (leave the current root
session open until this is confirmed working — Lesson 02's own warning
about not locking yourself out applies exactly here):

```bash
ssh deploy@<YOUR_SERVER_IP>
```

**Expected:** logged straight in, no password prompt, landing as
`deploy` (confirm with `whoami`). Once this works, disable root SSH
login and password authentication entirely, exactly as Lesson 02, Step 5
described:

```bash
sudo nano /etc/ssh/sshd_config
```
Set (uncommenting/editing as needed):
```
PermitRootLogin no
PasswordAuthentication no
```
```bash
sudo systemctl restart ssh
```
From your laptop, in yet another new terminal, confirm `ssh deploy@<IP>`
still works and `ssh root@<IP>` now fails outright — only then close your
original root session.

### Phase 2 — Update the system, install `ufw`

```bash
sudo apt update && sudo apt upgrade -y
```
**Expected:** downloads and installs any pending security/package
updates already present on the freshly created image — routine, often
takes a minute or two on a brand-new server.

```bash
sudo apt install -y ufw
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx HTTP'
sudo ufw enable
sudo ufw status verbose
```
**Expected:** exactly Lesson 05's output — `Status: active`, `OpenSSH`
and `Nginx HTTP` both `ALLOW IN`, default `deny (incoming)`. (`Nginx
HTTP` is allowed now even though Nginx isn't installed until Lesson
08 — the app profile itself doesn't require Nginx to already be
installed to reference it in a rule; it just describes port `80/tcp`.)

### Phase 3 — PostgreSQL

```bash
sudo apt install -y postgresql
sudo systemctl status postgresql
```
**Expected:** `Active: active (running)` — Ubuntu's `postgresql` package
installs and starts it as a `systemd` service automatically, exactly
like Nginx did in Lesson 06.

Create the `questlog` role and a fresh, real password for it — **not**
this course's local development password, which is fine on a machine
only you can reach but must never be reused on an internet-facing one:

```bash
sudo -u postgres psql
```
**Line by line:** `sudo -u postgres` runs the following command *as* the
`postgres` Linux user — PostgreSQL's own install creates this system
account specifically so administrative database commands run under it,
rather than under `root` or `deploy` directly. Inside the `psql` prompt
that opens:

```sql
CREATE USER questlog WITH PASSWORD 'a-real-random-password-here';
CREATE DATABASE questlog OWNER questlog;
\q
```

**Expected:** `CREATE ROLE` and `CREATE DATABASE`, each on its own line,
confirming success. Confirm the new role can actually connect:

```bash
psql -U questlog -d questlog -h localhost -c "SELECT 1;"
```
It will prompt for the password you just set — **Expected:** a one-row
table containing `1`, identical in shape to Module 06's own local
verification. Note the explicit `-h localhost` — without it, `psql`
would attempt a different connection method (a local Unix socket) that
uses OS-level trust instead of a password, which behaves differently and
isn't the scenario QuestLog's own `DATABASE_URL` (a TCP connection to
`localhost`) exercises.

**Why Postgres never needs a `ufw` rule, again, concretely:** run
`sudo ss -tlnp | grep 5432` — you should see it listening on
`127.0.0.1:5432` only (Ubuntu's `postgresql` package defaults to exactly
this, unmodified), confirming Lesson 04/05's reasoning holds for real,
not just in theory.

### Phase 4 — A dedicated, unprivileged user to run the app itself

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin questlog
```

**Line by line:** `--system` creates a **system account** — Linux's
convention for an account meant to run a service, not for an actual
human to log into interactively (it gets a lower-numbered UID from a
reserved range, and typically no password set at all). `--create-home`
still gives it a home directory (`/home/questlog` by default), useful
for things like a Python venv's cache files. `--shell /usr/sbin/nologin`
is the specific, deliberate hardening step: it sets this account's login
shell to a program whose entire job is refusing the login and printing
"This account is currently not available." — meaning even if someone
obtained this account's credentials (there aren't any — no password was
set), or tried `su questlog`, they could not get an interactive shell as
it. `systemd` doesn't need or use a login shell to run this account's
service (Lesson 03's `ExecStart` runs the program directly, never
through a shell login) — this is purely an extra restriction with no
downside for a service-only account.

```bash
sudo mkdir -p /opt/questlog
sudo chown questlog:questlog /opt/questlog
```
`/opt/` is the conventional Linux location for self-contained
third-party or locally-installed application software — not a `apt`-
managed system package, but not a random location either. Ownership by
`questlog:questlog` (Lesson 01's `chown` syntax: `user:group`) means
this account can read and write everything under it, while `deploy` (or
anyone else) cannot, by default.

### Phase 5 — Get the backend's code onto the server

Two realistic options; either is fine for this course:

**Option A — `git clone` (works if this course's repo, or your own fork
of it, is reachable from the server):**
```bash
sudo -u questlog git clone <YOUR_REPO_URL> /tmp/questlog-checkout
sudo -u questlog cp -r /tmp/questlog-checkout/module-09-linux-networking-servers/project/questlog/backend /opt/questlog/backend
rm -rf /tmp/questlog-checkout
```

**Option B — `scp`, copying directly from your own machine (simpler if
your repo is private and not yet set up with deploy credentials):**
```bash
# Run this from YOUR OWN machine, not the server:
scp -r module-09-linux-networking-servers/project/questlog/backend deploy@<YOUR_SERVER_IP>:/tmp/questlog-backend
# Then, back on the server:
sudo cp -r /tmp/questlog-backend /opt/questlog/backend
sudo chown -R questlog:questlog /opt/questlog/backend
rm -rf /tmp/questlog-backend
```

**Expected either way:** `ls /opt/questlog/backend` on the server shows
`app/`, `requirements.txt`, `alembic/`, and so on — the exact same files
you'd see locally, per Lesson 00's "this doesn't change QuestLog's code"
framing.

### Phase 6 — Python environment and dependencies

```bash
sudo -u questlog python3 -m venv /opt/questlog/backend/.venv
sudo -u questlog /opt/questlog/backend/.venv/bin/pip install -r /opt/questlog/backend/requirements.txt
```

**Line by line:** `sudo -u questlog` runs each command *as* the
`questlog` account (Phase 4) — meaning the venv and everything installed
into it are owned by `questlog`, not by `deploy` or `root`, matching who
`systemd` will later run the actual service as (Lesson 03's own
`User=`/`Group=` directives require the files they run to be readable by
that exact user). This deliberately installs only `requirements.txt`
(the app's real runtime dependencies) — **not** `requirements-dev.txt`
(`pytest`, `ruff`, etc.) — exactly the distinction Module 08's own setup
lesson drew: a deployed server never needs test tooling installed at
all.

**Expected:** the same `Successfully installed fastapi-... uvicorn-...`
list Module 07/08 produced locally.

### Phase 7 — The real, production `.env`

```bash
sudo -u questlog python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copy that output — a **fresh** secret, generated on this server,
different from any secret you've used locally. Then:

```bash
sudo cp /opt/questlog/backend/../deploy/backend.env.production.example /opt/questlog/backend/.env
```
(Adjust the source path to wherever you placed this module's `deploy/`
folder on the server — if you only copied `backend/` in Phase 5, instead
just `sudo -u questlog nano /opt/questlog/backend/.env` and paste this
module's `project/questlog/deploy/backend.env.production.example`
contents directly, from your own machine's copy, as a starting point.)
Edit it (`sudo nano /opt/questlog/backend/.env`) and replace:
- `DATABASE_URL`'s password with the real one you set in Phase 3.
- `SECRET_KEY` with the value you just generated above.

```bash
sudo chown questlog:questlog /opt/questlog/backend/.env
sudo chmod 600 /opt/questlog/backend/.env
```
**Why `600` specifically, again:** this file now holds a real database
password and a real JWT signing secret — Lesson 01's "guard this like a
private key" framing applies exactly here; only the `questlog` account
itself should be able to read it at all.

### Phase 8 — Apply migrations

```bash
cd /opt/questlog/backend
sudo -u questlog .venv/bin/alembic upgrade head
```
**Expected:** the same two `Running upgrade ... -> ...` lines Module
06/07's local setup produced, now applied against this server's own,
freshly created, empty `questlog` database.

### Phase 9 — The systemd service itself

Copy this module's `project/questlog/deploy/questlog-backend.service`
onto the server (via `scp`, or recreate it with `nano` — it's short) to
`/etc/systemd/system/questlog-backend.service`. Its content, reproduced
here for direct explanation:

```ini
[Unit]
Description=QuestLog FastAPI backend (Uvicorn)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=questlog
Group=questlog
WorkingDirectory=/opt/questlog/backend
EnvironmentFile=/opt/questlog/backend/.env
ExecStart=/opt/questlog/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**The lines new since Lesson 03's toy example, explained:**
- `After=network.target postgresql.service` / `Wants=postgresql.service`
  — Lesson 03's ordering-vs-dependency distinction, applied for real:
  `Wants=` tells `systemd` to also try starting `postgresql.service`
  whenever this service starts (a soft dependency — this service still
  attempts to start even if Postgres somehow failed, rather than
  refusing outright, which `Requires=` would do); `After=` makes sure
  that *if* both are starting (true at every normal boot), Postgres goes
  first, giving it a head start to be ready to accept connections before
  Uvicorn's own startup code tries to use the database.
- `User=questlog` / `Group=questlog` — the entire reason Phase 4 created
  a dedicated account: without these two lines, `systemd` runs a service
  as `root` by default, which would mean a bug or vulnerability in
  QuestLog's own code (or any of its dependencies) could, in principle,
  do anything root can do to the entire machine. Running as an
  unprivileged, `nologin` account limits the practical damage to
  whatever that one account can already touch — its own files under
  `/opt/questlog`, and its own network connections.
- `EnvironmentFile=/opt/questlog/backend/.env` — tells `systemd` to read
  this file and set every `KEY=value` line in it as an environment
  variable for the process it starts, **before** running `ExecStart`.
  This is how `SECRET_KEY` and `DATABASE_URL` actually reach
  `pydantic-settings` (`app/config.py`) without ever being typed
  directly into the unit file itself (which would otherwise be world-
  readable at `/etc/systemd/system/questlog-backend.service`'s own
  default permissions, unlike a `.env` file you can independently
  lock down to `600`).
- `NoNewPrivileges=true` — a genuinely simple, single-purpose
  restriction: prevents this process (or anything it might spawn) from
  gaining *any* additional privileges beyond what it already has, even
  briefly, for the rest of its life — closing off a whole category of
  privilege-escalation technique, at essentially zero cost to a normal
  Python web app, which never legitimately needs to gain new privileges
  mid-run.
- `PrivateTmp=true` — gives this specific service its own private,
  isolated view of `/tmp` (and `/var/tmp`), invisible to and from every
  other process on the system — meaning even if some other, unrelated
  process on this same machine were compromised, it couldn't read or
  tamper with anything QuestLog's backend happens to write to `/tmp`,
  and vice versa.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now questlog-backend
sudo systemctl status questlog-backend
```

**Expected:** `Active: active (running)`, `Main PID: <some number>
(uvicorn)` (or `python3`, depending on how Uvicorn's own process shows
up — either is fine). If it shows `failed` instead, go straight to:

```bash
journalctl -u questlog-backend -n 50 --no-pager
```
(`--no-pager` prints directly instead of opening the scrollable pager —
convenient when you just want the tail of output in one go.) The most
likely causes, in order of how often they actually happen: a typo'd
absolute path in `ExecStart`, a missing or malformed `.env` (check with
`sudo cat /opt/questlog/backend/.env` — remember its `600` permissions
mean only `sudo` or the `questlog` account itself can read it), or a
database connection failure (confirm Phase 3's `psql` check still
passes).

### Phase 10 — Confirm the backend, privately, before Nginx exists at all

From the server itself (Nginx doesn't exist yet — this deliberately
tests the backend alone, exactly as Lesson 06 did in its practice
environment):

```bash
curl http://127.0.0.1:8000/
```
**Expected:** `{"message":"QuestLog API. See /docs for interactive documentation."}`.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -d "username=player@questlog.local&password=dragon-slayer-1"
```
**Expected:** a real JSON access token — proof the seeded demo account,
password hashing, JWT signing, and the fresh database all genuinely work
together, on this real server, end to end. **From your own laptop**, try
the same `curl` against the server's public IP and port 8000 directly:
```bash
curl http://<YOUR_SERVER_IP>:8000/
```
**Expected:** this **times out or is refused** — proof Lesson 04's
`127.0.0.1`-only bind, combined with Lesson 05's `ufw` rules (which
never allowed port 8000 at all), together keep this port unreachable
from outside, exactly as intended. Only Nginx, in Lesson 08, will make
this backend reachable from the public internet — deliberately, on
purpose, and only through itself.

## Common mistakes & gotchas

- **`Permission denied` running any command as `questlog`.** Remember
  `questlog` has `--shell /usr/sbin/nologin` — you cannot `su questlog`
  into an interactive shell for it; every command targeting that account
  must go through `sudo -u questlog <command>`, run one at a time.
- **The service starts fine but immediately fails again in a restart
  loop.** Check `journalctl` first, per Phase 9. A very common specific
  cause here: the `.env` file's ownership wasn't fixed after being
  copied in (still owned by `root` or `deploy` from the `cp`/`scp` step)
  — since `questlog` needs to *read* it, not just for it to exist.
- **Forgetting Phase 1's "keep the original session open" rule** when
  testing `PermitRootLogin no` — exactly as damaging here as it was in
  Lesson 02's local practice, but now against a real, possibly billed,
  remote server that's genuinely harder to recover if you're locked out.
- **PostgreSQL's `psql -U questlog -d questlog -h localhost` fails with
  `password authentication failed`**, even though the password was just
  set correctly. Check for accidentally-included whitespace when pasting
  the password during `CREATE USER`, or a shell history expansion
  mangling special characters in the password if it was passed directly
  on a command line rather than typed at an interactive `psql` prompt —
  prefer the interactive prompt shown above for exactly this reason.

## How this connects

Lesson 08 picks up immediately where this lesson stops: the backend is
now running, privately, correctly, and provably unreachable from outside
— exactly the state Lesson 06's reverse-proxy lesson assumed as its
starting point. Lesson 08 installs Nginx, builds and ships the frontend,
and is the step that finally makes QuestLog reachable from the public
internet at all.

## Quick self-check

1. Why does the `questlog` system account get `--shell /usr/sbin/nologin`, and what does that specifically prevent?
2. What's the difference between `Wants=postgresql.service` and `Requires=postgresql.service`, and why does this lesson use the softer one?
3. Where does `SECRET_KEY` actually come from, mechanically, once `questlog-backend.service` starts Uvicorn — trace it from the `.env` file to `app/config.py`.
4. Why does Phase 10 deliberately try (and expect to fail) reaching port 8000 from outside the server, right after confirming it works from inside?
5. Why does this lesson install only `requirements.txt`, never `requirements-dev.txt`, on the real server?
