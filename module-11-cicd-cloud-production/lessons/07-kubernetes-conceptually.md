# Lesson 07 — Kubernetes, Conceptually

**Verified against (August 2026):** Pod, Deployment, and Service remain
Kubernetes' current, stable, actively-used core object types — no
renaming or deprecation found. Ingress (the API object) also remains
current, though the once-dominant **Ingress-NGINX controller project**
itself is being retired (maintenance ended March 2026), with the
ecosystem moving toward the newer **Gateway API** as its long-term
successor for traffic routing — worth knowing as current context, not a
reason this lesson's own Ingress explanation is wrong or outdated.

## What you'll learn

- What actual problem Kubernetes solves, and — deliberately, up front —
  when a project genuinely does NOT need it.
- Kubernetes' four core object types: **Pod**, **Deployment**,
  **Service**, and **Ingress** — enough to read a real
  `kubectl`/YAML-based project and hold a real technical conversation
  about it.
- Why this course teaches Kubernetes **conceptually only** — no hands-on
  requirement — and where QuestLog itself sits relative to "needs
  Kubernetes."
- (Optional appendix) How to try a tiny, real, local Kubernetes cluster
  yourself, if you want hands-on exposure beyond this lesson's own scope.

## Why this matters

Kubernetes is one of the single most commonly *name-dropped*, and most
commonly *misunderstood*, pieces of the whole DevOps world. You will see
it mentioned in job postings, in architecture diagrams, in casual
conversation with other engineers, long before (if ever) a project you
work on genuinely needs it. This lesson's entire goal is narrow and
specific: let you hold a real, informed conversation about what it is
and isn't, and correctly judge whether a given project needs it — not
teach you to operate a real cluster (the master plan for this course
explicitly scopes this as conceptual-only, with hands-on strictly
optional).

## Prerequisites

