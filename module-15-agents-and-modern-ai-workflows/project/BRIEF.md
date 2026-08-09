# Capstone Brief — QuestLog's Autonomous Agent, Verified End to End

## What you're doing

This is the final capstone of the entire course. This module's
`project/questlog/` already contains a real, working feature: a player
can converse with QuestLog's own assistant, which can list, create,
update, and complete their quests, search a specific quest's own notes
and answer with citations, and suggest a quest breakdown — all via real
tool calls, streamed live to a chat panel, with real guardrails (a hard
iteration cap, no destructive tool at all, ownership scoping on every
tool, and Pydantic-validated tool inputs) — see Lessons 10–11 for the
complete walkthrough. It's fully tested: 85 backend tests (2 intentionally
skipped without a real Postgres+pgvector instance, exactly as established
since Module 14) and 34 frontend tests, all passing with no real
Anthropic key required.

Your job in this capstone is **not to build this feature from scratch** —
it's to **get it running live (with your own Anthropic API key, or do a
thorough, honest dry run), verify it genuinely works the way Lessons
10–11 claim, extend it in one small, well-justified way, and write up
what you found and, since this is the last capstone of the whole course,
reflect honestly on the entire multi-month journey this project
represents** — the same "understand it well enough to explain and
extend" standard every capstone since Module 09 has used, one last time.

## Before you start

- [ ] All five exercises in this module are done and reviewed.
- [ ] You've read Lessons 00–11 in full, in order.
- [ ] You've completed Lesson 00's setup — QuestLog's own Module 14
      backend/frontend already running, plus (only if you're doing
      Exercise 04 or the optional MCP section below) `mcp[cli]` installed
      in its own scratch environment.
- [ ] You've read `project/questlog/README.md` for how to run the backend
      and frontend locally.

## What to actually do

### Part 1 — Get the feature running live

1. Start the backend and frontend, with a real `ANTHROPIC_API_KEY` set in
   `project/questlog/backend/.env`.
2. Log in as the seeded demo account (`player@questlog.local` /
   `dragon-slayer-1`) and click **Assistant** in the top nav.
3. **Ask it to list your quests** ("What quests do I have?"). Confirm you
   see a `tool_call` status ("Looking at your quests...") appear live,
   before the final answer.
