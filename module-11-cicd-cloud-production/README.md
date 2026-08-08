# Module 11 — CI/CD, Cloud & Production Operations

**Phase:** 3 — DevOps & Deployment (closing module)
**Estimated time:** 16-20 hours (mostly reading/config-writing, plus real
account setup and, if you choose the live path, real pipeline runs —
budget more time than a pure-reading module, less than Module 09's
real-VPS time)
**Verified against (August 2026):** `actions/checkout@v7`,
`actions/setup-python@v6`, `actions/setup-node@v6`,
`docker/setup-buildx-action@v4`, `docker/login-action@v4`,
`docker/build-push-action@v7` (all confirmed current via GitHub's own
Marketplace/release pages); **Render** as this module's chosen deploy
platform — free web services (Docker-image-backed, 750 shared free
instance-hours/workspace/month, spin down after 15 minutes idle),
free Postgres (1 GB, expires 30 days after creation + a 14-day grace
period), free Key Value/Redis-compatible cache (Valkey 8, in-memory
only), fully automatic Let's Encrypt/Google Trust Services TLS on both
`*.onrender.com` subdomains and custom domains — all confirmed via
Render's own documentation (`render.com/docs/free`,
`/docs/deploying-an-image`, `/docs/blueprint-spec`, `/docs/key-value`,
`/docs/tls`); **Sentry** Developer (free) plan — 5,000 errors/month, 1
user, 30-day retention, confirmed current; `sentry-sdk` (Python)
`2.62.0` and `@sentry/react` (npm) `^10.69.0` confirmed current via
PyPI/npm. Every fact above was checked with a live web search or a
direct fetch of the relevant official documentation while writing this
module, not recalled from memory — see each lesson's own header for the
specific source.

## What this module is

Module 09 deployed QuestLog to a real server **by hand**. Module 10
packaged it into containers so "run the whole stack" became one command.
Neither of those, on its own, gets a real user to a real URL: Module 09's
own server still needs a human to `git pull`, rebuild, and restart it
after every change; Module 10's own `docker compose up --build` still
needs a human to type it, on some machine, every time. **This module
removes the human from that loop.** Push a commit to `main`, and — with
zero further action from you — your tests run, both Docker images build,
and (if the tests passed) a real, internet-reachable, HTTPS-secured
deployment updates itself, automatically, usually within a couple of
minutes.

**A deliberate, explicit decision this module makes, up front (see
`lessons/04-cloud-fundamentals-and-your-chosen-platform.md` for the full
reasoning and research behind it):** Module 09's deploy target was a raw
Ubuntu VPS — a whole virtual machine you personally administer, patch,
and reboot. This module's deploy target is **Render**, a *container
platform* (a "Platform-as-a-Service," explained in full in that lesson) —
you never SSH into a machine, never run `apt`, never personally patch an
operating system. You hand Render a container image; it handles the
actual computer underneath. This is a genuinely different, higher tier of
the cloud "who manages what" spectrum than Module 09's VPS, chosen
specifically so this module's automatic HTTPS, automatic scaling-to-zero,
and one-file deploy configuration provide a real, felt contrast to
Module 09's fully manual, `certbot`-free, HTTP-only deploy — not a second
trip to the same kind of VPS with different branding.

## What you'll be able to do after this module

- Explain what CI/CD actually automates and why manual deploys eventually
  break down at any real team's scale, using a concrete build-farm
  analogy from game development.
- Write a real GitHub Actions workflow from scratch — triggers, jobs,
  steps, `needs:`, secrets, caching, matrix basics — and read any
  workflow file a real project throws at you without guessing at syntax.
- Explain, in plain language, what a cloud provider like AWS/GCP actually
  sells (compute, object storage, managed databases, IAM), and where a
  simpler container platform like Render sits relative to those.
- Explain exactly how a TLS certificate gets issued and renewed
  automatically, what DNS records (`A`, `CNAME`, `TXT`) a real domain
  needs to point at a real deployment, and read `dig`/`curl -I` output
  fluently.
- Explain what logs, metrics, uptime monitoring, error tracking, and
  health checks each catch that the others don't — and wire up a real
  health check and (optionally) real error tracking (Sentry) on both
  QuestLog's backend and frontend.
- Hold a real conversation about Kubernetes: what a Pod, a Deployment,
  and a Service each are, and — just as importantly — when a project
  genuinely needs Kubernetes and when it's pure, costly overkill.
- Deploy QuestLog's exact Module 10 containers via a real, automatic
  CI/CD pipeline: push to `main` → tests run → images build and push to a
  real container registry → Render auto-deploys → verify it live, over
  HTTPS, with a working health check.

## Prerequisites

- **Module 10 in full** — this module's pipeline builds and deploys the
  exact `backend/Dockerfile`/`frontend/Dockerfile`/`docker-compose.yml`
  that module wrote; it does not re-teach or re-invent containerization.
