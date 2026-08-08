# Lesson 01 — What CI/CD Is, and Why It Exists

## What you'll learn

- What **Continuous Integration (CI)** and **Continuous Deployment/
  Delivery (CD)** each actually mean, precisely — not just the acronym.
- The concrete, real-world failure modes that existed *before* CI/CD was
  common practice, and why each one keeps happening the moment a team
  stops automating.
- The difference between **Continuous Delivery** and **Continuous
  Deployment** specifically — a genuinely common point of confusion, even
  among working engineers.
- Why this course teaches CI/CD only now, at the very end of the
  DevOps/Deployment phase, after Linux (Module 09) and Docker (Module 10)
  — not before either.

## Why this matters

Every single lesson after this one in this module is really just "how do
I make the thing this lesson describes actually happen automatically."
If the *why* isn't solid first, the syntax in Lesson 02 will feel like
arbitrary YAML to memorize instead of a direct, sensible answer to a real
problem you already understand.

## Prerequisites

- **Module 08's testing material** — CI's entire value proposition is
  "run the tests that already exist, automatically, on every change";
  without a real test suite already existing (which QuestLog has had
  since Module 08), there would be nothing for CI to actually run.
- **Module 10's Docker material** — CD's entire value proposition, in
  this module's own pipeline, is "build the image that already builds
  correctly by hand, automatically, and ship it."

## The concept, explained simply

Picture how a AAA game studio historically shipped a build to QA, before
build automation was standard: an engineer, on their own machine, at the
end of the day, manually compiles the project, manually zips up the
resulting build, and manually copies it to a shared drive with a
filename like `build_final_v3_ACTUALLY_FINAL.zip`. This works, until it
doesn't: someone forgot to pull the latest changes before building, so
the "final" build is missing yesterday's fix. Someone's local machine has
a slightly different compiler version, so a bug that doesn't reproduce
on their machine ships anyway. QA spends half a day discovering the build
straight up doesn't compile on a clean machine, because it silently
depended on some file the engineer's own machine happened to already
have lying around from months ago.

A **CI/CD pipeline** is the automated build farm that replaced all of
that: a dedicated, clean, disposable machine (or several) that, every
single time someone pushes a change, automatically pulls the *exact*
latest code, builds it from a completely clean environment (so "works on
my machine" stops being a valid excuse — this is the *exact* same problem
Module 10's Docker lesson solved for running an app, now applied to
*building and testing* it too), runs every automated test against that
clean build, and — only if every single test passes — packages the
result and ships it somewhere real. No human decides, case by case,
whether today's build gets shipped; the pipeline's own pass/fail result
decides.

**Continuous Integration (CI)** is specifically the first half of that:
automatically building and testing every change, as often as possible
(ideally on every single push), so a broken change is caught within
minutes of being written — while whoever wrote it still remembers exactly
what they just changed — instead of being discovered days later, mixed in
with a dozen other people's changes, when nobody can quickly tell whose
change actually broke it.

**Continuous Delivery** is the second half: every change that passes CI
is automatically packaged into a deployable artifact (in this module's
case, a Docker image) that a human *could* deploy with one click or one
command, at any time — but a human still makes that final "deploy now"
decision.

**Continuous Deployment** goes one step further than Continuous
Delivery: every change that passes CI is automatically deployed to
production, with **no human approval step at all**. This module's own
capstone pipeline (Lesson 08) is Continuous Deployment, specifically:
push to `main`, and — if tests pass — it's live, full stop, no button to
click. This is a deliberate, real choice worth naming explicitly: many
real companies deliberately stop at Continuous *Delivery* instead (a
human clicks "deploy" after CI passes, often gated by a staging
environment or a manual QA pass) precisely because automatic deployment
means a genuinely broken idea that nonetheless passes every existing
automated test ships to real users with nobody in the loop. This course's
own QuestLog capstone accepts that trade-off because it's a personal
learning project with no real users at stake — see this lesson's own
"How this connects" section for exactly where you'd add a manual approval
step if you didn't want that trade-off for a real project.

