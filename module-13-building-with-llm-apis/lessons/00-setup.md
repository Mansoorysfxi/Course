# Lesson 00 — Setup: A Real Anthropic API Key, the SDK, and What It Actually Costs

**Verified against (August 2026), via live fetch of official sources on
August 9, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| `anthropic` Python SDK latest version | `0.121.0`, released August 7, 2026 | PyPI project page (`pypi.org/project/anthropic/`), fetched live |
| Claude Haiku 4.5 pricing (this module's model of choice — see below) | $1.00 / million input tokens, $5.00 / million output tokens | Anthropic's own current pricing page, `platform.claude.com/docs/en/about-claude/pricing`, fetched live |
| Claude Haiku 4.5 context window | 200,000 tokens | Verified in Module 12 (`platform.claude.com/docs/en/build-with-claude/context-windows`); re-confirmed unchanged this module |
| Structured outputs (Lesson 03) support Claude Haiku 4.5 | Yes — `claude-haiku-4-5-20251001` is on Anthropic's own current supported-model list for `output_config.format` | `platform.claude.com/docs/en/build-with-claude/structured-outputs`, fetched live |
| The SDK auto-retries transient errors | Yes — connection errors, 408, 409, 429, and 5xx, with exponential backoff, `max_retries=2` by default | Anthropic's own Python SDK reference documentation |

Module 12's own setup lesson verified `anthropic` `0.121.0` and Claude
Haiku 4.5's pricing one day before this lesson was written (August 8,
2026) — this table independently re-fetched both facts rather than
assuming a single day couldn't have changed anything, per this course's
own Rule 7 discipline. Both are unchanged.

## What you'll learn

- Exactly what this module costs, in real dollars, if you run every
  exercise and the capstone live — and why that cost is worth paying now
  rather than deferring.
- How to get a real Anthropic API key and install the `anthropic` Python
  SDK, on top of the FastAPI/Postgres/Redis environment Modules 05-11
  already set up.
- How to verify the SDK is installed correctly (with or without a key
  yet) and, if you do have a key, that a real, tiny, live call works.

## Why this matters

Module 12 could teach tokens, embeddings, context windows, and sampling
entirely with free, local, offline tools — `tiktoken` and
`sentence-transformers` never touch a paid API. This module is different,
and honestly so: **every exercise from Lesson 01 onward, and the entire
QuestLog AI-assistant capstone, genuinely needs a real Anthropic API key
to run live.** There is no free, local substitute for "call a real,
hosted large language model and observe what it actually does" — that is
the entire subject of this module. This lesson states the real cost
plainly, the same way Module 09 did for a VPS and Module 11 did for a
domain name, so you can make an informed decision before spending
anything.

## Prerequisites

- **Module 01's Python setup** — a working Python 3.10+ environment,
  comfort with `venv` and `pip`. This module's exercises are plain Python
  scripts, same as Module 12's.
- **Module 12 in full** — this module assumes you already know what a
  token, a context window, temperature/sampling, and prompt-engineering
  technique (system prompts, few-shot, chain-of-thought, "ask for JSON")
  are. If any of those feel shaky, revisit Module 12's Lessons 03, 04, 06,
  and 07 before continuing — this module builds directly on top of that
  vocabulary and will not re-teach it.
- **Module 11's finished QuestLog codebase** — this module's capstone
  (Lessons 07-08, `project/questlog/`) extends the exact backend/frontend
  Module 11 left off with, unchanged except for this module's own,
  documented additions. You don't need to have that project running yet
  to do Lessons 00-06's standalone exercises, but you will for Lessons
  07-08.

## The concept, explained simply

Think of the difference between Module 12's tools and this module's API
the way you'd think about the difference between a physics calculation
you can run entirely on your own machine versus renting time on someone
else's supercomputer cluster. `tiktoken` and `sentence-transformers` are
small enough, and their models are freely distributable enough, that they
run entirely on your laptop, for free, forever. A frontier LLM like
Claude is not that kind of thing — the model itself is enormous, runs on
specialized hardware Anthropic operates, and answering even one request
costs Anthropic real compute. An API key is your credential for renting a
small, metered slice of that compute, billed by how much you actually
use — and, as this lesson's cost table below shows, "how much you
actually use" for this entire module is genuinely small money, not a
real financial decision.

