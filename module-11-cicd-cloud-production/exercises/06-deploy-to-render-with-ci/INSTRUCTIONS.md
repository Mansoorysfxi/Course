# Exercise 06 — Deploy to Render With CI (Independent, Capstone Dress Rehearsal)

**Concepts this exercise uses (all taught in
[`lessons/04-cloud-fundamentals-and-your-chosen-platform.md`](../../lessons/04-cloud-fundamentals-and-your-chosen-platform.md)
and [`lessons/08-deploying-questlog-with-ci-cd.md`](../../lessons/08-deploying-questlog-with-ci-cd.md)):**
Render Blueprints (`render.yaml`), `runtime: image`, `healthCheckPath`,
Deploy Hooks, the `imgURL` query parameter, GitHub Actions secrets.

**Where to work:** `exercises/06-deploy-to-render-with-ci/starter/` —
Exercise 04's toy app, already with a real `/health` endpoint and a CI
pipeline that builds and pushes it to GHCR. **This is the last exercise
before this module's real capstone** (`project/BRIEF.md`, deploying
QuestLog itself the exact same way) — treat this exercise as that
capstone's dress rehearsal, exactly the same relationship Module 10's
own Exercise 06 had to ITS capstone.

## Your task

### Part 1 — Write `render.yaml`

Write a Render Blueprint, from scratch, for this one toy service:
- `name: toy-ci-app`, `type: web`, `runtime: image`.
- `plan: free`.
- `image.url:` pointing at your own GHCR image from Exercise 03/04
  (`ghcr.io/YOUR_USERNAME/toy-ci-app:latest`, all lowercase).
- `healthCheckPath: /health` (Exercise 04's own endpoint).
- One `envVars:` entry, `GREETING`, with a real value (not `sync: false`
  — this one isn't a secret, so setting a real value directly in the
  file is fine and simpler).

### Part 2 — Add a `deploy` job to `.github/workflows/ci.yml`

Add a third job that:
- `needs: build-and-push`.
- Calls a Render Deploy Hook via `curl`, appending `&imgURL=` with this
  exact run's own SHA-tagged image (exactly Lesson 08's own pattern for
  QuestLog).

### Part 3 — Actually apply it (or a thorough, honest dry run)

Either:
- **(A) For real:** make your GHCR package public (simplest path — see
  Lesson 08's own section on this), apply this Blueprint in your Render
  dashboard (New → Blueprint), get the real Deploy Hook URL from the
  resulting service's Settings page, add it as a
  `RENDER_DEPLOY_HOOK` secret in your GitHub repo, push, and watch the
  whole thing deploy for real.
- **(B) A thorough, honest dry run:** if you'd rather not create a real
  Render service for this toy exercise specifically, write out, in your
  own words, in a new `DRY_RUN.md` file in this folder, the exact
  sequence of dashboard clicks and values you WOULD enter, referencing
  this module's own Lesson 08 section by name for each step, and explain
  what you'd expect to see at each stage. This module's own scope
  decision (Lesson 00-setup.md) explicitly accepts this as legitimate —
  the same standard Module 09 used for its own VPS capstone.

## Verify it yourself

If you completed Part 3(A) for real:
```bash
curl -i https://toy-ci-app-XXXX.onrender.com/health
```
**Expected:** `HTTP/1.1 200 OK` (real HTTPS, no `-k`/`--insecure` flag
needed at all), `{"status":"ok","greeting_configured":true}`.

## Acceptance criteria

- [ ] `render.yaml` exists, uses `runtime: image`, and correctly names
      `healthCheckPath: /health`.
- [ ] The workflow's new `deploy` job correctly uses `needs:` so it only
      ever runs after a successful image push.
- [ ] The Deploy Hook call includes `&imgURL=` with the exact SHA-tagged
      image from the SAME run, not a hardcoded or `:latest` reference.
- [ ] Either a real, live, HTTPS-reachable deployment exists, OR a
      genuinely thorough `DRY_RUN.md` exists, referencing specific lesson
      sections by name.
- [ ] You can explain, unprompted, exactly what would happen (and why) if
      you removed `&imgURL=...` from the deploy hook call entirely.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 08's own `render.yaml` for QuestLog is longer only because it has
more services (Postgres, Redis, two web services) — the shape of ONE
`type: web, runtime: image` service block is identical to what this
exercise wants.

</details>

<details>
<summary>Hint 2</summary>

A real Render Deploy Hook URL already contains its own `?key=...` query
string — appending `imgURL` needs a leading `&`, not a second `?`.

</details>

A reference solution is in `solution/`.
