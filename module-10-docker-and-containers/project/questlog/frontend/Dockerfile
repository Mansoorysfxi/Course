# QuestLog frontend -- Dockerfile
#
# See module-10-docker-and-containers/lessons/08-containerizing-questlogs-frontend-and-full-compose.md
# for the full, line-by-line explanation. This is a genuinely necessary
# multi-stage build, not merely a nice-to-have optimization the way the
# backend's Dockerfile arguably is (Python's own dependencies aren't
# *that* large): a Node.js toolchain capable of running Vite, TypeScript,
# and this app's build step needs to exist somewhere -- but the actual,
# deployed frontend is just static HTML/CSS/JS files that any plain web
# server can serve, with zero need for Node.js, npm, or any of this
# app's ~170 npm packages to be present at all. Module 09's
# lessons/08-deploying-questlog-part2-frontend-and-going-live.md already
# established this exact idea by hand -- "build on your own machine,
# ship only dist/ to the server, the server never runs npm install at
# all." A multi-stage Docker build is the packaged, reproducible version
# of precisely that same idea: Stage 1 is "your own machine" (except it's
# a clean, disposable container instead of your actual laptop), Stage 2
# is "the server," and `COPY --from=build` is what ships only `dist/`
# between them.

# ---- Stage 1: build the static assets ---------------------------------
# `node:24-alpine` -- verified via Docker Hub (August 2026): Node.js 24 is
# the current Active LTS line (Active LTS since October 28, 2025, per
# nodejs.org's own release schedule), and `node:24-alpine` resolves to
# Node 24.19.0 on Alpine 3.24 at the time of writing. Unlike the backend's
# choice of `-slim` over `-alpine` (see backend/Dockerfile's own header),
# this stage's own musl-vs-glibc risk is much lower -- Vite's build step
# runs pure JavaScript plus this project's own Rust-based `rolldown`
# bundler binary, which ships prebuilt Linux binaries for Alpine's musl
# libc specifically (that's exactly what `optionalDependencies` entries
# like `@rolldown/binding-linux-x64-musl`, resolved automatically by npm
# on this exact base image, are for) -- and this whole stage is discarded
# after the build anyway, so even a musl-related quirk here couldn't
# affect the final, running container the way it might for a long-lived
# backend process.
FROM node:24-alpine AS build

WORKDIR /app

# Same layer-caching principle as the backend Dockerfile: copying only
# the two files `npm ci` actually needs, before any real source code,
# means editing a `.tsx` file never invalidates this (comparatively slow)
# dependency-install layer on a rebuild.
COPY package.json package-lock.json ./

# `npm ci` ("clean install"), not `npm install`, is this Dockerfile's
# deliberate choice -- see lessons/08's own section on the difference:
# `npm ci` deletes any existing node_modules first and installs EXACTLY
# what package-lock.json specifies, byte for byte, failing outright if
# package.json and package-lock.json have drifted out of sync with each
# other. `npm install` would instead quietly update the lockfile to
# reconcile any drift -- exactly the kind of silent, unreproducible
# behavior a Docker build should never have: this course wants "build
# this image" to produce the same result today as it will next year,
# given the same two files.
#
# This is also exactly why this module moved
# `@oxlint/binding-win32-x64-msvc` and `@rolldown/binding-win32-x64-msvc`
# out of `devDependencies` and into `optionalDependencies` in
# package.json (see lessons/08's own dedicated section on this real,
# necessary change) -- both packages are Windows-only native binaries.
# As plain `devDependencies`, npm treats a platform mismatch as a hard
# error (`EBADPLATFORM`) and `npm ci` would fail immediately on this
# Linux-based image. As `optionalDependencies`, npm correctly recognizes
# neither package applies to `linux`/`musl`/`x64` and silently skips
# them instead -- the exact same "belongs to a different platform,
# skip it" mechanism that already made `@rolldown/binding-linux-x64-musl`
# (and friends) install correctly and automatically above, with zero
# extra configuration.
RUN npm ci

# Now the actual application source.
COPY . .

# `ARG` declares a build-time-only variable -- available while this
# image is being built, gone from the final running container (unlike
# `ENV`, which persists). `ARG VITE_API_BASE_URL=""` sets this build's
# default to an empty string; docker-compose.yml passes this same name
# explicitly (see its own `build.args` block) so both stay in sync in
# one obvious place. Assigning it into `ENV` on the next line is what
# actually makes Vite's build step see it: Vite reads real OS-level
# environment variables (and gives them priority over any `.env` file's
# own value for the same name) at build time and bakes the result
# directly into the compiled JavaScript -- this is the exact same
# `VITE_API_BASE_URL=` (empty) mechanism
# module-09-linux-networking-servers/lessons/08's Step 1 already used, by
# hand, on a real machine; this Dockerfile just automates it.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ---- Stage 2: serve the built files with Nginx -------------------------
# `nginx:1.30-alpine` -- verified via Docker Hub (August 2026): Nginx
# 1.30.4 is the current stable release (matching the exact version
# module-09-linux-networking-servers/lessons/06 already verified and
# used), and its `-alpine` variant is a genuinely tiny (a few MB) base
# image -- appropriate here specifically because, unlike the backend's
# Python interpreter, Nginx itself has no equivalent musl-compatibility
# concern: it's a single, statically-focused C binary Alpine's own
# package maintainers build and test directly for Alpine.
FROM nginx:1.30-alpine

# Copies ONLY the finished, built files out of Stage 1 -- none of
# node_modules' ~170 packages, no npm, no Node.js runtime at all, exist
# anywhere in this final image. This one line is the entire payoff of
# this whole multi-stage Dockerfile.
COPY --from=build /app/dist /usr/share/nginx/html

# This module's own Nginx site config -- see nginx.conf in this same
# folder, and lessons/08's line-by-line walkthrough of it. Overwrites the
# image's own default config at the exact path Nginx's official image
# already includes by default, so no separate "remove the default site"
# step (module-09-linux-networking-servers/lessons/08's Step 3) is needed
# here at all -- there's only ever one config file in this image, period.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# No CMD needed -- the official nginx image's own base Dockerfile already
# defines `CMD ["nginx", "-g", "daemon off;"]`, which this Dockerfile
# never overrides. `daemon off;` is what keeps Nginx running in the
# foreground, as this container's own main process, instead of forking
# into the background and immediately exiting -- Docker considers a
# container "stopped" the moment its main process exits, so a
# foreground-running Nginx is what keeps this container alive at all.