## The details

### Step 1 — Get a real Anthropic API key

Go to `console.anthropic.com`, create an account (or sign in, if Module 12
already had you make one), and generate a key from the **API Keys**
section. New accounts typically start with a small amount of free credit
— Anthropic's own pricing FAQ mentions this without committing to a
specific figure, since promotional amounts change; check the console
itself for your account's current starting balance rather than trusting
a number quoted here.

**Frame this as groundwork, not a one-off expense.** The key you create
now is the exact same key Modules 14 (RAG) and 15 (Agents/final capstone)
will keep using — you are not paying this cost three separate times, you
are paying it once, here, because this is the first module that
genuinely needs it.

### Step 2 — What this module will actually cost you

Every exercise in this module uses **Claude Haiku 4.5** (`claude-haiku-4-5`)
— the same cheapest-and-fastest model Module 12's Lesson 07 used, and the
model QuestLog's own AI feature (Lessons 07-08) is built on. At the rates
verified in this lesson's header table ($1.00 / million input tokens,
$5.00 / million output tokens), a single exercise call — a short prompt,
a short response, a few hundred tokens each way — costs a small fraction
of a cent.

Here's a real, worked estimate, not a guess: this module has 5 exercises,
plus the capstone. If you ran every exercise 3-4 times each while
experimenting (the realistic, generous case — trying a prompt, seeing what
happens, tweaking it, running again), that's on the order of 20-25 live
calls, each roughly 500-900 input tokens (system prompt + tool/schema
overhead — Lesson 04 explains exactly why tool definitions add real
tokens) and 100-300 output tokens. That works out to:

| Item | Rough total tokens | Cost |
|---|---|---|
| ~25 calls × ~700 input tokens | ~17,500 input tokens | 17,500 / 1,000,000 × $1.00 ≈ **$0.018** |
| ~25 calls × ~200 output tokens | ~5,000 output tokens | 5,000 / 1,000,000 × $5.00 ≈ **$0.025** |
| **Total, generous estimate** | | **well under $0.10** |

Even doubling every number for extra experimentation, this module's exercises
realistically cost **under a quarter**, total. The capstone (Lessons
07-08) adds a handful more calls while you're testing QuestLog's real
`/suggest-breakdown` endpoint by hand — the same order of magnitude, not
a new category of cost. This is the same "real, but genuinely tiny, and
clearly disclosed" framing Module 09 used for a VPS, Module 11 used for a
domain name, and Module 12 used for its own optional Lesson 07 — not
free, but not a real financial decision either.

### Step 3 — Set the key as an environment variable

Never write a real key directly into a `.py` file or commit it to Git —
Module 07's whole `SECRET_KEY` lesson (`lessons/11-secrets-config-and-logging.md`
in that module) already established exactly why, and the same reasoning
applies to any secret, this one included.

```bash
export ANTHROPIC_API_KEY="sk-ant-...your-real-key..."
```

As Module 12's own setup lesson noted, this only lasts for your current
terminal session — re-run it in whichever terminal you're actually
working in for this module's exercises. Lesson 07's capstone work uses a
`.env` file instead (via `pydantic-settings`, exactly like Module 07's
`SECRET_KEY`) so QuestLog's own backend doesn't need this `export` at
all — see that lesson.

### Step 4 — Install the `anthropic` SDK

```bash
cd module-13-building-with-llm-apis
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows
pip install anthropic
```

**Expected:** pip resolves and installs `anthropic` and its dependencies
(`httpx`, `pydantic`, `distro`, `jiter`, `sniffio`) with no errors, ending
in a line like `Successfully installed anthropic-0.121.0 ...` (or newer —
this course pins the version it verified against, but a newer patch
release is fine; the core `client.messages.create(...)` shape this module
teaches has been stable for a long time).

**This install step needs no API key at all.** If you're deferring Step 1
for now, you can still do this step, and every exercise's own
`INSTRUCTIONS.md` will tell you exactly which parts need a real key and
which don't.

## Verify your setup

**1. Python version (should already be true from Module 01):**
```bash
python --version
```
**Expected:** `Python 3.10.x` or newer.

