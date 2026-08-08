# Lesson 04 — Cloud Fundamentals, and Why This Course Chose Render

**Verified against (August 2026), via live web search and direct fetch of
official documentation — see each row:**

| Fact | Verified value | Source |
|---|---|---|
| Fly.io free tier, 2026 | **Discontinued for new signups** — new organizations get only a 2-hour/7-day trial; only pre-existing accounts on legacy plans retain any free allowance | Multiple current (2026) sources cross-checked |
| Railway free tier, 2026 | A one-time $5 trial credit, then a **$1/month** free credit afterward — not enough for an always-on service; Railway's own paid Hobby plan is $5/month | Multiple current (2026) sources, `docs.railway.com/pricing/plans` |
| Render free tier, 2026 | Real, ongoing, no credit card required: free Docker-image-backed web services (750 shared instance-hours/workspace/month, spin down after 15 min idle), free Postgres (1 GB, 30-day expiry + 14-day grace period), free Key Value/Redis-compatible cache, free static sites, automatic TLS on `*.onrender.com` and custom domains | `render.com/docs/free`, `render.com/docs/tls`, `render.com/docs/key-value` |
| AWS/GCP core services | EC2/Compute Engine (raw virtual machines), S3/Cloud Storage (object storage), RDS/Cloud SQL (managed relational databases), IAM (Identity and Access Management) — all confirmed current, stable, long-standing product names | AWS's and Google Cloud's own current documentation |

## What you'll learn

- What a "cloud provider" actually sells, underneath the marketing:
  compute, storage, managed databases, and a permissions system (IAM) —
  in plain language, with no assumed prior cloud experience.
