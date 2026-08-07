# Exercise 03 — Convert a Bloated Single-Stage Build Into a Multi-Stage One (Guided → Independent)

**Concepts this exercise uses (all taught in
[`lessons/03-multi-stage-builds-and-image-size.md`](../../lessons/03-multi-stage-builds-and-image-size.md)):**
`FROM ... AS <name>`, `COPY --from=<stage>`, `pip install --prefix=`,
`docker images` (comparing sizes), `docker history`.

**Where to work:** `exercises/03-multi-stage-image-size/starter/` — a
real, working, but deliberately naive single-stage Dockerfile
(`Dockerfile`) that builds a tiny app using `pandas` (a real package
with real, non-trivial size, specifically chosen so the size difference
this exercise asks you to measure is genuinely visible, not a rounding
error).

## Setup — establish the "before" baseline

```bash
cd exercises/03-multi-stage-image-size/starter
docker build -t quest-report:single-stage .
docker run --rm quest-report:single-stage
```
**Expected output:**
```
                title priority
0     Slay the Dragon     high
1        Gather Herbs      low
2  Deliver the Letter   medium

Total quests: 3
```
Record the image's size:
```bash
docker images quest-report:single-stage
```
Write this `SIZE` value down somewhere — you'll compare against it.

## Your task

1. Rewrite this folder's `Dockerfile` as a genuine **multi-stage** build:
   - Stage 1, named `builder`, installs `requirements.txt` using
     `pip install --no-cache-dir --prefix=/install -r requirements.txt`
     (Lesson 03's own pattern).
   - Stage 2 starts fresh from the same base image, copies **only**
     `/install` from `builder` into `/usr/local`, then copies in
     `app.py`.
   - The final `CMD` is unchanged.
2. Build this new version as `quest-report:multi-stage` (a **different**
   tag from Setup's baseline, so both images exist side by side for
   comparison).
3. Run it and confirm the output is **identical**, byte for byte, to
   Setup's baseline.
4. Compare both images' sizes and confirm the multi-stage version is
   meaningfully smaller.

## Verify it yourself

```bash
docker build -t quest-report:multi-stage .
docker run --rm quest-report:multi-stage
```
**Expected:** the exact same DataFrame output as the single-stage
version.

```bash
docker images | grep quest-report
```
**Expected:** two rows, `single-stage` and `multi-stage`, with
`multi-stage`'s `SIZE` column noticeably smaller — exactly how much
smaller depends on your platform, but expect at least tens of MB of
difference, since pandas alone (plus numpy, one of its own real
dependencies) downloads a genuinely sizable set of wheel files pip would
otherwise leave cached inside the single-stage image's final layer.

```bash
docker history quest-report:multi-stage
```
**Expected:** no layer here corresponds to pip's own download cache —
only the layers the final stage's own instructions actually produced.

## Acceptance criteria

- [ ] Both `quest-report:single-stage` and `quest-report:multi-stage`
      build successfully.
- [ ] Both produce byte-for-byte identical `docker run` output.
- [ ] `quest-report:multi-stage` is measurably smaller than
      `quest-report:single-stage` (check with `docker images`).
- [ ] You can explain, specifically, what your multi-stage version's
      final image does *not* contain that the single-stage version does.
- [ ] You can explain why both versions produce the same *output*
      despite one image being meaningfully larger on disk than the
      other — what's different is what got shipped, not what the
      program itself does.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 03's own worked "Turning Lesson 02's example into a multi-stage
build" section is structurally identical to what this exercise wants —
same `--prefix=/install` / `COPY --from=builder /install /usr/local`
pattern, just with `pandas` instead of `requests` in `requirements.txt`.

</details>

<details>
<summary>Hint 2</summary>

Make sure **both** `FROM` lines in your multi-stage Dockerfile use the
exact same Python image tag (`python:3.14-slim` in both places) — a
version mismatch between the two stages is the most common reason
`COPY --from=builder /install /usr/local` "succeeds" but `import pandas`
still fails at runtime (Lesson 03's own gotchas section explains exactly
why).

</details>

A reference solution is in `solution/`.
