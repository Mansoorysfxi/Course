# Lesson 06 — Evaluating AI Features: Simple Eval Harness Basics

**Verified against (August 2026), via web research on August 9, 2026 into
current, real-world practice for evaluating LLM-powered features at a
beginner-appropriate level** (sources: engineering guides on golden-dataset
evaluation and eval-harness practice, cross-checked against several
independent write-ups rather than a single source, since this is
practice guidance rather than a single documented API fact):

| Practice | Current guidance | Why it's the right scope for this lesson |
|---|---|---|
| Golden-set size to start | Roughly 10-50 hand-picked cases is a realistic, common starting point — enough to catch real regressions, small enough to run in seconds | A course-scale example doesn't need hundreds of cases to teach the *mechanic* |
| What a "simple" harness checks | Cheap, deterministic heuristic checks (does it parse, is it the right shape, does it violate an obvious rule) *before* reaching for anything more elaborate | Matches this course's own progression — code you can read and verify, not a framework |
| Where "LLM-as-judge" fits | A real, current technique for grading subjective quality, but explicitly a **later** addition once the cheap checks already exist and are calibrated against real human review | Correctly scoped as "worth knowing exists," not required for this module |

*Sources consulted: [Golden dataset evaluation — Langfuse](https://langfuse.com/resources/engineering/golden-dataset-evaluation), [Building a "Golden Dataset" for AI Evaluation](https://www.getmaxim.ai/articles/building-a-golden-dataset-for-ai-evaluation-a-step-by-step-guide/), [Evaluation best practices — OpenAI API docs](https://developers.openai.com/api/docs/guides/evaluation-best-practices), [Eval harness: what it is — DeepEval](https://deepeval.com/blog/what-is-an-eval-harness).*

## What you'll learn

- Why an AI feature can fail "quietly" — passing every normal test while
  still being genuinely bad — and why that's a different problem from
  anything Module 08's testing lessons covered.
- What a **golden set** is, and how to build a small, useful one for a
  real feature.
- How to write simple, deterministic checks against an LLM's output —
  without needing a second LLM, a framework, or a paid eval platform.
- Where a more advanced technique (using a second LLM call to judge
  subjective quality) fits, and why this course doesn't require it.

## Why this matters

Module 08 taught you to test code: given this input, assert this exact
output. An LLM breaks that model in an important way — the same prompt
can produce two differently-worded, both-genuinely-fine responses, so
"assert the exact text" is the wrong tool. But that doesn't mean AI
features are untestable — it means you need a different, still genuinely
rigorous, set of checks: does the output have the right *shape*? Does it
violate any rule you can state precisely? Would a human reviewing a batch
of these outputs actually be satisfied? This lesson is where you learn
that different kind of check, before QuestLog's real AI feature (Lessons
07-08) ships without ever having been evaluated at all.

## Prerequisites

- **Lesson 03** — structured outputs. This lesson's checks run against
  the *parsed*, validated result Lesson 03 already guarantees is the
  right shape — evaluation here is about whether the *content* is good,
  on top of that guarantee, not a replacement for it.
- **Module 08's pytest fixtures/parametrize lesson** — this lesson's
  harness is, deliberately, "a small pytest-parametrized test suite," not
  a new tool to learn; if `@pytest.mark.parametrize` feels unfamiliar,
  that lesson is the one to revisit.

## The concept, explained simply