4. **Ask it to create a quest** ("Add a quest called 'Scout the Northern
   Pass', medium priority, in the Side Quests line"). Confirm the quest
   genuinely exists afterward — check QuestLog's own Quest Board, not
   just the chat's own claim that it worked.
5. **Add a note to an existing quest through QuestLog's own notes UI**
   (Module 14's own feature — still there, unchanged), then **ask the
   assistant a question about it** through the chat panel. Confirm a
   "Notes consulted" list appears, naming the real note, and the final
   answer cites it by title.
6. **Ask it to break down a quest** ("Break down my dragon quest"),
   confirm it suggests sub-quests **without creating anything**, then
   ask it to actually add one of the suggestions as a real quest, and
   confirm that one now exists too.
7. **Try to get it to delete something** ("Delete my dragon quest").
   Confirm it plainly tells you it can't, and doesn't attempt any
   workaround — this is Lesson 08's own guardrail, working as designed.

### Part 2 — Break something on purpose, then fix it (pick one)

- Temporarily unset `ANTHROPIC_API_KEY` (restart the backend) and send a
  chat message. Confirm a clean `503`, not a confusing crash — then
  restore the key and confirm it works again.
- Ask it something about a quest that belongs to a **different** account
  (sign up a second test account, note one of its quest ids, then ask the
  first account's assistant about that id directly). Confirm it reports
  the quest doesn't exist — never that it belongs to someone else — and
  explain, from `app/agent.py`'s own `_get_owned_quest`, exactly why.
- Ask it a question phrased so it needs several tool calls to answer
  (e.g., referencing a quest only by an approximate title, requiring
  `list_quests` first). Watch the `usage` footer after it answers, and
  explain, using Lesson 00's own cost math, roughly what that
  conversation turn cost in real terms.

### Part 3 — Extend it, in one small, well-justified way

Pick **one** small, real addition and implement it — not a large
redesign:

- Add a new, narrow, read-only tool: `quest_stats()`, wrapping
  `app/repository.py`'s own `quest_line_stats` (already built, in
  Module 06) — decide, and justify in writing, its description text
  (Lesson 03's own "what makes a description good" section).
- Add a genuine trajectory-level eval (Lesson 08's own pattern) for one
  real QuestLog scenario — e.g., "given a question naming a quest by
  title only, does the agent call `list_quests` before
  `search_quest_notes`?" — using `tests/test_agent.py`'s own
  `FakeAgentAnthropicClient` to script it, with no real API key required.
- Extract the third copy of the SSE-parsing loop Lesson 11's own
  `agentApi.ts` docstring named as a real, honest, undone piece of
  cleanup — a shared `parseSSEStream()` helper used by `aiApi.ts`,
  `notesApi.ts`, and `agentApi.ts` alike — and confirm all three
  features' own existing tests still pass unchanged afterward.

### Part 4 (optional, if you completed Exercise 04) — Run the real MCP tie-back

With a real `pgvector`-enabled Postgres running and at least one note
added to the seeded demo account through QuestLog's own UI, run
`python -m app.mcp_server` from `backend/` (after `pip install -r
requirements-mcp.txt`), and use `mcp dev app/mcp_server.py`'s own
inspector (Lesson 05) to call `search_quest_notes` for real, against that
note. Confirm you get a real excerpt back — this is the one thing this
module's own generation process could not verify live (no real
Postgres+pgvector was available while writing it), exactly the kind of
gap this capstone exists to close for real.

## Deliverables

Write up a short report (`project/AGENT_FEATURE_REPORT.md` — create this
yourself; no fixed template, honest content matters more than a fixed
shape) covering:

1. **Part 1's confirmation** — what you actually observed, for each of
   the seven numbered steps.
2. **Part 2's broken-then-fixed scenario** — the exact behavior you
   observed when it was broken, confirmed working again once fixed, and
   your own explanation of the guardrail or cost behavior involved.
3. **Part 3's extension** — what you built, why you chose it, and the
   actual diff.
4. **Part 4's result, if attempted** — did the real MCP tie-back actually
   return a real excerpt? If you couldn't run it, say so honestly.
5. **An honest accounting of what this feature still doesn't do** — for
   example: no persistence of a conversation across a page reload, no
   `delete_quest` tool at all (a guardrail, not a gap — say why), no
   human-in-the-loop confirmation step for any action (a real, considered
   decision — is it the right one for what this agent can currently do?
   argue it either way), no long-term memory of a player's preferences.
   For each, say whether it's a real gap or a reasonable, stated scope
   decision, and why.
6. **A final, whole-course reflection** — since this is the last capstone
   of the entire course: pick three modules, from any phase, and explain,
   in your own words, one specific piece of *this* capstone that
   genuinely would not exist, or would be meaningfully worse, without
   what that module taught. (For example: "Module 07's ownership-scoping
   discipline is the entire reason `_get_owned_quest` is safe to call
   with a model-supplied `quest_id`.")

## Acceptance criteria (what "done" looks like)

- [ ] The feature genuinely lists, creates, updates, and completes real
      quests, searches real notes with real citations, and suggests real
      breakdowns, when run live (or a thorough, honest dry-run account
      exists instead).
- [ ] Part 2's break-then-fix scenario is genuinely reproduced and
      explained, not just asserted.
- [ ] Part 3's extension is implemented, small, and well-justified, and
      the existing test suites (backend and frontend) still pass in full
      afterward.
- [ ] `AGENT_FEATURE_REPORT.md` exists and covers all six numbered points
      above, honestly.
- [ ] You can explain, without looking anything up, the complete path one
      chat message takes — the loop, the tool call, the guardrail checks,
      the streamed answer — and name, specifically, which guardrail from
      Lesson 08 would stop a plausible way that path could go wrong.
- [ ] No more than a few cents of real API spend was required for
      anything in this capstone, per Lesson 00's own cost estimate.

## A note on scope

Consistent with this module's own Lesson 00 framing, and the same pattern
every earlier module's capstone with a real infrastructure or paid-API
requirement has used: if you'd rather not spend even the small amount
this capstone genuinely costs right now, a thorough, honest dry run —
reading every relevant line of `app/agent.py`, `app/routers/agent.py`,
and `AgentChatPanel.tsx`, tracing exactly what would happen at each step
of Parts 1–3, and writing up precisely what you'd expect to observe,
citing this module's own lessons by name — is a fully legitimate way to
complete this capstone. What matters, one last time, is demonstrated
understanding of *why* the feature works the way it does, not a specific
number of dollars spent proving it.

Congratulations on reaching the final capstone of this course. Whatever
you write in `AGENT_FEATURE_REPORT.md`'s own final reflection is worth
taking seriously — you've built one real application, from a bare
`git init` in Module 00 to a tested, deployed, AI-agent-powered product,
and that arc is the actual portfolio piece this entire course exists to
produce.
