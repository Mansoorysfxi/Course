# Lesson 08 — Deploying QuestLog With Real CI/CD

**Verified against (August 2026):** every field name in `render.yaml`
below against Render's own Blueprint spec (`render.com/docs/blueprint-spec`)
and prebuilt-image docs (`render.com/docs/deploying-an-image`); every
GitHub Actions version against GitHub's own Marketplace pages (Lesson
02's own header repeats these). Render's own current behavior for
image-backed services — they do **not** auto-redeploy when a new image
is pushed to a registry; a **Deploy Hook** (optionally with an `imgURL`
query parameter to pin an exact tag/digest) is Render's own documented
way to trigger that redeploy — confirmed directly from Render's own
documentation.

## What you'll learn

- How to read `project/questlog/render.yaml` and
  `project/questlog/.github/workflows/ci-cd.yml`'s remaining two jobs
  (`build-and-push-images`, `deploy`) in full, as the direct payoff of
  every earlier lesson in this module.
- How to actually apply this Blueprint to a real Render workspace, wire
  up the required GitHub secrets, and watch a real, automatic deploy
  happen end to end.
- How to verify the result — HTTPS, a working health check, a genuinely
  reachable QuestLog — the same "prove it, don't just assume it" standard
  every earlier capstone in this course used.
- What this setup honestly still doesn't do, and exactly which future
  work (real production hardening) it deliberately leaves out.

## Why this matters

This is the payoff of the entire module: Lesson 01's "why," Lesson 02-03's
GitHub Actions syntax and QuestLog's own real test jobs, Lesson 04's
platform choice, Lesson 05's HTTPS/DNS mechanics, and Lesson 06's health
check and monitoring all combine into one real, working pipeline in this
lesson.

## Prerequisites

- **Lessons 00-07 in full** — every piece of syntax and every concept
  used below was taught, in order, in an earlier lesson.
- **All six exercises in this module** — Exercise 06 specifically is a
  full dress rehearsal of everything this lesson does, against a small
  toy app instead of QuestLog itself.

## The concept, explained simply

Everything from here is Lesson 01's own automated build farm, made fully
concrete and real, for QuestLog specifically: a push to `main` triggers
tests (Lesson 03); if they pass, two Docker images get built and pushed
to a real container registry (this lesson, Part 1); if THAT succeeds, a
signal gets sent to Render telling it "a new image is ready, go get it"
(this lesson, Part 2) — and Render, a platform that already knows how to
run a container, issue it a real HTTPS certificate, and health-check it
before routing traffic, takes it from there.

## The details

### Part 1 — Building and pushing images to GHCR

Open `.github/workflows/ci-cd.yml`'s `build-and-push-images` job. Its
`needs: [backend-tests, frontend-tests]` and `if:` condition (Lesson 02)
mean this job only runs after both test jobs succeed, and only for a real
push to `main` — never for a pull request. Its steps:

1. **Normalize the image owner to lowercase.** A real, common gotcha:
   Docker/OCI image names must be entirely lowercase, but GitHub allows
   mixed-case usernames/org names. GitHub Actions' own expression
   language has no built-in lowercase function (confirmed still true,
   August 2026) — this step uses a plain bash trick
   (`${OWNER,,}`) instead, and saves the result as a job **output**
   (`steps.normalize.outputs.owner`) so later jobs can reuse the exact
   same value.
2. **`docker/setup-buildx-action@v4`** — sets up Docker's own modern
   build engine (Buildx), needed for the caching this workflow uses next.
3. **`docker/login-action@v4`**, targeting `ghcr.io` (**G**it**H**ub
   **C**ontainer **R**egistry — GitHub's own, built-in Docker registry,
   one per GitHub account/org, at no extra signup) using `github.actor`
   and the automatic `secrets.GITHUB_TOKEN` (Lesson 02) — no separate
   Docker Hub account, and no separate password to create or store,
   needed at all.
