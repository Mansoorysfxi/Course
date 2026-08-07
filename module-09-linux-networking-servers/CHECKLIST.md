# Module 09 Checklist — Linux, Networking & Servers

Complete this before moving on to Module 10. Check off each item
honestly — this is a self-assessment, not a formality.

## Lessons

- [ ] Read `lessons/00-setup.md` and confirmed every command in its
      "Verify your setup" section, including `systemd` actually enabled
      in WSL2.
- [ ] Read `lessons/01-linux-processes-and-permissions.md` and can
      answer its self-check questions without looking back at the lesson.
- [ ] Read `lessons/02-ssh-and-key-based-auth.md` and generated a real
      Ed25519 key pair.
- [ ] Read `lessons/03-systemd-and-services.md` and wrote/ran a real unit
      file, watching `Restart=on-failure` actually recover a killed process.
- [ ] Read `lessons/04-networking-ports-and-ips.md` and can explain the
      practical difference between `127.0.0.1` and `0.0.0.0` as a bind
      address without hesitation.
- [ ] Read `lessons/05-firewalls-with-ufw.md` and can state, from
      memory, the exact order of operations for enabling `ufw` safely on
      a remote server.
- [ ] Read `lessons/06-nginx-and-reverse-proxies.md` and can explain the
      `proxy_pass` trailing-slash behavior difference without looking it up.
- [ ] Read `lessons/07-deploying-questlog-part1-server-and-backend.md`
      and `lessons/08-deploying-questlog-part2-frontend-and-going-live.md`
      in full.

## Exercises

- [ ] Exercise 01 (Linux processes and permissions) — done and reviewed.
- [ ] Exercise 02 (SSH key-based login) — done and reviewed, including
      correctly diagnosing Part C's deliberately broken permissions.
- [ ] Exercise 03 (systemd toy service) — done and reviewed, including
      the `Restart=always` vs. `Restart=on-failure` design question.
- [ ] Exercise 04 (ufw firewall rules) — done and reviewed.
- [ ] Exercise 05 (Nginx reverse proxy) — done and reviewed, including
      correctly explaining the prefix-stripping `proxy_pass` form.

## Capstone

- [ ] `project/BRIEF.md`'s deploy completed (live on a real VPS, or a
      thorough, honest dry run) and reviewed.
- [ ] `project/DEPLOYMENT_REPORT.md` written, covering all four required
      points from the brief.
- [ ] You can explain, unprompted, the complete request path a browser's
      `GET /api/quests` takes through the deployed system — every
      process, every port, in order.
- [ ] You can list, from memory, all four of Lesson 08's "deliberately
      not done yet" gaps and which later module closes each one.

## Spaced repetition — review questions from earlier modules

Per this course's Rule 6, answer these without re-reading the original
lesson first; check your answer against the linked material afterward.

1. **(Module 02)** What does "stateless" mean in the context of HTTP, and how does QuestLog's own JWT-based auth work around a stateless protocol to still know who's logged in on each request? *(See `module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md` and `module-07-auth-security/lessons/04-jwt-structure-in-depth.md`.)*
2. **(Module 06)** What is a database transaction, and which of the four ACID guarantees would be violated if two concurrent requests could both read, modify, and write back the same row without any locking or isolation at all? *(See `module-06-databases/lessons/02-indexes-transactions-and-acid.md`.)*
3. **(Module 07)** Why does QuestLog's backend hash passwords with `bcrypt` instead of storing them in plain text, and what specifically does a "salt" prevent an attacker from doing even if they steal the entire hashed-password database? *(See `module-07-auth-security/lessons/02-password-hashing.md`.)*
4. **(Module 08)** Why does this course's backend test suite use an in-memory SQLite database instead of a real running PostgreSQL instance, and what's the honest trade-off in doing so? *(See `module-08-testing-and-quality/lessons/06-testing-with-a-database.md`.)*
5. **(Module 05)** What does FastAPI's `Depends()` actually do, mechanically, when used on a route's parameter — and which of QuestLog's own routes uses it to enforce that a request is authenticated before the route's own code ever runs? *(See `module-05-backend-fastapi/lessons/04-dependency-injection-and-depends.md` and `module-07-auth-security/lessons/07-protecting-routes-with-dependencies.md`.)*

## Before moving to Module 10

- [ ] All boxes above are checked honestly.
- [ ] You understand, in your own words, why Module 10 (Docker) exists —
      specifically, which parts of this module's manual process it's
      about to automate/simplify.
