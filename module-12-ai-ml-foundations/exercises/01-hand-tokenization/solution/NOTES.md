# Solution Notes — Exercise 01

This solution was actually run (not just written) while generating this
module, using `tiktoken` `0.13.0`, the `o200k_base` encoding, with no API
key and no network access at run time (Lesson 00's setup already downloads
everything `tiktoken` needs at install time).

**Actual, verified output from running `python tokenize_playground.py`:**

```
Text: 'QuestLog helps you track quests, side-quests, and daily grinding. Complete a quest line to earn bonus experience points.'

Token count: 25
Token pieces: ['Quest', 'Log', ' helps', ' you', ' track', ' quests', ',', ' side', '-', 'quests', ',', ' and', ' daily', ' grinding', '.', ' Complete', ' a', ' quest', ' line', ' to', ' earn', ' bonus', ' experience', ' points', '.']

Naive word count: 18
Real token count: 25

Estimated input cost at $1.0/million tokens: $0.00002500
```

Notice the gap between the naive word count (18) and the real token count
(25) — exactly Lesson 03's core point. Several individual words split into
multiple tokens (`QuestLog` -> `Quest` + `Log`; `side-quests` -> `side` +
`-` + `quests`), and punctuation (commas, periods) each get their own
token, which a naive `.split()` on whitespace never counts as separate
units at all.

The estimated cost, `$0.00002500`, is a genuinely tiny number — this is
exactly why Lesson 00's setup could honestly frame real API usage as
costing "a fraction of a cent" per typical prompt: 25 input tokens at
$1.00/million tokens really is $0.000025.
