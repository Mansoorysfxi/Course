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
- **AI:** Anthropic API (Claude) as the primary LLM API taught in Modules 13–15, per the master plan.

## Repo location for the running project's actual code

Each module that touches QuestLog includes the growing codebase inside that
module's own `project/` folder (e.g.
`module-04-react/project/questlog/`), and each new module's starter code
is a copy of the *previous* module's finished reference solution — so a
learner who's behind can always pick up from a working prior state. This
mirrors exactly how you'd branch/continue a real evolving codebase, which
the learner already practiced in Module 00.
