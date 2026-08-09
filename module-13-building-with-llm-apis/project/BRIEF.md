# Capstone Brief — QuestLog's AI Assistant, Verified End to End

## What you're doing

This module's `project/questlog/` already contains a real, working
feature: `POST /api/quests/{quest_id}/suggest-breakdown`, backed by a
real tool-use round-trip, structured output, and streaming (Lessons
01-05, applied in Lessons 07-08), plus a `QuestBreakdownPanel` on the
frontend that calls it. Both are fully tested — 46 backend tests and 22
frontend tests, all passing with no real API key required (see
`backend/tests/test_ai_assistant.py` and
`frontend/src/components/QuestBreakdownPanel.test.tsx`).

Your job in this capstone is **not to build this feature from scratch** —
it's to **get it running live with your own API key (or do a thorough,
honest dry run), verify it genuinely works the way Lessons 07-08 claim,
run a real eval pass against it, break something on purpose and fix it,
and write up what you found** — the same "understand it well enough to
explain and to fix" standard every capstone since Module 09 has used.

## Before you start

- [ ] All five exercises in this module are done and reviewed.
- [ ] You've read Lessons 00-08 in full, in order.
- [ ] You have a real Anthropic API key (Lesson 00), or have decided to
      do a dry run instead (see "A note on scope," at the bottom).
- [ ] You've read `project/questlog/README.md` for how to run the backend
      and frontend locally (unchanged since Module 05 — this module adds
      no new setup step beyond the `.env` additions below).

## What to actually do

### Part 1 — Get the feature running live