- Where a full cloud provider (AWS/GCP), a raw VPS (Module 09's Hetzner),
  and a container platform (this module's Render) each sit on a real
  "how much do you personally manage" spectrum.
- The real, current (August 2026) research behind this module choosing
  Render specifically over Fly.io, Railway, and a raw AWS ECS setup.
- Exactly what Render's free tier includes and where its genuine,
  honestly-stated limits are.

## Why this matters

Module 09 deployed QuestLog to a VPS you personally administered — you
picked the Linux distro, ran `apt install postgresql` yourself, wrote a
`systemd` unit by hand. That's real, valuable knowledge (most engineers
never learn what's actually happening under a "cloud" deployment) — but
it's also not how most real production deployments happen today, because
most teams don't want to spend engineering time patching operating
systems and managing raw virtual machines when a platform can absorb
that work instead. This lesson explains that whole spectrum, and why this
module deliberately picks a genuinely different point on it than Module
09 did.

## Prerequisites

- **Module 09's whole VPS deployment** — this lesson repeatedly compares
  against it directly; the contrast is the entire point.
- **Module 10's Docker material** — Render, this lesson's chosen
  platform, deploys the exact Docker images that module builds; nothing
  here re-explains what a container image is.

## The concept, explained simply

Picture three different ways a small game studio might get a dedicated
multiplayer server running for players to connect to:

1. **Buy a physical rack server, install an OS on it yourself, wire it
   into a data center you rent space in.** You control absolutely
   everything, and you're responsible for absolutely everything —
   hardware failures, power, cooling, security patches, all of it. This
   is roughly what "owning your own data center" means; essentially no
   modern company outside the largest tech giants does this anymore.
2. **Rent a virtual slice of someone else's already-running physical
   machine — a VPS.** The data center, physical hardware, power, and
   cooling are someone else's problem now; the operating system,
   security patches, and everything that runs on top is still entirely
   yours. **This is Module 09's Hetzner VPS**, exactly.
3. **Hand a game-server *build* (a packaged, ready-to-run artifact) to a
   platform that runs it for you, on infrastructure you never see or
   manage at all** — you don't know or care which physical machine, which
   OS, or which exact virtual machine your server instance is running on
   at any given moment; you just know it's running, reachable, and the
   platform restarts it automatically if it crashes. **This is a
   container platform like Render** (or Fly.io, Railway, AWS ECS/Fargate,
   Google Cloud Run) — you hand it a Docker image; it worries about the
   actual computer.

Each layer trades control for convenience, and each is a completely
legitimate, real, professional choice depending on what a project
actually needs.

## The details

### What "the cloud" actually sells, underneath the branding

A "cloud provider" like AWS or Google Cloud is, underneath enormous
marketing and hundreds of individual product names, really selling four
foundational things:

- **Compute** — a place your code actually runs. AWS calls its raw
  virtual-machine product **EC2** (Elastic Compute Cloud); Google Cloud
  calls its equivalent **Compute Engine**. Conceptually, this is exactly
  Module 09's VPS, just from a bigger, more full-featured provider — you
  still pick an OS, still patch it yourself, still SSH in. Both providers
  also sell more managed compute tiers closer to what Render offers
  (AWS's **ECS/Fargate**, Google's **Cloud Run**) — "give us a container
  image, we run it" — sitting at exactly this lesson's third rung of the
  spectrum above.
- **Object storage** — a place to store files (images, backups, static
  website assets) as simple, named "objects" rather than on a traditional
  filesystem your own server manages. AWS's is called **S3** (Simple
  Storage Service); Google Cloud's is **Cloud Storage**. QuestLog doesn't
  currently need this (it stores no file uploads) — a later module
  (Module 14's RAG document uploads) is exactly the kind of feature that
  would.
- **Managed databases** — a database (Postgres, MySQL, and others) the
  provider itself installs, patches, and backs up for you, instead of you
  running `apt install postgresql` and managing it by hand the way Module
  09 did. AWS's is **RDS** (Relational Database Service); Google Cloud's
  is **Cloud SQL**. This is precisely the same idea as Render's own
  managed Postgres (this module's own `render.yaml`) — a smaller-scale,
  simpler version of the exact same "someone else manages the database
  server" idea.
- **IAM (Identity and Access Management)** — the system controlling
  *who* (which human, or which piece of automation) is allowed to do
  *what* to *which* resource. This is the cloud-provider-scale version of
  exactly the access-control thinking Module 07's auth lesson already
  taught for QuestLog's own users and quests — "can this specific
  identity read this specific thing, write to it, or nothing at all" —
  just applied to an entire company's cloud infrastructure instead of one
  app's data. This module's own GitHub Actions `permissions:` key
  (Lesson 02) is a small, direct cousin of the exact same idea: least
  privilege, granted explicitly, per identity, per resource.

A platform like Render is deliberately **not** trying to be a full cloud
provider selling all four of these things separately, with maximum
configurability — it wraps compute and managed databases specifically,
in a much simpler, more opinionated package, at the cost of some
flexibility a full AWS/GCP setup would offer. That trade-off — less
configurability, dramatically less operational burden — is exactly why
this module picked it.

### Why Render, specifically, over Fly.io, Railway, or raw AWS

This course's own `HANDOVER.md` (the internal generation notes for this
course) explicitly named Fly.io, Railway, and AWS ECS as candidates worth
researching before choosing. Here's what real, current (August 2026)
research found:

- **Fly.io** genuinely had a real, generous free tier for years — but, as
  of 2026, **new signups no longer get one at all**: new organizations
  receive only a 2-hour or 7-day trial (whichever ends first), after
  which real payment is required. This directly conflicts with this
  module's own scope decision (Module 09's same pattern: reading and
  completing this module should never *require* real spending) — so Fly.io
  was ruled out for this course's primary path, however good a platform
  it may otherwise be.
- **Railway** similarly no longer offers a real always-on free tier: a
  one-time $5 trial credit, then $1/month afterward — nowhere near enough
  to keep even one small always-on service running for a full month.
  Railway's own cheapest real plan (Hobby, $5/month) is a fine platform,
  but again conflicts with this module's "reading this never requires
  real spend" requirement.
- **Raw AWS (EC2 + RDS + ECS, configured by hand)** is an enormously
  valuable thing to eventually learn, and genuinely has a real free tier
  for new accounts — but its own setup complexity (VPCs, security groups,
  IAM policies written by hand, load balancer configuration) is large
  enough that teaching it properly would functionally require its own
  multi-lesson module, and would risk this module becoming "AWS
  fundamentals" instead of "CI/CD fundamentals, demonstrated on a real
  platform." This course's own Rule 1 (teach a concept fully before an
  exercise needs it) argues against introducing that much *additional*,
  AWS-specific complexity in a module whose actual subject is CI/CD.
