# Lesson 05 — Docker Volumes and Persistence, Explained Minutely

**Verified against (August 2026):** the volume/bind-mount mechanics
described here are stable, long-standing Docker Engine behavior,
confirmed against Docker's own current storage documentation while
writing this lesson.

## What you'll learn

- Why a container's own filesystem is, by default, **ephemeral** —
  gone the moment that specific container is removed.
- The two ways to make data outlive a container: **named volumes** and
  **bind mounts**, and when to reach for each.
- How to prove, hands-on, that a named volume genuinely survives a
  container being removed and recreated.
- Exactly how `docker-compose.yml`'s `questlog_pgdata` volume (Lesson 06
  onward) is what makes QuestLog's Postgres data survive
  `docker compose down` and a rebuild.

## Why this matters

Without this lesson, `docker-compose.yml`'s `volumes:` section (Lesson 06
onward) would look like unexplained boilerplate. With it, you'll know
*exactly* what happens to QuestLog's quests the moment you run
`docker compose down` versus `docker compose down -v`, and why those two
commands behave so differently.

## Prerequisites

- **Lesson 01** — this lesson assumes comfort with `docker run`,
  `docker rm`, and the container lifecycle that lesson introduced.
- **Module 06's PostgreSQL lesson** — a rough sense of what a database's
  own on-disk data files are (this lesson doesn't require deep Postgres
  internals knowledge, just the idea that a running Postgres process
  reads/writes real files somewhere on disk).

## The concept, explained simply

Every container gets its own thin, writable filesystem layer, sitting on
top of its image's own read-only layers (Lesson 02). Anything a running
container writes — a log file, an uploaded image, a database's own data
files — lands in this writable layer, **specific to that one container**.
The moment that container is removed (`docker rm`, or implicitly by
`docker compose down` for containers Compose created), this writable
layer is deleted along with it — permanently, with no undo.

**Game-dev analogy:** this is exactly the relationship between a game's
packaged build and a player's save file. Reinstalling (or updating) the
build shouldn't, and normally doesn't, erase the player's saved progress
— because a well-designed game keeps save data somewhere *outside* the
build's own installation folder specifically so the two can be managed
independently. A Docker **volume** is that same idea, applied to
containers: a place to keep data that needs to outlive the disposable
container (the "build") writing to it.

## The details

### Proving data loss, first, on purpose

```bash
docker run -d --name data-test alpine sleep 3600
docker exec data-test sh -c "echo 'important data' > /data.txt"
docker exec data-test cat /data.txt
```
**Expected:** `important data` — the file genuinely exists, inside this
container's own writable layer.

```bash
docker rm -f data-test
docker run -d --name data-test alpine sleep 3600
docker exec data-test cat /data.txt
```
**Expected:** `cat: can't open '/data.txt': No such file or directory`.
Even though the second container has the exact same name and comes from
the exact same image, it is a **completely new, separate container**,
with its own, brand-new, empty writable layer — `data.txt` was never
part of the `alpine` image itself; it only ever existed in the first
container's own now-deleted writable layer.

```bash
docker rm -f data-test
```

### Fixing it with a named volume

```bash
docker volume create demo-data
docker run -d --name data-test -v demo-data:/data alpine sleep 3600
docker exec data-test sh -c "echo 'important data' > /data/file.txt"
docker rm -f data-test
docker run -d --name data-test -v demo-data:/data alpine sleep 3600
docker exec data-test cat /data/file.txt
```
**Line by line:** `docker volume create demo-data` creates a **named
volume** — a storage location Docker itself manages (on Linux, physically
somewhere under `/var/lib/docker/volumes/`, though you should never need
to touch that path directly — always go through Docker's own volume
commands). `-v demo-data:/data` (equivalently `--mount
source=demo-data,target=/data`) mounts that named volume at `/data`
*inside* the container — anything written to `/data` is actually being
written into the volume, not into the container's own disposable
writable layer.

**Expected:** `important data` — this time, the second, brand-new
container can read a file it never itself created, because both
containers shared the *same* named volume, and the volume itself was
never deleted by `docker rm -f`.

```bash
docker rm -f data-test
docker volume ls
```
**Expected:** `demo-data` still appears — removing the *container* never
removes a named volume; that's a separate, deliberate action:
```bash
docker volume rm demo-data
```
**Expected:** `demo-data` removed. `docker volume ls` now shows it's
gone — and with it, permanently, `file.txt`'s contents.

### Named volumes vs. bind mounts

A **named volume** (used above) is entirely Docker-managed — you never
need to know or care exactly where on your host's disk it physically
lives; you refer to it purely by name, and Docker guarantees it's the
same volume every time.

