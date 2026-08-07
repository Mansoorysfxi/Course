# Module 10 Checklist — Docker & Containers

Complete this before moving on to Module 11. Check off each item
honestly — this is a self-assessment, not a formality.

## Lessons

- [ ] Read `lessons/00-setup.md` and confirmed every command in its
      "Verify your setup" section, including WSL integration actually
      enabled in Docker Desktop's settings.
- [ ] Read `lessons/01-containers-vs-vms-and-your-first-container.md`
      and can explain the real, mechanical difference between a
      container and a VM without hesitation.
- [ ] Read `lessons/02-dockerfiles-layers-and-caching.md` and can
      explain, from memory, why instruction order in a Dockerfile
      affects build-cache reuse.
- [ ] Read `lessons/03-multi-stage-builds-and-image-size.md` and can
      explain what `COPY --from=<stage>` actually does and why it
      matters for image size.
- [ ] Read `lessons/04-docker-networking.md` and can explain why the
      *default* Docker bridge network doesn't support name-based
      container resolution, but a user-defined one (including Compose's
      own) does.
- [ ] Read `lessons/05-docker-volumes-and-persistence.md` and can
      explain the difference between a named volume and a bind mount.
- [ ] Read `lessons/06-docker-compose-multi-service-apps.md` and can
      explain, without looking it up, what a cache hit/miss is, what a
      TTL is, and what cache invalidation is.
- [ ] Read `lessons/07-containerizing-questlogs-backend.md` and
      `lessons/08-containerizing-questlogs-frontend-and-full-compose.md`
      in full.

## Exercises

- [ ] Exercise 01 (first container) — done and reviewed.
- [ ] Exercise 02 (writing a Dockerfile) — done and reviewed, including
      correctly demonstrating cache reuse on a rebuild.
- [ ] Exercise 03 (multi-stage image size) — done and reviewed, with a
      real, measured size difference between both images.
- [ ] Exercise 04 (Docker networking) — done and reviewed, including
      correctly reproducing the default-bridge-network failure on
      purpose first.
- [ ] Exercise 05 (volumes and persistence) — done and reviewed,
      including correctly explaining why removing a volume actually
      deletes the data.
- [ ] Exercise 06 (compose two services) — done and reviewed, with a
      `docker-compose.yml` written entirely from scratch.

## Capstone

- [ ] `project/BRIEF.md`'s full stack (backend, frontend, Postgres,
      Redis) runs from a cold start with `docker compose up --build`.
- [ ] Cache hit/miss/invalidation behavior was genuinely observed via
      the `X-Cache` response header, not just read about.
- [ ] Volume persistence (`docker compose down`) and volume deletion
      (`docker compose down -v`) were both genuinely observed.
- [ ] `project/CONTAINERIZATION_REPORT.md` written, covering all four
      required points from the brief, including one deliberately broken
      and fixed scenario.
- [ ] You can explain, unprompted, the complete request path a browser's
      `GET /api/quests` takes through the containerized system — every
      container, every network hop, in order, including exactly where
      the Redis cache sits on a hit versus a miss.
- [ ] No stray containers, images, or volumes from this module are still
      running on your machine.

## Spaced repetition — review questions from earlier modules

Per this course's Rule 6, answer these without re-reading the original
lesson first; check your answer against the linked material afterward.

1. **(Module 01)** What is a context manager, mechanically — what two
   methods does an object need to support the `with` statement, and what
   guarantee does `with` give you that a plain `try`/`finally` doesn't
   already provide on its own? *(See `module-01-python-properly/lessons/10-decorators-and-context-managers.md`.)*
2. **(Module 04)** What does `useEffect`'s dependency array actually
   control, and what specifically happens if you omit it entirely versus
   passing an empty array `[]`? *(See `module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md`.)*
3. **(Module 06)** What does a database index physically do that makes a
   query faster, and what's the real cost of adding one that this
   course's own lesson warned isn't "always add more indexes"?
   *(See `module-06-databases/lessons/02-indexes-transactions-and-acid.md`.)*
4. **(Module 07)** What problem does CORS actually solve, and why did
   QuestLog's backend need an explicit `CORSMiddleware` configuration at
   all — what would happen without it, and from which side (browser or
   server) does that restriction actually originate? *(See
   `module-07-auth-security/lessons/10-cors-in-depth.md`.)*
5. **(Module 09)** What does a reverse proxy actually do, mechanically,
   and why does Module 09's Nginx config's `try_files $uri /index.html;`
   line matter specifically for a client-side-routed React app like
   QuestLog's frontend? *(See
   `module-09-linux-networking-servers/lessons/06-nginx-and-reverse-proxies.md`.)*

## Before moving to Module 11

- [ ] All boxes above are checked honestly.
- [ ] You understand, in your own words, exactly what Module 11 (CI/CD,
      Cloud & Production Operations) is about to automate on top of this
      module's work — specifically, that `docker compose up --build`
      still has to be run by a human, on some machine, today.
