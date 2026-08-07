# Master Learning Plan: Unreal Engine Dev → Full Stack + AI Engineer

> **PURPOSE OF THIS FILE:** This is the master specification for an AI (Claude Code) to generate a complete, self-paced learning course as a repository. The AI must read this entire file before generating anything. The rules in Section 1 are **non-negotiable** and apply to every single module, lesson, and exercise.

---

## SECTION 1 — NON-NEGOTIABLE RULES FOR THE AI COURSE GENERATOR

These rules exist because of past failures. Follow them exactly.

### Rule 1: Learning material ALWAYS comes before exercises
- Every exercise must have a matching lesson file that fully teaches **every concept the exercise uses**. No exercise may require knowledge that was not explicitly taught in that lesson or a previous one.
- Before writing any exercise, list the concepts it requires. Then verify each concept has a dedicated section in the lesson. If it doesn't, write that section first.
- Never say "look this up" or "research X" as a substitute for teaching. External links are allowed only as *optional* extras, never as required material.

### Rule 2: Explain everything in minute detail, assuming zero prior knowledge of the topic
- The learner is smart but new to web/AI development. Coming from Unreal Engine (C++, Blueprints, game loops), not from web development.
- Every new term must be defined **the first time it appears**, in plain language, before being used.
- Every code example must be explained **line by line** — not just "here's the code," but what each line does, why it's there, and what would break if you removed it.
- Use analogies constantly, especially to game development where possible (e.g., "middleware is like a component in the actor tick chain — every request passes through it before reaching the handler," "state in React is like a variable on an Actor that triggers a re-render when it changes, similar to how changing a property triggers a construction script").
- Explain the "why," not just the "how." Why does this technology exist? What problem does it solve? What did people do before it?
- When something has "magic" behavior (decorators, hooks, async), open the hood and explain what actually happens underneath.

### Rule 3: Every exercise must be checkable, and the AI must grade it properly
When the learner completes an exercise and asks for review, the AI must:
1. **Run/read the solution carefully** — never skim.
2. **State what was done right**, specifically (not "good job" — say *which* decisions were correct and why they were good decisions).
3. **State what was done wrong or is missing**, with the exact location (file, line, function) and an explanation of *why* it's wrong — what bug, security issue, or bad practice it causes.
4. **State what could be improved** even if technically correct — naming, structure, performance, idioms, edge cases.
5. **Give a score out of 10** with a short justification.
6. **Ask 2–3 follow-up comprehension questions** to verify the learner understands *why* the code works, not just that it works. (e.g., "What would happen if two requests hit this endpoint at the same time?")
7. If the score is below 7, suggest the learner revise and resubmit before moving on. Do NOT just give the correct answer immediately — give hints first, full solution only if the learner asks or fails twice.

**Module-end review (triggered when the learner says "check my module" / "review my progress"):**
At the end of every module, the AI must run a full review pass:
1. Grade all of the module's exercises and the capstone using the protocol above (any not yet reviewed, plus re-checking revised ones).
2. **Look back at the learner's previous exercises from earlier modules** (via PROGRESS.md and the actual solution files) and compare: are past weaknesses improving or repeating? Are old concepts still being applied correctly in new code, or fading?
3. Produce a module report: overall score, strongest areas, recurring weaknesses (with the specific evidence across exercises — "you handled errors well in 03 and 05, but exercise 07 still has the same missing-validation issue flagged in Module 04"), and 2–3 concrete focus points for the next module.
4. **Update PROGRESS.md** (see Section 4) with this report. The AI maintains this file — it is not optional and not the learner's job.
5. If recurring weaknesses are serious, generate 1–2 small remedial exercises targeting them (with the required lesson references) before recommending the learner move on.

### Rule 4: Structure of every module (mandatory folder layout)
```
module-XX-name/
├── README.md              — module overview, goals, prerequisites, estimated time
├── lessons/
│   ├── 00-setup.md        — environment setup, if this module needs any (see Rule 8)
│   ├── 01-topic.md        — full teaching material (see Rule 5)
│   ├── 02-topic.md
│   └── ...
├── exercises/
│   ├── 01-exercise/
│   │   ├── INSTRUCTIONS.md   — what to build, acceptance criteria, hints section
│   │   ├── starter/          — starter code if applicable
│   │   └── solution/         — reference solution (learner instructed not to peek)
│   └── ...
├── project/               — one capstone mini-project per module
│   └── BRIEF.md
└── CHECKLIST.md           — self-assessment checklist before moving to next module
```

