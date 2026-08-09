# Lesson 06 — Multi-Agent Patterns, Orchestration, and Human-in-the-Loop

## What you'll learn

- Why and when to use *more than one* agent for a single task, instead of
  one agent with a bigger tool set.
- The two most common multi-agent shapes: **coordinator/worker** and
  **handoff** — what distinguishes them and when each fits.
- **Human-in-the-loop**: how to pause an agent's own loop before a
  specific action and require a real approval before it proceeds — built
  by hand, on top of the exact loop you already know.

## Why this matters

Not every problem is well-served by one agent with a long list of tools.
Sometimes the right shape is several smaller, more focused agents working
together — and sometimes the right shape is one agent that simply isn't
allowed to act on something without a person's explicit say-so first.
Both are real, common patterns you'll recognize the instant you see them,
and both are built entirely out of the same loop primitive from Lesson 02
— nothing here requires new API surface.

## Prerequisites

- **Lessons 01–03, in full** — the loop, its vocabulary, and tool-design
  judgment.
- **Lesson 04** — memory scope, since coordinating multiple agents raises
  real questions about what each one can and can't see of the others'
  context.

## The concept, explained simply

Think about a multiplayer game server's own architecture: one central
**director** process that owns the authoritative game state and
coordinates several specialized **worker** processes — one handling
physics, one handling matchmaking, one handling chat moderation — each
doing one job well, reporting back to the director rather than trying to
do everything itself in one enormous process. This is exactly the
**coordinator/worker** pattern for agents: one "lead" agent that decides
*what* needs doing and delegates pieces of it to other, more specialized
agents, each with a narrower tool set and a narrower job, then combines
what comes back.

