# Full Stack + AI Engineering Course

Welcome. This repository is a complete, self-paced course that takes you from
a working knowledge of programming to "full stack engineer who can also build
AI-powered applications and agents." It is generated and maintained by
Claude Code according to the rules in
[MASTER_LEARNING_PLAN.md](MASTER_LEARNING_PLAN.md) — that file is the
specification this whole course follows. If anything here ever seems to
contradict it, the master plan wins.

!!! tip "You do not need a web development background"
    You do need to be comfortable with programming logic and debugging —
    that's the part that transfers directly regardless of which language
    or engine you're coming from. Everything else (HTTP, HTML/CSS/JS,
    frameworks, databases) is taught from zero.

## How the course is organized

The course is split into 16 modules across 4 phases, all built around one
continuous app — **QuestLog** — that grows a little more capable every
module (see [RUNNING_PROJECT.md](RUNNING_PROJECT.md)):

<div class="grid cards" markdown>

-   :material-hammer-wrench:{ .lg .middle } **Phase 0 — Foundations**

    ---

    **Modules 00–01**

    Shell, Git, and modern Python — the ground floor everything else stands on.

-   :material-web:{ .lg .middle } **Phase 1 — The Web & Frontend**

    ---

    **Modules 02–04**

    HTTP from first principles, then HTML/CSS/JS, then React. QuestLog's UI is born here.

-   :material-server:{ .lg .middle } **Phase 2 — Backend Engineering**

    ---

    **Modules 05–08**

    FastAPI, real databases, auth, and a real test suite. QuestLog becomes a full stack app.

-   :material-cloud-outline:{ .lg .middle } **Phase 3 — DevOps & Deployment**

    ---

    **Modules 09–11**

    Linux, Docker, CI/CD. QuestLog goes from "runs on my machine" to deployed, with HTTPS.

-   :material-robot-outline:{ .lg .middle } **Phase 4 — AI Engineering & Agents**

    ---

    **Modules 12–15**

    LLM APIs, RAG, and a real autonomous agent. QuestLog's final capstone form.

</div>

Each `module-XX-name/` folder contains:

```
module-XX-name/
├── README.md              ← what this module covers, prerequisites, estimated hours
├── lessons/                ← read these in order, top to bottom
├── exercises/               ← do these after the matching lesson
│   └── 0N-exercise/
│       ├── INSTRUCTIONS.md
│       ├── starter/         ← code to start from, if any
│       └── solution/         ← reference solution — don't peek before attempting!
├── project/                 ← one capstone mini-project per module
│   └── BRIEF.md
└── CHECKLIST.md             ← self-assessment + spaced-repetition questions
```

Modules are generated **one at a time**. Only the modules that currently
exist as full folders (with lesson content inside, not just an empty
skeleton) are ready to study — check each module's `README.md`; if its
`lessons/` folder is empty, ask your AI session to generate that module next.

## Your workflow (do this for every module)

1. **Read the lesson fully.** Answer the "Quick self-check" questions at the
   end of the lesson before moving on — if you can't answer them, re-read.
2. **Do the exercise without looking at the solution.** The `solution/`
   folder is there for after you've made a genuine attempt, or after two
   failed review rounds — not before.
3. **Ask the AI:** *"Review my solution for exercise `0N`"* (or paste your
   code). The AI will grade it against [GRADING_PROTOCOL.md](GRADING_PROTOCOL.md) —
   what you did right, what's wrong (with exact locations), what could be
   improved, a score out of 10, and 2–3 comprehension questions.
4. **Revise if the score is below 7.** Only move on once you're at 7+ or the
   AI tells you the remaining gaps are minor.
5. **At the end of the module**, complete the `project/BRIEF.md` capstone,
   then tell the AI: *"Check my module"* or *"Review my progress."* This
   triggers a full module-end review: every exercise and the capstone get
   graded (or re-graded if revised), your performance is compared against
   *earlier* modules to spot recurring weaknesses, and [PROGRESS.md](PROGRESS.md)
   gets updated with a module report. If serious recurring issues show up,
   the AI will hand you 1–2 small remedial exercises before you continue.
