# Exercise 02 — Tool Design and Multi-Step Reasoning

**Difficulty:** Guided. You'll redesign a genuinely bad tool, then build
a scenario that requires two tools to be called in sequence.

## What you'll build

A standalone Python script, `library_agent.py`, modeling a tiny library
system: an agent that can look up books and check them out. You'll first
**fix** a poorly-designed, overloaded tool the starter file gives you,
then wire up a second tool so the agent can chain "find the book" →
"check it out" across two iterations, the same "multi-step reasoning"
pattern Lesson 03 walked through for QuestLog's own agent.

## Concepts this exercise requires (all taught in Lesson 03)

- What makes a tool description good or bad.
- When a narrow, dedicated tool beats a general one with a flag.
- How multi-step reasoning falls out naturally from tools whose inputs
  and outputs chain (one tool's typical output feeding a later tool's
  required input).

## Instructions

1. Open `starter/library_agent.py`. It defines one, deliberately bad
   tool: `manage_book(action: str, title: str)`, where `action` is a
   free-form string that's supposed to be `"lookup"` or `"checkout"`
   internally. Read the whole file before changing anything.
2. **Redesign it into two separate, well-described tools:**
   - `find_book(title: str)` — returns the book's `book_id` and
     `available` status if a title match exists, or a clear "not found"
     message.
   - `checkout_book(book_id: str)` — marks that book checked out, using
     its `book_id` (never its title) as the argument. Return an error
     result (`is_error: True` in the tool_result) if the id doesn't exist
     or the book is already checked out.
3. Give each tool a description that states not just *what* it does but
   *when* to use it — re-read Lesson 03's own "what makes a tool
   description good" section before writing these.
4. Write a scripted fake-client conversation (in `if __name__ ==
   "__main__":`) where the user asks to check out a book **by title
   only** ("Check out Dune for me") — this requires the agent to call
   `find_book` first to get a `book_id`, then `checkout_book` with that
   id, in two separate iterations. Predict, in a comment, the exact
   sequence of tool calls before writing the scripted turns.
5. In a comment at the bottom, answer: why can't the agent call
   `checkout_book` directly with the title, skipping `find_book`
   entirely? What would have to be true about `checkout_book`'s own
   schema for that to even be possible, and why is that a worse design?

## Acceptance criteria

- `manage_book` no longer exists anywhere in your final file — it's been
  fully replaced by the two dedicated tools.
- `find_book` and `checkout_book` each have a description stating *when*
  to use them, not just what they do.
- Your scripted conversation demonstrates the real two-step chain
  (`find_book` then `checkout_book`), and the printed trace shows both
  tool calls happening in order.
- `checkout_book` returns an error tool result (not a crash) for an
  unknown `book_id` or a book that's already checked out.

## Hints

- **Level 1:** Re-read Lesson 03's `complete_quest` vs. `update_quest`
  discussion — `find_book`/`checkout_book` is the exact same "one general
  overloaded action becomes two narrow ones" transformation, applied to a
  different domain.
- **Level 2:** `find_book`'s return value needs to include a `book_id` a
  later tool call can use — pick something simple and stable, like the
  book's own index in a hard-coded list, turned into a string.
- **Level 3:** For the scripted conversation, your first fake turn should
  produce a `tool_use` block calling `find_book`; your second fake turn
  (after you supply that tool's result) should produce a `tool_use` block
  calling `checkout_book` with the `book_id` your `find_book`
  implementation actually returns; your third fake turn is the final
  text answer.

## Running it

```bash
cd module-15-agents-and-modern-ai-workflows/exercises/02-tool-design-and-multi-step-reasoning/starter
python library_agent.py
```

**Expected output shape:** a two-iteration tool-call trace (find, then
checkout), followed by a final confirmation message.