4. **`docker/build-push-action@v7`**, once per Dockerfile
   (`./backend`, `./frontend`) — builds using the EXACT, unmodified
   Dockerfiles Module 10 wrote, tags each image twice (`:latest`, and
   `:<the exact commit SHA that triggered this run>`), and pushes both
   tags to GHCR. `cache-from`/`cache-to: type=gha` reuses GitHub's own
   Actions cache between runs — the CI-scale equivalent of Module 10's
   own Dockerfile layer caching.

**Why tag with the commit SHA, not just `:latest`:** `:latest` is a
moving target — it always means "whatever was pushed most recently,"
which makes it impossible to know, later, exactly which commit produced
the image currently running in production. Tagging with `github.sha`
(a value GitHub Actions provides automatically, the exact, full commit
hash that triggered this run) gives every single deploy a permanent,
unambiguous, traceable link back to the exact code that produced it —
genuinely useful the moment something goes wrong in production and you
need to know precisely what's actually running.

**Making the GHCR package public (the simpler path this lesson
recommends):** by default, a newly created GHCR package is **private** —
Render would need a registry credential (a GitHub Personal Access Token
with `read:packages` scope) to pull it, configured once, by hand, in
Render's own dashboard (**Account Settings → Credentials**, or directly
on a service's own image settings) and referenced in `render.yaml` via
`image.creds:`. The simpler alternative, and this lesson's own
recommended default for a personal learning project with nothing
sensitive inside the image itself: after your first successful push,
go to your GitHub profile's **Packages** tab, open the
`questlog-backend`/`questlog-frontend` package, **Package settings →
Change visibility → Public**. A public GHCR package needs **no
credential at all** to pull — delete `render.yaml`'s `creds:` lines
entirely once you've done this. (The private+credential path is
genuinely closer to how a real company would do this, precisely because
a real company's own image usually contains code/config it doesn't want
publicly downloadable — worth knowing both paths exist, and why a real
team would pick differently than a personal course project might.)

### Part 2 — Applying `render.yaml` and wiring up secrets

Open `render.yaml` in full. Read Lesson 04's own platform reasoning
alongside it if any field feels unfamiliar. Two fields deserve a second
look, side by side, for exactly the contrast Lesson 04/05 set up:

```yaml
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        fromService:
          name: questlog-redis
          type: keyvalue
          property: connectionString
```
`REDIS_URL` wires up **fully automatically** — Render's own Key Value
connection string already uses the plain `redis://`/`rediss://` scheme
`redis.asyncio` already understands natively. `DATABASE_URL` is
deliberately `sync: false` (meaning: Render will prompt you to type a
value in by hand, rather than guessing) because Render's own Postgres
connection string uses a plain `postgresql://` scheme, but
`backend/app/database.py`'s async SQLAlchemy engine needs the
`postgresql+asyncpg://` scheme specifically — a real, genuine dialect
mismatch, not a Render limitation. To fill this in correctly: after
`questlog-db` exists (Render creates it as part of applying this
Blueprint), open its own dashboard page, copy its connection string,
and paste it into `questlog-backend`'s own `DATABASE_URL` environment
variable, **changing only the scheme prefix** from `postgresql://` to
`postgresql+asyncpg://` — everything else in the string (host,
port, username, password, database name) stays exactly as Render gave
it to you.

**Applying the Blueprint, step by step:**

1. Replace every `YOUR_GITHUB_USERNAME` in `render.yaml` with your own
   GitHub username or org, **all lowercase**.
2. Push at least once so `.github/workflows/ci-cd.yml` has already run
   successfully and both images exist on GHCR (Part 1) — Render needs a
   real image to pull the very first time it creates each service.
3. In Render's dashboard: **New → Blueprint**, connect it to your GitHub
   repo (the one containing `render.yaml`, per Lesson 00-setup.md's own
   repo-boundary explanation), and let Render read the file.
