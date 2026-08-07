# QuestLog backend -- Dockerfile
#
# See module-10-docker-and-containers/lessons/07-containerizing-questlogs-backend.md
# for a full, line-by-line explanation of every instruction below. This
# is a real, two-stage (multi-stage) build:
#   - Stage 1 ("builder") installs this app's Python dependencies into a
#     throwaway layer.
#   - Stage 2 (the final image) copies ONLY the already-installed
#     packages out of Stage 1 -- never pip's own cache, never pip itself
#     needing to exist in the final image, never any leftover files
#     `pip install` created along the way -- into a fresh, clean base
#     image, then adds this app's own code on top of that.
# The end result is a smaller final image than a single-stage
# `pip install` build would produce, for the same reason a smaller
# multi-stage frontend build (lessons/03, lessons/08) is smaller: nothing
# that was only ever needed to *produce* the final files ships inside the
# image that actually runs.
#
# Base image: `python:3.14-slim` -- verified via Docker Hub (August 2026):
# Python 3.14.7 (released August 5, 2026) is the current patch of the
# 3.14 line, matching the Python 3.14.x this exact backend already runs
# on locally (see backend/README.md's own stack table). `-slim` is a
# Debian-based image with the Python interpreter and the bare minimum of
# OS packages needed to run it -- not the absolute smallest possible
# Python image (`python:3.14-alpine` is smaller still), but `-slim` is
# this lesson's deliberate choice because Alpine's C library (`musl`,
# not `glibc`) has historically caused subtle, hard-to-debug binary
# incompatibilities with some compiled Python packages (a real,
# documented category of problem, not a hypothetical) -- `-slim`'s
# ordinary `glibc` avoids that whole class of issue, at the cost of a
# somewhat larger image. See lessons/03-multi-stage-builds-and-image-size.md
# for this trade-off discussed in full.

# ---- Stage 1: builder -----------------------------------------------
FROM python:3.14-slim AS builder

WORKDIR /app

# Copying ONLY requirements.txt first, before any other application code,
# is this Dockerfile's single most important line for build speed -- see
# lessons/02-dockerfiles-layers-and-caching.md for the full explanation
# of *why*. Short version: Docker caches each instruction as its own
# layer, keyed partly on the exact bytes of the files that instruction
# touches. If this line, and the `pip install` line below it, come
# before `COPY app ./app`, then editing `app/routers/quests.py` (which
# happens constantly) never invalidates this expensive dependency-install
# layer -- Docker reuses its cached result instantly, instead of
# re-downloading and reinstalling every package from scratch on every
# single rebuild.
COPY requirements.txt .

# `--prefix=/install` -- instead of installing into this stage's own
# normal system Python location, this tells pip to install every package
# into a self-contained folder at /install, structured exactly like a
# normal Python installation prefix (/install/lib/python3.14/site-packages,
# /install/bin, etc.). This is what makes it possible to copy JUST the
# installed packages into Stage 2 below, with a single COPY --from=builder,
# leaving pip itself, pip's download cache, and this stage's own base
# image behind entirely. `--no-cache-dir` additionally tells pip not to
# keep its own download cache on disk at all (irrelevant for the final
# image either way, since this whole stage is discarded, but it also
# keeps this intermediate layer itself smaller during the build).
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: the actual runtime image --------------------------------
FROM python:3.14-slim

WORKDIR /app

# Copies ONLY the installed packages from Stage 1 -- not pip, not the
# download cache, not requirements.txt, nothing else that stage's own
# filesystem contains. `/usr/local` is where a normal (non--prefix)
# `pip install` would have put these same files directly in this final
# image -- copying Stage 1's /install over this final image's /usr/local
# lands every package exactly where Python's own default `sys.path`
# already expects to find it, no extra configuration needed.
COPY --from=builder /install /usr/local

# `PYTHONDONTWRITEBYTECODE=1` -- stops Python from writing `.pyc`
# bytecode-cache files to disk as it imports modules. Those files exist,
# normally, purely as a speed optimization for a long-lived process that
# gets restarted and re-imports the same modules repeatedly on the same
# machine -- inside a container that gets rebuilt from scratch every
# deploy anyway, they're pure clutter with no benefit.
# `PYTHONUNBUFFERED=1` -- makes Python flush stdout/stderr immediately
# instead of buffering it in memory. Without this, `docker compose logs`
# (lessons/06) can appear to "hang," showing nothing for a while and then
# dumping a large chunk of output all at once, because Python was holding
# print()'d/logged lines in an internal buffer instead of handing them to
# the terminal (or, here, Docker's own log collector) right away.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# This app's own code, copied in AFTER dependencies are already installed
# -- see the layer-caching explanation above Stage 1's COPY requirements.txt
# line; this ordering is the entire point.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Running as root inside a container is the same bad idea it is on a real
# server -- see module-09-linux-networking-servers/lessons/07's Phase 4
# (`useradd --system ... questlog`) for the exact same reasoning applied
# by hand there. `--create-home` isn't needed here (nothing in this app
# writes to a home directory), `--shell /usr/sbin/nologin` is the same
# deliberate "this account can never get an interactive login" hardening
# Module 09 used for exactly the same reason.
RUN useradd --system --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

# Documents which port this container expects to receive traffic on.
# `EXPOSE` is metadata, not enforcement -- see
# lessons/04-docker-networking.md's "EXPOSE doesn't actually publish
# anything" box for exactly what this instruction does and does not do.
EXPOSE 8000

# `alembic upgrade head` runs this app's migrations (Module 06/07's own
# migrations, unchanged) against whatever database DATABASE_URL points
# at, EVERY time this container starts, before Uvicorn ever accepts a
# single request. Running this on every container start (not just once,
# by hand, the way Module 09's runbook did it) is safe specifically
# because Alembic tracks which migrations have already been applied --
# running `upgrade head` against an already-up-to-date database is a
# fast no-op, not a repeated, destructive re-run. See
# lessons/07-containerizing-questlogs-backend.md for the full "why here,
# why every start" explanation, including what this deliberately does
# NOT solve (two backend replicas racing to migrate at once -- out of
# scope for this module's single-backend-replica compose setup).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
