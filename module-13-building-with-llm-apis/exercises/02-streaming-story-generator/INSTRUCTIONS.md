# Exercise 02 — A Streaming Quest-Flavor-Text Generator

## What you'll build

A script, `stream_flavor_text.py`, that streams a short piece of
"in-universe" flavor text for a QuestLog quest line, showing it appear on
screen token by token, then reports the final, complete response's stats
once streaming finishes.

## Concepts this exercise uses (all taught in Lesson 02)

- `client.messages.stream(...)` as a context manager
- Iterating `stream.text_stream` and printing each piece immediately
  (`end=""`, `flush=True`)
- Calling `stream.get_final_message()` **after** the loop, to get the
  complete `Message` object (with `.stop_reason` and `.usage`)

## Requirements

Write `stream_flavor_text.py` that:

1. Accepts a quest line name as a command-line argument (e.g. `python
   stream_flavor_text.py "Village Errands"`) — use `sys.argv[1]`, falling
   back to `"Side Quests"` if no argument is given.
2. Opens a streamed request to `claude-haiku-4-5` asking for a short
   (3-4 sentence), evocative, in-universe description of what that quest
   line is generally about — no `system` prompt is required, but you may
   add one if you want to shape the tone.
3. Prints each piece of text as it arrives, with no trailing newline
   between pieces (so the output visibly builds up on one paragraph, not
   one line per chunk).
4. After the stream completes, on new lines, prints:
   - The final `stop_reason`.
   - The final `output_tokens` from `get_final_message().usage`.
5. **Guguard against `max_tokens` truncation**: pick a `max_tokens` value
   generous enough that a 3-4 sentence description should comfortably
   fit, and if `stop_reason` comes back as `"max_tokens"` anyway, print a
   clear warning saying so (don't just silently show the cut-off text as
   if it were complete — Lesson 05 covers this stop reason in more
   depth, but you don't need Lesson 05's content to handle it here; just
   check the value).

## Acceptance criteria

- [ ] Running the script with different quest-line names produces
      visibly different flavor text for each.
- [ ] You can actually observe the text appearing progressively when you
      run it (not all at once) — this is the entire point of the
      exercise, so don't just trust the code compiles; watch it run.
- [ ] `stop_reason` and `output_tokens` are printed only *after* the
      streamed text finishes, never before or during.
- [ ] If you deliberately set `max_tokens` very low (try `15`) and rerun,
      your script's own truncation warning fires correctly.

## Hints

1. **Level 1:** Lesson 02's `stream_basic.py` is almost this exact
   exercise already — the changes are the prompt content and the
   command-line argument.
2. **Level 2:** `sys.argv` is a plain list of strings; `sys.argv[0]` is
   always the script's own filename, so your quest-line argument (if
   given) is `sys.argv[1]`.
3. **Level 3:** The truncation check is just
   `if final_message.stop_reason == "max_tokens": ...` — nothing more
   exotic than an ordinary `if` statement on a field this lesson already
   showed you how to read.