**2. `anthropic` SDK installs and imports correctly, with or without a key:**
```bash
python -c "import anthropic; print(anthropic.__version__)"
```
**Expected:** `0.121.0` (or newer). This succeeds even with no
`ANTHROPIC_API_KEY` set at all — importing the library and checking its
version does no network activity and needs no credentials. This is
exactly why this module's backend tests (Lesson 07) never need a real
key either: constructing the client is cheap and safe; only actually
*calling* the API needs credentials.

**3. (Only if you completed Step 1) Your key is set:**
```bash
echo $ANTHROPIC_API_KEY
```
**Expected:** your real key prints, starting with `sk-ant-`.

**4. (Only if you completed Steps 1 and 3) A real, tiny, live API call works:**
```bash
python -c "
import anthropic
client = anthropic.Anthropic()
message = client.messages.create(
    model='claude-haiku-4-5',
    max_tokens=20,
    messages=[{'role': 'user', 'content': 'Say hello in exactly three words.'}],
)
print(message.content[0].text)
"
```
**Expected:** a short response of some kind, printing roughly three
words — the exact wording isn't guaranteed to be identical every run
(Module 12, Lesson 06's sampling material, made concrete again). This one
call costs a small fraction of a cent, well under $0.001 at the rates
verified above.

If checks 1-2 pass (and 3-4, if you did Steps 1 and 3), you're ready for
Lesson 01.

**Try it yourself:** Run check 4's command a second time with a different
instruction ("Say goodbye in exactly five words," for instance) and
predict, before running it, roughly how many output tokens it will use —
then check `message.usage.output_tokens` (Lesson 01 explains exactly what
`usage` is) against your prediction.

## Common mistakes & gotchas

- **`ModuleNotFoundError: No module named 'anthropic'`.** Your virtual
  environment isn't activated — check for `(venv)` in your prompt, and if
  it's missing, re-run `source venv/Scripts/activate` from inside
  `module-13-building-with-llm-apis/`.
- **`anthropic.AuthenticationError: ... invalid x-api-key`.** Almost
  always means `ANTHROPIC_API_KEY` isn't actually set in the terminal
  you're running from, or you copy-pasted the key with extra whitespace
  or a missing character. Re-check with `echo $ANTHROPIC_API_KEY` (check
  3 above) before assuming anything else is wrong.
- **Forgetting the key doesn't persist across terminals.** Exactly the
  same gotcha Module 12's setup lesson called out — plain `export` only
  lasts for the current shell session. Re-run it, or (better, for the
  capstone specifically) use the `.env`-file approach Lesson 07 sets up,
  which persists on disk.
- **Assuming the SDK needs a key just to install or import.** It doesn't
  — see Verify Step 2 above. If you're not ready to spend anything yet,
  you can still install the SDK, read every lesson in full, and treat
  every "a response along these lines" example honestly (see the next
  section) as your dry-run path through this module, exactly as Module 12
  accepted for its own Lesson 07.
- **Rate limits (`anthropic.RateLimitError`) on a brand-new account.**
  Rare at this module's tiny call volume, but if it happens, it's not a
  sign anything is broken — Lesson 05 covers exactly what a rate limit is
  and how the SDK already handles it for you automatically in most cases.

## How this connects

Every exercise from here on assumes the SDK verified above is installed,
and treats a real API key as genuinely necessary (unlike Module 12, which
had free local alternatives for its own core material) while still being
honest, per this lesson's cost table, that the total spend involved is
small. Wherever an exercise or lesson shows the *exact text* Claude
generated for a specific prompt, and no live key was available while
writing that content, it is explicitly labeled "a response along these
lines" — Module 12, Lesson 07's own convention, continued here — rather
than presented as something directly observed. Lesson 01 starts exactly
where this lesson leaves off: a working key, a working SDK, and your
first real call.

## Quick self-check

1. Why can't this module's core material be taught with a free, local
   tool the way Module 12's tokenization and embeddings lessons were?
2. Roughly how much would running every exercise in this module several
   times over, live, actually cost — and why does that number matter for
   deciding whether to get a key now?
3. What is the one command in this lesson that succeeds with **no** API
   key set at all, and why does that matter for this module's later
   backend tests?
4. Why does this lesson tell you to set your API key as an environment
   variable (or, later, a `.env` file) instead of writing it directly
   into a Python file?
5. If you skip getting an API key entirely for now, what can you still
   get out of this module's lessons, and what will you genuinely not be
   able to do?
