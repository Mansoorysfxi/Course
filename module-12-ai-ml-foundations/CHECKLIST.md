# Module 12 Checklist — AI/ML Foundations

Complete this after finishing all three exercises and the capstone project,
and after your module-end review ("Check my module"). Don't start Module 13
until every box below is checked and any remedial exercises from your
review are done.

## Lessons

- [ ] Read `lessons/00-setup.md` and confirmed every command in its
      "Verify your setup" section — `tiktoken`, `sentence-transformers`,
      and (if chosen) a real Anthropic API key.
- [ ] Read `lessons/01-what-machine-learning-actually-is.md` and can
      explain, from memory, the real mechanical difference between
      training and inference — not just "one happens first."
- [ ] Read `lessons/02-neural-networks-conceptually.md` and can explain
      what a single artificial neuron computes, and what backpropagation
      accomplishes, using the boss-fight "assign blame backward" analogy
      or one of your own.
- [ ] Read `lessons/03-tokens-and-tokenization.md` and have actually run
      `tiktoken` yourself on at least one piece of text you chose, not just
      the lesson's own examples.
- [ ] Read `lessons/04-embeddings-meaning-as-coordinates.md` and can
      explain what cosine similarity measures and why it divides out
      vector length.
- [ ] Read `lessons/05-attention-and-transformers-intuition.md` and can
      explain, using the boids/flocking analogy, what attention computes.
- [ ] Read `lessons/06-context-windows-hallucination-and-sampling.md` and
      can explain, mechanically, why a hallucination often sounds just as
      confident as an accurate statement.
- [ ] Read `lessons/07-prompt-engineering-as-a-skill.md` and can name all
      four prompting techniques it covers and explain, for each, *why* it
      changes the model's output the way it does.

## Exercises

- [ ] Exercise 01 (hand tokenization) — done and reviewed. You ran
      `tiktoken` for real, on real text, with real output.
- [ ] Exercise 02 (embedding visualization) — done and reviewed. You
      computed real cosine similarities and correctly identified the most
      similar pair among your sentences.
- [ ] Exercise 03 (prompt engineering experiments) — done and reviewed,
      either as a genuine live comparison (if you have an API key) or as a
      thorough, honest dry run with real reasoning about expected
      differences (if you don't) — and you added a genuine fifth
      experiment of your own.

## Capstone

- [ ] `ai_foundations_toolkit.py` runs end to end with no errors, with or
      without a real API key set.
- [ ] Part 1's token count and cost estimate are real, computed values that
      change when you change the input text.
- [ ] Part 2 correctly identifies the single highest-scoring sentence pair
      among all pairwise comparisons, not just a pair you picked by eye.
- [ ] Part 3 either made a real, live prompt comparison or cleanly dry-ran
      with a documented, reasoned explanation of the expected difference.
- [ ] You can explain, unprompted, which earlier lesson each of the three
      parts is built on.

## Spaced repetition — review questions from earlier modules

Per this course's Rule 6, answer these without re-reading the original
lesson first; check your answer against the linked material afterward.

1. **(Module 00)** What do the three Git conflict markers (`<<<<<<<`,
   `=======`, `>>>>>>>`) each represent inside a file, and what must you
   do with them before completing a merge? *(See
   `module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md`.)*
2. **(Module 04)** In React, what specifically has to happen for a
   component to re-render, and how is this comparable to an Unreal Actor
   property whose change should update a bound widget? *(See
   `module-04-react/lessons/02-state-and-the-rendering-model.md`.)*
3. **(Module 06)** What does the "I" in ACID stand for, and what
   specifically does it guarantee about two transactions running at the
   same time? *(See
   `module-06-databases/lessons/02-indexes-transactions-and-acid.md`.)*
4. **(Module 07)** A JWT is described as "signed, not encrypted." What
   does that distinction actually mean about who can *read* a JWT's
   payload versus who can *forge* one? *(See
   `module-07-auth-security/lessons/04-jwt-structure-in-depth.md`.)*
5. **(Module 09)** In SSH key-based authentication, which key — public or
   private — ever leaves your own machine, and how does logging in prove
   you hold the other one without ever transmitting it? *(See
   `module-09-linux-networking-servers/lessons/02-ssh-and-key-based-auth.md`.)*

## Before moving to Module 13

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your
      Module 12 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You understand, in your own words, that Module 13 (Building with LLM
      APIs) is where QuestLog itself gains its first real AI feature — an
      assistant endpoint using the Anthropic API — built directly on top of
      everything this module taught, and that this module's own
      standalone scripts do not carry forward as code.
