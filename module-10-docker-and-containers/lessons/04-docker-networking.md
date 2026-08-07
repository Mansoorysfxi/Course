# Lesson 04 — Docker Networking, Explained Minutely

**Verified against (August 2026):** the specific behavior described below
(the default `bridge` network has no automatic container-name DNS
resolution; user-defined networks — including the one `docker compose`
creates automatically for every project — do) is long-standing, stable
Docker Engine behavior, confirmed against Docker's own current networking
documentation while writing this lesson, not a fast-moving version-
specific fact.

## What you'll learn

- What a container's own, private network namespace actually is (tying
  directly back to Lesson 01's namespaces explanation).
- The real difference between `EXPOSE` (documentation) and `-p`/
  `--publish` (an actual mapping) — a distinction Lesson 01 used without
  fully explaining.
- How two separate containers find and talk to each other at all, given
  that each one believes it's alone on the machine.
- Why Docker's **default** network doesn't support finding a container
  by name, and why **user-defined** networks (including the one Compose
  creates automatically) do.
- How to build a genuine mental model for `docker-compose.yml`'s
  `http://backend:8000`-style URLs (Lesson 06 onward), instead of
  treating them as unexplained magic strings.

## Why this matters

Every one of QuestLog's Compose services (Lesson 06 onward) needs to
reach at least one other service by name — the backend needs to reach
`postgres` and `redis`, the frontend's Nginx needs to reach `backend`.
None of that works by accident; it works because of a specific, learnable
mechanism this lesson explains in full, before Lesson 06 asks you to
trust it.

## Prerequisites

- **Lesson 01** — this lesson directly extends the namespaces
  explanation from that lesson, specifically the *network* namespace.
- **Module 09, Lesson 04 (Networking, Ports and IPs)** — this lesson
  assumes you remember what a port is, the difference between
  `127.0.0.1` and `0.0.0.0` as a bind address, and what DNS resolves —
  this lesson applies all three ideas one level further in, inside
  Docker's own private networking layer.

## The concept, explained simply

Recall Lesson 01: a container has its own, private **network
namespace** — its own view of network interfaces, its own routing table,
its own `localhost`. This has a very concrete, sometimes surprising
consequence: **a container's `127.0.0.1`/`localhost` refers only to
itself** — never to your host machine, and never to any other container,
no matter how "close" they seem. This is exactly why Module 09's Nginx
(a real process on a real server, sharing the server's *one* `localhost`
with the backend) could reach the backend at `http://127.0.0.1:8000` —
but this module's containerized Nginx (`frontend/nginx.conf`) cannot use
that same address at all, because it's now a *separate* container with
its *own*, different, private `localhost` that has nothing listening on
port 8000.

**Game-dev analogy:** picture several game-server processes, each
running inside its own sandboxed, network-namespaced environment (much
like separate matches on a dedicated server farm) — each one has its own
private idea of "this machine," and a process in Match A can't just say
"connect to localhost" and expect to reach Match B's server, even though
both are, physically, running on the exact same underlying hardware.
They need a real, addressable way to find each other — which is exactly
what a Docker network provides.

## The details

### `EXPOSE` vs. `-p`/`--publish` — documentation vs. an actual mapping

A Dockerfile's `EXPOSE 8000` instruction (seen already in
`backend/Dockerfile`) does **not**, by itself, make anything reachable
from anywhere. It is purely **metadata** — a note, readable by a human or
another tool, saying "this image's application listens on port 8000." No
traffic can flow through it on its own. What actually makes a port
reachable **from your host machine** is `docker run`'s `-p`/`--publish`
flag (Lesson 01 already used this: `-p 8081:80`) — an explicit
`host_port:container_port` mapping Docker itself wires up. Try this
directly:

```bash
docker run -d --name expose-only-test nginx:alpine
docker port expose-only-test
```
**Expected:** no output at all — `EXPOSE 80`, baked into the official
`nginx` image itself, published nothing, because this `docker run`
included no `-p` flag.
```bash
curl http://localhost:80
```
**Expected:** connection refused/times out — proof nothing on your own
host machine is actually listening there.
```bash
docker rm -f expose-only-test
docker run -d --name published-test -p 8083:80 nginx:alpine
curl http://localhost:8083
```
**Expected:** Nginx's real welcome page — this time, because `-p`
actually created the mapping. **The lesson: `EXPOSE` is a hint; `-p` is
the mechanism.**

### Container-to-container: the default `bridge` network's real limitation

Every container, unless told otherwise, joins Docker's **default bridge
network** — a private virtual network Docker itself manages, giving each
container its own private IP address on it. Try reaching one container
from another, by name, on this default network:

