# Lesson 01 — What an Agent Is: The Loop

## What you'll learn

- A precise, working definition of "agent" — not the marketing version,
  the mechanical one.
- The **decide → act → observe → repeat** loop every agent, no matter how
  fancy the framework wrapping it, ultimately reduces to.
- How this differs from what you already built in Module 13 (a single
  tool-use round trip) and Module 14 (a single retrieval pass) — and why
  those two modules already taught you almost everything you need for
  this loop to feel obvious, not new.
- The vocabulary this whole module uses from here on: *turn*, *iteration*,
  *tool call*, *observation*, *termination condition*.

## Why this matters

Every real product feature in this module — QuestLog's own assistant,
built in Lessons 10–11 — is one instance of this loop, wearing an SSE
wire format and a React chat panel. If the loop itself isn't solid in
your head, everything downstream (tool design, memory, guardrails) is
just decoration on a shape you don't actually see yet. This lesson's
entire job is to make sure you see it — clearly enough that Lesson 02's
raw-Python implementation feels like writing down something you already
understand, not learning something new.

## Prerequisites

- **Module 13, Lesson 04 (tool use and function calling), in full.** This
  lesson assumes you can already explain the round trip: model responds
  with a `tool_use` block → your code runs the named function → you send
  a `tool_result` back → the model continues. If that's shaky, stop here
  and go back — this lesson builds directly on top of it and will not
  re-explain it.
- **Module 13's own `stream_quest_breakdown`** (`app/ai_assistant.py`) —
  you've already read a real, working tool-use loop; this lesson names
  what you already saw there.

## The concept, explained simply

You already know a loop shape from game development, even if you've never
called it "an agent": a behavior tree, or a finite state machine driving
an NPC. Every tick, the NPC's own "brain" does the same four things, in
order:

1. **Observe** the current world state (player distance, its own health,
   what it can currently see).
2. **Decide** what to do about it — pick one action from whatever its
   available actions are.
3. **Act** — actually execute that one action.
4. **Repeat**, next tick, with the world state now reflecting whatever
   just happened.

An **AI agent**, in the sense this module (and the wider industry) uses
the word, is the exact same loop, with one piece swapped out: instead of
a hand-written decision tree, an LLM is the thing deciding what to do at
step 2, and instead of "next tick," the loop repeats every time the model
asks for another action. Concretely:

