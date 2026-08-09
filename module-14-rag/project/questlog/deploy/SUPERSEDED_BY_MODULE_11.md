# This folder's role, updated again for Module 11

`deploy/` still holds Module 09's original manual-deploy artifacts
(`questlog-backend.service`, `nginx/questlog.conf`,
`backend.env.production.example`, `DEPLOY_RUNBOOK.md`, and this folder's
own `SUPERSEDED.md` explaining how Module 10 replaced each one with a
containerized equivalent). None of that changes here — this file adds one
more row to that same story, for the same reason: comparing what you did
by hand against what's automated is the whole point of keeping this
folder around at all.

Module 10 replaced Module 09's manual server setup with
`docker compose up --build` — one command, but still a command **a
human has to type, on some machine, every time.** Module 11 replaces
*that* human action with a real pipeline. Nothing about the containers
themselves changes — `backend/Dockerfile` and `frontend/Dockerfile` are
**byte-for-byte what Module 10 wrote**, plus the two small, documented
additions this module made (a `/health` endpoint, optional Sentry
init — see `../README.md`'s "What changed" section) — this module
automates *getting those exact images onto a real, internet-reachable
server*, not the packaging itself.

| Module 10's manual step | Module 11's automated replacement |
|---|---|
| A human runs `docker compose build` on their own machine, whenever they remember to, after making a change. | `.github/workflows/ci-cd.yml`'s `build-and-push-images` job builds both images automatically, on every push to `main` — see `lessons/03-a-real-ci-pipeline-for-questlog.md`. |
| A human runs the backend/frontend test suites locally, before (hopefully) pushing. | The same workflow's `backend-tests`/`frontend-tests` jobs run automatically, on every push AND every pull request, and **block** the build/deploy jobs entirely if either fails — see `lessons/01-what-ci-cd-is-and-why.md`. |
| A human manually `scp`s or rebuilds images on the target machine, then runs `docker compose up -d` there by hand (the natural next step Module 10 itself never took). | The workflow's `deploy` job calls Render's own Deploy Hook, which pulls the exact new image (pinned by commit SHA via `imgURL`) and redeploys it — see `lessons/08-deploying-questlog-with-ci-cd.md`. |
| No TLS at all — Module 10's stack is `http://localhost:8080` only. | Render issues and renews a real TLS certificate automatically, for both the platform's own `*.onrender.com` subdomain and any custom domain you add — see `lessons/05-https-tls-domains-and-dns.md`. |
| No error tracking, no uptime/health signal beyond "did `docker compose ps` show it running." | A real `/health` endpoint Render itself polls before routing traffic (`app/main.py`), plus optional Sentry error tracking on both frontend and backend — see `lessons/06-monitoring-logging-and-error-tracking.md`. |
| Nowhere a person outside your own machine/network could ever reach it. | A real, public URL (`https://questlog-frontend-XXXX.onrender.com` on the free path, or your own domain if you choose to buy one) — see `project/BRIEF.md`. |

**What this table deliberately does NOT claim:** this still isn't a
"real production system" in the sense of redundancy, autoscaling, or a
team of on-call engineers — Render's free tier specifically spins the
backend down after 15 minutes of no traffic and takes up to a minute to
wake back up on the next request (see `lessons/04`'s honest accounting).
That's an accepted, explicit trade-off for a free, always-following-along
capstone, not something this module pretends isn't true.
