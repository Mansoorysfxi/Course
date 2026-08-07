# Capstone Brief — Deploy QuestLog to a Real VPS, the Manual Way

## What you're doing

Take this module's `project/questlog/` — Module 08's finished,
fully-tested QuestLog, copied forward with its application code
completely unchanged — and deploy it to a real, internet-reachable
Ubuntu 24.04 server, entirely by hand: no Docker, no CI/CD, no managed
platform. Every command typed yourself, every config file written and
understood.

This is not a coding exercise. You will not write or modify a single
line of `backend/app/` or `frontend/src/`. Your deliverable is a
**working, real deployment** (or, if you're doing this as a dry run
without a paid VPS yet, a complete, correct, followable runbook you
demonstrably understand and could execute) plus a short written report.

## Before you start

- [ ] All five exercises in this module are done and reviewed.
- [ ] You've read Lessons 00–08 in full, in order.
- [ ] You've decided whether you're executing this live against a real
      VPS (recommended if you can — see `lessons/00-setup.md`'s cost
      note, roughly $4–6/mo for the time it takes to do this once) or
      working through it as a careful, honest dry run.

## What to actually do

Follow `lessons/07-deploying-questlog-part1-server-and-backend.md` and
`lessons/08-deploying-questlog-part2-frontend-and-going-live.md` in
order, using
[`project/questlog/deploy/DEPLOY_RUNBOOK.md`](questlog/deploy/DEPLOY_RUNBOOK.md)
as your working checklist. Concretely, you need to end up with:

1. A fresh Ubuntu 24.04 server, hardened per Lesson 07 (non-root sudo
   user, key-only SSH, `ufw` active with only `OpenSSH` and
   `Nginx HTTP` allowed).
2. PostgreSQL installed and configured with a fresh `questlog` database
   and role, using a real, freshly-generated password — never this
   course's local development password.
3. QuestLog's backend copied onto the server, running as a real,
   `enable`d `systemd` service (`questlog-backend.service`), owned by a
   dedicated, unprivileged `questlog` system user, reading a real
   production `.env` with a freshly-generated `SECRET_KEY`.
4. QuestLog's frontend, **built on your own machine** (not the server —
   Lesson 08 explains exactly why, including a real, checkable reason
   specific to this codebase's `package.json`), shipped to the server,
   and served as static files by Nginx.
5. Nginx reverse-proxying `/api/*` to the backend and serving the
   frontend for everything else, including correct SPA fallback
   (`try_files`).
6. The whole thing reachable, from a genuinely different machine (your
   own laptop's browser, not the server itself), at
   `http://<YOUR_SERVER_IP>/` — login working, quests loading, a
   direct-navigated client-side route (`/quests/<id>`) not producing a
   raw 404.

## Deliverables

Write up a short report (a new file,
`project/DEPLOYMENT_REPORT.md` — create this yourself; there's no
template, because the honest content matters more than a fixed shape)
covering:

1. **What you actually did** — real VPS or dry run, which provider (if
   real), and a summary of each phase.
2. **At least one thing that didn't work on the first try**, what the
   actual error/symptom was, and how you diagnosed and fixed it. (If
   you genuinely hit zero problems on a completely fresh attempt,
   that's worth mentioning too, but re-read this module's "Common
   mistakes & gotchas" sections and try to deliberately reproduce **one**
   of them on purpose, then fix it — the debugging experience itself is
   part of what this capstone is teaching, per this module's own
   "painful way, on purpose" framing.)
3. **Your own answers to Lesson 08's "what this deploy deliberately does
   not yet do" list** — for each of the four named gaps, explain in your
   own words why it's acceptable for now and which later module fixes
   it.
4. **Verification evidence** — the actual output (or a precise
   description, if you're on a dry run) of the negative checks: proving
   port 8000 and port 5432 are genuinely unreachable from outside the
   server, and that `ufw status verbose` shows exactly the two allowed
   rules and nothing more.

## Acceptance criteria (what "done" looks like)

- [ ] Every checklist item in
      `project/questlog/deploy/DEPLOY_RUNBOOK.md`'s Phases 1–6 is
      genuinely complete (or, for a dry run, you can explain in detail
      exactly what each step would produce and why).
- [ ] `DEPLOYMENT_REPORT.md` exists and covers all four numbered points
      above, honestly (a report that claims a suspiciously perfect,
      problem-free first attempt gets asked to try again with a
      deliberately reproduced failure, per point 2 above).
- [ ] You can explain, without looking anything up, the full request
      path a browser's `GET /api/quests` takes through this deployed
      system, naming every process and port involved, in order.
- [ ] You can explain why QuestLog's own application code required zero
      changes for any of this.

## If you're doing this as a dry run (no real VPS)

That's a legitimate, acceptable way to complete this capstone — this
module's own `lessons/00-setup.md` says so explicitly. Your
`DEPLOYMENT_REPORT.md` should say so honestly, and instead of real
command output, walk through each phase describing exactly what you'd
expect to see and why, referencing the specific lesson section that
explains it. The grading standard (Rule 3) is the same either way:
demonstrated understanding, not just a working URL.