- **Render**, by contrast, currently offers a genuinely real, ongoing,
  no-credit-card free tier: free Docker-image-backed web services, free
  managed Postgres, a free Redis-compatible cache, and fully automatic
  TLS on both its own subdomains and any custom domain you add — every
  single piece this module's capstone needs, at zero cost, verified
  directly from Render's own current documentation while writing this
  module (see this lesson's own header table).

**This is a real, researched decision, not an arbitrary one** — and it's
worth being honest that "which platform has the best free tier" is
exactly the kind of fact that changes over time (Fly.io's own free tier
existed, generously, as recently as a couple of years before this
lesson was written) — Rule 7's own instruction to verify current facts,
not memorized ones, applies especially strongly to this entire lesson.

### Render's free tier, honestly accounted for

- **Free web services** (what QuestLog's backend and frontend each are,
  per `render.yaml`) get 750 shared instance-hours per **workspace**, per
  calendar month — running two services continuously for a full month
  (~730 hours each, ~1,460 hours combined) would exceed that shared
  budget before the month ends. In practice, Render's own spin-down
  behavior (a free web service goes to sleep after 15 minutes with no
  inbound traffic) keeps a personal project's real usage well under this
  limit — but it's worth knowing the limit is shared across every free
  service in one workspace, not per-service.
- **Spin-down** means the FIRST request after 15 minutes of inactivity
  takes up to about a minute to respond, while Render wakes the container
  back up — a real, honest trade-off for a free, always-following-along
  learning deployment; not something a paying customer's production
  traffic would tolerate, which is exactly why Render's paid tiers remove
  this behavior.
- **Free Postgres expires** — 30 days after creation, plus a 14-day grace
  period before actual deletion. Completely fine for working through this
  module's lessons, exercises, and capstone; genuinely not a place to
  keep data you care about long-term without upgrading to a paid instance
  (Render's paid Postgres starts around $7/month at the time of writing).
- **Free Key Value (Redis-compatible)** instance is in-memory only — data
  does not survive a restart. For QuestLog's own use of this cache (a
  30-second TTL, entirely disposable by design — see Module 10's own
  `app/cache.py`), this is a complete non-issue.

## Common mistakes & gotchas

- **Assuming "free tier" means "identical to the paid tier, just
  cheaper."** Every platform's free tier exists specifically to be
  usable but genuinely limited (spin-down, storage caps, expiring
  databases) — designing around those limits *honestly*, rather than
  being surprised by them mid-capstone, is itself a real skill.
- **Confusing a container platform (Render, Fly.io, Railway, Cloud Run,
  ECS/Fargate) with a raw VPS (a Hetzner box, an EC2 instance you SSH
  into).** The giveaway: if you can `ssh` into the actual machine your
  app runs on and see its full operating system, that's a VPS; if you
  can only ever hand the platform a container image and never see or
  choose the underlying machine at all, that's a container platform.
- **Treating "the cloud" as one single thing.** AWS/GCP/Azure are full
  cloud providers selling dozens of individually-priced, separately-
  configured products; Render is a much smaller, more opinionated
  platform built specifically around "here's a container, run it" — both
  are legitimately "the cloud," at very different points on the
  control-vs-convenience spectrum this lesson opened with.

## How this connects

Lesson 05 picks up right where this lesson's "automatic TLS" mention left
off — the actual mechanics of certificates, domains, and DNS, in
practice. Lesson 08's capstone applies this lesson's platform choice for
real, via `render.yaml`.

## Quick self-check

1. Name the four things this lesson says a cloud provider "actually
   sells," and give Render's own rough equivalent of each (where Render
   has one).
2. Where does a raw VPS (Module 09's Hetzner box) sit on this lesson's
   "how much do you personally manage" spectrum, compared to Render?
3. Why did this module rule out Fly.io and Railway as its own primary
   teaching platform specifically, given this course's own scope rules —
   what changed about both of them that made them a worse fit in 2026
   than they might have been a couple of years earlier?
4. What are Render's free-tier Postgres's two real, honest limitations,
   and why are they acceptable for this module's own capstone anyway?
5. What does "spin-down" mean for a free Render web service, and what
   real, concrete effect would it have on the very first request after
   15 minutes of no traffic?
