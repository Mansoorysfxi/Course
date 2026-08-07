# Exercise 06 — Write a docker-compose.yml From Scratch: App + Redis (Independent)

**Concepts this exercise uses (all taught in
[`lessons/06-docker-compose-multi-service-apps.md`](../../lessons/06-docker-compose-multi-service-apps.md)):**
`services:`, `build:`, `image:`, `ports:`, `environment:`,
`depends_on:` with `condition: service_healthy`, `healthcheck:`, no
top-level `version:` key, `docker compose up --build`/`down`.

**Where to work:** `exercises/06-compose-two-services/starter/` — a real
app (`app/app.py`) that increments a per-quest-name counter in Redis
every time `/check?quest=<name>` is requested, and returns the new
count. **There is no `docker-compose.yml` in this folder at all — you
are writing one from scratch.** This is the last exercise before this
module's capstone (`project/BRIEF.md`), which asks you to write a
similar, larger Compose file for QuestLog's real four-service stack —
treat this exercise as that capstone's dress rehearsal.

## Your task

In `starter/` (alongside the `app/` folder, not inside it), write a
`docker-compose.yml` defining **two** services:

1. **`app`** — built from the `./app` folder (it has its own
   `Dockerfile` already). Must:
   - Publish port `5000` inside the container to port **5001** on your
     host.
   - Set an environment variable telling `app.py` how to reach Redis
     (re-read `app/app.py` — it reads `REDIS_HOST` from the environment,
     defaulting to `localhost`, which will **not** work once Redis is a
     separate container — see Lesson 04 if you're unsure why).
   - Not start until Redis reports genuinely healthy, not merely
     started.
2. **`redis`** — using the official `redis:8-alpine` image. Must:
   - Include a `healthcheck:` using `redis-cli ping`, matching Lesson
     06's own worked example.

Do **not** add a `version:` key at all — Lesson 06's own header explains
why current `docker compose` doesn't need or want one.

## Verify it yourself

```bash
cd exercises/06-compose-two-services/starter
docker compose up --build
```
**Expected:** `redis` reports healthy in the logs before `app` starts at
all (confirm this ordering by watching the log timestamps).

In another terminal:
```bash
curl "http://localhost:5001/check?quest=Slay+the+Dragon"
curl "http://localhost:5001/check?quest=Slay+the+Dragon"
curl "http://localhost:5001/check?quest=Gather+Herbs"
```
**Expected output, in order:**
```
'Slay the Dragon' has been checked 1 time(s).
'Slay the Dragon' has been checked 2 time(s).
'Gather Herbs' has been checked 1 time(s).
```
(two independent counters, correctly kept separate by quest name — proof
your `app` service is genuinely reaching the real `redis` service by
name, not silently falling back to `localhost` and failing).

```bash
docker compose restart app
curl "http://localhost:5001/check?quest=Slay+the+Dragon"
```
**Expected:** `3` — proof the count survived the `app` container being
restarted, because it was never stored there in the first place (exactly
Lesson 06's own toy counter demonstration, now written by you).

```bash
docker compose down
```

## Acceptance criteria

- [ ] Your `docker-compose.yml` has no top-level `version:` key.
- [ ] `docker compose up --build` starts `redis` before `app` (confirmed
      via `depends_on`'s healthcheck-based condition, not just
      coincidental timing).
- [ ] Two separate quest names produce two independent, correctly
      incrementing counters.
- [ ] The counter survives `docker compose restart app`.
- [ ] You can point to the exact line in your `docker-compose.yml` that
      makes `REDIS_HOST` resolve correctly, and explain, in terms of
      Lesson 04's own networking material, *why* it resolves at all.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 06's own toy "visit counter" example is structurally almost
identical to what this exercise wants — same `depends_on`/
`condition: service_healthy` pattern, same `healthcheck:` block for
Redis. The main difference here is you also need an `environment:` entry
this exercise's own app requires that the lesson's own example didn't.

</details>

<details>
<summary>Hint 2</summary>

`environment:` can be written as a YAML list (`- KEY=value`) or a
mapping (`KEY: value`) — both are valid; this module's own real
`project/questlog/docker-compose.yml` (which you'll see in the capstone)
uses the mapping form.

</details>

<details>
<summary>Hint 3</summary>

If `curl` gets a connection-refused error even after `docker compose up`
finishes, double check your `ports:` mapping is `"5001:5000"`
(host:container) and not accidentally reversed.

</details>

A reference solution is in `solution/`.
