# QuestLog — Deployment Runbook

A condensed, copy-paste-in-order checklist for deploying this exact
`project/questlog/` to a fresh Ubuntu 24.04 server. **This file is a
quick-reference companion, not a substitute for actually reading
[`../../lessons/07-deploying-questlog-part1-server-and-backend.md`](../../../lessons/07-deploying-questlog-part1-server-and-backend.md)
and
[`../../lessons/08-deploying-questlog-part2-frontend-and-going-live.md`](../../../lessons/08-deploying-questlog-part2-frontend-and-going-live.md)**
— those two lessons explain *why* every command below exists and what
each one does; this file exists purely so that once you've read them
once, you're not hunting back through prose to find the next command
while working on a real, live server. Every `<PLACEHOLDER>` below is
explained the first time it appears in Lesson 07.

## Phase 0 — Before you start

- [ ] A fresh Ubuntu 24.04 LTS server exists, and you have its public IP: `<SERVER_IP>`.
- [ ] Your SSH key pair exists locally (`lessons/02-ssh-and-key-based-auth.md`) and its **public** half was provided to the server at creation time.
- [ ] You can already run `ssh root@<SERVER_IP>` (or your provider's non-root default user) successfully.

## Phase 1 — Server hardening (Lesson 07)

- [ ] Create a non-root sudo-capable user (`deploy`), copy your SSH key to it, confirm login as that user works.
- [ ] Disable root SSH login and password authentication in `/etc/ssh/sshd_config`, restart `sshd`.
- [ ] `sudo apt update && sudo apt upgrade -y`.
- [ ] Install and enable `ufw`: allow `OpenSSH` and `'Nginx HTTP'`, then `ufw enable`.

## Phase 2 — PostgreSQL (Lesson 07)

- [ ] `sudo apt install -y postgresql`.
- [ ] Create the `questlog` role and database, with a freshly generated real password (not the local dev one).
- [ ] Confirm with `psql -U questlog -d questlog -h localhost -c "SELECT 1;"`.

## Phase 3 — The backend, as a systemd service (Lesson 07)

- [ ] Create the `questlog` system user: `sudo useradd --system --create-home --shell /usr/sbin/nologin questlog`.
- [ ] `sudo mkdir -p /opt/questlog && sudo chown questlog:questlog /opt/questlog`.
- [ ] Copy `backend/` to `/opt/questlog/backend` on the server (`scp` or `git clone`, both shown in Lesson 07).
- [ ] As the `questlog` user: create `.venv`, `pip install -r requirements.txt`.
- [ ] Copy `deploy/backend.env.production.example` to `/opt/questlog/backend/.env`, fill in a real `SECRET_KEY` and real database password.
- [ ] `alembic upgrade head`.
- [ ] Copy `deploy/questlog-backend.service` to `/etc/systemd/system/questlog-backend.service`.
- [ ] `sudo systemctl daemon-reload && sudo systemctl enable --now questlog-backend`.
- [ ] Confirm: `sudo systemctl status questlog-backend` shows `active (running)`; `curl http://127.0.0.1:8000/` (from the server itself) returns QuestLog's welcome JSON.

## Phase 4 — The frontend, built and served as static files (Lesson 08)

- [ ] **On your own machine** (not the server — see Lesson 08 for why): `VITE_API_BASE_URL= npm run build` inside `frontend/`.
- [ ] Copy the resulting `frontend/dist/` contents to the server, into `/var/www/questlog/`.

## Phase 5 — Nginx (Lesson 08)

- [ ] `sudo apt install -y nginx`.
- [ ] Copy `deploy/nginx/questlog.conf` to `/etc/nginx/sites-available/questlog`.
- [ ] `sudo ln -s /etc/nginx/sites-available/questlog /etc/nginx/sites-enabled/`.
- [ ] `sudo rm /etc/nginx/sites-enabled/default` (if present).
- [ ] `sudo nginx -t` (must pass before continuing).
- [ ] `sudo systemctl reload nginx`.

## Phase 6 — Go live and verify (Lesson 08)

- [ ] From your own laptop's browser: `http://<SERVER_IP>/` loads QuestLog's login page.
- [ ] Log in with the seeded demo account (`player@questlog.local` / `dragon-slayer-1`).
- [ ] Confirm the Quest Board loads real data — proof the full chain (browser → Nginx → Uvicorn → Postgres) works end to end.
- [ ] `curl -i http://<SERVER_IP>/quests/12345` (a client-side-only route) returns `200`, not `404` — proof `try_files` is working.
- [ ] `sudo ufw status verbose` shows exactly `OpenSSH` and `Nginx HTTP` allowed, nothing else.
- [ ] `curl http://<SERVER_IP>:8000/` (from your own laptop, **not** the server) times out / is refused — proof port 8000 is not directly reachable from outside.
- [ ] `curl http://<SERVER_IP>:5432` similarly fails — proof Postgres is not directly reachable from outside.

## Known, deliberate limitations of this deploy (see Lesson 08's closing section)

- **HTTP only, no HTTPS.** A real domain and TLS certificate are Module 11's job.
- **Fully manual.** No CI/CD (Module 11), no containers (Module 10) — every step above was typed by hand, on purpose, per this module's own framing.
- **Single server, single backend process.** No load balancer (conceptual only, Lesson 06) — not needed at QuestLog's scale.
