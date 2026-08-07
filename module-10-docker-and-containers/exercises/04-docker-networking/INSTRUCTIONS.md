# Exercise 04 — Two Containers, One Network, Name-Based DNS (Independent)

**Concepts this exercise uses (all taught in
[`lessons/04-docker-networking.md`](../../lessons/04-docker-networking.md)):**
`docker network create`, `docker run --network`, `--name`-based DNS
resolution on a user-defined network, why the **default** bridge network
doesn't support it, `-p`/`--publish` vs. no publishing at all.

**Where to work:** `exercises/04-docker-networking/starter/` — two
separate, tiny apps: `greeter-server/` (an HTTP server) and
`greeter-client/` (a script that makes one HTTP request to a host named
by the `GREETER_HOST` environment variable, defaulting to `localhost`).

This is this module's most independent exercise before the capstone —
no docker-compose.yml involved at all, on purpose (Lesson 06 introduces
Compose; this exercise wants you comfortable with the raw
`docker network`/`docker run --network` mechanics Compose builds on top
of, first).

## Setup

Build both images:
```bash
cd exercises/04-docker-networking/starter
docker build -t greeter-server ./greeter-server
docker build -t greeter-client ./greeter-client
```

## Your task

1. **First, deliberately reproduce the failure** Lesson 04 demonstrated:
   run `greeter-server` on Docker's **default** network (no `--network`
   flag at all), then run `greeter-client` also with no `--network` flag
   and `-e GREETER_HOST=<the server's --name>`. Confirm it prints a
   `FAILED to reach ...` message — this is expected and correct, given
   what Lesson 04 taught about the default bridge network.
2. **Create a user-defined network.**
3. Run `greeter-server` attached to **that** network, given a `--name`.
4. Run `greeter-client` attached to the **same** network, with
   `GREETER_HOST` set to the server's exact `--name` from step 3.
5. Confirm the client successfully receives and prints the server's
   greeting this time.
6. Clean up: remove both containers and the network you created.

## Verify it yourself

**Step 1's expected failure:**
```
Attempting to reach greeter-server at: http://my-server:5000
FAILED to reach http://my-server:5000: <Urlopen error ...>
```

**After steps 2-5, expected success:**
```
Attempting to reach greeter-server at: http://my-server:5000
Greetings, traveler! The greeter-server received your request.
```

Confirm the server was never actually reachable from your own host
machine either, at any point in this exercise (you never published a
port with `-p`):
```bash
curl http://localhost:5000
```
**Expected:** connection refused — Lesson 04's distinction between
container-to-container reachability (which you just achieved via the
shared network) and host-to-container reachability (which requires an
explicit `-p`/`--publish`, never happened here, and isn't needed for
this exercise's actual goal).

## Acceptance criteria

- [ ] You can show the exact failed output from Step 1's deliberate
      default-network attempt.
- [ ] You can show the exact successful output after attaching both
      containers to your own user-defined network.
- [ ] `curl http://localhost:5000` from your own host fails throughout
      this entire exercise, and you can explain why that's expected,
      not a bug.
- [ ] You can explain, precisely, what's different about a user-defined
      network that makes name-based resolution work, that the default
      bridge network lacks.
- [ ] Both containers and your network are cleanly removed at the end.

## Hints

<details>
<summary>Hint 1</summary>

`docker network create <name>` first; then both `docker run` commands
need `--network <that same name>`, matching Lesson 04's own `demo-net`
example exactly.

</details>

<details>
<summary>Hint 2</summary>

`greeter-client` reads its target host from the `GREETER_HOST`
environment variable — set it with `-e GREETER_HOST=<value>` on the
`docker run` command, matching whatever `--name` you gave the server
container in step 3.

</details>

<details>
<summary>Hint 3</summary>

If Step 4/5 still fails, double-check BOTH containers used the exact
same `--network` value, and that the server's `--name` in step 3 exactly
matches the `GREETER_HOST` value you passed to the client (`docker ps`
will show you every running container's exact name if you're unsure).

</details>
