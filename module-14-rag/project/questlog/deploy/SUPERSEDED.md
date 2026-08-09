# This folder is kept for historical reference only — it is not used by Module 10

Everything else in `deploy/` (`questlog-backend.service`, `nginx/questlog.conf`,
`backend.env.production.example`, `DEPLOY_RUNBOOK.md`) is **Module 09's**
work, copied forward unchanged. None of it is used, run, or referenced
by this module's own capstone — Module 10 replaces every one of these
files with a containerized equivalent, listed below.

This folder is deliberately **not deleted**, for the same reason
`RUNNING_PROJECT.md` frames Module 09 as "the painful way, on purpose":
the whole pedagogical point of this module is that you already know,
from first-hand experience, exactly what a `systemd` unit file, a
hand-written Nginx config, and a manual deploy runbook look like — so
you can look at this folder and Module 10's `docker-compose.yml` side by
side and see, concretely, what got automated and how.

| Module 09's manual artifact (this folder) | Module 10's containerized replacement |
|---|---|
| `questlog-backend.service` (a hand-written `systemd` unit: `ExecStart`, `User=questlog`, restart policy, `EnvironmentFile=`) | `../backend/Dockerfile`'s `CMD`, plus `docker-compose.yml`'s `backend` service block (`environment:`, `restart: unless-stopped`) — see `lessons/07-containerizing-questlogs-backend.md` |
| `nginx/questlog.conf` (hand-installed Nginx, reverse-proxying `/api/` to `127.0.0.1:8000`, serving `dist/` as static files) | `../frontend/nginx.conf`, baked into `../frontend/Dockerfile`'s final stage — see `lessons/08-containerizing-questlogs-frontend-and-full-compose.md`. The one real difference: `127.0.0.1:8000` (same machine) becomes `http://backend:8000` (a different container, reached by Compose's own service-name DNS) — see `lessons/04-docker-networking.md`. |
| Manually installing PostgreSQL via `apt`, creating a role/database by hand with `psql` (Lesson 07, Phase 3) | `docker-compose.yml`'s `postgres` service — one `image:` line and a named volume |
| No caching layer at all | `docker-compose.yml`'s `redis` service, wired into `../backend/app/cache.py` — new in Module 10, see `RUNNING_PROJECT.md`'s "Fixed technology decisions" |
| `backend.env.production.example` (a template for a hand-created, `chmod 600` production `.env` on the server) | `../.env.example` (compose-level) plus `docker-compose.yml`'s `environment:` blocks — secrets still never committed, but no longer copied to a server by hand either |
| `DEPLOY_RUNBOOK.md` (a human-followed, copy-paste-in-order checklist) | `docker compose up --build` — one command, the same every time, on any machine with Docker installed |

**What this table deliberately does NOT claim:** Module 10's
containerized QuestLog is not yet deployed anywhere a real user could
reach it — `docker compose up` on your own Windows/WSL2 machine proves
the exact same multi-service stack Module 09 deployed by hand *can* be
packaged and started with one command, but getting a container stack
running on a real, internet-reachable server, automatically, on every
push, is Module 11's job (CI/CD, cloud, a real domain). See this
module's own `lessons/00-setup.md` "How this connects" section.