- **Module 00's Git/GitHub lesson** — you should already have a GitHub
  account and be comfortable with `git add`/`commit`/`push`/branches.
- **Module 08's testing material** — this module's CI pipeline runs the
  exact backend pytest suite and frontend Vitest suite Module 08 wrote.
- **Module 09's networking lessons** (ports, reverse proxies) — this
  module's HTTPS/DNS lesson builds directly on that vocabulary.

## Real accounts this module uses, and what's genuinely free vs. optional

This module is unusually account-heavy for this course — read
`lessons/00-setup.md` in full before anything else; it states, precisely
and up front, exactly what costs nothing, what's optional-and-paid, and
why reading/understanding every lesson here never actually requires
spending money. Short version, expanded fully in that lesson:

- **GitHub** (already have it) and **GitHub Actions CI** (tests running
  on every push) — genuinely, unambiguously free, no ambiguity, treated
  as normal and required, exactly like Module 00's Git material was.
- **Render** — free to sign up (no credit card required, per Render's own
  current policy), and this module's entire capstone can be completed
  entirely on Render's free tier, with **no custom domain purchase at
  all** — Render issues you a real `https://your-app.onrender.com` URL
  with automatic HTTPS, free.
- **A real custom domain** — genuinely optional. If you want one, this
  module names a real registrar with real, current pricing; if not, the
  free `onrender.com` subdomain path is a legitimate, fully-accepted way
  to complete this module, the same "a thorough, honest dry run/free-path
  is a legitimate alternative to real spend" framing Module 09 used for
  its own VPS.
- **Sentry** — genuinely optional, genuinely free at this course's scale
  (5,000 errors/month, forever, no card required for the free Developer
  plan) if you choose to turn it on.

## Module structure

```
module-11-cicd-cloud-production/
├── README.md                                                     ← you are here
├── lessons/
│   ├── 00-setup.md                                                 ← accounts, what's free, verification
│   ├── 01-what-ci-cd-is-and-why.md                                   ← the concept, before any syntax
│   ├── 02-github-actions-from-zero.md                                 ← workflow syntax, line by line
│   ├── 03-a-real-ci-pipeline-for-questlog.md                            ← running QuestLog's real test suites in CI
│   ├── 04-cloud-fundamentals-and-your-chosen-platform.md                  ← AWS/GCP concepts + why Render
│   ├── 05-https-tls-domains-and-dns.md                                       ← certificates, DNS records, in practice
│   ├── 06-monitoring-logging-and-error-tracking.md                             ← logs, metrics, uptime, Sentry, health checks
│   ├── 07-kubernetes-conceptually.md                                             ← Pods/Deployments/Services, when you need it
│   └── 08-deploying-questlog-with-ci-cd.md                                         ← the capstone walkthrough itself
├── exercises/
│   ├── 01-first-github-actions-workflow/                          ← easy
│   ├── 02-ci-pipeline-for-a-toy-app/                                ← guided
│   ├── 03-build-and-push-a-docker-image/                              ← guided/independent
│   ├── 04-add-a-health-check-endpoint/                                  ← independent
│   ├── 05-dns-and-https-investigation/                                    ← independent
│   └── 06-deploy-to-render-with-ci/                                         ← independent, capstone dress rehearsal
├── project/
│   ├── BRIEF.md                                                    ← capstone: real CI/CD pipeline deploying QuestLog
│   └── questlog/                                                     ← QuestLog, copied forward from Module 10, now pipeline-ready
│       ├── .github/workflows/ci-cd.yml                                 ← NEW: test -> build -> push -> deploy
│       ├── render.yaml                                                   ← NEW: Render Blueprint
│       ├── backend/app/main.py                                             ← NEW: /health endpoint + optional Sentry
│       ├── frontend/src/monitoring.ts                                        ← NEW: optional Sentry init
│       └── deploy/                                                             ← Module 09/10's artifacts + a new comparison table
└── CHECKLIST.md
```

Read the lessons in order. Lesson 01 is concept-only, on purpose —
Rule 2 of this course insists the "why" comes before any syntax. Lessons
02-03 are GitHub Actions, applied immediately to QuestLog's own real test
suites. Lesson 04 is cloud fundamentals plus this module's platform
decision. Lessons 05-06 cover the production-operations half of this
module's title (HTTPS/DNS, monitoring). Lesson 07 is Kubernetes,
deliberately conceptual-only, with an optional hands-on appendix at the
end for anyone who wants to go further. Lesson 08 is the capstone
walkthrough itself.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without
looking at its solution, ask for a review, revise if needed, then move
on. Once all six exercises are done, work through `project/BRIEF.md`.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's `project/questlog/`
is Module 10's finished, containerized QuestLog, copied forward, with
`backend/app/` and `frontend/src/` each changed in exactly one small,
real, documented way (a `/health` endpoint; optional, off-by-default
Sentry error tracking) — see `project/questlog/README.md`'s "What
changed" sections for the complete, itemized account of both.