- **Module 10's Docker/Compose material in full** — Kubernetes is, at
  its core, a much larger, much more automated answer to a question
  `docker-compose.yml` already answers at a small scale ("run these
  several containers together, with these connections between them") —
  every concept in this lesson is explained by direct comparison to
  something Compose already does.
- **Lesson 04's cloud-platform spectrum** — Kubernetes sits at yet
  another point on that same "how much do you personally manage"
  spectrum, discussed explicitly below.

## The concept, explained simply

Recall Module 10's own `docker-compose.yml`: one file, describing
several containers, running on **one machine**. That's genuinely
sufficient for QuestLog's own scale — one backend container, one
frontend container, one database, one cache, all comfortably fitting on
a single server.

Now imagine a real, successful multiplayer game whose matchmaking service
needs to run not one instance, but **dozens**, spread across **many
different physical machines**, because no single machine has enough
capacity — and that number needs to grow automatically under heavy
player load, and shrink back down afterward to avoid paying for idle
capacity, and any one machine crashing at 3 AM should not take down the
whole matchmaking service, and a new version needs to roll out
gradually, replacing old instances one at a time, without ever dropping
below the minimum capacity needed to keep serving players.
**Docker Compose has no answer to any of that — it was never designed
to.** **Kubernetes** is the tool built specifically for exactly this
problem: a **fleet manager for containers, across many machines at
once** — conceptually, exactly like a dedicated-game-server fleet manager
that automatically spins up more server instances as player demand rises,
automatically kills and replaces instances that stop responding
correctly, and automatically spreads instances across many physical
machines so no single machine's failure takes the whole fleet down.

## The details

### Kubernetes' four core objects

- **Pod** — the smallest unit Kubernetes actually schedules and runs.
  Almost always one container (occasionally a small handful of tightly-
  coupled containers that must always run together, sharing a network
  namespace) — conceptually the Kubernetes-world equivalent of one
  running container from `docker compose up`, just described in
  Kubernetes' own vocabulary and API. Pods are **disposable** — Kubernetes
  routinely destroys and recreates them (to move them to a different
  machine, to roll out a new version, to replace one that crashed) — you
  are never meant to treat one specific Pod as precious or long-lived,
  exactly the same "containers are disposable, data belongs in a volume"
  lesson Module 10 already taught, just at a larger scale.
- **Deployment** — describes the DESIRED state of a set of identical
  Pods: "I want 5 replicas of this exact container image, always
  running." Kubernetes' own control loop continuously compares this
  desired state against reality, and takes action the moment they
  diverge — a Pod crashes, Kubernetes starts a replacement, without a
  human doing anything at all. This is conceptually similar to
  `docker-compose.yml`'s own `restart: unless-stopped` (Module 10), but
  operating across an entire fleet of identical replicas, across
  multiple machines, instead of one container on one machine.
- **Service** — gives a STABLE network name/address to a Deployment's own
  constantly-changing set of Pods. Because Pods are disposable (created
  and destroyed constantly, each getting a new internal IP address every
  time), something else in the cluster that wants to reach "the
  matchmaking service" can't reasonably track individual Pod IPs
  directly — a Service provides one stable name that automatically
  load-balances across whichever Pods are currently healthy, at any
  given moment. This is conceptually the cluster-scale version of exactly
  what Module 10's own Compose networking lesson taught: reaching a
  service by its stable *name*, never by chasing an individual
  container's own IP address.
- **Ingress** — routes real, external internet traffic INTO the cluster,
  to the correct Service, based on things like the request's hostname or
  URL path (`api.yourdomain.com` → the backend Service;
  `yourdomain.com` → the frontend Service) — conceptually the Kubernetes-
  world equivalent of Module 09's own Nginx reverse proxy, just
  operating as a first-class, cluster-managed object instead of a
  hand-configured file on one specific machine.

### When a project genuinely needs Kubernetes — and when it doesn't

Kubernetes solves real problems at real scale: many replicas, across
many machines, needing automatic healing, automatic scaling, and
coordinated rollouts. It also comes with real, genuine operational cost:
learning its own substantial vocabulary and API, running (or paying a
cloud provider to run) the cluster infrastructure itself, and
meaningfully more moving parts than a single `docker-compose.yml`.
**QuestLog, at this course's own scale, does not need Kubernetes at
all** — one backend container, one frontend container, comfortably
handled by Render's own much simpler container-platform abstraction
(Lesson 04). This is not a cop-out; it's the correct, honest engineering
judgment for this project's actual scale. A useful, real rule of thumb:
reach for Kubernetes when you genuinely need MULTIPLE replicas of a
service, coordinated automatic scaling, or multi-machine scheduling —
not by default, and not because it's the most talked-about tool in the
room.

**Where does a platform like Render fit into this?** Many container
platforms (including some of Render's own underlying infrastructure, and
definitely true of Google Cloud Run and AWS Fargate) actually run
Kubernetes (or something conceptually similar) underneath their own,
simpler interface — you get many of Kubernetes' real benefits
(automatic restarts, health-check-based routing) without ever writing a
line of Kubernetes YAML or learning its vocabulary yourself. This is
exactly Lesson 04's own spectrum, one more rung deep: sometimes the
"simpler platform" you're using is itself built on the "more complex"
tool underneath, deliberately hidden from you.

## Optional appendix — trying a real, local, tiny Kubernetes cluster

Entirely optional; nothing later in this course requires it. If you want
genuine hands-on exposure beyond this lesson's conceptual explanation,
look into **`minikube`** or **`kind`** ("Kubernetes IN Docker") — both
let you run a small, real, single-machine Kubernetes cluster locally
(using Docker itself, which you already have from Module 10), and
`kubectl` (Kubernetes' own command-line tool) to create a Deployment and
a Service by hand, and watch `kubectl get pods` show Kubernetes
automatically replacing a Pod you deliberately kill. This course does
not walk through the exact, current installation steps for either tool —
consistent with Rule 7, installation procedures for fast-moving tools
should be verified fresh at the moment you actually want to try this,
not learned from a lesson that could be stale by the time you read it.

## Common mistakes & gotchas

- **Assuming Kubernetes is required for "real" production deployments.**
  Plenty of real, successful, production systems (including this
  course's own QuestLog capstone) run happily on much simpler
  infrastructure. Kubernetes is a tool for a specific kind of scale and
  operational need, not a badge of engineering seriousness.
- **Confusing a Pod with a container.** A Pod is Kubernetes' own
  scheduling unit and USUALLY wraps exactly one container — but they are
  not the same word for the same thing; a Pod can, less commonly, wrap
  more than one tightly-coupled container.
- **Assuming a Service load-balances "physical machines."** A Service
  load-balances across currently-healthy PODS (which Kubernetes may have
  scheduled onto any number of underlying machines) — the "which
  physical machine" question is one layer further down, handled by
  Kubernetes' own scheduler, and mostly invisible to whatever's actually
  sending a request to a Service.

## How this connects

This lesson closes out the conceptual half of this module's curriculum.
Lesson 08 returns to concrete, hands-on work: the capstone walkthrough,
deploying QuestLog for real via this module's actual chosen platform
(Render) — deliberately NOT Kubernetes, for exactly the "right tool for
this project's actual scale" reasoning this lesson just explained.

## Quick self-check

1. What specific, real problem does Kubernetes solve that
   `docker-compose.yml` genuinely cannot?
2. What is a Pod, and why are Pods deliberately treated as disposable
   rather than precious/long-lived?
3. Why does a Deployment need a separate Service object at all — what
   problem would you have without one, given that Pods get new IP
   addresses constantly?
4. Using this lesson's own stated rule of thumb, explain in your own
   words why QuestLog, running on Render, does not need Kubernetes at
   this course's own scale.
5. What's the difference between a Service and an Ingress — which one
   handles traffic arriving from OUTSIDE the cluster, specifically?
