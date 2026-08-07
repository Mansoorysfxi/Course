# Lesson 08 — Deploying QuestLog, Part 2: The Frontend, Nginx, and Going Live

**Verified against (August 2026):** builds directly on Lesson 06's
already-verified Nginx facts (Ubuntu 24.04's packaged `1.24.0` vs.
upstream's current stable `1.30.4`); this lesson's one additional,
concrete, checkable claim — that `frontend/package.json`'s
`@oxlint/binding-win32-x64-msvc` and `@rolldown/binding-win32-x64-msvc`
`devDependencies` are Windows-only native binaries — was confirmed by
directly reading this exact repository's own
`module-09-linux-networking-servers/project/questlog/frontend/package.json`
(copied forward, unchanged, from Module 08). This lesson's claim about
what `npm install` would specifically do with those two packages on a
Linux machine is **reasoned from documented npm/`optionalDependencies`
platform-matching behavior, not personally re-executed against a live
Ubuntu server in the writing of this lesson** — stated explicitly here
per Rule 7, rather than presented as a directly-observed fact. If you
try it yourself and see different behavior than described, that's useful
real information — report back what actually happened.

## What you'll learn

- Why this deploy builds the frontend on your **own machine**, never on
  the server itself — including one very concrete, real reason specific
  to this exact codebase's `package.json`.
- How to ship a built frontend to a server and serve it correctly with
  Nginx, completing Lesson 06's static-serving config for real.
- How to remove Ubuntu's default Nginx site so your own config is the
  only one active.
- How to verify the **entire** deployed system end to end, from a real
  browser, on a machine that isn't the server itself.
- This module's own honest accounting of what this deploy deliberately
  does *not* yet do, and why — setting up exactly what Modules 10 and 11
  fix.

## Why this matters

Lesson 07 left QuestLog's backend running correctly but completely
unreachable from outside the server — by design, at that point. This
lesson is what actually makes the whole point of deploying anything come
true: a real browser, on a completely different machine, reaching
QuestLog over the actual internet.

## Prerequisites

- **Lesson 07, completed and verified** — this lesson assumes the
  backend is already running as `questlog-backend.service`, Postgres is
  seeded, and Phase 10's local `curl` checks passed.
- **Lesson 06 in full** — this lesson applies that lesson's exact
  reverse-proxy and `try_files` config, not a new one.

## The concept, explained simply

Think of Lesson 07 as building and pressure-testing a dedicated game
server binary entirely on a build machine, confirming it runs correctly,
before ever exposing its listen port to real players. This lesson is the
step where you finally open that port to the public and point real
clients at it — except here, "the client" is a browser loading a
website, and "opening the port" is Nginx becoming the public-facing
front door.

## The details

### Step 1 — Build the frontend on your own machine, not the server

```bash
cd module-09-linux-networking-servers/project/questlog/frontend
VITE_API_BASE_URL= npm run build
```

This is exactly Lesson 06's Step 4, repeated here as this capstone's real
production build. **Why build here, on your own Windows/WSL2 machine,
and never run `npm install`/`npm run build` on the actual Linux server
at all** — three real reasons, not just convention:

1. **A concrete, checkable one, specific to this exact codebase.** Open
   `frontend/package.json` and look at its `devDependencies`:
   `@oxlint/binding-win32-x64-msvc` and
   `@rolldown/binding-win32-x64-msvc` — Module 08's own setup lesson
   added these to fix a real Windows-specific native-binding bug
   (`lessons/00-setup.md`'s "Cannot find native binding" gotcha, in that
   module). Both packages, by their own names, are **Windows-only**
   compiled binaries. Running `npm install` on a Linux server, where
   these packages' own declared platform doesn't match the machine
   `npm` is running on, is a real, documented category of npm behavior
   worth knowing about even before you hit it — see this lesson's header
   for the honest caveat about exactly how deep this course verified it.
   The safe, simple fix that sidesteps the question entirely: never run
   `npm install` for this frontend anywhere except your own Windows/WSL2
   machine, where those bindings are exactly what's needed.
2. **The server doesn't need a JavaScript toolchain installed at all.**
   Once built, `dist/` is plain HTML/CSS/JS files — Nginx serves them
   with zero knowledge of React, Vite, TypeScript, or Node.js. Keeping
   Node.js off the production server entirely is one less thing to
   install, secure, and keep updated on a machine whose whole job is
   just serving files and proxying requests.
3. **This mirrors real professional practice directly.** Every CI/CD
   pipeline you'll ever encounter (Module 11 builds one for QuestLog
   specifically) builds frontend assets in a **build step**, completely
   separate from the server the built output eventually runs on — this
   manual capstone is deliberately rehearsing that exact separation by
   hand, before Module 11 automates it.

