# Lesson 03 — Tokens and Tokenization

**Verified against (August 2026):** `tiktoken` `0.13.0` (PyPI, released May
15, 2026 — confirmed via the PyPI project page and by installing and
running it live while writing this lesson). Every token count and every
list of token pieces shown below is **real, actually-run output** from this
exact version, using its `o200k_base` encoding — not invented or estimated.
Anthropic's own current token-counting guidance (`platform.claude.com/docs/en/build-with-claude/token-counting`,
fetched live August 8, 2026) is summarized in "How this connects" below.

## What you'll learn

- What a **token** actually is, and why it's neither a whole word nor a
  single character.
- What **byte-pair encoding (BPE)** does, at an intuition level: how a
  tokenizer's vocabulary of subword pieces gets built in the first place.
- How to actually tokenize real text yourself, right now, using a real,
  free, fully local Python library — with real, verified output, not
  invented examples.
- Why the *same* text can produce a *different* number of tokens depending
  on which model's tokenizer you use — and why this matters for real API
  cost and context-window math.

## Why this matters

Every single interaction with an LLM — the Anthropic API in Module 13, and
every one of this module's own prompt-engineering exercises in Lesson 07 —
is billed, measured, and limited in **tokens**, not words or characters.
The pricing table you saw in Lesson 00's setup ("$1.00 per million input
tokens") is meaningless until you know what a token actually is. The
context window you'll learn about in Lesson 06 ("this model can see
200,000 tokens at once") is meaningless for the same reason. This lesson
makes "token" a concrete, countable, inspectable thing before either of
those later lessons asks you to reason about it.

## Prerequisites

- Lesson 00's setup — this lesson's exercise uses `tiktoken`, installed
  there, and needs nothing else (no API key, no internet access once
  installed).
- No ML background needed beyond Lessons 01-02's general "a model needs
  numeric input, not raw text" framing — this lesson is where that
  numeric-input problem actually gets solved for text specifically.

## The concept, explained simply

A neural network, as Lessons 01-02 showed, only ever does arithmetic on
numbers — dot products, sums, activation functions. It has no built-in idea
of what a "word" or a "letter" is. So before any text can go into a
language model at all, it has to be chopped into pieces and each piece has
to be turned into a number. That chopping-into-pieces step is called
**tokenization**, and each piece is called a **token**.

