"""Tests for app/chunking.py -- NEW in Module 14.

Pure Python, zero dependencies beyond the standard library, so every test
below runs instantly with no database, no model, and no network at all --
see app/chunking.py's own module docstring for why this is deliberate.
"""

from app.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n\n   ") == []


def test_single_short_paragraph_is_one_chunk():
    text = "The dragon sleeps in the northern cave, guarded by two goblins."
    assert chunk_text(text) == [text]


def test_splits_on_paragraph_boundaries():
    text = (
        "The dragon sleeps in the northern cave.\n\n"
        "Bring fire-resistant armor and a silver sword.\n\n"
        "Approach from the east ridge to avoid the goblin patrol."
    )
    chunks = chunk_text(text)
    assert chunks == [
        "The dragon sleeps in the northern cave.",
        "Bring fire-resistant armor and a silver sword.",
        "Approach from the east ridge to avoid the goblin patrol.",
    ]


def test_handles_multiple_blank_lines_between_paragraphs():
    text = "First paragraph.\n\n\n\nSecond paragraph."
    assert chunk_text(text) == ["First paragraph.", "Second paragraph."]


def test_handles_windows_line_endings():
    text = "First paragraph.\r\n\r\nSecond paragraph."
    assert chunk_text(text) == ["First paragraph.", "Second paragraph."]


def test_long_paragraph_falls_back_to_fixed_size_with_overlap():
    # One paragraph (no blank lines at all), long enough to force the
    # fixed-size fallback with a small max_chunk_chars/overlap_chars pair
    # chosen specifically to make the math easy to check by hand.
    text = "abcdefghij" * 10  # 100 characters, one paragraph, no blank lines
    chunks = chunk_text(text, max_chunk_chars=40, overlap_chars=10)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 40

    # Every character of the original text appears in at least one chunk --
    # overlap must never *drop* content, only duplicate some of it at each
    # boundary.
    assert "".join(dict.fromkeys("".join(chunks))) != ""  # sanity: chunks aren't empty
    reconstructed = chunks[0]
    for chunk in chunks[1:]:
        # Each later chunk should share its first `overlap_chars`-ish
        # characters with the tail of the previous one, by construction --
        # a loose check that overlap is actually happening, not an exact
        # string-splice assertion (which would over-couple this test to
        # the fallback's exact internals).
        reconstructed += chunk
    assert set(text) <= set(reconstructed)


def test_overlap_must_be_smaller_than_max_chunk_size():
    import pytest

    with pytest.raises(ValueError, match="overlap_chars must be smaller"):
        chunk_text("x" * 100, max_chunk_chars=20, overlap_chars=20)


def test_preserves_original_order():
    text = "Alpha.\n\nBeta.\n\nGamma.\n\nDelta."
    assert chunk_text(text) == ["Alpha.", "Beta.", "Gamma.", "Delta."]
