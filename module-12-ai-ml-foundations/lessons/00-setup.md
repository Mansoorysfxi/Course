# Lesson 00 — Setup: Free Tools, an Optional API Key, and Verifying Everything Works

**Verified against (August 2026), via live web search/direct fetch of
official sources — see each row:**

| Fact | Verified value | Source |
|---|---|---|
| `tiktoken` latest version | `0.13.0`, released May 15, 2026 | PyPI project page (`pypi.org/project/tiktoken/`) |
| `tiktoken` cost/account requirements | Free, open-source, MIT-licensed; runs fully offline once installed; no API key, no account, no network access needed at run time | PyPI project page + confirmed by actually installing and running it offline in this course's own generation process |
| `sentence-transformers` latest version | `5.7.0`, released August 6, 2026 | PyPI project page (`pypi.org/project/sentence-transformers/`) |
| `sentence-transformers` requirements | Python 3.10+, PyTorch 1.11.0+, `transformers` 4.41.0+; installs via `pip install -U sentence-transformers` | PyPI project page |
| `all-MiniLM-L6-v2` embedding model | A small (~90 MB), free, openly-licensed sentence-embedding model that produces 384-dimensional vectors; downloads once from Hugging Face and then runs fully offline | Hugging Face model card (`huggingface.co/sentence-transformers/all-MiniLM-L6-v2`) |
| `anthropic` Python SDK latest version | `0.121.0`, released August 7, 2026 | PyPI project page (`pypi.org/project/anthropic/`) |
| Claude Haiku 4.5 pricing | $1.00 per million input tokens, $5.00 per million output tokens (standard, non-batch pricing) | Anthropic's own current pricing page, `platform.claude.com/docs/en/about-claude/pricing`, fetched live August 8, 2026 |
| Claude Haiku 4.5 context window | 200,000 tokens | Anthropic's own current context-windows page, `platform.claude.com/docs/en/build-with-claude/context-windows`, fetched live August 8, 2026 |

## What you'll learn

- Exactly which tools this module uses, and — for each one — whether it
  costs anything to install, to run, or to complete the module.
- How to install `tiktoken` and `sentence-transformers` in a normal Python
  virtual environment (the same kind Module 01 taught) with no API key and
  no account of any kind.
- How to (optionally) get an Anthropic API key for Lesson 07's
  prompt-engineering exercises, and exactly what it would cost you to run
  every example in that lesson for real.
- How to verify every piece of this setup actually works, with exact
  commands and exact expected output.

## Why this matters

Every lesson from here on assumes you have a working Python environment
(from Module 01) and, starting at Lesson 03, two specific free libraries
installed. Just like Module 09's VPS lesson and Module 11's Render/Sentry
lesson, this setup lesson states plainly, up front, exactly what's free and
what's optional-and-paid, so you never have to guess whether continuing
costs you money. Short version, expanded fully below: **the tokenization
and embeddings tooling is entirely free and runs on your own machine with no
account of any kind. Only Lesson 07's live-API prompting exercises touch a
paid service, and even that is optional, with a real current price quoted
below and a fully legitimate zero-cost alternative (reading the lesson's own
worked examples) if you'd rather not spend anything at all right now.**

## Prerequisites

- **Module 01's setup lesson** — a working Python 3.10+ installation (this
  module's libraries require at least Python 3.10; if you're on an older
  3.x you'll need to upgrade), comfort creating and activating a virtual
  environment (`venv`), and `pip`.
- A normal broadband connection for two one-time downloads: the Python
  packages themselves (a few hundred MB total, mostly from
  `sentence-transformers`' PyTorch dependency) and, the first time you run
  the embeddings exercise, a roughly 90 MB model file from Hugging Face.
  After that first download, everything in Lessons 03-04's exercises runs
  fully offline.

## The concept, explained simply

Think of this module's setup the way you'd think about installing a local
physics-debugging tool versus signing up for a paid cloud build farm. The
debugging tool (`tiktoken`, `sentence-transformers`) runs entirely on your
own machine, does real, useful, inspectable work, and costs nothing beyond
the disk space and download time. The cloud build farm (the Anthropic API)
is a genuinely different kind of thing — a hosted service run by someone
else's hardware, billed by usage — and it's the *right* tool for Lesson 07's
job (you cannot run a frontier LLM on a laptop), but it's optional here
specifically because this module's core concepts don't require it. You're
choosing the free local tool whenever it does the job, and reaching for the
paid hosted one only where the job genuinely needs it.

## The details

### Step 1 — Confirm your Python version

This module's embedding library needs Python 3.10 or newer (tiktoken has no
such restriction, but sentence-transformers does). Check what you have:

```bash
python --version
```

**Expected:** `Python 3.10.x` or newer. This course's own reference
environment used Python 3.12.2, and Python 3.14.x is current stable as of
this module's writing (per Module 01's own setup lesson) — either is fine,
as is anything at or above 3.10. If you're below 3.10, revisit Module 01's
setup lesson for how to install a current Python on Windows before
continuing.

