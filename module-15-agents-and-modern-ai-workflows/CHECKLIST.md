# Module 15 Checklist — Agents & Modern AI Workflows (Final Module)

Complete this before calling the entire course done. Check off each item
honestly — this is a self-assessment, not a formality, and it's the last
one.

## Lessons

- [ ] Read `lessons/00-setup.md` and confirmed every command in its
      "Verify your setup" section — QuestLog's own Module 14 backend
      still passes its full test suite, and the optional `mcp[cli]`
      package installs correctly in its own scratch environment.
- [ ] Read `lessons/01-what-an-agent-is-the-loop.md` and can state the
      four-step loop (observe, decide, act, observe) from memory.
- [ ] Read `lessons/02-building-a-minimal-agent-from-scratch.md`, ran
      `minimal_agent.py` yourself, and can explain every line of its own
      `run_agent` function.
- [ ] Read `lessons/03-tool-design-and-multi-step-reasoning.md` and can
      explain, from memory, the two real reasons `complete_quest` exists
      as its own tool instead of a flag on `update_quest`.
- [ ] Read `lessons/04-memory-and-planning.md` and can state, precisely,
      the difference between short-term and long-term memory — not just
      "how long it lasts," but what has to physically exist for each.
- [ ] Read `lessons/05-model-context-protocol-mcp.md`, ran
      `quest_notes_server.py` and `client_probe.py` yourself, and can
      explain MCP's three roles (host, client, server).
- [ ] Read `lessons/06-multi-agent-patterns-and-orchestration.md` and can
      explain the real difference between coordinator/worker and
      handoff, and ran the human-in-the-loop example yourself.
- [ ] Read `lessons/07-agent-frameworks-overview.md` and can give an
      honest, reasoned opinion on which framework (or none) fits a
      project you describe yourself.
- [ ] Read `lessons/08-agent-safety-guardrails-and-evals.md` and can name
      every guardrail QuestLog's own agent implements, plus the real
      reason for each.
- [ ] Read `lessons/09-ai-in-your-dev-workflow.md` and can name the two
      concrete habits it gives for avoiding skill atrophy.
- [ ] Read `lessons/10-building-questlogs-agent-backend.md` and
      `lessons/11-building-questlogs-agent-frontend-and-going-live.md` in
      full, and have actually read `project/questlog/backend/app/agent.py`
      and `project/questlog/frontend/src/components/AgentChatPanel.tsx`
      end to end, not just the lessons describing them.

## Exercises

- [ ] Exercise 01 (minimal agent loop) — done and reviewed.
- [ ] Exercise 02 (tool design and multi-step reasoning) — done and
      reviewed.
- [ ] Exercise 03 (memory and planning) — done and reviewed.
- [ ] Exercise 04 (building an MCP server) — done and reviewed, including
      a real, live run against the `mcp[cli]` inspector.
- [ ] Exercise 05 (guardrails and evals) — done and reviewed, including
      having actually broken your own guardrail on purpose and watched
      your evals react (correctly catching it, or — just as
      instructively — not catching it, per that exercise's own honest
      finding).

## Capstone

- [ ] `project/BRIEF.md` Part 1 — the agent genuinely lists, creates,
      updates, and completes real quests, searches real notes with real
      citations, and suggests real breakdowns, run live (or a thorough,
      honest dry run exists instead).
- [ ] Part 2 — the deliberately-broken scenario was genuinely reproduced
      and then fixed, with the real behavior documented.
- [ ] Part 3 — one small, real extension was implemented and explained,
      with existing tests still passing afterward.
- [ ] Part 4 (optional) — the real MCP tie-back was run against a real
      Postgres+pgvector instance, or an honest account exists of why
      that wasn't possible.
- [ ] `project/AGENT_FEATURE_REPORT.md` written, covering all six
      required points from the brief — including the final, whole-course
      reflection.
- [ ] You can explain, unprompted, the complete path one chat message
      takes — the loop, the tool call, the guardrail checks, and the
      streamed answer — from a player typing a message to a real action
      (or a real, cited answer) appearing.
- [ ] The backend test suite (`pytest`, from
      `project/questlog/backend/`) and frontend test suite (`npx vitest
      run`, from `project/questlog/frontend/`) both still pass in full,
      with no `ANTHROPIC_API_KEY` and no `TEST_PGVECTOR_DATABASE_URL` set
      anywhere in your shell (the pgvector-integration tests should show
      as **skipped**, not failed, in that case).

## Spaced repetition — review questions from earlier modules

Per this course's Rule 6, answer these without re-reading the original
lesson first; check your answer against the linked material afterward.

1. **(Module 07)** Why does a route that fetches "a quest by id" combine
   the existence check and the ownership check into one query
   (`WHERE id = ... AND owner_id = ...`), rather than fetching the quest
   first and checking ownership as a separate step? *(See
   `module-07-auth-security/lessons/07-protecting-routes-with-dependencies.md`
   — and notice this module's own `app/agent.py`'s `_get_owned_quest`
   applies the exact same discipline to a tool call's own arguments, not
   just an HTTP path parameter.)*
2. **(Module 08)** What does mocking actually mean, and why did this
   course choose to mock the Anthropic API in every AI feature's tests
   since Module 13, rather than either skipping those tests or requiring
   a real key to run them? *(See
   `module-08-testing-and-quality/lessons/03-parametrize-and-mocking.md`
   — this module's own `tests/test_agent.py` extends that exact same
   `FakeAnthropicClient` pattern to a multi-tool, multi-iteration loop.)*
3. **(Module 09)** What is the real difference between a `403 Forbidden`
   and a `404 Not Found` from a security-information point of view, and
   why does this course consistently prefer the second for an
   authorization failure? *(See
   `module-09-linux-networking-servers/lessons/07-deploying-questlog-part1-server-and-backend.md`
   and Module 07's own lessons — this module's own agent tools apply the
   identical reasoning to a tool result, not an HTTP response.)*
4. **(Module 13)** Describe the full tool-use round trip from memory:
   what does the model send, what does your own code have to do with it,
   and what goes back. *(See
   `module-13-building-with-llm-apis/lessons/04-tool-use-and-function-calling.md`
   — this entire module's own agent loop is that same round trip,
   repeated.)*
5. **(Module 14)** Why does this course's own RAG feature build citations
   from chunks the code already knows were retrieved, rather than asking
   the model to produce a citations object itself? *(See
   `module-14-rag/lessons/06-building-a-rag-pipeline-by-hand.md` — and
   notice this module's own `search_quest_notes` tool reuses that exact
   retrieval result for the same reason, one more time.)*

## Before finishing the course

- [ ] All boxes above are checked honestly.
- [ ] You understand, in your own words, why this module builds the
      agent loop by hand before ever mentioning a framework, and can name
      at least one concrete thing a framework like LangGraph or CrewAI
      would genuinely have saved you, and one thing it would have cost.
- [ ] You can explain why QuestLog's agent has no `delete_quest` tool at
      all, and why that's described as a guardrail, not a limitation.
- [ ] You understand this feature's memory scope well enough to explain
      it to someone using QuestLog for the first time: what it will and
      won't remember, and why.
- [ ] You've written the final, whole-course reflection `project/BRIEF.md`
      asks for, and it genuinely traces at least three modules' own
      contributions to this one, final feature.
