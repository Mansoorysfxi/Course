# Lesson 06 — Nginx and Reverse Proxies

**Verified against (August 2026), via live web search:** Nginx's current
**stable** release is **1.30.4** (released July 15, 2026; the parallel
**mainline** branch is at 1.31.3, same release date) — confirmed against
`nginx.org`'s own news page and release listings. Ubuntu 24.04's own
`apt` repository, however, ships a considerably older packaged version,
**1.24.0** (with Ubuntu's own backported security patches, currently at
patch level `1.24.0-2ubuntu7.15`) — confirmed against `packages.ubuntu.com`.
This lesson deliberately installs via `apt` (the older, Ubuntu-packaged
1.24.0) rather than Nginx's own upstream repository, and explains why,
below — the reverse-proxy configuration syntax this lesson teaches
(`location`, `proxy_pass`, `proxy_set_header`) is unchanged between these
versions and has been stable in Nginx for many years.

## What you'll learn

- What Nginx actually is, and the specific job it does that's separate
  from what Uvicorn (or any application server) does.
- What a **reverse proxy** is, mechanically — not "it sits in front,"
  but exactly what request comes in, what Nginx does with it, and what
  goes out the other side.
- How to write a real Nginx server block, including the single most
  common, most confusing reverse-proxy configuration mistake almost
  every beginner (and plenty of experienced engineers) hits at least
  once.
- How to serve a built static frontend (React's `dist/` folder) directly
  from Nginx, including the specific configuration a client-side-routed
  single-page app needs and *why* plain static-file serving alone breaks
  it.
- What a **load balancer** is, conceptually, and when a project actually
  needs one — without setting one up, which is this module's explicitly
  stated scope boundary.

## Why this matters

This is the module's "classic magic spot": nearly every tutorial that
mentions putting "Nginx in front of your app" treats it as an
unquestioned incantation — copy this config, restart Nginx, done. This
lesson opens the hood completely. By the end, "reverse proxy" should
mean something as concrete and mechanically clear to you as "middleware"
already does from Module 05, not a vague piece of infrastructure
folklore.

## Prerequisites

- `lessons/04-networking-ports-and-ips.md` — ports and bind addresses,
  used constantly below.
- `lessons/05-firewalls-with-ufw.md` — this lesson's Nginx install
  registers the `ufw` app profiles that lesson referenced.
- Module 07's CORS lesson
  (`module-07-auth-security/lessons/10-cors-in-depth.md`) — this
  lesson's payoff (same-origin frontend + API) directly resolves the
  cross-origin problem that lesson described.

## The concept, explained simply

Think back to Module 05's middleware analogy: "middleware is like a
component in the actor tick chain — every request passes through it
before reaching the handler." A **reverse proxy** is that same idea, one
level up the stack, running as a completely separate program in front of
your *entire application*, not inside it. Here's a closer, more
literal analogy for this specific module: think of Nginx as a
**matchmaking/lobby server** in a multiplayer game, and Uvicorn (running
QuestLog's actual FastAPI code) as the **dedicated game server instance**
that does the real gameplay simulation. Players (browsers) never connect
directly to a specific dedicated server instance's raw address — they
connect to the lobby server, which is the one thing with a well-known,
stable public address, and the lobby server routes them to whichever
actual game server instance should handle them. Nginx plays exactly this
role for QuestLog: browsers connect to Nginx, on the server's public
IP, on the standard web port (`80`); Nginx decides, based on the request,
whether to hand it off to QuestLog's backend (running privately on
`127.0.0.1:8000`, per Lesson 04) or serve a static frontend file
directly, itself.

**Why not just let Uvicorn listen on port 80 directly, and skip Nginx
entirely?** You technically could — nothing stops FastAPI's Uvicorn
process from binding `0.0.0.0:80` directly. Real deployments virtually
never do this, for several concrete, non-hand-wavy reasons this lesson
demonstrates directly:

1. **One address, multiple things behind it.** A real site typically
   needs to serve a static frontend *and* an API *and*, later, other
   services, all from one public IP on one standard port. Nginx is what
   makes "everything on port 80/443" possible while keeping those pieces
   as separate, independently-restartable processes behind it.
2. **Static files are not Uvicorn's job.** Uvicorn/FastAPI is built to
   run your Python application code — asking it to also efficiently
   serve a folder of built HTML/CSS/JS files is possible but wasteful;
   Nginx is written in C specifically optimized for exactly that task,
   and does it dramatically faster with far less resource use.
3. **A single point for cross-cutting concerns.** TLS/HTTPS termination
   (Module 11), request logging, rate limiting, and compression are all
   things you'd otherwise have to build into your own application code —
   Nginx does all of them, once, in front of everything, so your FastAPI
   code never has to.
4. **It's the standard, expected shape.** Virtually every production web
   deployment you'll ever work on professionally puts *something*
   reverse-proxy-shaped (Nginx, or a cloud load balancer doing the same
   job) in front of the actual application server — recognizing this
   shape instantly, rather than being confused by it, is itself a real,
   practical skill this lesson is teaching.

## The details

### Step 1 — Install Nginx

```bash
sudo apt update
sudo apt install -y nginx
nginx -v
```
**Expected:** `nginx version: nginx/1.24.0 (Ubuntu)` (or your Ubuntu
version's own packaged version — see this lesson's header).

**Why install the older `apt` version instead of upstream's newer
1.30.4?** Three honest, stated reasons: (1) `apt install nginx` is a
single command that also handles the `systemd` service file, log
rotation config, and default directory layout automatically — adding
Nginx's own upstream repository to get 1.30.4 is possible (their docs
cover it) but is genuinely more setup for a difference that doesn't
matter for anything this lesson teaches; (2) Ubuntu backports security
fixes into its own packaged 1.24.0 (note the `-2ubuntu7.15` patch level)
— you are not running an unpatched, insecure version, just an older
*feature* version; (3) every configuration directive this lesson uses
(`location`, `proxy_pass`, `proxy_set_header`) has been stable and
unchanged in Nginx for many years — nothing here requires 1.30.x's
newer features. If you ever need a cutting-edge Nginx feature for a
real project, know that installing upstream's own repository instead of
`apt`'s is the documented path — just not needed here.

