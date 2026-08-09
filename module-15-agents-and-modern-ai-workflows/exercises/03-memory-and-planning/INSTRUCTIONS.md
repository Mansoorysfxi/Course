# Exercise 03 — Memory and Planning

**Difficulty:** Guided. You'll turn a single-turn agent into a real,
multi-turn conversation, and add a simple, inspectable planning tool.

## What you'll build

A standalone Python script, `journal_agent.py`, modeling a tiny
adventure-journal assistant. You'll extend a single-call agent function
into a real `Conversation` class that keeps short-term memory across
several separate calls (the same shape Module 13's own
`ConversationManager` example first taught, now applied to a tool-using
agent instead of a plain chat), and add a `plan` tool the agent can use
to think out loud before acting.

## Concepts this exercise requires (all taught in Lesson 04)

- The real difference between short-term memory (this exercise) and
  long-term memory (not required here — you're not persisting anything
  to disk).
- Where an agent's short-term memory actually lives in code.
- Why "planning" is mostly not a separate mechanism — and what a
  dedicated planning tool actually adds when you do build one.

## Instructions

1. Open `starter/journal_agent.py`. It has a working single-turn
   `run_agent(client, messages)` function (note: it takes the **whole
   messages list**, not just one new message — that's already the right
   shape for what you're about to build) and one TODO: a `Conversation`
   class stub.
2. Implement `Conversation`:
   - `__init__(self, client)` stores the client and starts an empty
     `self.messages` list.
   - `send(self, user_text: str) -> str` appends a new user turn to
     `self.messages`, calls `run_agent` with the *entire* history so far,
     appends the agent's own final answer as an assistant turn, and
     returns that answer. (This mirrors `app/agent.py`'s own
     `run_agent_turn`, which also takes the full history and returns one
     final answer per call — the "memory" is simply the growing
     `self.messages` list living across separate `send()` calls.)
3. Add a new tool, `add_journal_entry(text: str)`, that appends to an
   in-memory list, `JOURNAL`. This is intentionally a plain action tool —
   nothing about it plans anything.
4. Add a second tool, `plan(steps: list[str])`, whose entire
   implementation just returns the steps back as a formatted string (no
   real side effect at all) — its only job is making the model's own plan
   visible before it starts calling `add_journal_entry`, per Lesson 04's
   own "a plan tool as an explicit, inspectable step" discussion.
5. Script a fake conversation with **two separate `send()` calls** — the
   second one should demonstrate the conversation remembering something
   from the first (e.g., the second message asks "what did I just add?"
   and the scripted final answer references the first entry) — proving
   your `Conversation` class genuinely carries memory across calls, not
   just within one.

## Acceptance criteria

- `Conversation.send()` can be called more than once on the same
  instance, and each call's own `messages` list passed to `run_agent`
  includes every prior turn, not just the newest one.
- `add_journal_entry` and `plan` are two separate tools — `plan` never
  writes to `JOURNAL` itself.
- Your scripted two-call conversation demonstrates memory working: the
  second `send()` call's own scripted final answer references something
  established in the first call.
- Restarting the script (a fresh `Conversation` instance) starts with
  empty memory — prove this to yourself by printing `conversation.messages`
  before and after your first `send()` call.

## Hints

- **Level 1:** Re-read Lesson 04's own "short-term memory: the
  conversation history you already have" section — `Conversation`'s
  entire job is owning the `messages` list across calls, nothing more.
- **Level 2:** `Conversation.send()` should look almost exactly like
  Lesson 02's own `run_agent`, except it takes `self.messages` as its
  starting point instead of building a fresh `[{"role": "user", ...}]`
  list from scratch each time.
- **Level 3:** For the second scripted `send()` call to reference the
  first entry, your fake client's second batch of turns needs a final
  text answer that literally mentions the journal text from your first
  scripted `add_journal_entry` call — this is scripted, not computed, so
  make sure the two match up by hand.

## Running it

```bash
cd module-15-agents-and-modern-ai-workflows/exercises/03-memory-and-planning/starter
python journal_agent.py
```

**Expected output shape:** two separate conversation turns printed in
sequence, the second one demonstrating it "remembers" the first.