1. **Observe** — the agent's current context: the conversation so far,
   plus the result of whatever it did last (a tool's return value).
2. **Decide** — the LLM looks at that context and either produces a final
   answer, or asks to call one of the tools it's been given.
3. **Act** — if it asked for a tool, your own code actually runs it (the
   model itself can't touch a database, a file, or a network call — it
   can only *ask* your code to).
4. **Observe** again — the tool's result becomes new context, and the
   loop goes back to step 2.

This repeats until the model produces a final answer with no further tool
request (or until some guardrail — Lesson 08's whole subject — stops it
first). That's it. That is the entire mechanical definition of "an
agent." Everything else you'll ever hear about agents — planning,
memory, multi-agent orchestration, frameworks — is built *on top* of this
one loop, not a replacement for it.

## The details

### What you already built, without the name

Look again at Module 13's `app/ai_assistant.py`'s `stream_quest_breakdown`
(`module-14-rag/project/questlog/backend/app/ai_assistant.py`, carried
forward into this module's own copy of QuestLog unchanged — go re-read it
now if it's not fresh). Strip away the streaming and the JSON-schema
detail, and its `for` loop is *exactly* the four-step shape above:

```python
for _ in range(MAX_TOOL_ITERATIONS):
    response = call_claude(messages)          # 1. observe (via messages) + 2. decide
    if response.stop_reason == "tool_use":
        result = run_the_tool(response)       # 3. act
        messages.append(tool_result(result))  # (result becomes new context)
        continue                              # 4. repeat
    return response.final_answer              # decided not to call a tool -> done
```

You built an agent loop in Module 13. It only ever had **one** possible
tool, and its own system prompt told the model to call that tool "exactly
once" before answering — so in practice, it never needed more than two
iterations. This module's own agent (Lessons 02 and 10) is the same loop,
with more tools, no instruction capping how many times it calls them, and
a genuinely open-ended job ("help the player with their quests") instead
of one narrow feature. The mechanism didn't change at all. The *scope*
did.

### The vocabulary this module uses

- **Turn** — one full pass through the loop from a fresh user message to
  a final answer, however many iterations it takes internally. "The agent
  took one turn to answer the player's question" is correct whether that
  turn involved zero tool calls or five.
- **Iteration** (or "step") — one single pass through decide → act →
  observe, inside one turn. `MAX_AGENT_ITERATIONS` (Lesson 08, and this
  module's own `app/agent.py`) caps the number of iterations *per turn*,
  not per conversation.
- **Tool call** — one specific request from the model to run one specific
  tool with one specific set of arguments. One iteration can contain
  *multiple* tool calls (the model can ask for several tools at once, in
  parallel — Lesson 03 covers this) or zero (if the model decides it's
  ready to answer).
- **Observation** — the result the agent's own code hands back to the
  model after running a tool. Borrowed directly from robotics and
  reinforcement-learning vocabulary, where an agent literally "observes"
  its environment after acting on it — the same word, the same idea,
  applied to an LLM instead of a physical or simulated robot.
- **Termination condition** — whatever makes the loop stop. The "good"
  termination condition is the model producing a final answer with no
  further tool request. The "bad" one — the one a guardrail exists to
  catch — is the loop never reaching that state at all.

### Why the loop, and not something more clever, is the right mental model

It might seem like there should be a smarter design — why not have the
model plan out every step up front, then execute the whole plan at once?
Two honest reasons this course's own agent (and most production agents)
don't work that way:

1. **The model doesn't know what a tool will return until it calls it.**
   A plan made before seeing any real data is a *guess* about what that
   data will look like. If the plan says "search quest notes, then create
   three quests from what it finds," but the search comes back empty, a
   rigid, pre-committed plan has no way to adapt — it either fails or
   barrels ahead with nothing to work from. The loop's whole value is
   that **every decision is made with the latest real information**, not
   a prediction of it.
2. **This mirrors exactly how a good behavior tree or state machine
   already handles adaptation.** You wouldn't hard-code an NPC's entire
   combat sequence as a fixed list of actions decided once at the start
   of the fight — you'd re-evaluate every tick precisely so the NPC can
   react to a player dodging, healing, or fleeing. An agent's loop is
   that same "re-evaluate before every action" discipline, just with an
   LLM doing the evaluating instead of a hand-written tree.

## Common mistakes & gotchas

- **Thinking "agent" means something architecturally exotic.** It
  doesn't. If you can write a `for` loop that calls an API, checks a
  field on the response, and conditionally calls a function, you can
  build an agent. The word describes a *pattern of use*, not a special
  kind of model or a piece of magic infrastructure.
- **Confusing "the agent decided to call a tool" with "the tool ran."**
  These are two separate steps, and conflating them is the single most
  common source of bugs in a hand-rolled agent loop: the model's
  `tool_use` block is a *request*. Nothing has actually happened in the
  real world (no quest created, no query run) until your own code
  executes it. This is precisely why guardrails (Lesson 08) are possible
  at all — your code sits between "the model asked for X" and "X actually
  happens," and can say no.
- **Assuming more iterations always means a better answer.** A model
  that needs ten iterations to answer a question a well-designed tool
  surface would answer in two isn't "trying harder" — it's usually a sign
  the tools themselves are poorly designed (Lesson 03) or the system
  prompt isn't giving the model what it needs to plan well (Lesson 04).
- **Forgetting the loop needs a termination condition you control, not
  just one you hope for.** "The model will eventually stop asking for
  tools" is not a guardrail — Lesson 08's `MAX_AGENT_ITERATIONS` is what
  actually guarantees the loop ends.

## How this connects

Lesson 02 writes this exact loop in raw Python, with no framework and no
streaming, so you can watch every step happen — the master plan's own
explicit instruction, and the most direct way to prove to yourself that
nothing about "an agent" is hidden or magic. Lesson 03 then asks the
harder question this lesson only touched on: given that a *tool's own
design* shapes how well (and how efficiently) an agent uses the loop, how
do you design a good one? Lessons 04–09 build every other real-world
concept — memory, MCP, multi-agent patterns, frameworks, guardrails,
evals, and using AI well in your own workflow — on top of this one loop.
Lessons 10–11 apply the whole thing, for real, inside QuestLog.

## Quick self-check

1. State the four-step loop from memory, in your own words, without
   looking back at this lesson.
2. What, exactly, is the difference between a "turn" and an "iteration"
   in this module's own vocabulary?
3. Why can't the model itself run a tool — what has to happen between the
   model asking for a tool and that tool's effect actually occurring?
4. Why does this lesson claim you already built an agent in Module 13,
   even though that module never used the word "agent"?
5. Give one concrete reason a fixed, pre-computed plan is a worse fit
   than a loop for a task like "search my notes, then create quests from
   what you find" — in your own words, not copied from this lesson.