Confirm it's already running (Ubuntu's `apt install nginx` starts it
automatically):
```bash
sudo systemctl status nginx
```
**Expected:** `Active: active (running)` — Nginx is already a `systemd`
service (Lesson 03's concept, already applied, by Ubuntu's own package,
before you wrote a single unit file yourself this module).

From a second terminal or your Windows browser (if using WSL2 — WSL2's
"mirrored" networking typically makes `localhost` reach WSL2 services
directly from Windows; check `hostname -I` inside WSL2 and use that
address in your browser if `localhost` doesn't work):
```bash
curl http://localhost/
```
**Expected:** a chunk of HTML starting with
`<!DOCTYPE html>\n<html>\n<head>\n<title>Welcome to nginx!</title>` —
Nginx's own default placeholder page, proving it's alive and serving
something, before you've written a single line of config.

### Step 2 — A minimal reverse proxy, from scratch

Nginx's site configuration files live in `/etc/nginx/sites-available/`,
and are made "live" by a symlink into `/etc/nginx/sites-enabled/` — a
pattern deliberately similar to `systemd`'s `enable` mechanism from
Lesson 03 (a unit file existing isn't enough; it also has to be
linked/enabled to actually take effect). Start QuestLog's backend, bound
to `127.0.0.1` this time (the correct, private bind address, per Lesson
04, since only Nginx — on the same machine — needs to reach it):

```bash
cd module-09-linux-networking-servers/project/questlog/backend
source .venv/Scripts/activate   # or your venv's activate path
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Leave that running. In a second terminal, write a new site config:

```bash
sudo nano /etc/nginx/sites-available/questlog-practice
```

```nginx
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Line by line:**
- `listen 80;` — accept connections on port 80, the well-known HTTP port
  (Lesson 04), on every interface Nginx itself binds to by default.
- `server_name _;` — the "catch-all" server name, meaning "match this
  block regardless of what `Host` header the request carries" —
  appropriate here since this practice server has no real domain name
  yet (Module 11 introduces real domains). A production config with a
  real domain would instead write `server_name questlog.example.com;`.
- `location /api/ { ... }` — a **location block**: a rule matching
  requests whose path starts with `/api/`. Every request landing here
  gets everything inside this block applied to it, and nothing outside.
  Not every `location` block has to `proxy_pass` somewhere else — a
  block can instead contain a bare `return <code>;`, which makes Nginx
  immediately send back that HTTP status code (and, optionally, a body)
  with no proxying and no file lookup involved at all — useful any time
  you want a `location` to deliberately produce a fixed, simple response
  (a `location / { return 404; }` catch-all for "nothing else matched,"
  for instance) rather than serving a real file or forwarding to a
  backend.
- `proxy_pass http://127.0.0.1:8000;` — **the single line doing the
  actual reverse-proxying.** For every request matched by this
  `location` block, Nginx opens its *own*, separate HTTP connection to
  `127.0.0.1:8000` (QuestLog's Uvicorn process), forwards the request
  there, waits for Uvicorn's response, and relays that response back to
  the original client — the client never talks to Uvicorn directly at
  any point; as far as the browser is concerned, it only ever spoke to
  Nginx, on port 80.
- `proxy_set_header Host $host;` — by default, the request Nginx forwards
  to Uvicorn would carry a `Host` header describing *Nginx's own*
  internal address (`127.0.0.1:8000`) instead of the original `Host` the
  browser actually requested — this line preserves the original,
  overwriting Nginx's default. `$host` is one of Nginx's built-in
  **variables**, evaluated per-request.
- `proxy_set_header X-Real-IP $remote_addr;` and
  `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` — solve
  a real, easy-to-miss problem: from Uvicorn/FastAPI's own point of view,
  *every single request* now appears to originate from `127.0.0.1` (since
  that's literally who's connecting to it — Nginx, not the real
  visitor), which would make QuestLog's own logs, or any future rate-
  limiting-by-IP feature, completely useless — every visitor would look
  identical. These two headers carry the *real* original client IP
  address through, as plain HTTP headers, so the backend application can
  read them if it needs to (FastAPI doesn't do this automatically —  a
  real production app would read `X-Forwarded-For` explicitly wherever
  it currently uses the raw connection's IP, which is outside this
  particular capstone's scope but worth knowing exists).
- `proxy_set_header X-Forwarded-Proto $scheme;` — similarly tells the
  backend whether the *original* request was HTTP or HTTPS, since
  (Module 11) Nginx itself will eventually be the only thing terminating
  HTTPS — Uvicorn, behind it, only ever sees plain HTTP either way.

Enable this site and reload Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/questlog-practice /etc/nginx/sites-enabled/
sudo nginx -t
```

**Expected from `nginx -t`:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```
**Always run `nginx -t` before reloading** — it validates every config
file's syntax without actually applying anything, catching a typo before
it can break a currently-working server. Only once it passes:

```bash
sudo systemctl reload nginx
```
(`reload`, not `restart` — `reload` tells Nginx to re-read its config
and gracefully finish in-flight requests on the old config before
switching, with zero dropped connections; `restart` fully stops and
starts the process, briefly dropping anything mid-flight. Prefer
`reload` whenever only the config changed.)

Now, **through Nginx, on port 80**, not directly to Uvicorn's 8000:

```bash
curl http://localhost/api/auth/login -X POST \
  -d "username=player@questlog.local&password=dragon-slayer-1"
```

**Expected:** the exact same JSON access-token response Module 07's own
`curl` command produced talking directly to port 8000 — proving the
request genuinely traveled browser → Nginx (port 80) → Uvicorn (port
8000, privately) → back through Nginx → to you, with the response
completely unchanged along the way.

### Step 3 — The single most common reverse-proxy mistake: the trailing slash

This is worth its own step because it trips up almost everyone at least
once, and the two configs *look* nearly identical. Compare:

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;     # (A) — no path after the port
}
```
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;     # (B) — trailing slash after the port
}
```

These behave **differently**, and the difference is exactly whether
Nginx **strips** the `location` block's own matched prefix (`/api/`)
before forwarding. With **(A)** (no URI part at all after the host:port
in `proxy_pass`), Nginx forwards the **entire original URI unchanged** —
a request for `/api/quests` arrives at Uvicorn as `/api/quests`, exactly
matching what FastAPI's own routes expect (recall QuestLog's routes are
themselves defined starting with `/api/...`). With **(B)** (a trailing
`/`, which counts as "a URI part, even an empty one, was given"), Nginx
**replaces** the matched `/api/` prefix with that URI part before
forwarding — a request for `/api/quests` would arrive at Uvicorn as
`/quests` (the `/api/` prefix stripped and replaced by the trailing `/`),
which does **not** match any of FastAPI's actual routes, producing a
mysterious `404 Not Found` that has nothing to do with your Python code
at all. **This module's config deliberately uses form (A)** because
QuestLog's own backend already expects the `/api/` prefix on every
route — there's no stripping to do. Getting this backwards is genuinely
the single most-reported real-world Nginx reverse-proxy bug, precisely
because both forms look almost identical and Nginx gives no warning
either way — it's valid syntax regardless of which one you meant.

**Try it yourself:** change the config to form (B), `nginx -t`,
`systemctl reload nginx`, then retry the `curl` command from Step 2.
Confirm you now get a `404` (add `-i` to `curl` to see the status line),
then put it back to form (A) and confirm it works again. Seeing this
exact failure once, on purpose, makes it dramatically easier to
recognize instantly for the rest of your career.

### Step 4 — Serving a built frontend, and why SPA routing needs `try_files`

Build the frontend for real (production build, not the dev server):

```bash
cd module-09-linux-networking-servers/project/questlog/frontend
VITE_API_BASE_URL= npm run build
```

**Line by line:** setting `VITE_API_BASE_URL=` to an **empty** string
(rather than leaving it unset, which would fall back to
`http://localhost:8000` per `src/api/http.ts`) makes every API call in
the built app use a *relative* path (`/api/auth/login`, exactly as
written in `authApi.ts`) instead of an absolute one — meaning the
browser will send it to whatever origin actually served the page it's
running on. This is the **entire mechanism** by which putting the
frontend and the API behind the same Nginx, on the same origin, makes
CORS (Module 07, Lesson 10) irrelevant here: there is no cross-origin
request happening at all anymore, because both now share one origin —
Nginx's own address, whether that's `localhost` right now or the real
VPS's IP/domain in the capstone. **No QuestLog application code changed
to achieve this** — only a build-time environment variable.

**Expected:** `npm run build` produces `frontend/dist/`, containing
`index.html`, a `assets/` folder of hashed `.js`/`.css` bundles, and
`favicon.svg`. Copy it somewhere Nginx can read (a real deploy path,
Lesson 07/08 uses `/var/www/questlog`; for this practice, anywhere
readable works):

```bash
sudo mkdir -p /var/www/questlog-practice
sudo cp -r dist/* /var/www/questlog-practice/
```

Update the site config to also serve this, alongside the existing
`/api/` proxy:

```nginx
server {
    listen 80;
    server_name _;

    root /var/www/questlog-practice;
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

**Line by line, the new pieces:**
- `root /var/www/questlog-practice;` — the folder Nginx serves static
  files from, for any `location` block that doesn't otherwise proxy
  somewhere else.
- `location / { try_files $uri /index.html; }` — matches everything
  *not* already claimed by the more specific `/api/` block above (Nginx
  matches the most specific `location` prefix, not simply top-to-bottom).
  `try_files $uri /index.html;` means: "first, try to serve a real file
  at exactly this path (`$uri`) from `root` — if `index.html`,
  `assets/index-abc123.js`, `favicon.svg`, whatever actually exists,
  serve it directly; **if no such file exists, serve `/index.html`
  instead**, regardless of what was actually requested."

**Why the fallback to `index.html` is required, specifically, and not
optional:** React Router (Module 04) handles routes like
`/quests/42` entirely in the **browser**, via JavaScript, using the
History API — no page navigation, no new request to the server, when you
click a link *within* the running app. But if a user directly types
`https://yourdomain.com/quests/42` into their browser's address bar (or
refreshes that page, or a bookmark, or a shared link lands there), the
*browser itself* makes a real, brand-new HTTP request for the literal
path `/quests/42` — and there is no real file at that path on disk
(there's no `/quests/42/index.html` — that route only exists as
JavaScript logic, running client-side, that hasn't loaded yet). Without
`try_files`'s fallback, Nginx would correctly, honestly report
`404 Not Found` for a route that, from the user's perspective, is a
perfectly real, working page of the app. `try_files ... /index.html`
serves the **same** `index.html` every real route falls back to — the
one file containing the React app's JavaScript bundle — letting React
Router take over *inside the browser* once that JavaScript loads, read
the actual URL (`/quests/42`) from the browser's own address bar, and
render the correct page client-side. This is a direct, necessary
consequence of QuestLog being a client-side-routed single-page app
(Module 04), not a server-rendered multi-page site — and it's exactly
why this one line is present in essentially every SPA's Nginx config
you'll ever encounter professionally.

**Try it yourself:** with this config live, `curl -i http://localhost/quests/999`
(a route your React app defines, even though quest 999 may not exist as
data) — confirm you get `200 OK` with `index.html`'s content, not a
`404`, proving the fallback works. Then try a genuinely nonexistent
asset path, `curl -i http://localhost/this-file-does-not-exist.png` —
same fallback behavior fires, which is an accepted, standard trade-off
of this exact pattern (a truly missing static asset also "succeeds" with
`index.html`'s content rather than a real 404) that real SPA deployments
universally accept.

### Load balancers, conceptually (no setup required this module)

Everything above assumes **one** Nginx routing to **one** backend
process. A **load balancer** solves a different, later-stage problem:
what happens once one single backend process can no longer keep up with
incoming traffic? The conceptual answer is to run **multiple identical
copies** of the backend process (say, three separate Uvicorn processes,
possibly on three separate machines entirely) and put something in front
of *all of them* that distributes incoming requests across whichever
copy is least busy (or simply round-robin, cycling through each in
turn) — spreading the total load instead of overwhelming one process.
Nginx itself can actually do exactly this (an `upstream` block listing
multiple backend addresses, and `proxy_pass http://that_upstream_name;`
instead of one hardcoded address) — meaning "reverse proxy" and "load
balancer" are not two unrelated technologies but the **same underlying
mechanism** (Nginx forwarding a request somewhere else and relaying the
response) applied to one backend versus several. This module's capstone
runs exactly one backend process, so a load balancer adds no value yet
— but recognizing the shape (one address in front, several equivalent
workers behind it, decided per-request which one handles it) means
you'll immediately understand a load balancer diagram in any future
professional context, rather than treating it as unrelated new magic.
Module 11 mentions this again in the context of real cloud
infrastructure; setting one up for real is out of this course's declared
scope entirely (per `RUNNING_PROJECT.md`, QuestLog never needs one at
its scale).

## Common mistakes & gotchas

- **The trailing-slash `proxy_pass` bug** — see Step 3 in full; this
  deserves repeating as its own bullet because it is genuinely the
  single most common real-world Nginx mistake.
- **`502 Bad Gateway`.** This specific error means Nginx itself is
  working fine and successfully received the request, but the thing it
  tried to `proxy_pass` to (Uvicorn on `127.0.0.1:8000`) refused the
  connection or wasn't there at all — check `sudo systemctl status
  questlog-backend` (Lesson 07) and `journalctl -u questlog-backend`
  first; the problem is almost never Nginx's own config once you've
  confirmed the config already parses (`nginx -t`).
- **`404 Not Found` for every route except `/`.** Almost always a missing
  `try_files $uri /index.html;` fallback — the site works for the exact
  root path (which genuinely has a real `index.html` on disk) but breaks
  for every client-side route, exactly as Step 4 explains.
- **Editing a config file and expecting the change to apply
  immediately, with no reload.** Nginx, like `systemd`, reads
  configuration once at startup (or at the last `reload`) and caches it
  in memory — always `nginx -t` then `sudo systemctl reload nginx` after
  any config edit.
- **Forgetting the symlink into `sites-enabled/`.** A perfectly correct
  file sitting only in `sites-available/` has zero effect — Nginx only
  reads configs actually linked (or copied) into `sites-enabled/`
  (or, on some installs, listed via an `include` directive in the main
  `nginx.conf` — check yours with `cat /etc/nginx/nginx.conf | grep include`
  if a config genuinely seems to be ignored).
- **Leaving Ubuntu's own `default` site enabled alongside a new one, both
  matching `server_name _;` (or both with no `server_name` at all).**
  Nginx picks one deterministically (generally whichever's `listen`
  directive was parsed first, or one marked `default_server`), which can
  look like "my new config is being silently ignored" when it's actually
  just losing to the pre-existing default. Remove or disable
  `/etc/nginx/sites-enabled/default` when a real single-site config
  should be the only one active — the capstone's runbook does this
  explicitly.

## How this connects

This lesson is the mechanical heart of the capstone: Lesson 07 installs
Postgres and gets QuestLog's backend running as a real `systemd`
service (combining Lessons 01–03); Lesson 08 takes exactly this lesson's
reverse-proxy and static-serving config, applied to the real, built
QuestLog frontend and the real backend service, and makes the whole
thing reachable from a real public IP address, protected by exactly
Lesson 05's `ufw` rules.

## Quick self-check

1. What specific job does Nginx do that Uvicorn/FastAPI could technically do itself, but shouldn't, and why not?
2. Walk through, in order, exactly what happens to a single `GET /api/quests` request from the moment a browser sends it to the moment a response arrives back — naming every process and port it passes through.
3. What's the practical difference between `proxy_pass http://127.0.0.1:8000;` and `proxy_pass http://127.0.0.1:8000/;` (with the trailing slash), and why does it matter for QuestLog specifically?
4. Why does a client-side-routed single-page app need `try_files $uri /index.html;`, specifically — what request would fail without it, and why?
5. What is a load balancer, in relation to a reverse proxy — are they different technologies, or the same mechanism applied differently?
