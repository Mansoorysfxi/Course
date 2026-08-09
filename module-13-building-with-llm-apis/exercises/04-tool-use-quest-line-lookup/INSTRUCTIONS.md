# Exercise 04 — A Real Tool-Use Round-Trip: Quest Line Completion Rates

## What you'll build

A script, `completion_advisor.py`, implementing a **complete manual
tool-use loop** (no copy-pasting Lesson 04's own `tool_round_trip_loop.py`
verbatim — this is a genuinely different scenario, and you should write
the loop yourself, using that lesson's structure as a reference, not a
template to retype). This is the last exercise before the capstone
lessons, and deliberately more independent than Exercises 01-03 — you're
given a scenario and a fake dataset, not a near-complete script.

## Concepts this exercise uses (all taught in Lesson 04)

- Defining a tool with a real, specific `description`
- Reading `stop_reason == "tool_use"` and a `tool_use` block's `.id`,
  `.name`, and `.input`
- Executing the tool yourself and sending a `tool_result` back, matched
  by `tool_use_id`
- Handling **more than one** `tool_use` block in the same turn (this
  scenario is specifically designed to trigger that)
- A hard iteration cap on the loop

## The scenario

QuestLog wants an "advisor" that tells a player which of their quest
lines most needs attention, based on **completion rate** (done quests ÷
total quests). Give the model one tool:

```python
GET_COMPLETION_RATE_TOOL = {
    "name": "get_quest_line_completion_rate",
    "description": (
        "Returns the fraction of quests marked done in a given quest "
        "line, as a number between 0.0 and 1.0. Call this once per quest "
        "line you need to compare before making a recommendation."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "quest_line": {"type": "string", "description": "The exact quest line name."},
        },
        "required": ["quest_line"],
    },
}
```

Back it with this fake data (a stand-in for a real database query, the
same way Lesson 04's own example stood in for one):

```python
FAKE_COMPLETION_RATES = {
    "Main Story": 0.8,
    "Side Quests": 0.25,
    "Village Errands": 0.5,
}
```

## Requirements

Write `completion_advisor.py` that:

1. Sends a user message: `"I have three quest lines: Main Story, Side
   Quests, and Village Errands. Which one most needs my attention, and
   why?"` — with `GET_COMPLETION_RATE_TOOL` available.
2. Implements the full manual loop: while `stop_reason == "tool_use"`,
   execute **every** `tool_use` block in that turn (there may be more
   than one — a real model asked this exact question will often check
   all three quest lines before answering, in one turn), collect all the
   `tool_result`s, and send them back together in one `user` message.
3. Caps the loop at 5 iterations, printing a clear message if it's ever
   exhausted without a final answer.
4. Once `stop_reason` is no longer `"tool_use"`, prints Claude's final
   answer.
5. Also prints, as your own script runs, which quest line(s) the model
   actually asked about, in the order it asked — so you can see the real
   round-trip happening, not just the final answer.

## Acceptance criteria

- [ ] Your script correctly handles a turn with more than one
      `tool_use` block — test this by checking your own printed "which
      quest line(s) the model asked about" output actually shows more
      than one line in a single turn at least once.
- [ ] Every `tool_result` you send back has the correct matching
      `tool_use_id` — a mismatch here usually shows up as a 400 error
      from the API, which is a good signal something's wrong.
- [ ] The final answer correctly identifies "Side Quests" (0.25
      completion) as needing the most attention — not a guess, a
      conclusion actually grounded in the real numbers your tool
      returned.
- [ ] The loop terminates correctly (it should never need anywhere close
      to 5 iterations for this scenario, but the cap exists and works).

## Hints

1. **Level 1:** Re-read Lesson 04's full walkthrough end to end,
   especially "The full round-trip, as one loop" — the *shape* of your
   loop should look like that one, even though the tool and scenario are
   different.
2. **Level 2:** The tricky part is handling multiple `tool_use` blocks in
   one turn correctly — loop over `response.content`, collecting a
   `tool_result` for every block whose `.type == "tool_use"`, and only
   append the combined list as **one** `user` message after the loop over
   blocks finishes, not one message per block.
3. **Level 3:** If the model only ever asks about one quest line at a
   time across several separate turns instead of asking about several in
   one turn, that's not a bug in your code — it's a legitimate way for
   Claude to approach the task. Your loop should handle either case
   correctly without you needing to force one behavior or the other.

If you get stuck for more than 30 minutes, ask for a hint before checking
`solution/completion_advisor.py`.
