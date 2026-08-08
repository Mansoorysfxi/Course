# Capstone Brief — A Real CI/CD Pipeline Deploying QuestLog

## What you're doing

Take this module's `project/questlog/` — Module 10's finished,
containerized QuestLog, plus this module's own small, real additions (a
`/health` endpoint, optional Sentry monitoring, a real
`.github/workflows/ci-cd.yml`, and a `render.yaml` Blueprint) — and make
the whole thing genuinely, automatically deploy: push a commit to
`main`, and, with no further human action, your tests run, both Docker
images build and push to GHCR, and Render redeploys, over real HTTPS.

Most of the pipeline already exists, fully built and explained
(Lessons 02-03 and 08). Your job is to **apply it for real (or a
thorough, honest dry run), close the one real, named gap Lesson 08 left
for you, verify it genuinely works end to end, and write up what you
found** — the same "understand it well enough to explain and to fix"
standard every capstone since Module 09 has used.

## Before you start

- [ ] All six exercises in this module are done and reviewed.
- [ ] You've read Lessons 00-08 in full, in order.
- [ ] You have a GitHub account, a Render account (Lesson 00-setup.md),
      and (optionally) a Sentry account and/or a real domain.
- [ ] You've read `project/questlog/README.md` and
      `project/questlog/deploy/SUPERSEDED_BY_MODULE_11.md` so you know
      exactly what changed since Module 10 and why.

## What to actually do

### Part 1 — Push QuestLog to its own real GitHub repo

Per Lesson 00-setup.md's own "which repo does this even run in"
explanation:
```bash
cd module-11-cicd-cloud-production/project/questlog
git init
git add .
git commit -m "Module 11: QuestLog with CI/CD"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/questlog.git
git push -u origin main
```
**Confirm:** `backend-tests` and `frontend-tests` both run automatically
and pass (Lesson 03), and `build-and-push-images` runs and pushes two new
GHCR packages (Lesson 08, Part 1) — `deploy` will fail at this point,
since no Render secrets exist yet; that's expected, continue to Part 2.

### Part 2 — Apply `render.yaml` and wire up secrets

Follow Lesson 08's "Part 2" and "Part 3" exactly: replace
`YOUR_GITHUB_USERNAME` in `render.yaml`, decide public-GHCR-package vs.
private-with-credential (Lesson 08's own recommended default: public,
for a personal learning project), apply the Blueprint in Render's
dashboard, fill in `SECRET_KEY` and `DATABASE_URL` (with the
`postgresql+asyncpg://` scheme fix Lesson 08 explains), and add
`RENDER_BACKEND_DEPLOY_HOOK`/`RENDER_FRONTEND_DEPLOY_HOOK` (and,
optionally, `VITE_SENTRY_DSN`) as GitHub Actions secrets.

### Part 3 — Close the one real, named gap: cross-service API calls

Lesson 08 names this honestly rather than pre-solving it for you:
`frontend/nginx.conf`'s `proxy_pass http://backend:8000;` is a Compose-
network hostname that doesn't exist once `questlog-backend` and
`questlog-frontend` are two separate Render services. **Pick ONE of the
two approaches Lesson 08 names**, implement it for real, and document
which one and why in your own capstone report:

- **Approach A:** edit `frontend/nginx.conf`'s `proxy_pass` to point at
  your real `questlog-backend-XXXX.onrender.com` URL, rebuild/redeploy.