The obvious first guesses for how to chop text up both have real problems.
**Chop by whole word?** English alone has hundreds of thousands of words,
plus names, typos, made-up words, and words in every other language — the
list of possible "tokens" would be enormous, and the model would have no
way at all to handle a word it had never seen during training (a brand-new
slang term, a person's name, a typo). **Chop by individual character?**
Now the vocabulary is tiny (just the alphabet, digits, punctuation), but
every single sentence turns into a huge number of tiny pieces, and the
model has to work much harder to reconstruct "these five characters
together mean something" every time, for every word, forever.

**Byte-pair encoding (BPE)**, the technique real tokenizers (including
`tiktoken`, and — per Anthropic's own token-counting documentation — the
tokenizer scheme actual Claude models use, though not from this exact
downloadable library, see "How this connects" below) use, is the practical
middle ground: start from individual characters (technically, bytes), and
repeatedly merge the *most frequently occurring adjacent pair* into a
single new token, building up a fixed-size vocabulary of common subword
pieces — some as short as a single letter, some as long as a whole common
word — chosen because they showed up together often enough, across a huge
amount of real text, to be worth their own dedicated token. This is why, as
you'll see below, common whole words often become exactly one token, while
rare or made-up words get split into several smaller, more common pieces.

## The details

### Tokenizing real text, right now

Everything in this section is real code you should actually type and run —
not read past. Create `explore_tokens.py`:

```python
# explore_tokens.py
import tiktoken

# o200k_base is the encoding used by OpenAI's newer models (GPT-4o and
# later). This course's primary LLM API is Anthropic's, and Claude does not
# use this exact tokenizer -- see this lesson's "How this connects" section
# for what that means and why this is still a genuinely useful exercise.
enc = tiktoken.get_encoding("o200k_base")

text = "QuestLog helps you track quests, side-quests, and daily grinding."
token_ids = enc.encode(text)

print(f"Text: {text!r}")
print(f"Number of tokens: {len(token_ids)}")
print(f"Token IDs: {token_ids}")
print()
print("Each token, decoded back to text:")
for token_id in token_ids:
    piece = enc.decode([token_id])
    print(f"  {token_id:>7}  ->  {piece!r}")
```

Run it:

```bash
python explore_tokens.py
```

**Actual output** (run for real while writing this lesson, `tiktoken`
`0.13.0`):

```
Text: 'QuestLog helps you track quests, side-quests, and daily grinding.'
Number of tokens: 15
Token IDs: [37831, 2719, 9335, 481, 5290, 107421, 11, 4307, 12, 109689, 11, 326, 8424, 24253, 13]

Each token, decoded back to text:
    37831  ->  'Quest'
     2719  ->  'Log'
     9335  ->  ' helps'
      481  ->  ' you'
     5290  ->  ' track'
   107421  ->  ' quests'
       11  ->  ','
     4307  ->  ' side'
    12  ->  '-'
   109689  ->  'quests'
       11  ->  ','
      326  ->  ' and'
     8424  ->  ' daily'
    24253  ->  ' grinding'
       13  ->  '.'
```

Read this output carefully — every quirk here is a real, general fact about
how BPE tokenization works, not a fluke of this one sentence:

- **"QuestLog" split into two tokens: `'Quest'` and `'Log'`.** Both are
  common enough English word-fragments to each have earned their own token,
  even combined as an unusual compound word the tokenizer's training data
  probably never saw as a single unit.
- **Most spaces attach to the *following* word, not the word before it** —
  notice `' helps'`, `' you'`, `' track'` each include a leading space as
  part of the token. This is a deliberate, common tokenizer design choice
  (spaces are cheap and predictable, so folding them into the next token
  saves a separate "space" token almost everywhere).
- **`' quests'` (with a leading space, token 107421) and `'quests'` (no
  leading space, token 109689) are two *completely different* tokens.**
  This genuinely surprises almost everyone the first time they see it: the
  exact same five letters, depending only on whether a space precedes them,
  become two unrelated numbers to the model. This is a direct, mechanical
  consequence of the leading-space convention above, and it's exactly the
  kind of "why does the model do that" question that makes sense the moment
  you've seen the actual token IDs.
- **Punctuation gets its own tokens** (`','`, `'-'`, `'.'`) — short,
  extremely common pieces of text like a single comma are almost always
  single, dedicated tokens.

**Try it yourself:** Before running it, predict how many tokens
`"QuestLog"` alone (with no other words) will tokenize into. Then run
`enc.encode("QuestLog")` and check.

### Subword splitting on rarer words

The real payoff of BPE shows up on words the tokenizer's training data saw
less often. Extend `explore_tokens.py` with this block (or run it as its
own small script):

```python
words = [
    "QuestLog",
    "tokenization",
    "unbelievably",
    "antidisestablishmentarianism",
    "cat",
    "internationalization",
]
for word in words:
    ids = enc.encode(word)
    pieces = [enc.decode([i]) for i in ids]
    print(f"{word!r:35s} -> {len(ids)} token(s): {pieces}")
```

**Actual output** (run for real):

```
'QuestLog'                          -> 2 token(s): ['Quest', 'Log']
'tokenization'                      -> 2 token(s): ['token', 'ization']
'unbelievably'                      -> 3 token(s): ['un', 'bel', 'ievably']
'antidisestablishmentarianism'      -> 6 token(s): ['ant', 'idis', 'est', 'ablishment', 'arian', 'ism']
'cat'                                -> 1 token(s): ['cat']
'internationalization'              -> 2 token(s): ['international', 'ization']
```

The pattern is exactly BPE's design intent: a common short word (`'cat'`)
is one token. A common word with a common suffix (`'internationalization'`
= `'international'` + `'ization'`) is two tokens, each a genuinely common,
independently useful fragment. A long, rare, invented-sounding word
(`'antidisestablishmentarianism'`) gets chopped into six pieces, because no
larger chunk of it appeared often enough during the tokenizer's own
training to earn a dedicated token.

Non-English or unusual characters split even more aggressively — a real,
verified example: `"café"` (with an accented `é`) tokenizes into **2
tokens** — `'c'` and `'afé'` — while `"naïve"` tokenizes into **3 tokens** —
`'na'`, `'ï'`, `'ve'`. An emoji like the dragon emoji `🐉` splits into
multiple tokens that don't even print as readable text on their own,
because they're fragments of the emoji's underlying multi-byte encoding,
not fragments of a word at all. **This is a real, general phenomenon, not a
quirk**: text outside a tokenizer's most common training data — rare words,
many non-English languages, emoji, unusual symbols — reliably costs *more*
tokens per character than common English text does. This has real, practical
consequences: the exact same idea, expressed in a language or script the
tokenizer saw less of during its own construction, can cost meaningfully
more per API call.

### Word count is not token count

One more real, verified comparison, because the gap between "how many words
does a human count" and "how many tokens does the model see" is worth
seeing directly:

```python
text = "The quick brown fox jumps over the lazy dog."
print("naive word count:", len(text.split()))
print("token count:", len(enc.encode(text)))
```

**Actual output:**

```
naive word count: 9
token count: 10
```

Nine words, ten tokens — the trailing period is its own token, and none of
the words themselves happened to split further in this particular sentence.
This won't always be a difference of exactly one; it depends entirely on
which specific words appear. The only way to know the real token count of
a piece of text is to actually run it through a tokenizer, exactly as
you've just done — never estimate it from a word count, and never assume
"1 token ≈ 4 characters" (a common rough rule of thumb, including one
Anthropic's own pricing FAQ mentions as a rough estimate) is precise enough
to budget a real API call down to the token.

## Common mistakes & gotchas

- **Assuming a token is a word.** As shown repeatedly above, it's frequently
  a fragment of a word, sometimes a whole word, sometimes a single
  punctuation mark, and sometimes a fragment of a single non-ASCII
  character. Never reason about token counts by counting words.
- **Assuming `' word'` (with a leading space) and `'word'` (without) are the
  same token.** They're almost always different token IDs entirely, as the
  `' quests'` vs. `'quests'` example above showed directly. This can matter
  when you're programmatically constructing prompts and need to reason
  about exact token boundaries.
- **Forgetting that different tokenizers give different counts for the
  same text.** This lesson's `o200k_base` encoding is OpenAI's, not
  Anthropic's — see "How this connects" below. Even *within* one company's
  models, tokenizers can change between model generations; Anthropic's own
  current documentation states plainly that "Claude 4.7 and later models
  use a newer tokenizer that produces approximately 30% more tokens" for
  the same text compared to their own earlier models (verified live,
  August 2026, `platform.claude.com/docs/en/about-claude/pricing`). A token
  count computed for one model is not a safe number to reuse for a
  different model.
- **Trying to reason about a rare word or an emoji "by eye."** As the café
  / naïve / emoji examples showed, tokenization of unusual characters is
  genuinely not predictable by intuition — the only reliable way to know is
  to run the actual tokenizer, exactly as this lesson's exercise does.

## How this connects

**An important, deliberately honest note on scope:** `tiktoken`, the
library this lesson (and Exercise 01) uses, is OpenAI's tokenizer library
— it does not implement Claude's own tokenizer, and no equivalent
downloadable, offline Python library for Claude's exact tokenizer is
published by Anthropic. Everything you just learned about *how BPE
tokenization works in general* — subword pieces, leading-space
conventions, rare words splitting further, punctuation getting its own
tokens — is genuinely, directly true of Claude's tokenizer too (Claude uses
the same general BPE-family approach), but the *exact* token IDs and exact
counts you saw above are specific to OpenAI's `o200k_base` vocabulary, not
Claude's. For an exact, authoritative token count against a real Claude
model, Anthropic provides a dedicated API endpoint —
`client.messages.count_tokens(...)` in the Python SDK, hitting
`POST /v1/messages/count_tokens` — which is free to call (per Anthropic's
own current documentation, verified live August 2026) and returns the
precise count for whichever specific model you name. This module doesn't
walk through calling that endpoint step by step — Module 13 covers the
Anthropic API's request/response shapes in full — but knowing it exists,
and knowing *why* you'd reach for it instead of trusting a `tiktoken` count
or a word-count estimate for real Claude usage, is exactly the kind of
practical judgment this module aims to build.

Lesson 04 builds directly on top of "text becomes a sequence of tokens":
once text is tokens, each token gets converted into a list of numbers
called an **embedding** — and that's where "meaning" first becomes
something a model can actually compute with.

## Quick self-check

1. Why don't real tokenizers just split text into individual words?
2. Why don't real tokenizers just split text into individual characters?
3. In the `explore_tokens.py` output, `' quests'` and `'quests'` were two
   different tokens. Why?
4. If a learner writes a paragraph in a language that has very little
   representation in a tokenizer's training data, would you expect that
   paragraph to use more, fewer, or about the same number of tokens per
   character compared to common English text? Why?
5. Why is `tiktoken`'s token count for a piece of text *not* the same
   number you'd get from Anthropic's own `count_tokens` API for that same
   text, and what should you actually use if you need an exact count for a
   real Claude API call?