A **bind mount** instead maps a *specific folder you choose, on your own
host machine*, directly into a container:
```bash
mkdir -p /tmp/bind-demo
docker run -d --name bind-test -v /tmp/bind-demo:/data alpine sleep 3600
docker exec bind-test sh -c "echo 'from a container' > /data/note.txt"
cat /tmp/bind-demo/note.txt
```
**Expected:** `from a container` — printed directly by your **host's**
own `cat`, proving the container really did write straight into a real,
ordinary folder on your host filesystem, one you chose and can see
directly without going through any Docker command at all.

```bash
docker rm -f bind-test
```

**Try it yourself:** create a named volume and start **two** containers
at the exact same time, both mounting it (`docker run -d --name writer-a
-v shared-data:/data alpine sleep 3600` and `docker run -d --name
writer-b -v shared-data:/data alpine sleep 3600`). Use `docker exec` to
have `writer-a` create a file, then confirm `writer-b` can immediately
read it too. Now predict: if both containers tried appending to the
*exact same* file at the *exact same* instant, would Docker prevent the
two writes from corrupting each other? (It would not — a volume is
shared storage, nothing more; whatever's writing to it is entirely
responsible for its own concurrency safety, exactly as if two ordinary
processes on a real server both opened the same file directly.) Clean up
both containers and `shared-data` when done.

**When to use which:** this course's `docker-compose.yml` (Lesson 06
onward) uses **named volumes** for `questlog_pgdata` and
`questlog_redisdata` — the right choice whenever you don't need to
directly, manually browse or edit the data from outside a container, and
want Docker itself to manage exactly where the data physically lives. A
bind mount is the right choice when you specifically *do* want that —
the most common real example, seen constantly in professional local
development (though not needed anywhere in this specific module's own
Compose file), is bind-mounting your own source code folder into a
container so a dev server running inside it picks up your file edits
live, without rebuilding the image on every change.

## Common mistakes & gotchas

- **Confusing "the container was removed" with "the data is gone,"
  when a volume was actually involved.** As demonstrated above, a named
  volume or bind mount specifically decouples the two — always check
  which one applies before assuming data loss (or safety).
- **`docker compose down` "deleting my data" when it shouldn't have.**
  Plain `docker compose down` removes containers and the network Compose
  created, but leaves named volumes alone — only the explicit `-v` flag
  (`docker compose down -v`) additionally removes them. If your data
  really did disappear after a plain `down`, double-check your
  `docker-compose.yml`'s `volumes:` section actually names a volume for
  that service at all (Lesson 06's own worked example shows exactly what
  this should look like).
- **Two containers writing to the same named volume simultaneously,
  assuming Docker handles any conflicts for you.** It doesn't — a named
  volume is just shared storage; whatever's writing to it (Postgres, in
  QuestLog's case) is responsible for its own concurrent-access safety,
  exactly the same as if two processes on a real server both tried
  writing to the same real folder.
- **Trying to directly edit files under
  `/var/lib/docker/volumes/.../_data` by hand**, from your host, for a
  named volume. Technically possible on native Linux, but fragile and
  discouraged — you're bypassing Docker's own management of that path
  entirely, and (on Windows/WSL2 specifically) that path lives inside
  Docker Desktop's own internal VM, not somewhere your regular Windows
  filesystem can browse to at all. Use `docker exec` into a container
  that already has the volume mounted instead, exactly as this lesson's
  own examples did.

## How this connects

This lesson directly explains `docker-compose.yml`'s
`questlog_pgdata`/`questlog_redisdata` named volumes (Lesson 06 onward):
without them, every `docker compose down` (which removes containers)
would silently wipe every quest QuestLog's Postgres container ever
stored, and every `docker compose up --build` afterward would start from
a completely empty database — obviously unacceptable for anything beyond
a five-minute demo. Lesson 06 is where this module shifts from
individual `docker run`/`docker network`/`docker volume` commands to
`docker-compose.yml`, the one file that describes an entire multi-service
application, networking and volumes included, at once.

## Quick self-check

1. What specifically happens to a container's own writable layer the
   moment that container is `docker rm`'d?
2. What's the practical difference between a named volume and a bind
   mount, in terms of *where* the data actually lives and how you'd find
   it?
3. Does `docker compose down` (no flags) delete named volumes? Does
   `docker compose down -v`? What's the practical consequence of each,
   for QuestLog's own Postgres data specifically?
4. If two separate containers both mount the same named volume, do they
   see the same files, or separate copies?
5. Why does this course use a named volume, not a bind mount, for
   QuestLog's Postgres data specifically?
