# Lesson 05 — Error Handling, Retries, and Cost Management

**Verified against (August 2026), via live fetch of official Anthropic
documentation on August 9, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| SDK auto-retries these automatically | Connection errors, HTTP 408, 409, 429, and any 5xx, with exponential backoff | Anthropic's own Python SDK reference |
| Default retry count | `max_retries=2` (configurable per-client or per-call) | Same |
| Typed exception hierarchy | `anthropic.APIError` (base) with specific subclasses per status code (`RateLimitError`, `AuthenticationError`, `NotFoundError`, `APIConnectionError`, etc.) | Same |
| `refusal` is not an exception | It's a normal, successful HTTP response with `stop_reason: "refusal"` and a `stop_details` object | Anthropic's own Messages API reference |
| Rate-limit response includes | A `retry-after` header telling you how many seconds to wait | Same |
| Claude Haiku 4.5 pricing (this module's model) | $1.00 / million input tokens, $5.00 / million output tokens | Verified again in Lesson 00 |

## What you'll learn

- Which failures the SDK already retries for you automatically, and why
  those specific ones are the retryable ones.
- The difference between an exception the SDK *raises* (a real HTTP
  error) and a `refusal`, which is not an error at all from the API's
  point of view.
- How to write your own error-handling code around a Messages API call,
  using the SDK's typed exception classes instead of guessing from a raw
  string message.
- How to actually reason about, and control, what a real AI feature
  costs — beyond just "check the pricing page once."

## Why this matters

Every previous lesson in this module assumed every call succeeded. Real
production code cannot make that assumption: networks drop, servers get
overloaded, accounts hit rate limits, and — a failure mode unique to LLM
APIs — the model itself can decline to answer for safety reasons, which
looks nothing like a normal error. QuestLog's real `/suggest-breakdown`
endpoint (Lesson 07) has to handle a refusal, a truncated response, and a
missing API key gracefully, returning something honest to the player
instead of a confusing crash — this lesson is where you learn exactly how.

## Prerequisites

- **Lessons 01-04 in full** — this lesson is about what can go wrong with
  the exact request shapes those lessons already taught, not a new kind
  of request.
- **Module 08's testing lesson on mocking** — this lesson's exercise
  simulates failures without needing to actually trigger a real rate
  limit, using the same kind of mock/fake objects Module 08 taught for
  testing.

## The concept, explained simply

Think of the difference between an HTTP error and a refusal the way
you'd think about the difference between a multiplayer server rejecting
your connection outright (wrong port, server down, connection timed out —
you never even got to talk to it) versus a server that accepted your
connection just fine but a specific game-rule check inside it decided
your requested action isn't allowed right now (you tried to enter a
zone you're not high-enough level for). Both are "the thing you wanted
didn't happen," but they're fundamentally different situations requiring
different handling: the first is a connectivity/infrastructure problem
you'd typically retry; the second is a legitimate, informed "no" from a
system that's working exactly as designed, and retrying the identical
request won't change the outcome. The Anthropic API has both kinds of
"didn't work," and treating them the same way is a real, common bug.

## The details

### Category 1: real HTTP errors, and what the SDK already does for you

A genuine failure — the network dropped, your API key is invalid, you
exceeded a rate limit — raises a Python exception, not a normal response
object. The SDK defines a specific exception class per situation, all
inheriting from `anthropic.APIError`:

```python
import anthropic

client = anthropic.Anthropic()

try:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello"}],
    )
except anthropic.AuthenticationError:
    print("Your API key is missing or invalid.")
except anthropic.RateLimitError as exc:
    retry_after = exc.response.headers.get("retry-after", "unknown")
    print(f"Rate limited. Retry after {retry_after} seconds.")
except anthropic.APIConnectionError:
    print("Couldn't reach the API at all -- check your network.")
except anthropic.APIStatusError as exc:
    print(f"API error ({exc.status_code}): {exc.message}")
```

Order matters: catch the **most specific** exception classes first,
falling back to broader ones — exactly the same "catch the specific
exception before the general one" discipline Module 01's own exception
lesson taught, applied here to a real library's exception hierarchy
instead of a hand-rolled one. `AuthenticationError` (bad or missing key),
`RateLimitError` (too many requests too fast — see `retry_after` above),
and `APIConnectionError` (a network-level failure, before any HTTP
response even came back) are the three you'll realistically hit while
developing; `APIStatusError` is the catch-all base for any other non-2xx
response.

**The SDK already retries some of these for you, automatically, before
any exception ever reaches your code.** Connection errors, HTTP 408, 409,
429 (rate limited), and any 5xx (server-side failure) are retried up to
`max_retries` times (default `2`) with exponential backoff — meaning the
wait between attempts grows each time, rather than hammering an already
struggling server at a fixed interval. This is why the `try`/`except`
block above only actually triggers for a *persistent* failure — one that
outlasted the SDK's own automatic retry attempts, not a single transient
blip.

```python
# Tune it per-client, or per-call:
client = anthropic.Anthropic(max_retries=5)
# or:
client.with_options(max_retries=0).messages.create(...)  # disable retries for this one call
```

### Category 2: a refusal — not an exception at all

A refusal is a **normal, successful HTTP response.** No exception is
raised; `response.stop_reason` is simply `"refusal"`, and
`response.stop_details` carries structured information about why.

```python
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    messages=[{"role": "user", "content": "..."}],
)

if response.stop_reason == "refusal":
    print("Claude declined to answer this request.")
    if response.stop_details:
        print(f"Category: {response.stop_details.category}")
else:
    print(response.content[0].text)
```

**Always check `stop_reason` before indexing into `response.content`.**
Code that does `response.content[0].text` unconditionally will raise an
`IndexError` on a refusal, since a declined request can come back with an
empty `content` list. This is exactly the check QuestLog's real
`stream_quest_breakdown` function (Lesson 07) makes before ever touching
the accumulated text.

### Category 3: a truncated answer — `stop_reason: "max_tokens"`

Not an error, and not a refusal — the model was still generating a
perfectly normal answer when it hit the `max_tokens` ceiling (Lesson 01)
and had to stop. The fix is almost always to raise `max_tokens`, or (for
a long answer) switch to streaming (Lesson 02) so the response doesn't
need to fit under a smaller non-streaming timeout in the first place.

```python
if response.stop_reason == "max_tokens":
    print("The response was cut off. Consider raising max_tokens.")
```

**Try it yourself:** Set `max_tokens=10` on a request whose answer clearly
needs more than that (e.g. Lesson 04's quest-line comparison prompt), and
add both checks above to the same script. Predict, before running it,
which branch fires — then confirm your prediction against the real
`stop_reason` you get back.

### Writing your own retry loop (when you need more than the default)

The SDK's built-in retries cover the common case well. Occasionally you
want custom behavior — a different backoff schedule, or logging every
retry attempt. Here's a real, correct pattern, distinguishing retryable
failures from ones that will never succeed no matter how many times you
try:

```python
import time
import random
import anthropic


def call_with_retry(client: anthropic.Anthropic, max_attempts: int = 4, **kwargs):
    for attempt in range(max_attempts):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            pass  # retryable -- fall through to the backoff below
        except anthropic.APIStatusError as exc:
            if exc.status_code < 500:
                raise  # a 4xx (other than 429) will never succeed on retry
            # a 5xx is worth retrying

        if attempt == max_attempts - 1:
            raise RuntimeError(f"Gave up after {max_attempts} attempts.")

        delay = min(2**attempt + random.uniform(0, 1), 30)
        time.sleep(delay)
```

**The one rule this code enforces that matters most:** a `400 Bad
Request` (a malformed request body — nothing about retrying will ever fix
that) is re-raised immediately, never retried. Only genuinely transient
failures (429, 5xx) get another attempt. Retrying a request that's
structurally wrong just wastes time and, in a loop like Lesson 04's tool
round-trip, real money on repeated, doomed calls.

### Cost management: reasoning about what a real feature actually costs

Three real levers, all of which QuestLog's own capstone (Lesson 07)
applies:

1. **Pick the cheapest model that does the job well enough.** This
   module's exercises and QuestLog's own quest-breakdown feature both use
   Claude Haiku 4.5 ($1.00/$5.00 per million tokens — this lesson's
   header table) specifically because suggesting 2-4 sub-quest titles
   doesn't need a larger, more expensive model's deeper reasoning.
   Reaching for the most capable (and most expensive) model by default,
   for every feature regardless of how hard the actual task is, is a real
   and common cost mistake.
2. **Size `max_tokens` to what the task actually needs**, not a
   generously large round number "just in case." A feature that only ever
   needs a few hundred output tokens gains nothing from `max_tokens=4096`
   except a slightly higher worst-case cost if something ever does run
   long — but it does mean a genuinely runaway response burns more real
   money before hitting the ceiling.
3. **Know your real cost per request before you ship it**, using
   `response.usage` (Lesson 01) or `count_tokens` (also Lesson 01) rather
   than guessing. Here's a real, worked calculation for QuestLog's own
   feature: a single `/suggest-breakdown` call's tool-definition and
   schema overhead alone adds roughly 500-600 input tokens on Claude
   Haiku 4.5 (Anthropic's own published, per-model tool-use token-overhead
   table), on top of the actual quest title/description and system
   prompt — call it roughly 700-900 input tokens and 100-250 output
   tokens per turn, times up to two turns if the tool round-trip happens.
   At this lesson's verified rates, that's well under a tenth of a cent
   per full feature invocation — a number worth actually calculating for
   any real feature you ship, not assuming.

## Common mistakes & gotchas

- **Catching `Exception` broadly instead of the SDK's specific classes.**
  You lose the ability to tell "this will never succeed, don't retry"
  (a 4xx) apart from "this is worth trying again" (429, 5xx) — exactly
  the distinction this lesson's retry loop depends on.
- **Retrying a 400 Bad Request.** A malformed request body, an invalid
  parameter, an unsupported model name — none of these will ever succeed
  no matter how many times you resend the identical request. Fix the
  request; don't retry it.
- **Treating a refusal as a bug in your code.** It's the model correctly
  declining a request it judged inappropriate to answer — check
  `stop_reason` and handle it as a real, expected outcome, the same way
  QuestLog's backend does (Lesson 07), not as something to debug.
- **Indexing into `response.content[0]` before checking `stop_reason`.**
  This lesson's own refusal example shows exactly why: an empty
  `content` list on a refusal turns an unconditional `[0]` into a crash.
- **Assuming the SDK's default retry settings are always right for your
  use case.** They're a sensible default, not a universal one — a
  latency-sensitive, user-facing request might want `max_retries=0` and
  its own, faster failure handling; a background batch job might want
  more retries and a longer backoff. Know what you're getting by default,
  and change it deliberately when the default doesn't fit.
- **Never actually calculating a real cost number for a shipped
  feature.** "It's an LLM call, it's probably cheap" is not the same as
  knowing the actual number, the way this lesson's worked example does.

## How this connects

Every failure mode this lesson covers — a rate limit, a refusal, a
truncation — is something QuestLog's real `/suggest-breakdown` endpoint
(Lesson 07) handles explicitly and honestly, turning each one into a
clear, specific message the frontend (Lesson 08) can show the player,
rather than a generic crash. Lesson 06 is next, and it asks a different
kind of question about the same feature: even when every call
*technically* succeeds — no error, no refusal, no truncation — how do
you know the *suggestions themselves* are actually any good?

## Quick self-check

1. What's the real, structural difference between an exception the SDK
   raises and a `refusal` — why isn't a refusal just another kind of
   exception?
2. Which specific HTTP situations does the SDK already retry
   automatically, and roughly how many times, by default?
3. Why should a `400 Bad Request` never be retried, while a `429` or a
   `5xx` usually should be?
4. Name the three concrete levers this lesson names for controlling what
   a real AI feature costs, and give one sentence on each.
5. What check must run before `response.content[0]` is ever safely
   indexed, and what real failure mode is it protecting against?
