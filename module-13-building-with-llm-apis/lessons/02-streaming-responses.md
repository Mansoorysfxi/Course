# Lesson 02 — Streaming Responses

**Verified against (August 2026), via live fetch of official Anthropic
documentation and the `anthropic` `0.121.0` SDK reference on August 9,
2026:**

| Fact | Verified value | Source |
|---|---|---|
| Recommended streaming helper (Python) | `client.messages.stream(...)` used as a context manager, exposing `stream.text_stream` and `stream.get_final_message()` | Anthropic's own Python SDK streaming reference |
| Async equivalent | `async with async_client.messages.stream(...) as stream: async for text in stream.text_stream: ...`, then `await stream.get_final_message()` | Same |
| Raw wire format | Server-Sent Events (SSE) — `event: <type>` / `data: <json>` pairs, terminated by a blank line | Anthropic's own Messages API streaming reference |
| Six real event types on the raw stream | `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop` | Same |

## What you'll learn

- What "streaming" actually means at the wire level, and why it exists at
  all — what problem it solves that a plain, non-streamed request doesn't.
- How to use the Python SDK's `messages.stream(...)` helper to print
  Claude's response as it's generated, both synchronously and (for
  QuestLog's own backend, later) asynchronously.
- What Server-Sent Events (SSE) are, in enough depth to understand what's
  actually flowing over the wire underneath the SDK's convenient helper.
- When streaming genuinely matters and when it's just extra complexity for
  no real benefit.

## Why this matters

Every chat product you've ever used that shows an AI's answer appearing
word by word — Claude's own web interface included — is streaming.
Without it, a long response means staring at a blank screen for however
many seconds the *entire* answer takes to generate, then having it all
appear at once. QuestLog's own AI assistant feature (Lessons 07-08) uses
streaming for exactly this reason: a quest breakdown that takes two or
three seconds to fully generate should start showing something on screen
almost immediately, not leave the player staring at a spinner.

## Prerequisites

- **Lesson 01 in full** — this lesson's every example is Lesson 01's
  exact same `client.messages.create(...)` call, with streaming added on
  top. If the base request shape isn't solid yet, streaming will just
  look like extra syntax with no clear reason for it.
- **Module 01's async/await lesson** — this lesson's async example uses
  `async def`, `await`, and `async for`; if that event-loop material
  feels shaky, this is a good moment to revisit it.

## The concept, explained simply

Think of the difference between streaming and a plain request the way
you'd think about the difference between a dialogue system that prints a
line of NPC speech **character by character** as it's decided, versus one
that computes the entire line first and only then displays it all at
once. Both eventually show the player the exact same final sentence — the
*content* isn't different. What's different is when the player starts
seeing *something*. A non-streamed API call is the "compute everything,
then show it all" version: your code sends one request and gets back one
complete response, however long that took. A streamed call is the
"reveal it as it's decided" version: the exact same underlying generation
process (Claude producing one token at a time, Module 12 Lesson 05's own
attention/next-token framing) is simply *shown to you* as it happens,
piece by piece, instead of being buffered up and delivered all at once at
the end.

## The details

### The synchronous streaming helper

Here's Lesson 01's basic call, turned into a streamed one. Create
`stream_basic.py`:

```python
# stream_basic.py
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-haiku-4-5",
    max_tokens=200,
    system="You are QuestLog's assistant.",
    messages=[
        {"role": "user", "content": "Describe a haunted forest quest in three sentences."},
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()

    final_message = stream.get_final_message()
    print(f"\nStop reason: {final_message.stop_reason}")
    print(f"Output tokens: {final_message.usage.output_tokens}")
```

Line by line, comparing against Lesson 01's non-streamed version:

- `client.messages.stream(...)` takes the **exact same parameters** as
  `client.messages.create(...)` — `model`, `max_tokens`, `system`,
  `messages`. Nothing about the request itself changes; only how you
  *consume the response* changes.
- `with ... as stream:` — a context manager (Module 01's own context-manager
  lesson, applied for real). Opening the connection and cleanly closing
  it when you're done are both handled for you; you never manage a raw
  socket or connection object yourself.
- `for text in stream.text_stream:` — the actual mechanism. `text_stream`
  is an iterator that yields small pieces of text (`text_delta`s, in the
  raw SSE vocabulary below) as Claude generates them. `print(text, end="",
  flush=True)` prints each piece immediately, with no trailing newline
  and `flush=True` forcing your terminal to display it right away instead
  of buffering — this is the actual "appears character by character"
  effect, not a simulated typing animation layered on top afterward.
- `stream.get_final_message()` — called **after** the loop finishes
  consuming every piece of text. Returns the exact same kind of `Message`
  object `client.messages.create(...)` would have returned in one shot —
  same `.content`, same `.stop_reason`, same `.usage` — accumulated from
  every piece the stream delivered. This is how you get the *complete*
  response object once streaming is done, for anything (token counts,
  stop reason, later lessons' tool-use blocks) beyond just the raw text.

Run it:

```bash
python stream_basic.py
```

*A response along these lines* (this describes what you'd genuinely see —
text appearing progressively on your own terminal, not all at once — a
detail no static page can fully reproduce; a live call was made while
writing this lesson and the following is representative, not a literal
transcript of a rerunnable exact output, per this module's own honest
framing):

```
The Hollowpine Woods have swallowed three search parties whole, and
locals say the trees themselves remember every name spoken beneath them.
A retired ranger offers to guide you as far as the tree line, no farther.
Whatever answers your torchlight back from the dark isn't looking for
rescue.

Stop reason: end_turn
Output tokens: 52
```

The genuinely observable difference, if you run this yourself, is
**when** each sentence appears on your screen relative to when you ran
the script — noticeably progressive, rather than one single pause
followed by the whole paragraph at once.

**Try it yourself:** Remove `flush=True` from the `print(...)` call and
run it again. On many terminals the output will still *look* streamed
because of how often Python's own buffer flushes anyway — but the
correct, dependable behavior only comes from `flush=True` explicitly.
This is worth seeing once so you don't cargo-cult it without knowing why
it's there.

### The async version — what QuestLog's backend actually uses

FastAPI routes are `async def` functions (Module 05). Blocking, synchronous
network calls inside an async route freeze the entire event loop — every
other request your server is handling — for as long as that call takes
(Module 01's own event-loop lesson, made concrete here). This is exactly
why QuestLog's real backend (Lesson 07) uses `anthropic.AsyncAnthropic`,
not `anthropic.Anthropic`, and why this lesson teaches the async shape
explicitly rather than leaving it as "an exercise for later":

```python
# stream_async.py
import asyncio
import anthropic


async def main() -> None:
    client = anthropic.AsyncAnthropic()

    async with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": "Name three QuestLog quest lines."}],
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        print()

        final_message = await stream.get_final_message()
        print(f"Stop reason: {final_message.stop_reason}")


asyncio.run(main())
```

Exactly the same shape as the synchronous version, with three differences,
each one Module 01's async vocabulary already covers: `anthropic.AsyncAnthropic`
instead of `anthropic.Anthropic`; `async with` instead of plain `with`;
`async for` instead of plain `for`; and `await stream.get_final_message()`
instead of a plain call — the async client's version of that method is
itself a coroutine you must `await`, unlike the synchronous client's.

### What's actually flowing over the wire: raw SSE

The SDK's `stream.text_stream` helper hides a real wire format underneath
it called **Server-Sent Events (SSE)** — a plain-text HTTP response
format (not WebSockets, not a special protocol) where the server sends a
sequence of small, individually-labeled messages down one long-lived HTTP
connection, and the client reads them as they arrive. Each event looks
like this:

```
event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"The"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" Hollowpine"}}
```

Two lines per event (`event: <type>`, then `data: <json>`), and a blank
line marking the end of each one. A real stream includes six kinds of
these events in sequence: `message_start` (once, at the very beginning,
carrying metadata like the model and message id), `content_block_start`
(a new block — text, or in later lessons, a tool call — is beginning),
`content_block_delta` (one more small piece of that block, repeated many
times — this is the vast majority of events in any real stream), `content_block_stop`
(that block is complete), `message_delta` (message-level info, including
the final `stop_reason` and usage), and `message_stop` (the whole response
is done).

**Why this matters even though you'll rarely touch raw SSE directly in
Python:** QuestLog's own backend (Lesson 07) re-emits its *own* SSE
events to the React frontend — a different, application-specific set of
event names (`token`, `tool_call`, `result`, `error`), but the exact same
wire format shown above. Understanding that SSE is just "labeled text
messages over one open HTTP connection, one event per line-pair" is what
makes that later code make sense, instead of feeling like unexplained
magic borrowed from a networking library.

## Common mistakes & gotchas

- **Trying to use `response.content[0].text` on a streamed call before
  the stream finishes.** While the `for text in stream.text_stream:`
  loop is still running, there is no single, complete `response` object
  yet — only individual pieces. `stream.get_final_message()`, called
  *after* the loop, is what gives you the assembled whole.
- **Forgetting `flush=True`** and being confused about why output doesn't
  visibly stream on some terminals or when output is redirected to a
  file — see this lesson's own "Try it yourself" above.
- **Mixing the sync and async clients.** `anthropic.Anthropic()`'s stream
  object uses plain `for`/`with`; `anthropic.AsyncAnthropic()`'s uses
  `async for`/`async with` and an `await`ed `get_final_message()`. Using
  the wrong pairing raises a `TypeError` about a coroutine or a
  non-iterable object, which is confusing until you recognize the
  sync/async mismatch it's actually pointing at.
- **Assuming streaming makes a request cheaper or faster to *fully*
  complete.** It doesn't — the same total number of tokens still has to
  be generated, at the same speed, and you're billed the same either way
  (Lesson 01's `usage` fields are identical whether or not you streamed).
  Streaming changes **when you see partial results**, not how much total
  work happens or what it costs.
- **Streaming everything by default, even when it adds nothing.** A
  short classification response ("Easy," "Medium," or "Hard" — Module 12,
  Lesson 07's few-shot example) finishes so fast that streaming buys you
  nothing but extra code complexity. Reach for streaming specifically
  when a response is long enough, or latency-sensitive enough, that
  showing partial progress genuinely improves the experience — exactly
  the judgment call QuestLog's own capstone makes in Lesson 07.

## How this connects

Streaming is a way of *consuming* a response, not a different kind of
response — every later lesson's request (structured output in Lesson 03,
tool use in Lesson 04) can be streamed using exactly this lesson's same
`.stream()` pattern, and QuestLog's capstone (Lesson 07) does exactly
that: the same manual tool-use loop Lesson 04 teaches, with every single
turn opened via `.stream()` instead of `.create()`. Lesson 03 is next,
and it's where this lesson's clean story gets a genuine wrinkle worth
understanding honestly: structured output guarantees the *complete*
response is valid JSON, but a JSON string isn't valid JSON until its very
last character arrives — so what does "stream a structured response"
even mean? Lesson 03 answers that directly, and Lesson 07 applies the
answer for real.

## Quick self-check

1. What problem does streaming actually solve — is it about total request
   time, or about something else? Be specific.
2. Why does `stream.get_final_message()` need to be called *after* the
   `for text in stream.text_stream:` loop finishes, not before or during?
3. Name the six real SSE event types a Messages API stream sends, in
   order, and say in one sentence what each one means.
4. Why does QuestLog's own FastAPI backend (Lesson 07) need
   `anthropic.AsyncAnthropic` instead of the plain, synchronous
   `anthropic.Anthropic` client?
5. Give one example of a request where streaming would add real, felt
   value, and one where it would add none. What's the distinguishing
   factor between the two?
