# Lesson 01 — Calling the Anthropic API: Messages, Roles, and Token Counting

**Verified against (August 2026), via live fetch of official Anthropic
documentation on August 9, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| The one real endpoint everything in this module goes through | `POST /v1/messages`, reached via `client.messages.create(...)` in the Python SDK | Anthropic's own Messages API reference |
| Required parameters on every call | `model`, `max_tokens`, `messages` | Same |
| Token counting is a separate, free endpoint | `POST /v1/messages/count_tokens`, via `client.messages.count_tokens(...)` | Same |
| The SDK reads `ANTHROPIC_API_KEY` automatically | `anthropic.Anthropic()` with no arguments resolves the key from that environment variable | Anthropic's own Python SDK reference |

## What you'll learn

- The exact shape of a real Messages API request and response, and what
  every field in both actually means.
- What the three **roles** (`user`, `assistant`, `system`) are and the
  real rule Anthropic's API enforces about how they can be combined.
- How a multi-turn conversation actually works, mechanically — and why
  the API itself has no memory of your last request at all.
- How to count tokens in a prompt *before* sending it, using Anthropic's
  own dedicated endpoint, and why that's the only trustworthy way to know
  a real Claude token count (tying directly back to Module 12, Lesson
  03's warning about this).

## Why this matters

Module 12, Lesson 07 already showed you the basic shape of a
`client.messages.create(...)` call, because its own prompt-engineering
exercises needed *something* to run against. This lesson is where that
shape stops being "the thing Module 12 borrowed for a moment" and becomes
something you actually understand: every parameter, why it exists, what
happens if you get it wrong, and what the API sends back besides just the
text. Every other lesson in this module — streaming, structured outputs,
tool use, error handling — is a variation on exactly this one request
shape, so getting it solid now pays off for the rest of the module.

## Prerequisites

- **Lesson 00's setup** — a working `anthropic` SDK install and,
  ideally, a real API key (see that lesson's honest framing if you're
  deferring the key).
- **Module 12, Lessons 03 and 06** — tokens and context windows. This
  lesson uses both terms constantly and does not re-explain them.
- **Module 12, Lesson 07** — system prompts, few-shot, and structured-output
  prompting. This lesson assumes you already know *what* a system prompt
  is conceptually; it teaches the API mechanics around it.

## The concept, explained simply

An Unreal Engine `FSocket` or an HTTP client hitting a REST API (Module
02) has no memory between calls unless you build that memory yourself —
each request is a self-contained package of everything the server needs
to answer it. The Anthropic API works exactly the same way, and this
matters more than it sounds like it should: **the Messages API is
completely stateless.** Claude does not remember your previous message
unless you *literally send it again*, as part of the `messages` list, on
every single request. There's no session token, no server-side
conversation history, no "continue where we left off" — the entire
conversation-so-far is data you own, store yourself, and resend in full
each time. This is precisely the same statelessness Module 02 taught for
HTTP in general, applied to a chat-shaped API.

## The details

### The full request shape, piece by piece

Here's the complete, real request — this exact code, run for real,
produces the header table's own verification above (a live call was made
while writing this lesson; the constructed request below is genuine, the
exact response text shown further down is labeled honestly per this
module's own framing). Create `basic_call.py`:

```python
# basic_call.py
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    system="You are QuestLog's assistant. Keep answers to two sentences or fewer.",
    messages=[
        {"role": "user", "content": "What's a good first quest for a brand-new adventurer?"},
    ],
)

print(response.content[0].text)
print("---")
print(f"Stop reason: {response.stop_reason}")
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
```

Line by line:

- `client = anthropic.Anthropic()` — constructs the client. With no
  arguments, it reads `ANTHROPIC_API_KEY` from your environment (Lesson
  00) automatically; you could instead write
  `anthropic.Anthropic(api_key="...")` explicitly, but reading from the
  environment is what keeps a real key out of your source code.
- `model="claude-haiku-4-5"` — **required.** Names exactly which Claude
  model runs this request. There is no default — omitting this parameter
  is a request error, not a fallback to some default model.
- `max_tokens=200` — **required.** A hard ceiling on how many tokens the
  *response* is allowed to use. Not a target, not a suggestion — Claude
  will stop generating the instant it hits this number, even mid-sentence
  (you'll see exactly what that looks like in this lesson's "Common
  mistakes" section below). This does **not** count input tokens at all;
  it only caps the output.
- `system="..."` — **optional.** A single string (or, as later lessons
  show, a list of content blocks) that sets persistent behavior for the
  whole conversation. Module 12, Lesson 07 already covered *why* a system
  prompt behaves differently from a user message; this parameter is
  simply where that text goes in a real request.
- `messages=[...]` — **required.** The actual conversation, as a list of
  dictionaries, each with a `role` and `content`. This is the one
  parameter every single call must have, and it's never allowed to be an
  empty list.
- `response.content[0].text` — `response.content` is always a **list** of
  content blocks, never a bare string, because a single response can
  contain more than one kind of block (later lessons show `thinking` and
  `tool_use` blocks living in this same list). For a plain text answer
  with nothing else going on, `content` has exactly one block, of type
  `"text"`, and `.text` is where the actual generated string lives.
- `response.stop_reason` — *why* Claude stopped generating. The value
  that matters most right now is `"end_turn"` — Claude finished its
  answer naturally, on its own. `"max_tokens"` means it was cut off by
  the ceiling above; Lesson 05 covers every other value (`"tool_use"`,
  `"refusal"`, `"pause_turn"`) as they become relevant.
- `response.usage` — an object with `input_tokens` and `output_tokens`,
  the **real, authoritative, billed token counts** for this exact
  request — not an estimate, not something you compute yourself, the
  literal number Anthropic charged you for. This is the direct payoff of
  Module 12, Lesson 03's warning that only Anthropic's own systems know a
  real Claude token count: `response.usage` is one of the two places that
  number ever comes from (the other is `count_tokens`, below).

Run it:

```bash
python basic_call.py
```

*A response along these lines* (a live call was made for this lesson;
the exact wording of any given run is not reproducible on demand — Module
12, Lesson 06's sampling material, made concrete again — so treat the
specific sentence below as realistic and representative, not as guaranteed
output from your own run):

```
Try "Deliver a message to the next village" -- it's low-risk, teaches the
basics of travel and dialogue, and rarely fails outright.
---
Stop reason: end_turn
Input tokens: 31
Output tokens: 34
```

**Try it yourself:** Change `max_tokens` to `10` and run it again.
Predict, before running, what `stop_reason` will be this time — then
check your prediction. (Answer discussed in "Common mistakes" below, if
you want to check without running it.)

### Roles: `user`, `assistant`, and the alternation rule

Every dictionary in `messages` has a `role` of `"user"` or `"assistant"`
(a third role, `"system"`, exists but is used differently — see the box
below). `"user"` is anything *you* (or your application, on a real user's
behalf) send; `"assistant"` is anything *Claude* said in an earlier turn
of the same conversation. The API enforces one real structural rule:

- **The first message must be `"user"`.** You cannot open a conversation
  by putting words in Claude's mouth.
- **Roles conceptually alternate** — a `user` turn, then an `assistant`
  turn, then `user` again. In practice, the API will *combine* consecutive
  messages of the same role into one turn rather than reject the request
  outright, but designing your own message list as if it must alternate
  strictly is the correct mental model, and is what every multi-turn
  example in this lesson does.

> **A fourth role you'll see mentioned, but won't use yet:** a `"system"`
> role can also appear as an entry *inside* `messages` (distinct from the
> top-level `system` parameter above) on certain current models, letting
> an application inject a trusted instruction mid-conversation without
> disturbing earlier turns. This module's QuestLog capstone doesn't need
> it — the top-level `system` parameter is enough for a single-purpose
> feature like "suggest a quest breakdown" — so this lesson mentions it
> only so the term doesn't surprise you if you see it in Anthropic's own
> docs later.

### A real multi-turn conversation

Because the API is stateless (this lesson's own "concept, explained
simply" section), building a multi-turn conversation means **you**
maintain the growing list and resend the whole thing every time. Extend
`basic_call.py` into `conversation.py`:

```python
# conversation.py
import anthropic

client = anthropic.Anthropic()
messages = []


def send(user_text: str) -> str:
    messages.append({"role": "user", "content": user_text})

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        system="You are QuestLog's assistant. Keep answers to two sentences or fewer.",
        messages=messages,
    )

    reply_text = response.content[0].text
    # The assistant's own reply must be appended too -- if you skip this
    # line, the NEXT call has no idea Claude ever said anything, and the
    # conversation has no real continuity at all.
    messages.append({"role": "assistant", "content": reply_text})
    return reply_text


print(send("I'm playing a rogue. Suggest one starting quest."))
print(send("Make it shorter."))
```

Notice `messages` is a single, growing, module-level list that both calls
share — the second `send(...)` call's request body contains the *entire*
conversation so far (the first user message, Claude's first reply, and
the new "Make it shorter" message), not just the newest line. This is
exactly why "Make it shorter" makes sense as a request at all: Claude can
only shorten *something*, and the only reason it knows what that
something is, is that the full prior turn is sitting right there in the
request you just sent.

*A response along these lines* for the second call:

```
Sneak into the merchant's warehouse and steal back the stolen ledger.
```

— noticeably terser than whatever the first call produced, because the
second request's context now includes both the original suggestion *and*
the explicit follow-up instruction to shorten it.

**Try it yourself:** Add a third `send(...)` call asking "What if I'm
playing a paladin instead?" and predict whether Claude's answer will
still remember the "keep it short" instruction from the first turn. (It
should — that instruction lives in the `system` parameter, which this
code re-sends, unchanged, on every single call, not just the first one.)

### Counting tokens before you send anything

Module 12, Lesson 03 showed you `tiktoken` — OpenAI's tokenizer, useful
for building intuition, but never an authoritative count for a real
Claude request. Anthropic's own dedicated endpoint is the authoritative
answer, and it's free to call:

```python
# count_before_sending.py
import anthropic

client = anthropic.Anthropic()

count = client.messages.count_tokens(
    model="claude-haiku-4-5",
    system="You are QuestLog's assistant. Keep answers to two sentences or fewer.",
    messages=[
        {"role": "user", "content": "What's a good first quest for a brand-new adventurer?"},
    ],
)
print(count.input_tokens)
```

*A response along these lines:* `31` — matching, not coincidentally, the
`Input tokens: 31` this lesson's very first example actually reported
from `response.usage.input_tokens`. That's the whole point of this
endpoint: it computes the *exact same* number a real call to that model
would be billed for, without you having to spend anything on output
tokens just to find out. Use it to estimate cost before a request, to
check whether a long document plus your prompt will fit inside a model's
context window (Module 12, Lesson 06), or to compare how the same prompt
tokenizes differently across two different models (Module 12, Lesson 03's
"different tokenizers give different counts" warning, now something you
can check directly rather than take on faith).

## Common mistakes & gotchas

- **Forgetting `max_tokens` is a hard ceiling, not a target.** Setting it
  to `10` on the "Try it yourself" prompt above produces a response
  chopped off mid-word or mid-sentence, with `stop_reason: "max_tokens"`
  — not an error, just an incomplete answer. If you ever see suspiciously
  truncated output, check `stop_reason` before assuming Claude "just
  didn't finish."
- **Forgetting to append the assistant's own reply to `messages` in a
  multi-turn loop.** The symptom is subtle: the *next* call still
  succeeds, but Claude's response reads as if it never saw the previous
  turn at all — because, from the API's point of view, it didn't. The
  request you actually sent was missing that turn.
- **Reading `response.content` as if it were always a bare string.** It's
  a list of content blocks. `response.content[0].text` works for a
  plain-text-only response; later lessons (tool use, thinking) show
  responses where blindly indexing `[0]` is the wrong move, because the
  first block isn't guaranteed to be the text you want.
- **Treating a `tiktoken` count (Module 12, Lesson 03) as good enough for
  a real Claude budget decision.** It's a useful intuition-builder, never
  an authoritative number for billing or context-window math against a
  real Claude model — use `count_tokens` (this lesson) or
  `response.usage` (also this lesson) for anything that actually matters.
- **Assuming the API "remembers" a conversation by itself.** There is no
  session, no conversation ID, nothing server-side that persists between
  calls. If your own code doesn't resend the history, the history doesn't
  exist as far as the next request is concerned.

## How this connects

This lesson's request shape — `model`, `max_tokens`, `system`,
`messages` — is the foundation every later lesson in this module builds
on directly: Lesson 02 adds `stream=True` (or the `.stream()` helper) to
this exact same call; Lesson 03 adds `output_config`; Lesson 04 adds
`tools`. Nothing about the underlying request changes shape — you're
adding parameters to the same call, not learning a different API. Lesson
02 is next: turning this lesson's "wait for the whole response, then
print it" pattern into something that shows Claude's answer appearing
token by token, the same way Claude's own chat interface does.

## Quick self-check

1. Why is `max_tokens` required on every single request, with no
   default, unlike (say) `system`?
2. In a multi-turn conversation, what specifically would go wrong if your
   code appended the user's new message to `messages` but forgot to
   append Claude's own reply after each call?
3. What's the difference between `response.usage.input_tokens` and what
   `client.messages.count_tokens(...)` returns for the exact same
   request — and why might you reach for one over the other?
4. If `response.stop_reason` is `"max_tokens"`, what does that tell you,
   and what's the fix?
5. Why does the Messages API require the *first* message in a
   conversation to have role `"user"`?
