"""Exercise 01 -- Chunking Strategies. See INSTRUCTIONS.md.

Implement both functions below, then run this file directly:
    python chunking_lab.py
"""

SAMPLE_NOTE = """The dragon sleeps in the northern cave, guarded by two goblins near the entrance.

Bring fire-resistant armor and a silver sword -- regular steel won't cut its scales.

Approach from the east ridge at dawn to avoid the goblin patrol, which circles the cave every hour on the hour."""


def fixed_size_chunks(text: str, max_chunk_chars: int, overlap_chars: int) -> list[str]:
    """TODO: split `text` into pieces of at most `max_chunk_chars`
    characters each, where each chunk after the first starts
    `overlap_chars` characters before the previous one ended.

    Must raise ValueError if overlap_chars >= max_chunk_chars.
    Must return [] for empty or whitespace-only input.
    """
    raise NotImplementedError


def paragraph_chunks(text: str, max_chunk_chars: int) -> list[str]:
    """TODO: split `text` on blank lines into paragraphs, and return each
    non-empty, whitespace-trimmed paragraph as one chunk.

    You do not need to handle a single paragraph longer than
    max_chunk_chars for this exercise -- just return it as one chunk.
    Must return [] for empty or whitespace-only input.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print("=== Fixed-size chunking (max=60, overlap=10) ===")
    fixed = fixed_size_chunks(SAMPLE_NOTE, max_chunk_chars=60, overlap_chars=10)
    for i, chunk in enumerate(fixed):
        print(f"[{i}] ({len(chunk)} chars) {chunk!r}")
    print(f"Total chunks: {len(fixed)}\n")

    print("=== Paragraph-based chunking ===")
    paragraphs = paragraph_chunks(SAMPLE_NOTE, max_chunk_chars=800)
    for i, chunk in enumerate(paragraphs):
        print(f"[{i}] ({len(chunk)} chars) {chunk!r}")
    print(f"Total chunks: {len(paragraphs)}")

    # TODO (Step 5): add your written answer here as a comment.
