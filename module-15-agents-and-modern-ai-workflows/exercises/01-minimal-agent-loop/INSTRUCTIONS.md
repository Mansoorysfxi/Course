# Exercise 01 — Minimal Agent Loop

**Difficulty:** Easy. If you've read Lesson 02 carefully, this exercise
should be almost impossible to fail — it's the same loop, with two
different tools.

## What you'll build

A standalone Python script, `mini_agent.py`, implementing a complete
agent loop from scratch — the same decide → act → observe → repeat shape
Lesson 02 built, with two new tools: a **unit converter** and a **dice
roller**. No API key required — you'll run it against a scripted fake
client, exactly like Lesson 02 did.

## Concepts this exercise requires (all taught in Lesson 01 and Lesson 02)

- The four-step loop: observe, decide, act, observe again.
- Tool definitions (`name`, `description`, `input_schema`).
- Dispatching a `tool_use` block to real Python code and building a
  `tool_result`.
- A hard iteration cap as a real, enforced guardrail.

## Instructions

1. Open `starter/mini_agent.py`. It has the loop's overall shape already
   written, with two gaps marked `# TODO`.
2. Implement `TOOLS`: two tool definitions.
   - `convert_units(value: float, from_unit: str, to_unit: str)` —
     supports at least `"km"` ↔ `"miles"` (1 km = 0.621371 miles).
   - `roll_dice(sides: int, count: int)` — returns `count` random integers
     between 1 and `sides` (inclusive).
3. Implement `run_tool(name, tool_input)` to actually execute each one,
   returning a string result (never a raw Python object).
4. Run the script against the provided scripted fake client (already
   written for you in `starter/mini_agent.py` — you don't need to change
   it) and confirm the printed trace matches your own prediction, made
   *before* you run it.
5. In a comment at the bottom of the file, answer: if `roll_dice` were
   given `count=0`, what should it sensibly return, and does your
   implementation actually handle that case? (You don't have to add a
   dice roll of 0 to the scripted fake client — just answer the
   question honestly about your own function.)

## Acceptance criteria

- `run_agent` correctly loops until `stop_reason != "tool_use"`, exactly
  like Lesson 02's own version.
- `convert_units` correctly converts both directions (km → miles and
  miles → km).
- `roll_dice` returns exactly `count` integers, each between 1 and
  `sides` inclusive.
- The loop still has a `MAX_ITERATIONS` cap, and the script prints a
  clear "gave up" message if it's ever reached (you can test this by
  temporarily scripting a fake client that always returns `tool_use`, the
  same trick Lesson 02's own "Try it yourself" used — remove that test
  scripting before you consider the exercise done).

## Hints

- **Level 1:** Re-read Lesson 02's own `run_agent` function line by line
  before touching the starter file — this exercise's loop is
  *deliberately* almost identical.
- **Level 2:** `convert_units`'s `input_schema` needs three properties:
  `value` (number), `from_unit` (string), `to_unit` (string). Handle
  exactly two unit names for this exercise — you don't need a general
  unit-conversion library.
- **Level 3:** For `roll_dice`, use Python's own `random.randint(1, sides)`
  in a list comprehension repeated `count` times, and join the results
  into a readable string (e.g. `"Rolled: [4, 1, 6]"`) for the tool
  result's own `content`.

## Running it

```bash
cd module-15-agents-and-modern-ai-workflows/exercises/01-minimal-agent-loop/starter
python mini_agent.py
```

**Expected output shape:** a printed trace of each iteration
(`stop_reason`, which tool was called, what it returned), ending with a
final answer line.
