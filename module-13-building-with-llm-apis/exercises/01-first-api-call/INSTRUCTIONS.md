# Exercise 01 — Your First Real API Call

## What you'll build

A small script, `hello_questlog.py`, that sends one real request to
Claude and prints the answer along with real, observed token usage. This
exercise is intentionally almost impossible to get wrong if you've read
Lesson 01 — its whole purpose is to prove your setup (Lesson 00) actually
works end to end before this module asks anything harder of you.

## Concepts this exercise uses (all taught in Lesson 01)

- Constructing an `anthropic.Anthropic()` client
- The required `model`, `max_tokens`, and `messages` parameters
- The `system` parameter
- Reading `response.content[0].text`, `response.stop_reason`, and
  `response.usage`

## Requirements

Write `hello_questlog.py` that:

1. Creates a client with `anthropic.Anthropic()` (no hardcoded key).
2. Sends **one** request to `claude-haiku-4-5` with:
   - A `system` prompt establishing that Claude is "QuestLog's onboarding
     assistant" and should keep every answer to two sentences or fewer.
   - A single user message asking: `"I'm new to QuestLog. What's a quest
     line, and how is it different from a single quest?"`
   - `max_tokens=150`.
3. Prints:
   - The response text.
   - The `stop_reason`.
   - Both `input_tokens` and `output_tokens` from `response.usage`.
4. Runs a **second** request with a follow-up user message — `"Give me
   one example."` — as a genuine multi-turn conversation (append the
   first `user` message and Claude's own reply to a shared `messages`
   list before sending the second request, exactly as Lesson 01's
   `conversation.py` example does), and prints that second response's
   text too.

## Acceptance criteria

- [ ] The script runs with no exceptions when a valid `ANTHROPIC_API_KEY`
      is set.
- [ ] The first response's `stop_reason` is `"end_turn"` (not
      `"max_tokens"` — if you see `"max_tokens"`, your prompt or
      `max_tokens` value needs adjusting).
- [ ] The second response is clearly a continuation of the same
      conversation (it should make sense as an answer to "give me one
      example," which only makes sense if it can see the first exchange).
- [ ] `response.usage.input_tokens` and `.output_tokens` are printed as
      real integers, not estimated.

## Hints

1. **Level 1:** Re-read Lesson 01's `basic_call.py` and `conversation.py`
   examples side by side — this exercise is a direct combination of both.
2. **Level 2:** Remember the two-step pattern for a multi-turn
   conversation: append the user's message to `messages`, call the API,
   then append the assistant's reply to `messages` *before* the next
   call — skipping the second append is the most common bug here.
3. **Level 3:** If `stop_reason` keeps coming back as `"max_tokens"`,
   your `system` prompt's "two sentences or fewer" instruction may not be
   working as hard as you'd like at `max_tokens=150` — try raising it to
   `250` and see whether the *content* still respects the instruction
   even if the raw ceiling is more generous.

If you get stuck for more than 30 minutes, ask for a hint rather than
looking at `solution/hello_questlog.py` — see the root `README.md` for
this course's hint workflow.