**Human-in-the-loop** is a different, related idea: instead of a second
agent reviewing an action, a real *person* does — the loop pauses right
before a specific action executes and waits for a person to say yes or
no, the same way a game might pause and show a confirmation dialog before
an irreversible action ("Are you sure you want to delete this save
file?") rather than letting a single misclick proceed straight to
data loss.

## The details

### Coordinator/worker

The shape: one agent (the coordinator) has tools that don't do the real
work themselves — they hand a sub-task to a *different* agent (the
worker), wait for that worker's own result, and use it. Each worker can
have its own, much narrower tool set and system prompt, tuned for exactly
one kind of job.

**When this genuinely helps, concretely:**

- **The work splits into independent pieces.** Several sources to
  research, many files to process, several unrelated quests to check —
  each piece can run as its own worker, potentially even in parallel,
  rather than one agent doing everything serially in a single, ever
  growing conversation.
- **A cheaper model can do the bulk of the reading.** A common, genuinely
  valuable split: a large, expensive model plans and synthesizes; a
  smaller, cheaper model (this course's own `claude-haiku-4-5`, for
  instance) does the repetitive reading/searching work each worker needs
  to do. The coordinator's own context stays small — it only ever sees
  each worker's *finished report*, not everything that worker read to
  produce it.
- **Different jobs genuinely need different tools.** A worker that only
  ever searches and reads doesn't need — and shouldn't have — a tool that
  can write to a database. Narrower tool sets per worker are also a real
  safety benefit, not just an organizational one (see Lesson 08).

**A worked sketch** (illustrative — showing the *shape*, not something
this lesson runs live, since it would need two real, coordinated Claude
conversations to demonstrate honestly rather than one scripted fake):

```python
def run_worker(client, system_prompt, tools, user_message):
    """A complete, ordinary agent loop (Lesson 02's own shape) -- just
    parameterized by its own system prompt and tool set, so it can be
    reused as a "worker" the coordinator below calls into."""
    messages = [{"role": "user", "content": user_message}]
    # ... the exact same loop from Lesson 02 ...
    return final_answer


def coordinator_delegate_tool(sub_task: str) -> str:
    """The coordinator's own tool -- from the coordinator's point of
    view, this looks like any other tool call. What actually happens
    underneath is a whole separate agent loop, with its own tools and its
    own system prompt, run to completion, its finished answer returned as
    this tool's own result."""
    return run_worker(
        client,
        system_prompt="You are a research assistant. Answer exactly the question you're given.",
        tools=[WEB_SEARCH_TOOL],
        user_message=sub_task,
    )
```

The coordinator's own loop never needs to know a worker exists as
anything other than a tool call — from the coordinator's perspective,
`coordinator_delegate_tool` is indistinguishable from `calculate` or
`get_current_time` in Lesson 02. This is the entire mechanism: **a
sub-agent is just a tool whose implementation happens to be another
agent loop.**

### Handoff

A different shape: instead of a coordinator that stays in charge and
delegates pieces of work, one agent **transfers the entire conversation**
to a different agent better suited to continue it — think of a support
chatbot that starts as a general triage agent, and once it determines the
conversation is actually a billing question, hands the *whole*
conversation over to a specialized billing agent, which takes over
completely rather than reporting back to the triage agent. The triage
agent's own job ends at the handoff; it isn't coordinating a report back
from the billing agent the way a coordinator would from a worker.

**When handoff fits better than coordinator/worker:** when the
sub-task genuinely isn't a "sub"-task at all — it's the *entire*
remaining conversation, and the original agent has no further role to
play once the right specialist takes over.

### Human-in-the-loop, built by hand

This is the most directly useful pattern for this module's own capstone,
and it needs no new API surface at all — just a check, inserted into the
exact loop you already know, right before a flagged tool actually runs:

```python
"""Pause before a flagged tool executes, and only run it if approved."""
from types import SimpleNamespace

SENSITIVE_TOOLS = {"send_email"}

def run_tool(name, tool_input):
    if name == "send_email":
        return f"Email sent to {tool_input['to']}."
    return f"Unknown tool {name}"

def run_agent(client, user_message, approve_fn, max_iterations=5):
    messages = [{"role": "user", "content": user_message}]
    for iteration in range(1, max_iterations + 1):
        response = client.messages.create(
            model="claude-haiku-4-5", max_tokens=512, tools=[], messages=messages
        )
        if response.stop_reason != "tool_use":
            return next(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name in SENSITIVE_TOOLS:
                approved = approve_fn(block.name, block.input)
                if not approved:
                    print(f"   [human-in-the-loop] DENIED: {block.name}({block.input})")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "The user declined to approve this action.",
                        "is_error": True,
                    })
                    continue
                print(f"   [human-in-the-loop] APPROVED: {block.name}({block.input})")
            result = run_tool(block.name, block.input)
            print(f"   tool result: {result}")
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "user", "content": tool_results})
    return "Gave up."
```

`approve_fn` is the entire mechanism — a plain function that decides yes
or no. In a real terminal script it might call `input("Approve? [y/n] ")`;
in QuestLog's own frontend (Lesson 10) it would be a button a player
clicks; in an automated test (as below), it's a scripted, predictable
function.

**Live-verified, August 9, 2026, running the exact code above against
scripted fake turns** — one run where the human approves, one where they
deny:

```python
def text_block(t): return SimpleNamespace(type="text", text=t)
def tool_use(id_, name, inp): return SimpleNamespace(type="tool_use", id=id_, name=name, input=inp)
def final(c, sr): return SimpleNamespace(content=c, stop_reason=sr)

class FakeMessages:
    def __init__(self, turns): self._turns = iter(turns)
    def create(self, **kw): return next(self._turns)
class FakeClient:
    def __init__(self, turns): self.messages = FakeMessages(turns)

fake = FakeClient(turns=[
    final([tool_use("t1", "send_email", {"to": "guild@example.com", "body": "We won!"})], "tool_use"),
    final([text_block("Sent the email to the guild.")], "end_turn"),
])
print(run_agent(fake, "Email the guild that we won.", approve_fn=lambda name, inp: True))
```

**Expected output, exactly as observed:**

```
   [human-in-the-loop] APPROVED: send_email({'to': 'guild@example.com', 'body': 'We won!'})
   tool result: Email sent to guild@example.com.
Sent the email to the guild.
```

**Try it yourself:** Change `approve_fn` to always return `False`, and
script the second Claude turn to respond gracefully to a denial (a real
model, told via a `tool_result` with `is_error: true` that the user
declined, will typically acknowledge that and offer an alternative rather
than trying the same tool again immediately — script a `final(...)` turn
that does this, and confirm the printed output matches what you scripted).

## Common mistakes & gotchas

- **Reaching for multiple agents before confirming one agent, well
  tooled, can't already do the job.** Coordinating agents is real,
  additional complexity — extra round trips, extra places for context to
  get lost between agents. Most tasks this course's own scope covers are
  genuinely better served by one well-designed agent (Lesson 03) than by
  splitting it prematurely.
- **Letting a coordinator's own context fill up with everything a worker
  read.** The entire value of the coordinator/worker split evaporates if
  you pass a worker's full raw search results back to the coordinator
  instead of its finished, synthesized report — you've just built one
  giant agent with extra steps.
- **Treating human-in-the-loop as "ask before literally everything."** A
  confirmation gate on every single tool call trains users to click
  "approve" reflexively without reading what they're approving — the same
  failure mode as a game that pops up a confirmation dialog for every
  trivial action until players stop reading them. Gate the genuinely
  risky, hard-to-undo actions; let the safe, reversible ones proceed
  automatically (Lesson 08 covers exactly this judgment call for real).
- **Forgetting the denied path needs a real `tool_result`.** The loop
  still needs *some* result to send back for a denied tool call — an
  `is_error: true` result explaining the user declined (as in the example
  above) lets the model react sensibly, instead of the loop simply
  hanging with no way to continue.

## How this connects

Lessons 02–05 gave you the loop, tool design, memory vocabulary, and MCP;
this lesson added two real ways to structure work across more than one
"decision-maker" — either another agent, or a real person. Lesson 07
steps back and surveys the frameworks (LangGraph, CrewAI, the OpenAI
Agents SDK) that formalize these exact patterns — coordinator/worker,
handoff, human approval gates — as first-class, built-in primitives,
which you're now positioned to evaluate honestly rather than take on
faith. Lesson 08 covers the guardrail judgment calls this lesson only
touched on (which actions genuinely need a human gate at all).

## Quick self-check

1. What's the concrete difference between coordinator/worker and handoff
   — not just "there are two agents," but what actually happens to the
   conversation in each?
2. From a coordinator's own loop's point of view, what *is* a worker
   agent, mechanically? (Hint: think about what kind of thing
   `coordinator_delegate_tool` looks like from inside the coordinator's
   own tool list.)
3. Why does this lesson argue that gating *every* tool call behind human
   approval is actually worse than gating none at all, in the long run?
4. In the human-in-the-loop example above, what does the agent's own loop
   actually receive when a human denies an action — and why does it need
   to receive *something*, rather than the loop just stopping silently?
5. Give one concrete, realistic scenario (not from this lesson) where
   coordinator/worker would genuinely help, and one where it would just
   add overhead for no benefit.