**Expected:** `frontend/dist/` now contains `index.html`, an `assets/`
folder with hashed filenames (e.g. `index-a1b2c3.js`), and
`favicon.svg`. Confirm the API base URL really did bake in as relative,
not absolute:

```bash
grep -o "VITE_API_BASE_URL[^,}]*\|http://localhost:8000" dist/assets/*.js | head -5
```
**Expected:** no `http://localhost:8000` string found anywhere in the
built output (if it *is* present, the `VITE_API_BASE_URL=` empty-string
build didn't take — re-run Step 1's command exactly as written, on the
same line, so the environment variable is actually empty rather than
unset).

### Step 2 — Ship `dist/` to the server

```bash
scp -r dist/* deploy@<YOUR_SERVER_IP>:/tmp/questlog-frontend/
```
On the server:
```bash
sudo mkdir -p /var/www/questlog
sudo cp -r /tmp/questlog-frontend/* /var/www/questlog/
sudo chown -R www-data:www-data /var/www/questlog
rm -rf /tmp/questlog-frontend
```
**Line by line:** `www-data` is the conventional Linux system user Nginx
itself runs as by default (confirm with
`ps aux | grep nginx` — you'll see multiple `nginx` worker processes,
running as `www-data`, plus one `master` process typically running as
`root`, which exists specifically to be able to bind low-numbered ports
like `80` before dropping to `www-data` for the actual request-handling
workers — a real, deliberate `systemd`/Unix pattern, mentioned here for
completeness, not something you need to configure yourself). Static
files just need to be *readable* by whichever user Nginx's worker
processes run as — `www-data` ownership is the conventional, simplest
way to guarantee that.

### Step 3 — Install Nginx and deploy this module's config

```bash
sudo apt install -y nginx
```

Copy this module's `project/questlog/deploy/nginx/questlog.conf` onto
the server (via `scp`, or recreate with `nano` — it's short) to
`/etc/nginx/sites-available/questlog`. Its content, reproduced here:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name _;

    root /var/www/questlog;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri /index.html;
    }
}
```

This is **exactly** Lesson 06's worked example, with two literal path
changes (`root /var/www/questlog;` instead of the practice folder) and
no other differences at all — proof that everything Lesson 06 taught in
a low-stakes practice setting transfers directly, unchanged, to the real
capstone.

```bash
sudo ln -s /etc/nginx/sites-available/questlog /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
```
**Expected from `nginx -t`:** `syntax is ok` / `test is successful`
(Lesson 06's own reminder: never skip this check). The `rm -f` removes
Ubuntu's own placeholder default site — **necessary**, not optional:
leaving it enabled alongside your own `server_name _;` block risks
exactly the "which one wins" ambiguity Lesson 06's gotchas section
warned about; removing it makes your config the unambiguous, only match.

```bash
sudo systemctl reload nginx
```

### Step 4 — Go live: verify from a genuinely different machine

**From your own laptop's actual web browser** (not `curl`, not the
server itself — the real, final test) navigate to:

```
http://<YOUR_SERVER_IP>/
```

**Expected:** QuestLog's login page loads, styled correctly (Tailwind's
CSS loaded from `/assets/...`, proof static serving works), with no
console errors about a failed API connection. Log in with the seeded
demo account (`player@questlog.local` / `dragon-slayer-1`). **Expected:**
the Quest Board loads five real, seeded quests — proof the entire chain
(your browser → the internet → your server's public IP → Nginx on port
80 → proxied to Uvicorn on `127.0.0.1:8000` → SQLAlchemy → PostgreSQL on
`127.0.0.1:5432` → and the same full chain in reverse for the response)
is genuinely working, for real, over the actual public internet.

Open your browser's developer tools (Network tab) and inspect one of the
`/api/quests` requests: confirm its **Request URL** shows your server's
own address (`http://<YOUR_SERVER_IP>/api/quests`), not
`localhost:8000` — direct, visible confirmation that
`VITE_API_BASE_URL=` (empty, at build time) produced a same-origin,
relative request, exactly as Lesson 06 explained.