```bash
docker run -d --name web-a nginx:alpine
docker run --rm busybox wget -qO- http://web-a
```
**Expected:** this **fails** — something like
`wget: bad address 'web-a'` — even though `web-a` is a real, running
container. This is the real, important gotcha this lesson exists to
explain: **the default bridge network provides no automatic DNS
resolution by container name at all.** Two containers on it can only
reach each other by raw IP address (discoverable, but inconvenient and
liable to change), never by name.

### User-defined networks: name-based DNS, for real

Create your own network instead:
```bash
docker network create demo-net
docker rm -f web-a
docker run -d --name web-a --network demo-net nginx:alpine
docker run --rm --network demo-net busybox wget -qO- http://web-a
```
**Expected:** this time, real HTML output — `<!DOCTYPE html>...Welcome
to nginx!...` — proof `web-a` resolved correctly to that container's own
address, purely because both containers are on the same **user-defined**
network. Docker automatically runs a small internal DNS server for every
user-defined network it creates, resolving every container's own `--name`
to its current address on that specific network — no manual `/etc/hosts`
editing, no hardcoded IPs, and correct even if a container is removed and
recreated with a new IP address later (as long as it keeps the same
name).

**This is the entire mechanism behind `docker-compose.yml`'s
`http://backend:8000` and `http://redis:6379` URLs** (Lesson 06 onward):
`docker compose` automatically creates exactly one user-defined network
per project and attaches every service to it, giving each one this exact
same name-based DNS resolution for free — `backend`, `postgres`, and
`redis` are every bit as real and resolvable as `web-a` was here, for
precisely the reason just demonstrated.

**Try it yourself, before cleaning up:** run
`docker network inspect demo-net` and find the exact `"IPv4Address"`
Docker assigned to `web-a` inside its `"Containers"` section. Then run
`docker run --rm --network demo-net busybox wget -qO- http://<that IP address>`
(substituting the real address you found) and confirm it works too —
proof that name-based DNS resolution is a *convenience* layered on top
of real IP addressing, not a replacement for it; both ways of reaching
`web-a` work simultaneously, for the same underlying reason.

Clean up:
```bash
docker rm -f web-a
docker network rm demo-net
```

### Inspecting a network directly

```bash
docker network ls
```
**Expected:** a table including Docker's own built-in `bridge`, `host`,
and `none` networks, alongside any user-defined ones you've created (like
`demo-net`, if you haven't removed it yet).

```bash
docker network inspect bridge
```
**Expected:** a JSON document, including a `"Containers"` section listing
every container currently attached to it, each with its own assigned
`"IPv4Address"` — direct, checkable proof that every container really
does get its own private address on this virtual network.

## Common mistakes & gotchas

- **A container's own code hardcodes `http://localhost:PORT` to reach
  "the other service" and mysteriously fails once both are
  containerized**, despite working perfectly when both ran as plain
  processes on the same machine (exactly Module 09's setup). This is the
  single most common Docker networking mistake, and this lesson's whole
  first section exists because of it: `localhost` inside a container
  means *that container*, never a sibling container. Use the sibling
  container's **service name** (Compose) or **`--name`** (plain `docker
  run` on a shared user-defined network) instead.
- **Expecting `EXPOSE` alone to make a service reachable from your
  browser.** It doesn't — see this lesson's first section. You need an
  actual `-p`/`--publish` (plain `docker run`) or a `ports:` entry
  (`docker-compose.yml`, Lesson 06) for that.
- **Two containers on the *default* bridge network trying to reach each
  other by name**, copying a pattern that works fine once Compose is
  involved (Compose networks *do* support this) but fails on the default
  bridge specifically, for the exact reason demonstrated above.
- **Forgetting to `docker network rm` a network that still has attached
  containers.** Docker refuses, with an error naming which container is
  still using it — remove or disconnect the container(s) first.

## How this connects

This lesson explains exactly why `docker-compose.yml`'s service names
work as hostnames at all (Lesson 06 onward) and why `frontend/nginx.conf`
(Lesson 08) correctly targets `http://backend:8000` instead of
`http://127.0.0.1:8000`, the address Module 09's non-containerized Nginx
correctly used instead. Lesson 05 shifts from networking to storage — how
a container's data can (or can't) survive that container being removed
and recreated, the other half of "what changes when you containerize
something you used to run directly."

## Quick self-check

1. Why did `wget http://web-a` fail on Docker's default bridge network,
   but succeed once both containers were on a user-defined network
   instead?
2. What is the actual difference between what `EXPOSE` does and what
   `-p`/`--publish` does?
3. If QuestLog's containerized backend tried to reach Postgres at
   `postgresql+asyncpg://.../@localhost:5432/questlog` instead of
   `@postgres:5432/questlog`, what would actually happen, and why?
4. What creates the Docker network `docker-compose.yml`'s services all
   share, and when, exactly, is it created?
5. Does a container's own `EXPOSE`'d port need to match the `-p`
   mapping's container-side port number? Why or why not?
