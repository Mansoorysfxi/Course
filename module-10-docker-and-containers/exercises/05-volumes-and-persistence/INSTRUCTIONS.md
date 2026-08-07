# Exercise 05 — Prove Persistence (and Its Absence) With a Real Volume (Independent)

**Concepts this exercise uses (all taught in
[`lessons/05-docker-volumes-and-persistence.md`](../../lessons/05-docker-volumes-and-persistence.md)):**
`docker volume create`, `-v <volume>:<path>`, `docker volume ls`,
`docker volume rm`, the difference between a container's own disposable
writable layer and a named volume.

**Where to work:** `exercises/05-volumes-and-persistence/starter/` — a
tiny app that appends one timestamped note to `/data/notes.txt` every
time it runs, then prints every note in that file so far.

## Setup

```bash
cd exercises/05-volumes-and-persistence/starter
docker build -t quest-notes .
```

## Your task, Part 1 — prove data loss without a volume

Run the container **three separate times**, with `--rm` and **no**
volume mount at all:
```bash
docker run --rm quest-notes
docker run --rm quest-notes
docker run --rm quest-notes
```
**Predict, before running the second and third commands**, whether
you'll see 1, 2, or 3 notes printed each time — then run them and check.
Be ready to explain, precisely, *why* you saw what you saw (hint: is
`docker run` reusing the same container across these three commands, or
creating a new one each time?).

## Your task, Part 2 — fix it with a named volume

1. Create a named volume.
2. Run the container **three separate times**, `--rm`, this time **with**
   your named volume mounted at `/data`.
3. Confirm the note count now genuinely accumulates: 1, then 2, then 3.
4. Without removing the volume, run the container a fourth time. Confirm
   it shows **4** notes — proof this isn't a fluke of running the
   commands close together in time; the data is genuinely, durably
   stored in the volume itself.
5. Remove the named volume, then run the container one more time (with
   the same `-v` flag, pointing at a volume that no longer exists — Docker
   will silently recreate an empty one with that name). Confirm you're
   back down to **1** note — proof removing the volume genuinely deleted
   the data, not just "hid" it somewhere recoverable.

## Verify it yourself

Part 1, all three runs, expected:
```
All notes so far:
<one timestamp> - a quest log entry
```
(exactly one line, every single time — a fresh, empty `/data` each run.)

Part 2, runs 1-4, expected note counts: 1, 2, 3, 4 (one new timestamp
line added to the growing list each time).

Part 2, step 5 (after removing the volume), expected: back to exactly 1
note.

## Acceptance criteria

- [ ] You can show Part 1's output proving each of the three runs saw
      exactly one, fresh note — never an accumulating count.
- [ ] You can show Part 2's output proving the note count genuinely
      accumulated to 4 across four separate container runs, all sharing
      one named volume.
- [ ] You can show that removing the volume and running again resets the
      count back to 1.
- [ ] You can explain, in your own words, exactly what changed between
      Part 1 and Part 2's `docker run` commands that caused such
      different behavior — nothing in `app.py` or the `Dockerfile`
      itself changed at all between the two parts.
- [ ] The volume is removed by the end of this exercise (`docker volume
      ls` shows no leftover volume from this exercise).

## Hints

<details>
<summary>Hint 1</summary>

Part 1's behavior is exactly Lesson 05's own first "proving data loss"
demonstration, just phrased as "three runs" instead of "run, remove,
run again" — every `docker run` (without `docker start` on an existing
container) always creates a brand-new container, with a brand-new, empty
writable layer, regardless of what image or name you use.

</details>

<details>
<summary>Hint 2</summary>

The flag is `-v <volume-name>:/data` — matching Lesson 05's own
`-v demo-data:/data` example exactly, just naming your own volume
however you like.

</details>