4. Render will prompt for every `sync: false` value (`SECRET_KEY`,
   `DATABASE_URL` — filled in per above, `SENTRY_DSN` if you're using it)
   and, if you kept `creds:` in for a private GHCR package, ask you to
   add that registry credential.
5. Click **Apply**. **Expected:** Render creates `questlog-db`,
   `questlog-redis`, then `questlog-backend` and `questlog-frontend`,
   pulling each image and starting each container, polling
   `questlog-backend`'s own `/health` (Lesson 06) before routing any real
   traffic to it.
6. Once `questlog-backend` deploys successfully, find its real
   `https://questlog-backend-XXXX.onrender.com` URL and update
   `questlog-frontend`'s `VITE_API_BASE_URL` build argument (Lesson 08's
   own frontend build args, in the CI workflow) — **or**, the simpler
   option this course's own architecture already supports: keep it
   pointed at the frontend's OWN origin with relative paths (as Module
   09/10 already do), and instead have `questlog-frontend`'s own served
   Nginx `proxy_pass` to `questlog-backend`'s real URL — see this
   lesson's own "Common mistakes" section for exactly why the second
   option needs one small, real edit to `frontend/nginx.conf` that
   this module's own copied-forward file does not yet make (an honest,
   named gap — see "What this still doesn't do," below).

### Part 3 — Wiring up GitHub Actions secrets for the `deploy` job

Open the workflow's final `deploy` job:
```yaml
  deploy:
    needs: build-and-push-images
    steps:
      - run: curl --fail --silent --show-error \
          "${{ secrets.RENDER_BACKEND_DEPLOY_HOOK }}&imgURL=ghcr.io/.../questlog-backend:${{ github.sha }}"
      - run: curl --fail --silent --show-error \
          "${{ secrets.RENDER_FRONTEND_DEPLOY_HOOK }}&imgURL=ghcr.io/.../questlog-frontend:${{ github.sha }}"
```
Get each Deploy Hook URL from Render: open `questlog-backend`'s own
**Settings** page, find **Deploy Hook**, copy the URL (a real one looks
like `https://api.render.com/deploy/srv-XXXXXXXX?key=YYYYYYYY`). In your
GitHub repo's own **Settings → Secrets and variables → Actions**, add:
- `RENDER_BACKEND_DEPLOY_HOOK` — the backend service's own Deploy Hook
  URL.
- `RENDER_FRONTEND_DEPLOY_HOOK` — the frontend service's own.
- (Optional) `VITE_SENTRY_DSN` — if you're using Sentry on the frontend
  (Lesson 06); the workflow's own `build-args:` already reads this.

**The `&imgURL=...` part, explained:** a Deploy Hook alone just tells
Render "redeploy this service using whatever image tag/reference is
already configured" — since `render.yaml` configures `:latest`, that
alone would technically work, but would mean "redeploy whatever `latest`
happens to mean by the time Render gets to it" rather than "redeploy
THIS EXACT commit's image" — appending `&imgURL=` with the specific,
commit-SHA-tagged image (from Part 1) makes each deploy pin an exact,
known, traceable image, closing the same "which exact code is actually
running" gap this lesson's earlier SHA-tagging section already opened.

### Part 4 — Verifying the whole thing, end to end

Push a real commit to `main` (even a trivial one, like a comment change).
**Expected**, watching the repo's own **Actions** tab:
1. `backend-tests` and `frontend-tests` run in parallel, both green.
2. `build-and-push-images` runs next, pushing two new, SHA-tagged images.
3. `deploy` runs last, two successful (HTTP 200) `curl` calls.