**Try it yourself:** directly type
`http://<YOUR_SERVER_IP>/quests/999999` into your browser's address bar
(a client-side route, not a real quest ID) and hit Enter — a genuinely
new HTTP request, not client-side navigation. **Expected:** the app
loads normally (React Router takes over and shows whatever QuestLog's
own UI does for a quest that doesn't exist — not a raw Nginx 404),
proof of Lesson 06's `try_files` fallback working for real, against a
real browser's real address-bar navigation, not just a `curl` command.

### Step 5 — The complete verification checklist

Run every check in this module's own
[`project/questlog/deploy/DEPLOY_RUNBOOK.md`](../project/questlog/deploy/DEPLOY_RUNBOOK.md)
"Phase 6 — Go live and verify" section — it restates every check above
plus the negative checks (port 8000 and 5432 unreachable from outside)
Lesson 07 already introduced, as one final, complete pass.

## What this deploy deliberately does not yet do (and why)

Be honest with yourself about this list — it's not a list of things you
did wrong, it's this module's stated, deliberate scope boundary:

- **No HTTPS.** The site is plain `http://`, meaning traffic (including
  the login password, in transit) is not encrypted. A real production
  deployment would never ship this way — Module 11 adds a real domain
  name and a free TLS certificate (via Let's Encrypt/Certbot), which
  requires owning a domain, which this module never assumed you have.
- **Fully manual, with no memory of what was done.** If this server were
  destroyed right now, reproducing it means re-reading and re-typing
  every command in this lesson and Lesson 07, by hand, hoping nothing
  was forgotten. Module 10 (Docker) packages the backend and its exact
  dependencies into a single, reproducible image; Module 11 (CI/CD)
  automates the entire deploy sequence so it runs identically, every
  time, on every push.
- **One backend process, one database, one server, no redundancy.** If
  this one VPS goes down, or the one Uvicorn process crashes in a way
  `systemd`'s `Restart=on-failure` can't recover from (e.g. the disk
  fills up), QuestLog is entirely offline until a human intervenes. This
  is an accepted, reasonable trade-off at a learning project's scale —
  Lesson 06's load-balancer discussion is exactly what a real production
  system would add first, once this stops being acceptable.
- **No monitoring, alerting, or centralized logging beyond `journalctl`
  on this one box.** You'd only find out something's wrong by manually
  checking. Module 11 covers this properly.

Every one of these is a deliberate, named gap — not an oversight — and
each one is the specific reason the next two modules exist at all. This
is the payoff of "the painful way, on purpose": you now know, from
direct, first-hand experience, exactly what problem each of Docker and
CI/CD is solving, instead of taking it on faith.

## Common mistakes & gotchas

- **The site loads but shows a blank white page, no errors visible in
  the page itself.** Almost always a JavaScript error — open the
  browser's console (not just Network tab) and look for a red error;
  the most common cause at this exact step is `VITE_API_BASE_URL` not
  actually having been built empty (recheck Step 1's `grep` verification).
- **The frontend loads and looks correct, but every API call fails with
  a network error, and the Network tab shows the request going to
  `http://localhost:8000/...` instead of your server's own address.**
  The `dist/` folder currently deployed was built *before* Step 1's
  environment variable was set correctly, or an old cached `dist/` got
  copied by mistake — rebuild with the exact command shown and re-`scp`
  it.
- **`sudo nginx -t` passes, `systemctl reload nginx` succeeds, but the
  site still shows Ubuntu's default "Welcome to nginx!" page.** The
  default site (`/etc/nginx/sites-enabled/default`) is still present —
  Step 3's `rm -f` step was skipped or failed silently (confirm with
  `ls /etc/nginx/sites-enabled/`).
- **Everything works over HTTP but a browser shows a security warning
  or refuses to load a resource.** Expected and correct, given this
  module's stated scope — this is plain HTTP with no TLS at all; that
  warning is your browser correctly telling you the truth. Do not "fix"
  this by trying to force HTTPS without a real certificate — Module 11
  covers doing this properly.

## How this connects

This is the end of the running capstone for this module — everything
QuestLog has been through Modules 04–08 is now reachable, for real, from
a real public IP address. Module 10 picks up here directly: it
containerizes exactly this backend and this Postgres setup so the "get a
fresh copy of QuestLog running correctly" process this lesson and Lesson
07 just walked through by hand becomes a single `docker compose up`
command instead. Module 11 automates the entire deploy sequence itself,
including adding the HTTPS this module explicitly left out.

## Quick self-check

1. Why does this deploy build the frontend on your own machine instead of the server, and what specific, concrete problem in this exact codebase's `package.json` supports that choice (beyond just "it's standard practice")?
2. What does `VITE_API_BASE_URL=` (built empty) actually change about the requests QuestLog's frontend makes, and how would you confirm it worked by inspecting a real request in a browser?
3. Why is removing Ubuntu's default Nginx site a necessary step, not just tidiness?
4. Name three things this deploy deliberately does not do yet, and which later module is responsible for each one.
5. If the deployed site shows a blank page with no visible error on the page itself, what's the very first thing you should check, and where?