### Rule 5: Structure of every lesson file (mandatory)
Every `lessons/XX-topic.md` must contain, in order:
1. **What you'll learn** — bullet list of outcomes.
2. **Why this matters** — the real-world problem this solves, where you'll use it.
3. **Prerequisites** — which earlier lessons this builds on.
4. **The concept, explained simply** — plain-language explanation with an analogy before any code.
5. **The details** — thorough walkthrough with code, every line explained. Build up gradually: simplest possible example first, then add complexity one piece at a time.
6. **Common mistakes & gotchas** — the errors beginners actually hit, what the error messages look like, and how to fix them.
7. **How this connects** — how this topic relates to what came before and what comes next.
8. **Quick self-check** — 3–5 questions the learner should be able to answer before doing the exercise.

### Rule 6: Pacing and difficulty
- Exercises within a module go from very easy → guided → independent. The first exercise of any module should be almost impossible to fail if the lesson was read.
- Every 3rd or 4th module includes a **review project** that combines previous modules, because the learner retains through repetition and struggles when material is only seen once.
- Spaced repetition: each module's CHECKLIST.md includes 5 review questions from *earlier* modules.

### Rule 7: Verify accuracy with real research — never rely on memory alone
- Before writing any lesson that involves a specific tool, library, framework, API, or installation procedure, the AI **must perform web searches** to verify that the information is current and correct: latest stable versions, current syntax, current best practices, and whether anything has been deprecated or renamed.
- This applies especially to fast-moving areas: React/Next.js, FastAPI/Pydantic, Docker, GitHub Actions syntax, cloud provider consoles/pricing, LLM APIs, model names, agent frameworks, and MCP. These change frequently — AI training data goes stale.
- Check the **official documentation** of each tool as the primary source. If official docs conflict with the AI's memory, the docs win.
- Pin versions in the course material (e.g., `fastapi==X.Y.Z` in requirements.txt) so exercises don't break, and note in the lesson which version the material was written against and when it was last verified.
- If the AI cannot verify something through research, it must say so explicitly in the lesson rather than presenting uncertain information as fact.