## The details

### What actually happens without CI/CD (a concrete before/after)

Before this module, running QuestLog's tests and deploying it looked
like this, entirely by hand:
```bash
cd backend && python -m pytest -v      # a human remembers to run this
cd ../frontend && npm run test          # and this
docker compose build                     # and this
# ...then, per Module 09's own manual runbook, SSH into a server and
# restart services by hand, or per Module 10, docker compose up -d
# on whatever machine happens to be running the stack.
```
Every single step above depends on a human remembering to do it, doing
it in the right order, and doing it on a machine that's actually
correctly configured. Skip the test step just once, under deadline
pressure ("I'm sure it's fine, it's a one-line CSS fix") and a real bug
ships. This isn't hypothetical or exaggerated — it is, genuinely, the
single most common way real production incidents happen at companies
that haven't automated this.

### The exact same steps, automated

This module's own `.github/workflows/ci-cd.yml` (Lesson 02 explains its
syntax in full; Lesson 03 explains QuestLog's specific test jobs) runs
those same commands — literally the same `pytest`, the same `npm run
test`, the same `docker build` — but on a fresh, clean, disposable
virtual machine GitHub provides, triggered automatically by the act of
pushing code, with zero possibility of "I forgot" or "it works on my
machine." The deploy step at the end (Lesson 08) only ever runs if every
earlier step succeeded — this is the whole mechanism that makes it
impossible to accidentally deploy code that fails its own tests.

### Why this course teaches CI/CD last, in Phase 3, not earlier

CI/CD automates *existing* processes — it has nothing to build a
pipeline around without Module 08's real test suites already existing,
and nothing meaningful to package and ship without Module 10's Docker
images already existing. Learning CI/CD before either of those would
mean learning YAML syntax with no real muscle memory of *why* each step
exists — exactly the kind of "here's a workflow file, copy it" cargo-cult
learning this course's Rule 2 is built to avoid.

## Common mistakes & gotchas

- **Treating "CI" and "CI/CD" as interchangeable.** A project can have a
  real, valuable CI pipeline (tests run automatically on every push) with
  **no** deployment automation at all — this is genuinely common and
  genuinely fine; CD is a separate, additional decision, not something
  CI implies.
- **Assuming CI/CD makes testing itself optional or less important.**
  It's the opposite: a CI pipeline with a weak or missing test suite
  automates shipping bugs *faster* and with *more confidence* than
  before, which is strictly worse than a human at least occasionally
  hesitating. Module 08's real test suite is what makes this module's
  automation trustworthy at all.
- **Confusing "Continuous Deployment" with "no testing/review at all."**
  Real Continuous Deployment setups still gate on automated tests,
  linting, and often additional automated checks (security scans,
  smoke tests against a staging environment) — "continuous" describes
  the deploy *cadence*, not the *rigor*.

## How this connects

Lesson 02 gives this lesson's "automated build farm" idea a real, exact
syntax: GitHub Actions. Lesson 08's capstone pipeline is a concrete,
working Continuous Deployment setup for QuestLog — its own
`lessons/08-deploying-questlog-with-ci-cd.md` includes a short, explicit
note on exactly which one YAML condition you'd change to turn it into
Continuous *Delivery* instead (requiring a manual approval before the
deploy job runs), for anyone who wants to see that trade-off made
concrete rather than just described here.

## Quick self-check

1. In your own words, using this lesson's own build-farm analogy, what
   specific real-world failure does CI directly prevent?
2. What's the precise difference between Continuous Delivery and
   Continuous Deployment — where exactly does the human decision point
   move (or disappear)?
3. Why would a CI/CD pipeline built on top of a codebase with no
   automated tests at all arguably be *worse* than no pipeline?
4. Why does this course teach Modules 08 and 10 (testing, Docker) before
   this module, rather than teaching CI/CD earlier in the course?
5. Name one real reason a company might deliberately choose Continuous
   Delivery over Continuous Deployment for a real product, even though
   the fully automated version is technically possible.
