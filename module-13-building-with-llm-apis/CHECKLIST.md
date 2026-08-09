# Module 13 Checklist — Building with LLM APIs

Complete this before moving on to Module 14. Check off each item
honestly — this is a self-assessment, not a formality.

## Lessons

- [ ] Read `lessons/00-setup.md` and confirmed every command in its
      "Verify your setup" section — the `anthropic` SDK installs and
      imports correctly, and (if you got a key) a real, tiny, live call
      succeeds.
- [ ] Read `lessons/01-calling-the-anthropic-api.md` and can explain, from
      memory, every required parameter on a Messages API call and what
      `response.usage` actually tells you.
- [ ] Read `lessons/02-streaming-responses.md` and can explain what
      Server-Sent Events are, in enough depth to know what's happening
      underneath `stream.text_stream`.
- [ ] Read `lessons/03-structured-outputs-with-pydantic.md` and can
      explain precisely what `output_config.format` guarantees, and why
      QuestLog's own backend still validates the result with Pydantic
      afterward anyway.
- [ ] Read `lessons/04-tool-use-and-function-calling.md` and can walk
      through the full tool-use round-trip from memory, including how to
      handle more than one `tool_use` block in the same turn.
- [ ] Read `lessons/05-error-handling-retries-and-cost-management.md` and
      can explain the real difference between an exception the SDK
      raises and a `refusal`.
- [ ] Read `lessons/06-evaluating-ai-features.md` and can explain what a
      golden set is and why `assert output == "exact text"` is the wrong
      tool for evaluating an LLM's output.
- [ ] Read `lessons/07-building-questlogs-ai-assistant-backend.md` and
      `lessons/08-building-questlogs-ai-assistant-frontend.md` in full,
      and have actually read `project/questlog/backend/app/ai_assistant.py`
      and `project/questlog/frontend/src/components/QuestBreakdownPanel.tsx`
      end to end, not just the lessons describing them.

## Exercises

- [ ] Exercise 01 (first API call) — done and reviewed.
- [ ] Exercise 02 (streaming story generator) — done and reviewed,
      including genuinely watching text stream progressively, not just
      confirming the code runs.
- [ ] Exercise 03 (structured quest extractor) — done and reviewed, with
      a real, validated `ExtractedQuest` object printed from real (or
      honestly dry-run) output.
- [ ] Exercise 04 (tool-use quest line lookup) — done and reviewed,
      including correctly handling a turn with more than one `tool_use`
      block.
- [ ] Exercise 05 (eval harness) — done and reviewed; the mocked mode
      runs with zero API key required, and at least one golden case's
      canned result was deliberately written to fail a check.

## Capstone

- [ ] `project/BRIEF.md` Part 1 — the feature genuinely runs live (or a
      thorough, honest dry run exists instead): visible streaming, the
      tool-use round trip firing on at least one real quest, and a real
      accepted suggestion becoming a real new quest.
- [ ] Part 2 — a real eval pass ran against at least 5 real cases, with
      real, reported PASS/FAIL results.
- [ ] Part 3 — the deliberately-broken scenario was genuinely reproduced
      and then fixed, with the real behavior documented.
- [ ] Part 4 — one small, real extension was implemented and explained.
- [ ] `project/AI_ASSISTANT_REPORT.md` written, covering all five
      required points from the brief.
- [ ] You can explain, unprompted, the complete path a single "Suggest a
      Breakdown" click takes, from the button being clicked to a new
      quest appearing on the Quest Board — every request, every streamed
      event, every state transition, in order.
- [ ] The backend test suite (`pytest`, from
      `project/questlog/backend/`) and frontend test suite (`npx vitest
      run`, from `project/questlog/frontend/`) both still pass in full,
      with no `ANTHROPIC_API_KEY` set anywhere in your shell.

## Spaced repetition — review questions from earlier modules

Per this course's Rule 6, answer these without re-reading the original
lesson first; check your answer against the linked material afterward.

1. **(Module 02)** In what specific sense is HTTP "stateless," and what
   real consequence does that have for how a client has to behave across
   multiple requests? *(See
   `module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md`
   — and notice this module's own Lesson 01 makes exactly the same claim
   about the Messages API, for exactly the same underlying reason.)*
2. **(Module 05)** What does FastAPI's `Depends()` actually do,
   mechanically, when a route function declares a parameter using it —
   and why does that make it easy to swap in a fake for testing? *(See
   `module-05-backend-fastapi/lessons/04-dependency-injection-and-depends.md`
   — this module's own `get_ai_client`/`AiClient` is built from exactly
   this mechanism.)*
3. **(Module 07)** What does it mean that a JWT is "signed, not
   encrypted," and what does that distinction actually protect against
   (and not protect against)? *(See
   `module-07-auth-security/lessons/04-jwt-structure-in-depth.md`.)*
4. **(Module 08)** What is a mock actually standing in for when you use
   one in a test, and why is a fake object (like this module's own
   `FakeAnthropicClient`) usually easier to reason about than a
   general-purpose mocking library's auto-generated mock? *(See
   `module-08-testing-and-quality/lessons/03-parametrize-and-mocking.md`.)*
5. **(Module 12)** Why can't a `tiktoken` token count be trusted as an
   authoritative number for a real Claude API call, and what should you
   use instead? *(See
   `module-12-ai-ml-foundations/lessons/03-tokens-and-tokenization.md`
   — and notice this module's own Lesson 01 answers the "what to use
   instead" half directly.)*

## Before moving to Module 14

- [ ] All boxes above are checked honestly.
- [ ] You understand, in your own words, why Module 12 could use free,
      local tools for its core material while this module genuinely
      needed a real, paid API key — and roughly what this module actually
      cost you.
- [ ] You can explain why QuestLog's own AI feature streams raw text
      while it's generating but only renders the final sub-quest list
      once a `result` event confirms the complete, validated JSON
      arrived — the real tension between streaming and structured output,
      resolved honestly, in your own words.
