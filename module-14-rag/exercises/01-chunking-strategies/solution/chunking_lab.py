"""Exercise 01 -- Chunking Strategies. Reference solution. See INSTRUCTIONS.md.

Do not read this until you've attempted the exercise yourself in
starter/chunking_lab.py.
"""

SAMPLE_NOTE = """The dragon sleeps in the northern cave, guarded by two goblins near the entrance.

Bring fire-resistant armor and a silver sword -- regular steel won't cut its scales.

Approach from the east ridge at dawn to avoid the goblin patrol, which circles the cave every hour on the hour."""


def fixed_size_chunks(text: str, max_chunk_chars: int, overlap_chars: int) -> list[str]:
    if overlap_chars >= max_chunk_chars:
        raise ValueError("overlap_chars must be smaller than max_chunk_chars")

    stripped = text.strip()
    if not stripped:
        return []

    chunks: list[str] = []
    start = 0
    step = max_chunk_chars - overlap_chars
    text_length = len(stripped)
    while start < text_length:
        end = min(start + max_chunk_chars, text_length)
        piece = stripped[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == text_length:
            break
        start += step
    return chunks


def paragraph_chunks(text: str, max_chunk_chars: int) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []

    raw_paragraphs = [p.strip() for p in stripped.split("\n\n")]
    return [p for p in raw_paragraphs if p]


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

    # Step 5 answer: For this sample note, paragraph-based chunking
    # produces the more sensible result. Each of the three paragraphs is
    # a genuinely separate, complete thought (where the dragon is; what
    # gear to bring; how to approach) -- fixed-size chunking at 60
    # characters cuts straight through the middle of sentences (e.g. it
    # splits "goblins near the entrance." across two chunks), which would
    # hurt both an embedding's ability to represent a coherent idea and a
    # later citation's readability. Fixed-size chunking would only win
    # here if the note had no paragraph breaks at all -- exactly the case
    # app/chunking.py's real fallback handles.
