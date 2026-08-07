# Lesson 09 — Normalization and Schema Design, in Plain Language

## What you'll learn

- What normalization actually means, without the formal "normal forms" jargon overload.
- The concrete problem normalization solves (duplicate/inconsistent data).
- When *not* to normalize further (over-normalization is a real cost).
- A repeatable process for designing a schema from requirements.

## Why this matters

Lesson 01 already showed you one normalization decision (splitting quest
line names into their own table) without naming it. This lesson names the
underlying principle and gives you a process to apply it yourself, before
Lesson 10 uses that process on QuestLog's full schema.

## Prerequisites

Lessons 01 and 04 (keys, foreign keys, joins — normalization is the reason
those exist).

## The concept, explained simply

**Normalization** means organizing a schema so that every real-world fact
is stored in exactly one place. The opposite — storing the same fact
redundantly in multiple rows — is what causes **update anomalies**: change
the fact in one place, forget the other copies, and now your data
contradicts itself with no way to tell which copy is "right." Lesson 01's
motivating example — a `quest_line: str` column repeated on every quest —
is exactly this: the fact "this quest line is called Side Quests" gets
copied onto every single quest belonging to it, instead of stored once.

## The details

### The three anomalies normalization prevents (plain language, not jargon)

1. **Update anomaly:** you rename "Side Quests" to "Bonus Quests," but only
   update 40 of the 43 quests referencing it (a bug, a missed row, a
   partial script) — now three quests disagree with the other forty about
   what their own quest line is called.
2. **Insertion anomaly:** you want to record that a new quest line called
   "Endgame" exists, but your schema only lets you create a quest line
   *by* creating a quest that uses it — you can't represent "this quest
   line exists, with zero quests in it yet" at all, because the fact "quest
   line X exists" was never given its own place to live.
3. **Deletion anomaly:** you delete the one remaining quest in "Bonus
   Quests" — and lose all record that a quest line called "Bonus Quests"
   ever existed, purely as a side effect of deleting an unrelated quest,
   because the quest line's existence wasn't stored anywhere independent
   of the quests referencing it.

`QuestLine` as its own table (Lesson 01) fixes all three at once: rename
its `name` column exactly once, insert a `QuestLine` row with zero quests
attached, or delete every quest in it — the quest line's own existence and
identity live in one place, unaffected by any of that.

### A repeatable process for designing a schema from requirements

1. **List the real-world "things" your application needs to remember**
   (nouns) — for QuestLog: quests, quest lines, users.
2. **For each thing, list its own facts** (the ones that don't depend on
   any *other* thing) — a quest's title/description/priority/done-status;
   a quest line's name; a user's email.
3. **Identify relationships between things** — "a quest belongs to exactly
   one quest line," "a quest belongs to exactly one user" (Lesson 01's
   one-to-many shape, twice).
4. **Turn each "thing" into a table**, its own-facts into columns, and each
   relationship into a foreign key column on the "many" side (Lesson 01)
   — never duplicate a fact that belongs to a different table.
5. **Check each table against the three anomalies above** — can you
   represent "this thing exists, unconnected to anything else yet"? Can
   you change one fact in exactly one place? If not, something's still
   duplicated or missing its own table.

### When *not* to normalize further

Normalization isn't "always split everything into more tables." Consider a
`Quest.priority` field — you could theoretically create a `priorities`
table (`id`, `name`) and reference it by foreign key, the same way
`quest_line` was split out. Whether that's worth it depends on a real
question: **will "high"/"medium"/"low" ever need more than a name** (an
associated color, a sort order, per-user customization)? If genuinely not,
a plain string column (or, more precisely, `db_models.py`'s constrained
`Literal["low", "medium", "high"]` type on the Pydantic side, enforced at
the API boundary) is simpler and correct — adding a table for three values
that will never grow independent facts of their own is complexity without
payoff. Over-normalizing has a real cost: more tables means more joins
(Lesson 04) for even simple reads, and more code, for a flexibility you
may never use.

**Try it yourself:** apply the same question to `Quest.done` — should
"done" be its own table? (Almost certainly not — a boolean has no
independent facts of its own to ever need; this is an easy case precisely
because the answer to "will this ever need more than its current value"
is a clear no.)

## Common mistakes & gotchas

- **Treating normalization as a purity rule to maximize.** It's a tool for
  solving the three specific anomalies above — apply it where those
  anomalies would actually bite, not everywhere reflexively.
- **Confusing "duplicated across tables" with "duplicated within a
  request's response."** `repository.py`'s `_to_pydantic` still returns a
  `quest_line` *name* string in the API response, duplicated across many
  quests' JSON — that's fine; normalization is about how data is *stored*,
  not how it's *presented* to a client. The stored fact still lives in
  exactly one row.
- **Designing tables before listing requirements.** Jumping straight to
  "I'll make a table for X" without first listing the real facts and
  relationships (steps 1–3 above) is how accidental duplication sneaks in.

## How this connects

Lesson 10 runs this exact five-step process against QuestLog's real
requirements, explaining precisely why the schema ended up as three tables
(`users`, `quest_lines`, `quests`) and not more or fewer.

## Quick self-check

1. Name the three anomalies normalization prevents, in your own words, not the formal names.
2. Why couldn't a "quest-lines-are-just-a-string-column" design represent an empty quest line with zero quests?
3. Give one concrete reason `Quest.priority` was kept as a simple column rather than its own table.
4. Does normalization mean data can never appear duplicated anywhere, including in an API response? Why or why not?
