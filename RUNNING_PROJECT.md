# The Running Project: QuestLog

Per `MASTER_LEARNING_PLAN.md` Section 5 ("keep a consistent running project
... so the learner sees one app evolve"), this course builds one
continuous application across most modules, alongside smaller standalone
exercises. This file is the single source of truth for what that project is
so every module stays consistent — any session generating a new module
must read this first.

## The concept

**QuestLog** — a personal task tracker with light RPG framing (a nod to the
learner's game-dev background): tasks are called "quests," completing a
task is "completing a quest," a group of related tasks is a "quest line."
This is a deliberately simple domain (nothing about the business logic
should ever be the hard part) so every module's added complexity is about
the *technology*, not about understanding a complicated domain.

## How it evolves, module by module

| Module | Form | What's added |
|---|---|---|
| 01 — Python | **QuestLog CLI** — a standalone command-line tool, JSON file persistence | Conceptual precursor only — a fresh, separate codebase from the CLI capstone. Establishes the domain (quests, quest lines, done/not-done, priority) the rest of the course reuses. |
| 02 — Web Fundamentals | *(standalone)* | No QuestLog code — capstone is a written exploration/documentation exercise against a real public API (Module 02's own BRIEF.md picks one). |
| 03 — HTML/CSS/JS | *(standalone)* — a weather dashboard, per the master plan | Deliberately **not** QuestLog — the point of Module 03's capstone is calling a real external API in vanilla JS/TS, which QuestLog (an internal-data app) doesn't need. QuestLog itself starts fresh in Module 04. |
| 04 — React | **QuestLog (web)** begins — React + TypeScript + Tailwind, Vite-built, data held in local component state (no backend yet) | Multi-page (React Router), forms to add/edit quests, list/filter/sort, loading/error UI patterns practiced against a mocked delay. |
| 05 — FastAPI | **QuestLog API** — in-memory CRUD backend | React frontend now calls a real HTTP API instead of local state. |
| 06 — Databases | QuestLog API gains Postgres + SQLAlchemy 2.0 + Alembic | Quests persist across restarts; schema designed from the domain. |
| 07 — Auth & Security | QuestLog gains signup/login, JWTs, per-user quests, protected routes | Multi-user; every quest belongs to an owner. |
| 08 — Testing (Review Project milestone) | Full stack QuestLog — React + FastAPI + Postgres + auth — gets a real test suite | First major milestone; this exact app is what gets deployed starting Module 09. |
| 09 — Linux/Servers | QuestLog deployed manually to a VPS | The "painful way," on purpose. |
| 10 — Docker | QuestLog containerized (app + Postgres + Redis via compose) | |
| 11 — CI/CD & Cloud | QuestLog deployed via a real pipeline, HTTPS, real domain, monitoring | |
| 12 — AI Foundations | *(standalone exercises — tokenization, embeddings, prompting)* | No QuestLog code yet — concepts first, per Rule 1. |
| 13 — LLM APIs | QuestLog gains an AI assistant endpoint ("suggest a quest breakdown," streamed to the frontend) | |
| 14 — RAG | QuestLog gains "chat with your quest notes" — upload notes/docs, chunk, embed, retrieve, answer with citations | |
| 15 — Agents (Final Capstone) | QuestLog gains an autonomous agent that can create/update/complete quests via tool calls, with RAG + guardrails | Portfolio piece. |

## Fixed technology decisions (so later modules don't re-litigate earlier ones)

These are chosen once, here, verified via web research when the module that
introduces them is generated, and then treated as fixed for the rest of the
course:

- **Frontend:** React + TypeScript, built with Vite; Tailwind CSS for styling; React Router for routing. Next.js is taught conceptually (SSR/SSG/CSR) in Module 04 but QuestLog itself stays a Vite SPA — introducing a second frontend build system mid-course would add incidental complexity Rule 1 doesn't require.
- **Backend:** Python + FastAPI, Pydantic v2 for models.
- **Database:** PostgreSQL, accessed via SQLAlchemy 2.0 (async) + Alembic for migrations. Redis introduced in Module 06 conceptually, used for real starting Module 10 (caching + Docker Compose multi-service example).
- **Auth:** JWT-based, `passlib`/`bcrypt` for password hashing (exact package verified when Module 07 is generated, since this space changes).
- **Containers/Deploy:** Docker + docker-compose; concrete cloud target for Module 11 chosen (with research) when that module is generated, with alternatives mentioned per the master plan.
- **CI/CD and cloud deploy target (decided when Module 11 was generated):** **GitHub Actions** for CI/CD (free, no ambiguity, verified current syntax/action versions as of August 2026) and **Render** as the concrete container-platform deploy target — chosen over Fly.io and Railway specifically because both discontinued their own genuine free tiers by 2026 (verified via live research at generation time; Fly.io now offers only a 2-hour/7-day trial for new signups, Railway a one-time $5 credit then $1/month), and over configuring raw AWS/GCP compute by hand because that would require its own multi-lesson module of IAM/VPC/networking setup this module's actual subject (CI/CD) doesn't need. Render's free tier — Docker-image-backed web services, managed Postgres, a Redis-compatible Key Value cache, and fully automatic Let's Encrypt/Google Trust Services TLS on both its own subdomains and custom domains — covers every piece this module's capstone needs at zero cost. This is a deliberately different, higher-management tier than Module 09's raw Hetzner VPS (never re-litigating that module's own choice — the VPS lessons/exercises are unchanged), chosen specifically so Module 11's automatic HTTPS and one-file (`render.yaml`) deploy configuration read as a real, felt contrast to Module 09's manual, HTTP-only deploy. QuestLog's backend/frontend images (Module 10's own, unmodified Dockerfiles) are pushed to GitHub Container Registry by a GitHub Actions pipeline and deployed to Render via its Deploy Hook mechanism, pinned to an exact commit SHA. See `module-11-cicd-cloud-production/lessons/04-cloud-fundamentals-and-your-chosen-platform.md` for the full research and reasoning, and `lessons/08-deploying-questlog-with-ci-cd.md` for the complete, applied walkthrough.
- **AI:** Anthropic API (Claude) as the primary LLM API taught in Modules 13–15, per the master plan.
- **Redis's concrete use case (decided when Module 10 was generated):** a Redis-backed cache for `GET /api/quests`'s *unfiltered* quest list only (the call QuestLog's own Quest Board page makes on every load) — a 30-second TTL plus active invalidation (a `redis.delete` call) on every `create`/`update`/`delete` quest route, keyed per-owner so two users never share a cached answer; any filtered call (`?done=`, `?priority=`, `?quest_line=`) deliberately bypasses the cache entirely and always hits Postgres, keeping this module's scope to "a real, working example of the concept," not a general-purpose caching layer. Implemented via `redis.asyncio` (the `redis` PyPI package, not the deprecated standalone `aioredis`), wired in as a FastAPI dependency (`RedisClient`, mirroring the existing `DbSession`) entirely inside `app/routers/quests.py` — `app/repository.py` is untouched. See `module-10-docker-and-containers/lessons/06-docker-compose-multi-service-apps.md` and `lessons/07-containerizing-questlogs-backend.md` for the full explanation.

## Repo location for the running project's actual code

Each module that touches QuestLog includes the growing codebase inside that
module's own `project/` folder (e.g.
`module-04-react/project/questlog/`), and each new module's starter code
is a copy of the *previous* module's finished reference solution — so a
learner who's behind can always pick up from a working prior state. This
mirrors exactly how you'd branch/continue a real evolving codebase, which
the learner already practiced in Module 00.