1. In `project/questlog/backend/.env` (copy from `.env.example` if you
   haven't already), set a real `ANTHROPIC_API_KEY`. Leave `AI_MODEL`
   unset (it defaults to `claude-haiku-4-5`, this module's own fixed
   choice — see Lesson 00).
2. Start the backend (`uvicorn app.main:app --reload`, same as every
   earlier module) and the frontend (`npm run dev`).
3. Log in as the seeded demo account (`player@questlog.local` /
   `dragon-slayer-1`, unchanged since Module 07) and open any quest's
   detail page.
4. Click **"Suggest a Breakdown."** **Confirm, watching it happen live:**
   - Text visibly streams in, token by token — not a single pause
     followed by everything appearing at once (Lesson 02's whole point,
     made observable).
   - A brief "Checking your other quests for duplicates..." message
     appears at some point (the tool-use round trip, Lesson 04, actually
     firing) — note that Claude decides on its own whether to call the
     tool, so this may not appear on every single quest; if it doesn't
     appear on your first try, try a quest whose plausible sub-quests are
     more likely to overlap with your account's existing quest titles.
   - A clean list of 2-4 suggested sub-quest titles appears once
     streaming finishes.
5. Click **"Add as quest"** on one suggestion. **Confirm** a real new
   quest appears on the Quest Board, with the same priority and quest
   line as its parent.

### Part 2 — Run a real eval pass against the live feature

Using Lesson 06 and Exercise 05's pattern, write a small script (or adapt
`exercises/05-eval-harness-for-breakdown/solution/eval_breakdown.py`) that
runs **at least 5 real, live calls** to `stream_quest_breakdown` (or a
simplified equivalent, non-streamed, is fine for this check — see
Exercise 05's own note about that trade-off) against **QuestLog's own
seeded demo quests** ("Slay the Dragon," "Gather Healing Herbs," etc. —
see `backend/app/repository.py`'s `seed_if_empty` for the full list) or
your own real quests, checking: correct count (2-4), no duplicate of an
existing quest title, no verbatim restatement of the original quest, and
title length under 12 words. Record the real, actual results — not a
prediction of what you'd expect.

### Part 3 — Break something on purpose, then fix it (pick one)

- Temporarily unset `ANTHROPIC_API_KEY` (comment it out in `.env`,
  restart the backend) and click "Suggest a Breakdown" again. **Confirm**
  you get a clean `503` with a clear message, not a confusing crash —
  then restore the key and confirm it works again.
- Deliberately lower `MAX_TOOL_ITERATIONS` in `app/ai_assistant.py` to
  `0` and try the feature again. **Confirm** you now always see the
  "gave up after checking too many times" error message, even for a
  quest that would normally succeed — then explain, in your own words,
  exactly why a `0` here breaks every single request (re-read Lesson 04's
  own loop code if this isn't immediately obvious), and restore the real
  value.

### Part 4 — Extend it, in one small, well-justified way

Pick **one** small, real addition and implement it — not a large
redesign, one focused change, in the same spirit as every earlier
module's own capstone additions:

- Add a "Regenerate" option once suggestions are showing, letting the
  player ask again without leaving the page.
- Surface the real per-request cost (Lesson 05's cost-management
  material) somewhere in the UI or a backend log line, computed from
  `response.usage` at the point where the final structured result is
  produced.
- Extend the eval harness from Part 2 into a real `pytest` file
  (`backend/tests/test_ai_assistant_eval.py` or similar) that's safe to
  run in CI by default (skipping the live-call cases automatically when
  no `ANTHROPIC_API_KEY` is set, rather than failing) — a real
  application of Lesson 06's own "don't require a key" principle to your
  own new test file, not just this module's existing ones.

## Deliverables

Write up a short report (`project/AI_ASSISTANT_REPORT.md` — create this
yourself; no fixed template, honest content matters more than a fixed
shape) covering:

1. **Part 1's confirmation**, describing what you actually observed —
   real screenshots, terminal output, or a precise written account if you
   did a dry run instead (see "A note on scope" below).
2. **Part 2's real eval results** — every case you ran, what passed,
   what (if anything) failed, and your honest assessment of whether the
   feature is working well.
3. **Part 3's broken-then-fixed scenario** — the exact behavior you
   observed when it was broken, and confirmation it works again once
   fixed.
4. **Part 4's extension** — what you built, why you chose it, and the
   actual diff.
5. **An honest accounting of what this feature still doesn't do** — for
   example: no way to edit a suggestion's title before accepting it, no
   caching of repeated identical requests (contrast with Module 10's own
   Redis cache for `GET /api/quests` — why doesn't this feature use the
   same pattern? Is that a gap, or a reasonable choice? Explain your
   reasoning either way).

## Acceptance criteria (what "done" looks like)

- [ ] The feature genuinely streams, calls its tool, and produces valid
      suggestions when run live with a real key (or a thorough, honest
      dry-run account exists instead).
- [ ] A real eval pass (Part 2) ran against at least 5 real cases, with
      real, reported results.
- [ ] Part 3's break-then-fix scenario is genuinely reproduced and
      explained, not just asserted.
- [ ] Part 4's extension is implemented, small, and well-justified.
- [ ] `AI_ASSISTANT_REPORT.md` exists and covers all five numbered points
      above, honestly.
- [ ] You can explain, without looking anything up, the complete path a
      single "Suggest a Breakdown" click takes — every request, every
      streamed event, every state transition — from the button being
      clicked to a new quest appearing on the Quest Board.
- [ ] No more than a few cents of real API spend was required for
      anything in this capstone, per Lesson 00's own cost estimate.

## A note on scope

Consistent with this module's own Lesson 00 framing, and the same pattern
Modules 09, 11, and 12 all used for real infrastructure or paid-API
requirements: if you'd rather not spend even the small amount this
capstone genuinely costs right now, a thorough, honest dry run —
reading every relevant line of `app/ai_assistant.py` and
`QuestBreakdownPanel.tsx`, tracing exactly what would happen at each step
of Parts 1-3, and writing up precisely what you'd expect to observe,
citing this module's own lessons by name — is a fully legitimate way to
complete this capstone. What matters is demonstrated understanding of
*why* the feature works the way it does, not a specific number of dollars
spent proving it.