### Rule 8: Environment setup must come BEFORE the material that needs it
- If a module's lessons or exercises require any tool, service, or configuration to be installed/set up (WSL2 on Windows, Docker Desktop, PostgreSQL, Node.js, a cloud account, an API key, etc.), the module must begin with a dedicated **`lessons/00-setup.md`** file that covers it completely — before any teaching content that depends on it.
- The learner is on **Windows**, so all setup instructions must be written for Windows first (using WSL2 where that's the professional norm — e.g., for Linux tooling and Docker), with exact steps: what to download, what commands to run, what settings to change, and what each step actually does (setup should teach, not just instruct).
- Every setup lesson must end with a **"Verify your setup" section**: exact commands to run and the exact expected output, so the learner can confirm everything works before moving on. Include a troubleshooting subsection for the most common failures (e.g., WSL virtualization disabled in BIOS, Docker daemon not running, PATH issues, port already in use).
- Never assume a tool from an earlier module is still configured — if a later module depends on it, the setup lesson briefly re-verifies it.
- Setup instructions must also be verified through web research (Rule 7) since installation procedures change often.

### Rule 9: Lessons must be hands-on — every concept comes with runnable code
- Learning material is not read-only. Every lesson must be built around **complete, runnable code snippets** that the learner is explicitly instructed to type out, run, and observe — not pseudocode, not fragments that can't execute.
- For each snippet, include: the exact file name/path to create it in, the exact command to run it, and the **expected output** so the learner can compare against what they actually see.
- After key snippets, add short **"Try it yourself"** prompts: small modifications to make ("change X to Y and predict what happens before running it") so the learner experiments actively, not passively.
- Snippets must build incrementally — each one a small step from the previous — so the learner is never handed a 100-line wall of code with no path to it.
- All snippets must be tested and working (against the versions pinned per Rule 7) before being included.

### Rule 10: The learner's workflow (put this in the repo's root README)
1. Read the lesson fully. Answer the self-check questions.
2. Do the exercise without looking at the solution.
3. Ask the AI: *"Review my solution for exercise X"* — AI applies Rule 3 grading.
4. Revise if needed. Only then move forward.
5. At module end, do the capstone project, then tell the AI: *"Check my module / review my progress."* The AI runs the full module-end review from Rule 3 — grading everything, comparing against your previous modules' work, writing the report, and updating PROGRESS.md.
6. Complete CHECKLIST.md and address any remedial exercises the review generated before starting the next module.
7. If stuck >30 minutes, ask the AI for a **hint**, not the answer. AI gives progressively stronger hints (3 levels) before revealing solutions.

---

## SECTION 2 — LEARNER PROFILE (the AI must keep this in mind)

- **Background:** Professional Unreal Engine developer. Comfortable with programming logic, C++, game architecture, debugging.
- **Python:** Knows a little; needs revision from near-fundamentals but can move fast through basics.
- **Web development:** Essentially new. Do not assume knowledge of HTTP, HTML, DNS, browsers internals, etc.
- **Goal:** Become a genuinely excellent full stack engineer who can also build AI-powered applications and agents, and who understands deployment/DevOps deeply — not surface-level.
- **Learning style:** Struggles when explanations skip steps. Needs minute details, simple wording, worked examples, and feedback loops. Gets frustrated when exercises assume untaught material.
- **Time assumption:** Structure for ~10–15 hours/week; each module README should state estimated hours.

---

## SECTION 3 — THE CURRICULUM

Generate the modules in this exact order. Phases build on each other.

---

### PHASE 0 — Foundations & Environment (Modules 0–1)

**Module 00 — Developer Environment & Tooling**
- Installing and understanding: VS Code, terminals/shell basics (bash), what a shell actually is, navigating the filesystem via CLI, environment variables, PATH.
- Git from zero: what version control is and why, init/add/commit/branch/merge, resolving conflicts, GitHub, pull requests, .gitignore, writing good commit messages.
- How to read documentation and error messages (a skill lesson — teach a systematic approach to reading stack traces).
- Exercise ideas: shell scavenger hunt; create a repo, branch, merge a conflict on purpose and fix it.

**Module 01 — Python, Properly (Revision → Solid)**
- Start from variables/types but move briskly; slow down at the point where "a little Python" usually ends:
  - Functions, scope, *args/**kwargs, default argument gotchas
  - Data structures deeply: lists vs tuples vs sets vs dicts — when and why, time complexity intuition
  - Comprehensions, generators, iterators (explain what `for` actually does under the hood)
  - OOP in Python: classes, dunder methods, inheritance vs composition — compare/contrast with C++ classes the learner already knows
  - Error handling: exceptions, try/except/finally, custom exceptions
  - Modules, packages, imports, `__init__.py`, virtual environments (venv), pip, requirements.txt — explain why isolation matters
  - File I/O, JSON handling
  - Type hints and why modern Python uses them
  - Decorators and context managers — full "open the hood" treatment (these are needed later for FastAPI)
  - Async/await fundamentals — event loop explained with an analogy to the game loop
- Capstone: a CLI tool (e.g., a task tracker with JSON persistence) reviewed against Rule 3.

---

### PHASE 1 — How the Web Actually Works + Frontend (Modules 2–4)

**Module 02 — Internet & Web Fundamentals (do NOT skip or compress)**
- What happens when you type a URL: DNS, IP, TCP, TLS, HTTP request/response — step by step.
- HTTP in detail: methods, headers, status codes, cookies, what "stateless" means.
- What a server is vs. a client. What an API is. What JSON is and why it won.
- REST explained from first principles.
- Exercise: use `curl` and a REST client to explore a public API; document the request/response cycle.

**Module 03 — HTML, CSS, and JavaScript Fundamentals**
- HTML: semantic structure, forms, accessibility basics.
- CSS: box model, flexbox, grid, responsive design. (Analogy: layout systems vs. UMG anchors/slots.)
- JavaScript properly: how it differs from Python/C++, the event loop, DOM manipulation, events, fetch/promises/async-await, ES6+ features (destructuring, spread, arrow functions, modules).
- TypeScript introduction: why types matter at scale (learner will appreciate this from C++).
- Capstone: a small interactive app in vanilla JS/TS (no framework) — e.g., a weather dashboard calling a real API.

**Module 04 — React (Modern Frontend)**
- Why frameworks exist — what pain vanilla JS causes at scale.
- Components, props, state (analogy to Actors and properties), JSX, rendering model — explain re-rendering minutely.
- Hooks: useState, useEffect (explain the dependency array pitfalls in extreme detail), useRef, custom hooks.
- Forms, controlled components, lifting state, context.
- Data fetching patterns, loading/error states.
- Routing (React Router), and a lesson on Next.js: what SSR/SSG/CSR mean and when each matters.
- Styling options (Tailwind chosen for the course — explain utility-first thinking).
- Capstone: multi-page app with routing, API data, forms, and state management.

---

### PHASE 2 — Backend Engineering (Modules 5–8)

**Module 05 — Backend with Python (FastAPI)**
- What a backend framework does. Why FastAPI (async, type hints, docs).
- Routing, path/query params, request bodies, Pydantic models (validation explained deeply).
- Middleware, dependency injection (explain FastAPI's `Depends` under the hood).
- Error handling, status codes, structured responses.
- Auto docs (Swagger/OpenAPI) — what OpenAPI is.
- Capstone: a full CRUD API (no database yet — in-memory), tested with the docs UI and curl.

**Module 06 — Databases**
- What a database is; why not just files. Relational model from scratch: tables, rows, keys, relationships.
- SQL properly: SELECT/INSERT/UPDATE/DELETE, JOINs (explained with diagrams), GROUP BY, indexes (what they physically do), transactions and ACID.
- PostgreSQL setup and use.
- ORMs: what they are, SQLAlchemy 2.0 with FastAPI, migrations with Alembic (what a migration is and why).
- NoSQL overview: when a document store (MongoDB) or key-value store (Redis) fits; Redis for caching explained.
- Database design: normalization in plain language, designing a schema from requirements.
- Capstone: wire the Module 05 API to Postgres with SQLAlchemy + Alembic.

**Module 07 — Auth, Security & API Best Practices**
- Authentication vs authorization. Password hashing (why bcrypt, what a salt is). Sessions vs JWTs — full comparison, how a JWT is actually structured.
- OAuth2 flow explained step by step with diagrams ("login with Google" demystified).
- Common attacks and defenses: SQL injection, XSS, CSRF, secrets management, rate limiting, CORS (explain CORS minutely — everyone gets bitten by it).
- Environment/config management, logging done right.
- Capstone: add signup/login/JWT auth + protected routes to the ongoing API.

**Module 08 — Testing & Software Quality**
- Why tests exist; the testing pyramid.
- pytest deeply: fixtures, parametrize, mocking (explain what a mock actually is).
- Testing FastAPI endpoints; testing with a test database.
- Frontend testing basics (Vitest/React Testing Library).
- Debugging techniques, linters/formatters (ruff, prettier), pre-commit hooks.
- **REVIEW PROJECT:** Full stack app combining Modules 3–8 — React frontend + FastAPI + Postgres + auth + tests. This is the first major milestone.

---

### PHASE 3 — DevOps & Deployment (Modules 9–11)

**Module 09 — Linux, Networking & Servers**
- Linux deeper: processes, permissions, systemd, SSH (how key-based auth works), package managers.
- Networking for developers: ports, localhost, private vs public IPs, firewalls, reverse proxies (what Nginx does and why it sits in front of your app), load balancers conceptually.
- Deploy the review project manually to a cheap VPS — on purpose, the painful way, so later tools make sense.

**Module 10 — Docker & Containers**
- The problem containers solve ("works on my machine"). Containers vs VMs — explained with diagrams.
- Dockerfile line by line: layers, caching, multi-stage builds, image size optimization.
- docker-compose for multi-service apps (app + db + redis).
- Networking and volumes in Docker, explained minutely.
- Capstone: containerize the full stack review project with compose.

**Module 11 — CI/CD, Cloud & Production Operations**
- What CI/CD is and why. GitHub Actions from zero: workflow syntax explained line by line; build → test → deploy pipelines.
- Cloud fundamentals: what AWS/GCP actually sell; core concepts (compute, object storage, managed databases, IAM in plain words). Deploy using one concrete path (e.g., a container platform like AWS ECS/Fly.io/Railway — pick one and go deep, mention alternatives).
- HTTPS/TLS certificates, domains, DNS records in practice.
- Monitoring & observability: logs, metrics, uptime, error tracking (e.g., Sentry), health checks.
- Kubernetes: a conceptual module only — what it is, when you actually need it, core objects (pods, deployments, services) so the learner can hold a conversation; hands-on optional appendix.
- Capstone: full CI/CD pipeline — push to main → tests run → image builds → auto-deploys to production with HTTPS on a real domain.

---

### PHASE 4 — AI Engineering & Agents (Modules 12–15)

**Module 12 — AI/ML Foundations (concepts before tools)**
- What machine learning actually is — training vs inference, explained with intuition, minimal math (dot products and gradients conceptually, no heavy calculus).
- Neural networks conceptually: neurons, weights, loss, backpropagation intuition.
- What an LLM is: tokens, embeddings (explained deeply — the "meaning as coordinates" analogy), attention/transformers at an intuition level, why LLMs hallucinate, context windows, temperature/sampling.
- Prompt engineering as a real skill: system prompts, few-shot, chain-of-thought, structured outputs.
- Exercise: hand-tokenize text, visualize embeddings with a small script, systematic prompt experiments.

**Module 13 — Building with LLM APIs**
- Calling LLM APIs (use the Anthropic API as the primary example): messages format, roles, streaming, token counting, cost management, error handling and retries.
- Structured outputs (JSON mode / schema validation with Pydantic).
- Tool use / function calling — explained minutely: the full round-trip of model → tool call → result → model.
- Building an AI feature into the existing full stack app (e.g., an AI assistant endpoint with streaming to the React frontend).
- Evaluation basics: how do you know your AI feature works? Simple eval harnesses.

**Module 14 — RAG (Retrieval-Augmented Generation)**
- The problem RAG solves. Chunking strategies, embeddings for search, vector databases (pgvector so it builds on Postgres knowledge; mention alternatives).
- Similarity search explained (cosine similarity with intuition).
- The full RAG pipeline built by hand first (no framework) so nothing is magic; then discuss frameworks (LangChain/LlamaIndex) and their trade-offs honestly.
- Capstone: "chat with your documents" feature added to the app — upload PDF → chunk → embed → store → retrieve → answer with citations.

**Module 15 — Agents & Modern AI Workflows**
- What an agent is: the loop (LLM decides → calls tool → observes → repeats). Build a minimal agent from scratch in raw Python — no framework — so the learner truly understands.
- Tool design for agents, multi-step reasoning, memory patterns (short-term vs long-term), planning.
- MCP (Model Context Protocol): what it is, building a simple MCP server.
- Multi-agent patterns, orchestration, human-in-the-loop.
- Agent frameworks overview after fundamentals (so choices are informed, not cargo-culted).
- Safety/reliability: guardrails, sandboxing tool execution, cost/loop limits, evals for agents.
- Using AI in the dev workflow itself: effective use of Claude Code/AI pair programming — how to prompt for code, review AI output critically, avoid skill atrophy.
- **FINAL CAPSTONE:** A production-grade AI application — full stack app (React + FastAPI + Postgres) with auth, an agent that uses tools + RAG, streaming UI, tests, containerized, CI/CD deployed with monitoring. This is the portfolio piece.

---

## SECTION 4 — REPO-LEVEL FILES THE AI MUST GENERATE

1. **README.md (root):** course overview, the learner workflow (Rule 10), how to ask for reviews and hints, progress tracking table (checkbox per module).
2. **PROGRESS.md:** the learner's progress tracker, **maintained by the AI** (updated after every exercise review and every module-end review — see Rule 3). Required structure:
   - **Status table:** one row per module — status (not started / in progress / complete), completion date, module score.
   - **Exercise log:** one entry per reviewed exercise — date, score /10, what was done right, what was wrong, resubmissions.
   - **Skills tracker:** running lists of "demonstrated strengths" and "recurring weaknesses," each item citing the exercises that evidence it; items move off the weaknesses list only when later exercises show the issue is fixed.
   - **Module reports:** the module-end review reports from Rule 3, newest first.
   - **Focus points:** the current 2–3 things to concentrate on, carried into the next module.
   Any AI session must read PROGRESS.md at the start of a review so grading and feedback build on the full history, not just the current exercise. Spaced-repetition questions (Rule 6) are also drawn from the weaknesses recorded here.
3. **GRADING_PROTOCOL.md:** a copy of Rule 3, so any AI session can be pointed at it with "grade my exercise using GRADING_PROTOCOL.md."
4. **GLOSSARY.md:** every term defined in the course gets appended here alphabetically as modules are generated.

## SECTION 5 — GENERATION INSTRUCTIONS

- Generate **one module at a time**, fully (all lessons + all exercises + solutions + capstone brief), starting with Module 00. Do not scaffold empty files across the whole course.
- **Before generating a module**, perform the web research required by Rule 7 for every tool/library that module touches, and confirm the setup requirements per Rule 8. Only then write the content.
- After generating a module, self-audit it against Section 1 rules — explicitly verify Rule 1 (every exercise concept is taught), Rule 8 (all required setup is covered in 00-setup.md with a verification section), and Rule 9 (every lesson has runnable snippets with run commands and expected outputs) before declaring the module done.
- Lessons should be long. Err on the side of over-explaining. A lesson that takes 30–45 minutes to read carefully is correct; a 5-minute skim file is a failure.
- All code must actually run. Test it before including it.
- Keep a consistent running project where specified so the learner sees one app evolve from Module 03 through the final capstone, alongside smaller standalone exercises.
