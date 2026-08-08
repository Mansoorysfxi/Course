# Module 11 Checklist — CI/CD, Cloud & Production Operations

Complete this before moving on to Module 12. Check off each item
honestly — this is a self-assessment, not a formality.

## Lessons

- [ ] Read `lessons/00-setup.md` and confirmed every command in its
      "Verify your setup" section — GitHub, a free Render account, and
      (if chosen) Sentry/a real domain.
- [ ] Read `lessons/01-what-ci-cd-is-and-why.md` and can explain the
      real difference between Continuous Integration, Continuous
      Delivery, and Continuous Deployment without hesitation.
- [ ] Read `lessons/02-github-actions-from-zero.md` and can read any
      real workflow YAML file without guessing at its syntax.
- [ ] Read `lessons/03-a-real-ci-pipeline-for-questlog.md` and have
      genuinely watched a test fail in CI, on purpose, and read the
      resulting log.
- [ ] Read `lessons/04-cloud-fundamentals-and-your-chosen-platform.md`
      and can explain why this module chose Render over Fly.io, Railway,
      and raw AWS, using this module's own researched reasoning.
- [ ] Read `lessons/05-https-tls-domains-and-dns.md` and can explain the
      ACME protocol and the difference between an `A` and a `CNAME`
      record without looking it up.
- [ ] Read `lessons/06-monitoring-logging-and-error-tracking.md` and can
      explain the real difference between logs, metrics, uptime
      monitoring, and error tracking.
- [ ] Read `lessons/07-kubernetes-conceptually.md` and can explain what a
      Pod, a Deployment, and a Service each are, and correctly judge
      whether a given project needs Kubernetes.
- [ ] Read `lessons/08-deploying-questlog-with-ci-cd.md` in full.

## Exercises

- [ ] Exercise 01 (first GitHub Actions workflow) — done and reviewed.
- [ ] Exercise 02 (CI pipeline for a toy app) — done and reviewed,
      including a real, watched test run (or a genuinely thorough
      reasoning-through if you didn't push a real repo).
- [ ] Exercise 03 (build and push a Docker image) — done and reviewed,
      including correctly explaining the lowercase-image-name gotcha.
- [ ] Exercise 04 (health check endpoint) — done and reviewed, including
      both the healthy and unhealthy test cases genuinely passing.
- [ ] Exercise 05 (DNS and HTTPS investigation) — done and reviewed, with
      real, live command output, not paraphrased from memory.
- [ ] Exercise 06 (deploy to Render with CI) — done and reviewed, either
      for real or via a genuinely thorough dry run.

## Capstone

- [ ] `project/BRIEF.md`'s pipeline runs completely automatically on a
      real push to `main` — tests, build, push, and (Part 1-2 complete)
      deploy — with zero manual intervention beyond the push itself.
- [ ] Part 3's cross-service API fix is genuinely implemented and
      verified, with a documented explanation of which approach and why.
- [ ] The live deployment (or dry run) genuinely serves QuestLog over
      real HTTPS, with a working `/health` endpoint.
- [ ] Part 5's deliberately broken-then-fixed scenario is genuinely
      reproduced and documented.
- [ ] `project/CICD_REPORT.md` written, covering all five required
      points from the brief.
- [ ] You can explain, unprompted, the complete path a `git push` takes
      from your own machine to a real user seeing an updated Quest Board.
- [ ] No stray real cloud resources (test services, unused databases) are
      left running that you don't intend to keep.

## Spaced repetition — review questions from earlier modules

Per this course's Rule 6, answer these without re-reading the original
lesson first; check your answer against the linked material afterward.

1. **(Module 02)** What specifically does a TLS certificate prove, and
   what does it deliberately NOT prove about the site presenting it?
   *(See `module-02-internet-and-web-fundamentals/lessons/02-tcp-tls-and-the-request-response-journey.md`.)*
2. **(Module 05)** What does FastAPI's `Depends()` actually do,
   mechanically, when a route function declares a parameter using it —
   and why does this make a route's own database dependency easy to
   swap out inside a test? *(See
   `module-05-backend-fastapi/lessons/04-dependency-injection-and-depends.md`.)*
3. **(Module 07)** What specific problem does CORS solve, and from which
   side (browser or server) does the restriction it enforces actually
   originate? *(See `module-07-auth-security/lessons/10-cors-in-depth.md`.)*
4. **(Module 08)** Why did QuestLog's own backend test suite choose an
   in-memory SQLite database instead of a real, dedicated Postgres
   database for tests — what's the honest trade-off involved? *(See
   `module-08-testing-and-quality/lessons/06-testing-with-a-database.md`.)*
5. **(Module 10)** Why does `backend/Dockerfile` run `alembic upgrade
   head` on every single container start, rather than once, by hand,
   the way Module 09's manual deploy did — and why is this safe to do
   repeatedly? *(See
   `module-10-docker-and-containers/lessons/07-containerizing-questlogs-backend.md`.)*

## Before moving to Module 12

- [ ] All boxes above are checked honestly.
- [ ] You understand, in your own words, that Module 12 (AI/ML
      Foundations) is intentionally concept-only, with no QuestLog code
      changes — standalone exercises on tokenization, embeddings, and
      prompting, before any of that gets wired into the running project
      starting Module 13.