- **Approach B:** rebuild the frontend with `VITE_API_BASE_URL` set to
  your backend's real URL (a new build argument in the CI workflow), and
  correctly set `CORS_ORIGINS` on the backend to the frontend's real
  origin (Module 07's own CORS lesson).

### Part 4 — Verify it, end to end, like a real user

```bash
curl -i https://questlog-backend-XXXX.onrender.com/health
```
**Expected:** `200 OK`, `{"status":"ok","database":"ok","cache":"ok"}`,
real, valid, browser-trusted HTTPS.

Open `https://questlog-frontend-XXXX.onrender.com` in a real browser
(not `curl`, for this part). Log in with `player@questlog.local` /
`dragon-slayer-1`. **Confirm the Quest Board genuinely loads five real
quests** — proof the entire chain (browser → real HTTPS → Render's
`questlog-frontend` → your Part 3 fix → Render's `questlog-backend` →
Render's managed Postgres, with Render's managed Redis caching the
unfiltered list call) genuinely works, for real, on the internet, not
just on your own machine.

Push one more trivial commit (a comment change is fine). **Confirm the
entire pipeline — tests, build, push, deploy — runs completely
automatically**, and the live site reflects the new deploy (check
Render's own dashboard for a fresh deploy timestamp).

### Part 5 — Break something on purpose, then fix it (pick one)

- Deliberately misspell `DATABASE_URL`'s scheme (back to plain
  `postgresql://`) in Render's dashboard, redeploy, and observe exactly
  how `/health` reports the failure (Lesson 08's own "common mistakes"
  section names this exact scenario).
- Deliberately break a backend test on a feature branch, open a pull
  request, and confirm `build-and-push-images`/`deploy` never run at all
  for that PR (only `backend-tests`/`frontend-tests` do) — exactly
  Lesson 03's own "Try it yourself," now against the real capstone
  pipeline instead of a toy example.

Fix it, confirm the pipeline/deployment works again, and document
exactly what broke, the real error/log output, and how you diagnosed it.

## Deliverables

Write up a short report (`project/CICD_REPORT.md` — create this
yourself; no fixed template, honest content matters more than a fixed
shape) covering:

1. **Confirmation of Parts 1-4**, with real command output/URLs (or a
   precise description of what you observed) — including your live
   deployment's real URL if you completed this for real, or a thorough,
   honest dry-run account per this module's own accepted alternative
   (Lesson 00-setup.md) if you didn't.
2. **Which approach you picked for Part 3**, and why, with the actual
   diff/change you made.
3. **Part 5's deliberately broken-then-fixed scenario** — the exact
   error, how you found it, and the fix.
4. **A comparison, in your own words, of at least three specific things**
   that were manual steps in Module 09/10 and are now fully automated by
   this module's pipeline — name the specific earlier-module step and
   its Module 11 replacement for each (see
   `project/questlog/deploy/SUPERSEDED_BY_MODULE_11.md` for a starting
   point, but answer in your own words, not by copying that table).
5. **An honest accounting of what this deployment still doesn't do** —
   your own answers to Lesson 08's own "What this still doesn't do"
   list, explaining why each gap is acceptable for now.

## Acceptance criteria (what "done" looks like)

- [ ] A push to `main` runs tests, builds and pushes both images, and
      (Part 1-2 complete) deploys automatically, with zero manual
      intervention beyond the push itself.
- [ ] Part 3's cross-service API fix is genuinely implemented and
      verified working, not just described.
- [ ] The live deployment (or a thorough, honest dry run) serves QuestLog
      over real, valid HTTPS, and `/health` returns `200` with all
      dependencies reporting `"ok"`.
- [ ] Part 5's broken-then-fixed scenario is genuinely reproduced and
      documented, not just asserted.
- [ ] `CICD_REPORT.md` exists and covers all five numbered points above,
      honestly.
- [ ] You can explain, without looking anything up, the complete path a
      `git push` takes from your own machine to a real user seeing an
      updated Quest Board in their browser — every job, every service,
      in order.
- [ ] No real money was spent unless you deliberately chose to (a real
      domain, a paid Render tier) — the free path fully satisfies every
      criterion above.

## A note on scope

Consistent with this module's own scope decision (Lesson 00-setup.md)
and the exact same pattern Module 09 used for its own VPS requirement: a
thorough, honest dry run — reading every step, understanding exactly what
each one does and why, and writing up precisely what you WOULD observe
at each stage, citing this module's own lessons by name — is a fully
legitimate way to complete this capstone if you'd rather not create real
accounts/spend real time on a live deployment right now. What matters is
demonstrated understanding, not a specific URL existing on the internet
forever.