6. **Complete `CHECKLIST.md`** for the module, including its spaced-repetition
   questions pulled from earlier modules, and resolve any remedial exercises.
7. **If you're stuck for more than ~30 minutes, ask for a hint — not the
   answer.** The AI gives you three escalating levels of hint before it will
   show a full solution. Say "give me a hint" or "hint level 2" etc.

## Asking for reviews and hints — exact phrases that work

- `Review my solution for exercise 02` — single-exercise grading (Rule 3).
- `Check my module` / `Review my progress` — full module-end review, updates PROGRESS.md.
- `Give me a hint` / `Hint level 2 please` — progressive hints, no spoilers.
- `Grade my exercise using GRADING_PROTOCOL.md` — same as the above, explicit.
- `What's my progress so far?` — the AI reads PROGRESS.md and summarizes.

## Progress tracking

Live status lives in [PROGRESS.md](PROGRESS.md) (skills tracker, exercise
log, module reports — maintained by the AI, not you). The checkbox table
below is the simple at-a-glance version; the AI keeps both in sync.

- [ ] Module 00 — Developer Environment & Tooling
- [ ] Module 01 — Python, Properly
- [ ] Module 02 — Internet & Web Fundamentals
- [ ] Module 03 — HTML, CSS & JavaScript
- [ ] Module 04 — React
- [ ] Module 05 — Backend with FastAPI
- [ ] Module 06 — Databases
- [ ] Module 07 — Auth, Security & API Best Practices
- [ ] Module 08 — Testing & Software Quality *(Review Project milestone)*
- [ ] Module 09 — Linux, Networking & Servers
- [ ] Module 10 — Docker & Containers
- [ ] Module 11 — CI/CD, Cloud & Production Operations
- [ ] Module 12 — AI/ML Foundations
- [ ] Module 13 — Building with LLM APIs
- [ ] Module 14 — RAG (Retrieval-Augmented Generation)
- [ ] Module 15 — Agents & Modern AI Workflows *(Final Capstone)*

## Other repo-level files

- [MASTER_LEARNING_PLAN.md](MASTER_LEARNING_PLAN.md) — the full specification this course is generated from. Read this if you're curious why the course is structured the way it is.
- [RUNNING_PROJECT.md](RUNNING_PROJECT.md) — **QuestLog**, the single app that evolves from Module 04 through the final capstone, and the fixed tech stack decisions behind it.
- [GRADING_PROTOCOL.md](GRADING_PROTOCOL.md) — the exact rubric the AI uses to grade every exercise and module.
- [GLOSSARY.md](GLOSSARY.md) — every term defined anywhere in the course, alphabetical, growing as modules are added.
- [PROGRESS.md](PROGRESS.md) — your living progress record.

## Reading this course as a website

This repo also builds into a browsable website (MkDocs Material) with
search and a proper sidebar, deployed automatically to GitHub Pages on
every push to `main` (see `.github/workflows/deploy-docs.yml`).

**One-time setup** (only needed once, by a repo admin): in this repo's
GitHub **Settings → Pages → Build and deployment**, set **Source** to
**"GitHub Actions"** (not "Deploy from a branch"). After that, every push
to `main` redeploys the site automatically.

**To build/preview it locally:**
```bash
python -m venv .venv-docs
source .venv-docs/Scripts/activate   # Windows Git Bash
pip install -r requirements-docs.txt
source .venv-docs/Scripts/activate && mkdocs serve   # live-reloading preview at http://127.0.0.1:8000
# or, for a one-shot build into ./site:
bash build_docs.sh
```
See `build_docs.sh`'s header comment for why it copies the repo into a
throwaway `.docs_src/` folder before building (MkDocs 1.6+ won't allow
`docs_dir` to be the same directory as `mkdocs.yml` itself, and moving the
actual course content into a `docs/` subfolder would break the relative
links already used throughout every module).

## A note on pacing

This is meant to run at roughly 10–15 hours/week. Lessons are intentionally
long and thorough — a lesson that takes 30–45 minutes to read carefully is
working as intended. Don't skim. The exercises are designed so the first one
in any module is nearly impossible to fail if you actually read the lesson;
if it's not clicking, that's signal to re-read, not to push through.
