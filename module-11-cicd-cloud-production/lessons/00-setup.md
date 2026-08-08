# Lesson 00 — Setup: Accounts, What's Actually Free, and Verifying Everything Works

**Verified against (August 2026), via live web search/direct fetch of
official sources — see each row:**

| Fact | Verified value | Source |
|---|---|---|
| Render free-tier signup | No credit card required (confirmed via multiple current, 2026 sources cross-checked against Render's own marketing/docs; one older, unverified third-party report claimed otherwise — this lesson trusts Render's own current documentation) | `render.com` articles/docs, cross-checked August 2026 |
| Render free web service | 750 shared free instance-hours per **workspace** per calendar month; a free web service spins down after 15 minutes with no inbound traffic and takes up to ~1 minute to wake back up | `render.com/docs/free` |
| Render free PostgreSQL | 1 GB storage; **expires 30 days after creation**, with a further 14-day grace period before actual deletion | `render.com/docs/free` |
| Render free Key Value (Redis-compatible) | One per workspace; runs Valkey 8; in-memory only, data does not survive a restart | `render.com/docs/key-value` |
| Render TLS | Free, fully automatic (Let's Encrypt / Google Trust Services) certificates for both `*.onrender.com` subdomains and any custom domain you add, auto-renewed, with automatic HTTP→HTTPS redirect | `render.com/docs/tls` |
| Sentry Developer (free) plan | 5,000 errors/month, 1 user, 30-day retention, free forever, no card required | multiple current (2026) sources cross-checked |
| GitHub Actions | Free for public repos; a generous free monthly minutes allowance for private repos on a personal account (this course's usage is far below any such limit) | GitHub's own current documentation |

## What you'll learn

- Exactly which accounts this module uses, and — for each one — whether
  it costs anything to sign up, to read this module, or to complete the
  capstone.
- How to create a free Render account and understand what its free tier
  actually includes and where its real limits are.
- How to (optionally) create a free Sentry account, and how to (also
  optionally) buy a real domain, if you choose to.
- Exactly which repository a GitHub Actions workflow file actually runs
  against — a genuinely confusing point this course addresses directly,
  once, here.
- How to verify every piece of this setup actually works, with exact
  commands and exact expected output.

## Why this matters

Every lesson from here on assumes these accounts exist (or explains
clearly which specific step needs them). Module 09 asked you a similar
question about a VPS; this module asks it again, for a different,
higher-level kind of infrastructure — and, just like Module 09, the
honest answer is: reading and understanding every single lesson in this
module requires **zero** spending. Only if you choose to *execute* the
capstone live, on a real, internet-reachable Render deployment, do any
of these accounts actually get used for real — and even then, the
default path (Render's free tier, no custom domain) costs nothing.

## Prerequisites

- **Module 00** — a GitHub account, `git` installed and configured
  (`git config user.name`/`user.email`), comfort with `push`/`pull`.
- **Module 10** — Docker Desktop installed and working (`docker compose
  version` succeeds) — this module's exercises and capstone still build
  and run the exact containers Module 10 taught, locally, before ever
  touching a real deploy.
- A web browser and, ideally, 15-20 uninterrupted minutes to click
  through two or three signup flows in one sitting.

## The concept, explained simply

Think of this module's whole account setup the way you'd think about
setting up a build farm and a distribution platform for a real game
studio, before writing a single line of the actual CI pipeline: you need
somewhere the automated builds *run* (GitHub Actions — you already have
this, from Module 00's GitHub account), somewhere the finished, packaged
build actually *ships to and runs on* for players to reach (Render), and,
optionally, somewhere that watches the shipped build for crashes once
real players are hitting it (Sentry) and a real, memorable address
players type in instead of a build-server-generated URL (a custom
domain). None of the "watches for crashes" or "memorable address" pieces
are required to have a working, automated pipeline at all — they're
genuinely optional layers on top of a build farm and a distribution
platform that already work without them.

## The details

### Step 1 — GitHub (you already have this)

Module 00 already had you create a GitHub account. Confirm it still
works:

```bash
git config --get user.name
git config --get user.email
```
**Expected:** your name and email print, with no error. If either is
empty, revisit Module 00's own setup lesson before continuing.

**A genuinely important point this lesson addresses once, up front:**
GitHub Actions only ever runs a `.github/workflows/*.yml` file for the
specific GitHub repository that file's own commit actually lives in, on
GitHub's own servers — never for a folder sitting on your own machine
that hasn't been pushed anywhere, and never "for this whole course," if
this whole course's repository is itself one giant monorepo you haven't
pushed as-is. Every workflow file this module writes (starting with
`project/questlog/.github/workflows/ci-cd.yml`) is written **as if the
folder it lives inside (`project/questlog/`, or a given exercise's own
`starter/`/`solution/` folder) is the ROOT of its own, separate GitHub
repository** — not this whole course's repo. This mirrors exactly how
Module 09's own `lessons/07` already treated `project/questlog/` as a
`git clone`-able unit on its own. To actually run any of this module's
pipelines for real: create a new, empty repository on GitHub (green "New"
button, `github.com/new`), then, from your own machine:
```bash
cd module-11-cicd-cloud-production/project/questlog
git init
git add .
git commit -m "Module 11: QuestLog with CI/CD"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/questlog.git
git push -u origin main
```
**Expected:** GitHub's own repository page, once refreshed, shows every
file from `project/questlog/`, including the `.github/workflows/`
folder — and, within a few seconds, a new run appears under that repo's
own **Actions** tab, because pushing to `main` is exactly this pipeline's
own configured trigger (Lesson 02 explains `on: push:` in full). This
step is entirely optional for *reading and understanding* this module —
it's only needed the moment you want a workflow to genuinely execute.

### Step 2 — Create a free Render account

Go to `render.com`, click **Get Started**, and sign up (signing up with
your existing GitHub account is the most convenient option — it also
sets up the permission Render needs later to read your repos, if you
ever use its native git-based deploys instead of this module's
registry-image approach). **No credit card is requested during this free
signup**, per Render's own current policy (verified above). You now have
a Render **workspace** — the container for every service, database, and
Key Value instance you create, and the unit its 750 free instance-hours/
month are shared across (Lesson 04 explains this fully).

### Step 3 — (Optional) Create a free Sentry account

If you want real error tracking (Lesson 06), go to `sentry.io`, sign up
for the free **Developer** plan (no card required), and create one
project — choose **Python** for a project that will receive backend
errors, and note you'll create a *second* project (or add a second
platform to the same project, Sentry supports both) for the frontend.
Skip this step entirely if you'd rather read Lesson 06 conceptually for
now — nothing else in this module requires it.

### Step 4 — (Optional) Buy a real domain

Completely optional. If you want a real domain pointed at your
deployment (Lesson 05), a `.com` currently costs roughly **$9-10 for the
first year** at a registrar like Namecheap (`namecheap.com`), with
renewal typically **$14-19/year** afterward (verified August 2026 —
promotional first-year pricing is common and never guarantees the
renewal price, so read the renewal price before buying anywhere). If you
skip this, Render's own free `https://your-app.onrender.com` subdomain,
with automatic HTTPS already included, is a completely legitimate way to
complete this entire module — see Lesson 05's own explicit framing.

### Step 5 — Re-verify Module 10's Docker setup

```bash
docker compose version
```
**Expected:** `Docker Compose version v2.x.x` (Module 10's own
`lessons/00-setup.md` has the full troubleshooting if this fails — per
this course's Rule 8, no earlier module's setup is assumed to still be
fine without re-checking).

## Verify your setup

Run through every check below before starting Lesson 01.

**1. Git and GitHub:**
```bash
git config --get user.name && git config --get user.email
```
**Expected:** both print, no error.

**2. Render account exists and its dashboard loads:**
Log into `dashboard.render.com` in your browser. **Expected:** an empty
workspace (no services yet) with a **New +** button — this is exactly
what a freshly created account looks like; you'll create your first
service in this module's capstone (Lesson 08).

**3. Docker still works:**
```bash
docker run --rm hello-world
```
**Expected:** the same `Hello from Docker!` message Module 10's own
setup lesson had you confirm.

**4. (Only if you completed Step 1's optional "push a real repo" part)
GitHub Actions actually ran:**
Open `https://github.com/YOUR_USERNAME/questlog/actions` in a browser.
**Expected:** at least one workflow run listed, with a status icon
(a yellow dot while running, a green check once finished, a red X if
something failed — this module's later lessons explain how to read a
failed run's own logs in full).

**5. (Only if you completed Step 3) Sentry project exists:**
Your Sentry dashboard shows at least one project, and its **Settings →
Client Keys (DSN)** page shows a real DSN string starting with
`https://` — you'll paste this into an environment variable in Lesson 06
/ Lesson 08, never directly into any file this course commits to Git.

If every check you attempted matches, you're ready for Lesson 01.

**Try it yourself:** Before moving on, open your new (or existing)
Render workspace's **Account Settings** page and find the exact wording
Render itself currently uses to describe its free tier's limits (instance
hours, database expiry). Compare it, in your own words, against this
lesson's own header table — platform free-tier terms are exactly the
kind of fact this course's Rule 7 says to verify fresh rather than trust
a lesson written months or years before you're reading it.

## Common mistakes & gotchas

- **"My GitHub Actions workflow never runs at all."** By far the most
  common cause, especially given this module's own repo-boundary
  explanation above: the `.github/workflows/` folder has to sit at the
  literal root of the repository GitHub is watching — a
  `.github/workflows/ci-cd.yml` that's actually nested one level deeper
  (e.g. inside a folder GitHub sees as `questlog/.github/workflows/...`
  because you pushed a parent folder as the repo root by mistake) is
  silently ignored; GitHub Actions only ever looks in `.github/workflows/`
  relative to the true repo root.
- **"Render asked for a credit card after all."** If you're offered a
  *paid* plan upgrade or a specific *paid* add-on, that's expected and
  fine to decline — the free web service / free Postgres / free Key
  Value tiers themselves, per Render's own current policy, do not require
  one. If the base signup flow itself demands one before you can create
  even a single free resource, something has changed since this lesson
  was verified (August 2026) — treat this lesson's own Rule 7 header as
  what to re-check, not as unquestionable fact forever.
- **Signing up for Sentry and immediately being confused about "projects"
  vs. "organizations."** An **organization** is the top-level account
  (usually just you, for this course); a **project** is one specific
  app's error stream inside it — QuestLog's backend and frontend get
  either two separate projects, or one project with two "platforms"
  attached, depending on which option Sentry's own current onboarding
  flow offers when you get there.
- **Forgetting which `.env` a given environment variable belongs in.**
  This module reuses Module 10's own local `docker-compose.yml`/`.env`
  files unchanged for local work, and introduces GitHub **Actions
  secrets** (Lesson 02) and Render **environment variables** (Lesson 08)
  as two entirely separate places the *same* values (like `SECRET_KEY`)
  sometimes need to be re-entered — there is no automatic syncing between
  any of these three locations.

## How this connects

Lesson 01 starts with the *why* of CI/CD — no syntax yet, per this
course's Rule 2 (concepts before code). Lesson 02 is the first lesson
that actually needs a real GitHub repository to push to, if you want to
run anything for real, which is exactly what this lesson's Step 1 set
up. Lessons 04, 06, and 08 each depend on the Render, Sentry, and
optional-domain accounts this lesson created.

## Quick self-check

1. Which of this module's accounts genuinely requires payment to *read
   and understand* every lesson in this module?
2. Where, specifically, does a `.github/workflows/*.yml` file have to
   live for GitHub to actually run it — and why does this matter for how
   this course's own `project/questlog/` folder is meant to be used?
3. What are the two real limits on Render's free Postgres that make it
   fine for this module's capstone but not a permanent home for real
   data without upgrading?
4. If you skip creating a Sentry account entirely, what specifically
   breaks in this module's own capstone or exercises?
5. Name one concrete thing you'd need to check, right now, to confirm
   this lesson's own "no credit card required" claim about Render is
   still true by the time you're reading it, rather than trusting this
   lesson's own text forever.