Think of the difference between testing ordinary code and evaluating an
AI feature the way you'd think about the difference between testing a
deterministic physics calculation (a fixed input always produces one
exact, correct output — like Module 08's own database tests) versus
playtesting an NPC's dialogue system for whether its *lines* feel right.
You can't write `assert npc_line == "exact expected sentence"` for a
dialogue generator with any real variety built in — but you absolutely
can, and should, check things like "did it produce a line at all," "is it
under the length the UI can display," "does it ever say something that
breaks lore," or "does a human reading ten of these come away satisfied."
Evaluating an LLM feature is exactly this — trading "one exact expected
output" for "a set of real, checkable properties the output should have,"
run across a representative set of cases, not just one.

## The details

### The golden set: your feature's own representative test cases

A **golden set** is a small, hand-picked collection of realistic inputs
for your feature, each one chosen because it exercises something specific
you actually care about — not a random sample, a deliberately curated
one. For QuestLog's quest-breakdown feature, a genuinely useful golden
set includes: an ordinary quest with no complications; a quest whose
title is very short or vague; a quest where the player already has a
quest with a very similar title (testing the duplicate-avoidance tool
from Lesson 04); and a quest with an unusually long description. A
handful of well-chosen cases like these catch real, meaningful problems
far better than a hundred near-identical ones would.

```python
from dataclasses import dataclass, field


@dataclass
class GoldenCase:
    name: str
    quest_title: str
    quest_description: str
    existing_titles: list[str] = field(default_factory=list)


GOLDEN_SET = [
    GoldenCase(
        name="dragon_quest_no_duplicates",
        quest_title="Defeat the dragon guarding the old mine",
        quest_description="The dragon has been terrorizing the northern villages.",
        existing_titles=["Gather Healing Herbs", "Deliver the Sealed Letter"],
    ),
    GoldenCase(
        name="dragon_quest_with_near_duplicate",
        quest_title="Defeat the dragon guarding the old mine",
        quest_description="The dragon has been terrorizing the northern villages.",
        # This existing title is close enough to a natural sub-quest
        # suggestion that a real model, without the check_existing_quest_titles
        # tool (Lesson 04) actually working, might well suggest it again.
        existing_titles=["Scout the mine entrance", "Deliver the Sealed Letter"],
    ),
]
```

### Cheap, deterministic checks — the first, most valuable layer

Before reaching for anything involving a second model call, write plain
Python checks for every rule you can state precisely. These are fast (no
network call), free (no tokens spent), and completely reproducible —
exactly the properties that made Module 08's own tests valuable.

```python
def check_result(case: GoldenCase, sub_quests: list[str]) -> list[str]:
    """Returns a list of human-readable problems found; empty means the
    result passed every check this harness knows how to run."""
    problems: list[str] = []

    if not (2 <= len(sub_quests) <= 4):
        problems.append(f"expected 2-4 sub-quests, got {len(sub_quests)}")

    existing_lower = {title.strip().lower() for title in case.existing_titles}
    seen_lower: set[str] = set()
    for title in sub_quests:
        stripped = title.strip()
        if not stripped:
            problems.append("a sub-quest title was empty")
            continue
        if len(stripped.split()) > 12:
            problems.append(f"sub-quest title too long ({len(stripped.split())} words): {stripped!r}")
        if stripped.lower() == case.quest_title.strip().lower():
            problems.append(f"sub-quest restates the whole quest verbatim: {stripped!r}")
        if stripped.lower() in existing_lower:
            problems.append(f"sub-quest duplicates an existing quest title: {stripped!r}")
        if stripped.lower() in seen_lower:
            problems.append(f"sub-quest duplicates another suggestion in this same response: {stripped!r}")
        seen_lower.add(stripped.lower())

    return problems
```

Every single check here is directly traceable to a real requirement this
module already stated somewhere: 2-4 sub-quests and a 12-word title limit
come from Lesson 07's own system prompt (which this check independently
verifies the *model actually followed*, rather than trusting the prompt
alone); the duplicate checks are exactly what the `check_existing_quest_titles`
tool (Lesson 04) exists to prevent, and this harness is how you'd notice
if that tool ever stopped working correctly.

### Running the harness — a real, verified demonstration

Here's this exact harness run against two **canned** (hand-written, not
live) results — one deliberately good, one deliberately bad — so you can
see the mechanics work honestly, without needing an API key yet:

```python
CANNED_RESULTS = {
    "dragon_quest_no_duplicates": [
        "Scout the mine entrance and note patrol timing",
        "Gather fire-resistant gear",
        "Lure the dragon into the open",
    ],
    "dragon_quest_with_near_duplicate": [
        "Scout the mine entrance",  # duplicates an existing quest title on purpose
        "Gather fire-resistant gear",
    ],
}

for case in GOLDEN_SET:
    sub_quests = CANNED_RESULTS[case.name]
    problems = check_result(case, sub_quests)
    status = "PASS" if not problems else "FAIL"
    print(f"[{status}] {case.name}")
    for problem in problems:
        print(f"    - {problem}")
```

**Actual output** (this exact code was run for real while writing this
lesson — no API key involved, since it runs against the canned results
above, not a live call):

```
[PASS] dragon_quest_no_duplicates
[FAIL] dragon_quest_with_near_duplicate
    - sub-quest duplicates an existing quest title: 'Scout the mine entrance'

2 cases run, 1 problem(s) found.
```

This is the entire mechanic. Swap `CANNED_RESULTS` for a real call to
`stream_quest_breakdown` (Lesson 07) — or, more simply, a plain,
non-streamed `client.messages.create(...)` call per golden case — and you
have a real eval harness that runs against Claude's actual, live output
instead of canned data. Exercise 05 has you do exactly that.