Then, in Render's own dashboard, watch `questlog-backend` and
`questlog-frontend` each show a new deploy in progress, then healthy.
Once both are healthy:
```bash
curl -i https://questlog-backend-XXXX.onrender.com/health
```
**Expected:** `HTTP/1.1 200 OK` (or `HTTP/2 200`, since Render terminates
real HTTPS traffic — Lesson 05), `{"status":"ok","database":"ok","cache":"ok"}`,
plus a real, valid TLS certificate your browser (or `curl -v`, Module
02's own approach) would confirm without any warning. Open your
frontend's own `https://questlog-frontend-XXXX.onrender.com` URL in a
real browser, log in with the seeded demo account, and confirm the Quest
Board genuinely loads — the same "prove it actually works, don't just
assume it" standard every earlier module's capstone has used.

**Note on Continuous Deployment vs. Continuous Delivery (Lesson 01):**
this pipeline is Continuous *Deployment* — nothing gates the `deploy`
job beyond the two test jobs passing. To turn this into Continuous
*Delivery* instead (a human approves before deploying), you'd wrap the
`deploy` job's own environment in a GitHub **Environment** with a
required reviewer configured in the repo's own Settings — GitHub then
pauses that job, waiting for a named human to click "approve," before it
runs at all. This course's own capstone deliberately doesn't require
this (Lesson 01's own reasoning: an acceptable trade-off for a personal
project with no real users at stake) but knowing exactly which one
config change bridges the two is worth having.

## What this still doesn't do (honest accounting, same standard every earlier module used)

- **The frontend's own `nginx.conf` still `proxy_pass`es to
  `http://backend:8000`** — Module 10's own Compose-network hostname,
  which does not exist once `questlog-backend` and `questlog-frontend`
  are two, separate, independently-addressed Render services rather than
  two containers on one shared Compose network. Making cross-service API
  calls work for real on Render specifically needs one more, real change
  this lesson names but does not make for you: either rebuild the
  frontend image with `VITE_API_BASE_URL` set to the backend's own real
  `https://questlog-backend-XXXX.onrender.com` URL (simpler, but
  reintroduces the cross-origin CORS considerations Module 07's own CORS
  lesson covered, needing `CORS_ORIGINS` on the backend correctly set to
  the frontend's own origin — already reflected in `render.yaml`), or
  edit `frontend/nginx.conf`'s own `proxy_pass` target to point at the
  backend's real URL instead. `project/BRIEF.md` asks you to make and
  document this exact, small, necessary fix yourself as part of the
  capstone — a deliberate, real decision this lesson leaves as your own
  work, not a gap in the lesson's own explanation.
- **No staging environment, no gradual rollout, single replica of
  everything** — identical, honestly, to every earlier module's own
  accepted trade-off at this scale.
- **No automated database backups configured beyond whatever Render's
  own free-tier defaults are** — a real production system would set this
  up explicitly and verify it; out of this module's own scope.
- **No automated rollback on a failed health check beyond Render's own
  default behavior** — worth knowing this exists as a real, further
  topic (canary deploys, automatic rollback), not something this
  capstone implements itself.

## Common mistakes & gotchas

- **`docker/build-push-action` fails with an authentication error.**
  Almost always `docker/login-action`'s own step running with the wrong
  `permissions:` — double-check the job has `packages: write` explicitly
  set (Lesson 02).
- **Render's deploy succeeds, but `/health` returns `503`.** Check
  `questlog-backend`'s own Render **Logs** tab first (Lesson 06) — the
  single most common real cause is `DATABASE_URL` still using the plain
  `postgresql://` scheme instead of `postgresql+asyncpg://` (this
  lesson's own dedicated section above).
- **The frontend loads, but every API call fails.** See "What this still
  doesn't do," above — this is the expected, named gap this lesson
  leaves for `project/BRIEF.md` to have you close yourself.
- **A deploy hook `curl` succeeds (`200 OK`) but nothing actually
  changes in Render's dashboard.** Double-check the `imgURL` value is
  spelled and cased correctly (a genuinely different, non-existent tag
  fails silently from Render's own perspective in some cases — always
  cross-check against GHCR's own **Packages** tab that the exact tag you
  referenced genuinely exists).

## How this connects

This lesson is the direct payoff of every lesson before it in this
module. `project/BRIEF.md` is this module's actual capstone assignment,
building on everything demonstrated here.

## Quick self-check

1. Why does the `build-and-push-images` job tag each image with both
   `:latest` and the commit SHA, instead of just `:latest`?
2. Why does `render.yaml` mark `DATABASE_URL` as `sync: false` instead of
   wiring it automatically via `fromDatabase`, the way `REDIS_URL` is
   wired via `fromService`?
3. What does appending `&imgURL=...` to a Render Deploy Hook URL actually
   change, compared to hitting the same hook with no query parameter at
   all?
4. What real, honest gap does this lesson name regarding
   `frontend/nginx.conf`'s own `proxy_pass` target, and why does that gap
   exist specifically because of the move from Compose to two separate
   Render services?
5. Which single configuration change would turn this pipeline from
   Continuous Deployment into Continuous Delivery?
