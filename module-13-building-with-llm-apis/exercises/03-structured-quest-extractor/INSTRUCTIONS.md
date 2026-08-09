# Exercise 03 — A Structured Quest Extractor

## What you'll build

A script, `extract_quest.py`, that takes a messy, free-text paragraph
describing a quest idea and turns it into a clean, validated,
QuestLog-shaped quest — `title`, `description`, `priority`
(`"low"`/`"medium"`/`"high"`), and `quest_line` — using structured output,
not free-form prompting.

## Concepts this exercise uses (all taught in Lesson 03)

- `output_config={"format": {"type": "json_schema", "schema": ...}}`
- JSON Schema's `enum` keyword, to constrain `priority` to exactly the
  three values QuestLog's own `Priority` type allows (Module 05's
  `app/models.py`)
- Defining a Pydantic model and validating the parsed JSON against it —
  the "defense in depth" pattern Lesson 03 taught, not just trusting the
  raw JSON

## Requirements

Write `extract_quest.py` that:

1. Defines a Pydantic model, `ExtractedQuest`, with fields matching
   QuestLog's own quest shape: `title: str`, `description: str`,
   `priority: Literal["low", "medium", "high"]`, `quest_line: str`.
2. Defines a raw JSON Schema (matching `ExtractedQuest`'s shape,
   including an `enum` for `priority`) to pass as
   `output_config.format.schema`.
3. Sends a request to `claude-haiku-4-5` with a system prompt instructing
   Claude to extract a structured quest from whatever messy text the user
   provides, and a user message containing this exact messy input:

   > "so basically there's this old lighthouse keeper on the coast who
   > hasn't sent his weekly signal in like three weeks and people are
   > getting worried, someone should probably go check on him, it's not
   > urgent-urgent but it shouldn't wait forever either, this'd go under
   > our coastal errands stuff"

4. Parses the response text with `json.loads()`, then validates it with
   `ExtractedQuest.model_validate(...)`.
5. Prints the validated object's fields, and confirms `priority` is
   exactly one of the three allowed values (it will be, by construction —
   print a line confirming this rather than just trusting it silently).

## Acceptance criteria

- [ ] The script runs with no `json.JSONDecodeError` and no Pydantic
      `ValidationError` — if you get either, re-read your schema (a
      common bug: forgetting `additionalProperties: false`, or forgetting
      `required` on the inner object).
- [ ] `priority` in the printed output is a real judgment call based on
      the input's own tone ("it's not urgent-urgent but shouldn't wait
      forever" is a "medium," not a "low" or "high") — not something you
      hardcoded.
- [ ] `quest_line` reflects something like "Coastal Errands," picked up
      from the input's own "coastal errands stuff" phrase, not invented
      from nothing.

## Hints

1. **Level 1:** Lesson 03's raw-schema example (`structured_raw_schema.py`)
   is the shape to copy, with a different schema and a different Pydantic
   model.
2. **Level 2:** Your JSON Schema's `priority` property needs
   `{"type": "string", "enum": ["low", "medium", "high"]}` — `enum` is
   explicitly one of the supported JSON Schema features Lesson 03's own
   header table lists.
3. **Level 3:** If validation keeps failing, print the raw
   `response.content[0].text` *before* trying to parse it, so you can see
   exactly what Claude actually returned rather than debugging blind.

If you get stuck for more than 30 minutes, ask for a hint before checking
`solution/extract_quest.py`.