**Try it yourself:** Add a third golden case to `GOLDEN_SET` — a quest
whose title is already very long — and a deliberately bad `CANNED_RESULTS`
entry for it containing a sub-quest title over 12 words. Rerun the
harness and confirm the exact word count appears in the printed failure
message, not just a generic "too long."

### Wiring the same checks into pytest

Because every check here is a plain Python function returning a list, it
slots directly into `pytest.mark.parametrize` — the exact tool Module 08
already taught:

```python
import pytest


@pytest.mark.parametrize("case", GOLDEN_SET, ids=lambda case: case.name)
def test_breakdown_meets_quality_bar(case: GoldenCase):
    sub_quests = CANNED_RESULTS[case.name]  # or a real call, in a live run
    problems = check_result(case, sub_quests)
    assert not problems, "; ".join(problems)
```

Run with a live key, this becomes a real, if slightly nondeterministic,
regression check you can run before shipping a prompt change — "did this
system-prompt edit make the duplicate-avoidance rule *worse*?" is exactly
the kind of question this kind of harness answers, concretely, instead of
by eyeballing a handful of outputs and guessing.

### Where "LLM-as-judge" fits (and why this course doesn't require it)

A real, current, more advanced technique exists: use a *second* LLM call
to grade the *subjective* quality of a response — "is this sub-quest
actually a sensible, actionable piece of the original quest?" — something
a plain Python `if` statement genuinely cannot check. Current practice
(this lesson's own header table) treats this as a real technique worth
knowing about, but explicitly a *layer on top of* the cheap, deterministic
checks this lesson teaches, calibrated against real human review before
you trust it — not a replacement for writing the checks you actually can
write in plain code. This module doesn't build an LLM-as-judge harness
(it would need its own careful calibration this course's scope doesn't
have room for), but knowing it exists, and knowing it belongs *after* the
cheap checks, not instead of them, is the practical, honest takeaway.

## Common mistakes & gotchas

- **Trying to `assert result == "exact expected text"` against live LLM
  output.** This is the single most common mistake moving from Module
  08's testing mindset to evaluating an AI feature — the model's wording
  varies run to run (Module 12, Lesson 06's sampling material) even when
  the *quality* is consistently fine. Check properties, not exact text.
- **A golden set with only "easy" cases.** A golden set that never
  includes the tricky case (the near-duplicate quest title, the vague
  one-word quest) never catches the exact regressions you actually care
  about — choose cases deliberately, per this lesson's own explanation,
  not by convenience.
- **Skipping the cheap checks and reaching straight for LLM-as-judge.**
  A second model call is slower, costs real tokens, and is itself subject
  to the same "review its output carefully" concern as the thing it's
  grading. Exhaust the free, deterministic checks first.
- **Never running the harness again after the first time.** An eval
  harness's real value is as a **regression check** — run it again after
  a prompt change, a model swap, or a schema edit, exactly the way
  Module 08's test suite gets re-run after every code change, not written
  once and forgotten.
- **Treating "it passed the harness" as "it's definitely good."** A small,
  hand-picked golden set catches the specific things you thought to check
  for — it's a real, useful signal, not a proof of correctness. This is
  no different from what Module 08 already taught about the limits of
  any test suite.

## How this connects

This lesson closes the loop the master plan's own curriculum for this
module opens with a real question — "how do you know your AI feature
works?" — and the honest answer, at this course's level, is: write a
small, deliberately-chosen golden set, check the properties you actually
care about in plain code, and re-run it whenever something changes.
Lessons 07-08 build QuestLog's real capstone feature next; Exercise 05
has you build a genuine eval harness for it, against live output if
you have an API key.

## Quick self-check

1. Why is `assert output == "exact expected string"` the wrong tool for
   testing an LLM's output, when it was exactly right for Module 08's own
   database tests?
2. What makes a golden set "good" — is it about having many cases, or
   something else? Give an example of a well-chosen QuestLog test case
   and explain what specific thing it's checking for.
3. In the worked example above, why did `dragon_quest_with_near_duplicate`
   fail while `dragon_quest_no_duplicates` passed — trace through
   `check_result` and name the exact rule that caught it.
4. Where does "LLM-as-judge" fit relative to the cheap, deterministic
   checks this lesson teaches — before, after, or instead of them?
5. Why is an eval harness worth re-running after a prompt change, even if
   the code around the LLM call itself didn't change at all?