### Step 2 — Create a fresh virtual environment for this module

Exactly the workflow Module 01 taught — a dedicated `venv` keeps this
module's packages from cluttering (or conflicting with) anything else on
your machine.

```bash
cd module-12-ai-ml-foundations
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows
```

**Expected:** your shell prompt gains a `(venv)` prefix, and
`which python` (or `where python` in cmd.exe) points inside this new
`venv` folder rather than your system Python.

### Step 3 — Install the two free, local libraries

```bash
pip install tiktoken sentence-transformers
```

**Expected:** pip resolves and installs both packages plus their
dependencies (this pulls in PyTorch as a dependency of
`sentence-transformers`, which is the largest single download — expect this
step to take a few minutes and a few hundred MB of disk space, one time
only). No errors at the end; the last line should look like
`Successfully installed ... sentence-transformers-5.7.0 ... tiktoken-0.13.0 ...`
(exact dependency versions will vary; the two package names and the
versions shown are what this lesson verified against).

**Neither of these packages requires an account, an API key, or any
network access to actually *run*** — `tiktoken`'s tokenizer data ships
inside the package itself, and `sentence-transformers`' model weights are
downloaded once (Step 4 below) and cached locally afterward.

### Step 4 — Do the one-time model download

`sentence-transformers` doesn't ship its models inside the pip package —
the actual neural network weights (the small `all-MiniLM-L6-v2` model this
module uses) download from Hugging Face the first time you load them, then
get cached on disk (by default under `~/.cache/huggingface/` on Linux/macOS
or `%USERPROFILE%\.cache\huggingface\` on Windows) for every run after
that. Trigger this download now, deliberately, so it doesn't surprise you
mid-exercise:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Expected:** a progress indicator while ~90 MB of model files download
(this took well under a minute on a normal connection when this lesson was
verified), then the command exits with no error and no other output. If you
run this exact command a second time, it should return almost instantly —
that's the cache working.

### Step 5 — (Optional) Get an Anthropic API key for Lesson 07

Skip this step entirely if you'd rather not spend anything right now —
Lesson 07 is still fully readable and its worked examples are still fully
explained without ever running a live API call yourself, and this module's
capstone (`project/BRIEF.md`) has an explicit, fully-accepted dry-run path
if you choose to skip live API calls throughout the whole module.

If you do want to run real prompts against a real model — which is
genuinely the best way to build intuition for prompt engineering, and which
you'll need anyway starting in Module 13 — go to `console.anthropic.com`,
create an account, and generate an API key from the **API Keys** section of
the console. New accounts typically receive a small amount of free credit
to start (Anthropic's own FAQ on its pricing page notes this, without
committing to a specific dollar figure, since promotional credit amounts
change over time — check the console itself for your account's current
starting balance rather than trusting a number quoted here). Beyond any
starting credit, real usage is billed per token at the rates in this
lesson's header table above.

**Exactly what this would cost you for real:** Lesson 07's exercises use
Claude Haiku 4.5 (`claude-haiku-4-5`), Anthropic's cheapest current model,
specifically chosen for this kind of cheap, fast experimentation. At
$1.00 per million input tokens and $5.00 per million output tokens
(verified above), a single short prompt-and-response exchange — a few
hundred tokens in, a few hundred out — costs a small fraction of a cent.
Running every single example in Lesson 07 and Exercise 03 for real, several
times over while experimenting, would realistically cost you well under
ten cents total. This is the same "real, but genuinely tiny, and clearly
disclosed" framing Module 09 used for a VPS and Module 11 used for a domain
name — not free, but not a real financial decision either.

Once you have a key, set it as an environment variable rather than ever
typing it into a file this course (or you) might commit to Git:

```bash
export ANTHROPIC_API_KEY="sk-ant-...your-real-key..."
```

**Never put a real API key directly in a `.py` file or commit it to Git.**
Reading it from an environment variable, as shown above and as the SDK does
automatically, keeps it out of your source code entirely.

### Step 6 — (Optional) Install the Anthropic SDK

Only needed if you're doing Step 5. This module doesn't need it for
anything else.

```bash
pip install anthropic
```

**Expected:** `Successfully installed anthropic-0.121.0` (or newer — check
`pip show anthropic` if a newer version has shipped since this lesson was
verified; the SDK's core `client.messages.create(...)` call shape used in
this module has been stable for a long time and isn't expected to break).

## Verify your setup

Run through every check below before starting Lesson 01. Checks 1-4 are
required for every learner; checks 5-6 only apply if you did the optional
Steps 5-6.

**1. Python version:**
```bash
python --version
```
**Expected:** `Python 3.10.x` or newer.

**2. `tiktoken` installed and working, fully offline:**
```bash
python -c "import tiktoken; enc = tiktoken.get_encoding('o200k_base'); print(len(enc.encode('Hello, QuestLog!')))"
```
**Expected:** a small integer printed (this exact string tokenizes to `5`
tokens with the `o200k_base` encoding this module uses — Lesson 03 explains
exactly why it isn't a plain word count). No network activity should be
required for this command to succeed — try it with your Wi-Fi briefly
turned off if you want to confirm this yourself.

**3. `sentence-transformers` installed, model cached, and working:**
```bash
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
emb = model.encode('Hello, QuestLog!')
print(emb.shape)
"
```
**Expected:** `(384,)` — a 384-dimensional vector, printed with no errors.
This should run in well under a second if Step 4's download already
happened (the model loads from your local cache).

**4. Both together, in a fresh shell (confirms nothing was a fluke of your
current terminal session):** close and reopen your terminal, re-activate
the `venv` (`source venv/Scripts/activate`), and re-run checks 2 and 3.
Same expected output both times.

**5. (Only if you did Step 5) API key is set:**
```bash
echo $ANTHROPIC_API_KEY
```
**Expected:** your real key prints, starting with `sk-ant-`. If this is
empty, the export from Step 5 didn't persist — environment variables set
with `export` only last for the current terminal session unless you add
them to your shell's startup file (e.g. `~/.bashrc` for Git Bash); for this
module, just re-run the `export` line in the terminal you're actually
working in.

**6. (Only if you did Steps 5-6) A real, tiny, live API call works:**
```bash
python -c "
import anthropic
client = anthropic.Anthropic()
msg = client.messages.create(
    model='claude-haiku-4-5',
    max_tokens=20,
    messages=[{'role': 'user', 'content': 'Say hello in exactly three words.'}],
)
print(msg.content[0].text)
```
**Expected:** a short response printing three words of some kind (the exact
wording is up to the model and isn't guaranteed to be identical every run —
that unpredictability is itself a preview of Lesson 06's sampling
material). This one real call costs a fraction of a cent, well under
$0.001 at the rates above.

If every check you attempted matches, you're ready for Lesson 01.

**Try it yourself:** Before moving on, run check 2's command a second time
with a completely different sentence of your own choosing, and predict the
token count before running it. You'll almost certainly be off by a little —
that's normal, and exactly what Lesson 03 exists to fix.

## Common mistakes & gotchas

- **"`ModuleNotFoundError: No module named 'tiktoken'`" (or
  `sentence_transformers`).** Almost always means your virtual environment
  isn't activated — check for the `(venv)` prefix in your prompt, and if
  it's missing, re-run `source venv/Scripts/activate` from inside
  `module-12-ai-ml-foundations/`.
- **The `sentence-transformers` install seems to hang or takes a very long
  time.** This is very likely genuinely working, not frozen — installing
  PyTorch (a dependency) downloads several hundred MB and can legitimately
  take a few minutes on a slower connection. Give it time before
  interrupting; interrupting mid-install and re-running `pip install` is
  safe (pip resumes/re-downloads as needed) if you do give up and retry.
- **The first `SentenceTransformer('all-MiniLM-L6-v2')` call is slow, but
  every call after that is instant.** This is expected and is exactly what
  Step 4 above walks you through deliberately — the first call downloads
  and caches the model; every later call in this module (including your
  exercise runs) reuses that cache and is fast.
- **Disk space.** Between PyTorch and the cached model, expect this
  module's `venv` plus Hugging Face cache to use a few hundred MB to
  slightly over a gigabyte of disk space total. This is normal for a local
  ML library and isn't a sign anything went wrong.
- **"My `ANTHROPIC_API_KEY` environment variable disappears every time I
  open a new terminal."** Environment variables set with plain `export` in
  Git Bash only last for that one terminal session. That's fine for this
  module — just re-run the `export` line in whichever terminal you're
  actually working in when you get to Lesson 07 or Exercise 03. Module 13
  will show a more permanent way to manage this once QuestLog itself needs
  the key.
- **A live API call returns a `401` / authentication error.** Almost
  always means `ANTHROPIC_API_KEY` isn't actually set in the terminal
  you're running from — re-check with `echo $ANTHROPIC_API_KEY` (check 5
  above) before assuming anything else is wrong.

## How this connects

This is the only setup lesson in this module — everything from Lesson 01
onward assumes the two free libraries verified above are installed and
working, and treats the optional API key as exactly that: optional, checked
for explicitly wherever Lesson 07 or Exercise 03 needs it, never silently
assumed. Module 13's own setup lesson will ask you to re-verify this same
Anthropic API key still works, exactly the way this course re-verifies
earlier setup at the start of every module that depends on it (Rule 8).

## Quick self-check

1. Which two Python libraries does this module require, and which of them
   (if either) needs an API key or an internet connection to actually run,
   once installed?
2. What is cached on your first run of `SentenceTransformer('all-MiniLM-L6-v2')`,
   and why does the second run go so much faster?
3. Roughly how much would it cost, in real dollars, to run every one of
   Lesson 07's live examples once each against Claude Haiku 4.5, at the
   pricing verified in this lesson's header table?
4. Why does this lesson tell you to set your API key as an environment
   variable instead of writing it directly into a Python file?
5. If you skip Step 5 entirely and never get an API key, what specifically
   can you still do in this module, and what specifically can't you do?
