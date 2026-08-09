"""Splits a raw quest note's text into smaller pieces ("chunks") -- NEW in
Module 14. See lessons/02-chunking-strategies.md for the full "why chunk
at all" explanation (short version: an embedding model, and the context
you hand an LLM, both work far better over a handful of focused
paragraphs than over one giant wall of text -- see that lesson's
"streaming a level in cells" analogy).

Pure Python, zero dependencies beyond the standard library, on purpose --
this is the one piece of this module's whole RAG pipeline that needs no
database, no model, and no network to test, and tests/test_chunking.py
takes full advantage of that.

**The strategy, decided in lessons/02 and used exactly as described
there:** paragraph-first. Split the input on blank lines (`\n\n`) --
matching how a human naturally separates distinct thoughts when typing a
note -- and treat each resulting paragraph as one chunk. Any single
paragraph that's still longer than `max_chunk_chars` (an unusually long
wall of text with no blank lines in it at all) falls back to a fixed-size
split with overlap, so no single chunk this function ever produces
exceeds `max_chunk_chars` by more than a rounding amount.

Characters, not tokens, are used to measure chunk size -- a deliberate
simplification (see lessons/02's "characters vs. tokens" section) that
avoids pulling in a second tokenizer dependency (this course already uses
`tiktoken` in Module 12, but that library counts tokens for OpenAI-family
models, not Claude, and this feature's own embedding model has yet a
different tokenizer again) just to measure chunk size approximately.
`max_chunk_chars=800` and `overlap_chars=150` are this module's own
decided defaults (roughly 150-200 tokens at the commonly-cited "~4
characters per token" rule of thumb) -- see lessons/02's own header table
for the current, honestly-labeled research this default is based on.
"""


def chunk_text(text: str, max_chunk_chars: int = 800, overlap_chars: int = 150) -> list[str]:
    """Returns a list of non-empty, whitespace-trimmed chunks, in the
    original order they appeared in `text`. Never returns an empty list
    for non-empty input containing at least one non-whitespace character;
    returns an empty list if `text` is empty or entirely whitespace, since
    there is nothing to chunk.

    Two passes: first split on paragraph boundaries (a blank line -- one
    or more fully-empty lines between two chunks of text), then, for any
    single paragraph still too long, further split it with
    `_split_with_overlap` below. Most quest notes (a few sentences to a
    few short paragraphs, per this module's own scope decision -- see
    lessons/00-setup.md) never hit the second pass at all; it exists for
    the unusual case of one long paragraph with no blank lines in it.
    """
    stripped = text.strip()
    if not stripped:
        return []

    # `splitlines()` then regrouping, rather than a single `text.split("\n\n")`,
    # so that notes using Windows-style "\r\n" line endings, or more than
    # exactly two consecutive newlines between paragraphs, both still
    # split correctly -- a paragraph boundary is "one or more blank
    # lines," not literally the two-character string "\n\n".
    raw_paragraphs: list[str] = []
    current_lines: list[str] = []
    for line in stripped.splitlines():
        if line.strip() == "":
            if current_lines:
                raw_paragraphs.append("\n".join(current_lines).strip())
                current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        raw_paragraphs.append("\n".join(current_lines).strip())

    chunks: list[str] = []
    for paragraph in raw_paragraphs:
        if not paragraph:
            continue
        if len(paragraph) <= max_chunk_chars:
            chunks.append(paragraph)
        else:
            chunks.extend(_split_with_overlap(paragraph, max_chunk_chars, overlap_chars))
    return chunks


def _split_with_overlap(text: str, max_chunk_chars: int, overlap_chars: int) -> list[str]:
    """The fixed-size-with-overlap fallback, used only for a single
    paragraph that's already longer than `max_chunk_chars` on its own
    (chunk_text's normal paragraph-based path never calls this for
    anything shorter). Each chunk after the first starts `overlap_chars`
    characters before the previous chunk ended, so a sentence that would
    otherwise land exactly on a cut point still appears in full inside at
    least one chunk. See lessons/02-chunking-strategies.md's "why overlap
    at all, and why this course doesn't treat it as settled science" box
    for the honest, current (still-debated) research this default is
    based on.
    """
    if overlap_chars >= max_chunk_chars:
        # A misconfiguration that would otherwise never advance (the next
        # window would start at or before where the current one started),
        # looping forever. Guarded here, not just documented, so a bad
        # call from `app/routers/notes.py` fails loudly and immediately
        # instead of hanging a real HTTP request.
        raise ValueError("overlap_chars must be smaller than max_chunk_chars")

    chunks: list[str] = []
    start = 0
    text_length = len(text)
    step = max_chunk_chars - overlap_chars
    while start < text_length:
        end = min(start + max_chunk_chars, text_length)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == text_length:
            break
        start += step
    return chunks
