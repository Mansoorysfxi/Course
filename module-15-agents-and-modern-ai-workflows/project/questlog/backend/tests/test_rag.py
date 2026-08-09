"""Tests for app/rag.py -- NEW in Module 14.

`cosine_similarity`, `rank_by_cosine_similarity`, and `build_answer_prompt`
are pure Python/numpy -- no database, no model, no network. Only
`stream_note_answer` talks to "Claude," and it does so through the exact
same fake-client pattern tests/test_ai_assistant.py already established
(reused directly from that file below) -- no real ANTHROPIC_API_KEY
required anywhere in this file.
"""

from app.rag import (
    RetrievedChunk,
    build_answer_prompt,
    cosine_similarity,
    rank_by_cosine_similarity,
    stream_note_answer,
)
from tests.test_ai_assistant import FakeAnthropicClient, _final_message, _text_block


def _chunk(note_id, note_title, chunk_index, content, embedding) -> RetrievedChunk:
    return RetrievedChunk(
        note_id=note_id,
        note_title=note_title,
        chunk_index=chunk_index,
        content=content,
        embedding=embedding,
    )


def test_cosine_similarity_identical_vectors_is_one():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0


def test_cosine_similarity_orthogonal_vectors_is_zero():
    assert abs(cosine_similarity([1.0, 0.0], [0.0, 1.0])) < 1e-9


def test_cosine_similarity_opposite_vectors_is_negative_one():
    assert abs(cosine_similarity([1.0, 0.0], [-1.0, 0.0]) - (-1.0)) < 1e-9


def test_rank_by_cosine_similarity_orders_most_similar_first():
    query = [1.0, 0.0]
    close = _chunk("n1", "Boss Fight Prep", 0, "close chunk", [0.9, 0.1])
    far = _chunk("n1", "Boss Fight Prep", 1, "far chunk", [0.0, 1.0])
    medium = _chunk("n2", "Shopping List", 0, "medium chunk", [0.5, 0.5])

    ranked = rank_by_cosine_similarity([far, close, medium], query, top_k=3)

    assert [chunk.content for chunk in ranked] == ["close chunk", "medium chunk", "far chunk"]


def test_rank_by_cosine_similarity_respects_top_k():
    query = [1.0, 0.0]
    chunks = [_chunk("n1", "Note", i, f"chunk {i}", [1.0 - i * 0.1, i * 0.1]) for i in range(5)]

    ranked = rank_by_cosine_similarity(chunks, query, top_k=2)

    assert len(ranked) == 2
    assert ranked[0].content == "chunk 0"


def test_build_answer_prompt_labels_each_excerpt_with_its_note_title():
    chunks = [
        _chunk("n1", "Boss Fight Prep", 0, "Bring fire resistant armor.", [0.1, 0.2]),
        _chunk("n2", "Shopping List", 0, "Buy silverleaf herbs.", [0.3, 0.4]),
    ]

    prompt = build_answer_prompt("What armor should I bring?", chunks)

    assert 'Excerpt from note "Boss Fight Prep"' in prompt
    assert "Bring fire resistant armor." in prompt
    assert 'Excerpt from note "Shopping List"' in prompt
    assert "Question: What armor should I bring?" in prompt


async def _collect(events_generator):
    return [event async for event in events_generator]


async def test_stream_note_answer_with_no_chunks_never_calls_claude():
    """If retrieval found nothing, this function must not call Claude at
    all -- `FakeAnthropicClient([])` has zero turns configured, so any
    attempt to call `.stream(...)` would raise `StopIteration`, which
    would fail this test loudly if that guarantee were ever broken."""
    fake_client = FakeAnthropicClient(turns=[])

    events = await _collect(stream_note_answer(fake_client, "Any question?", []))

    assert events == [
        {
            "event": "error",
            "data": {"message": "This quest has no notes yet. Add one before asking a question."},
        }
    ]


async def test_stream_note_answer_sends_sources_before_tokens():
    chunk = _chunk("n1", "Boss Fight Prep", 0, "Bring fire resistant armor.", [0.1, 0.2])
    answer_text = "According to your note 'Boss Fight Prep': bring fire resistant armor."
    fake_client = FakeAnthropicClient(
        turns=[([answer_text], _final_message([_text_block(answer_text)], stop_reason="end_turn"))]
    )

    events = await _collect(stream_note_answer(fake_client, "What armor?", [chunk]))

    assert events[0]["event"] == "sources"
    assert events[0]["data"]["sources"] == [
        {
            "note_id": "n1",
            "note_title": "Boss Fight Prep",
            "chunk_index": 0,
            "excerpt": "Bring fire resistant armor.",
        }
    ]
    assert events[1] == {"event": "token", "data": {"text": answer_text}}
    assert events[-1] == {"event": "result", "data": {"answer": answer_text}}


async def test_stream_note_answer_handles_a_refusal():
    chunk = _chunk("n1", "Boss Fight Prep", 0, "content", [0.1, 0.2])
    fake_client = FakeAnthropicClient(turns=[([], _final_message([], stop_reason="refusal"))])

    events = await _collect(stream_note_answer(fake_client, "question", [chunk]))

    assert events[0]["event"] == "sources"
    assert events[-1] == {
        "event": "error",
        "data": {"message": "Claude declined to answer this question."},
    }


async def test_stream_note_answer_handles_max_tokens():
    chunk = _chunk("n1", "Boss Fight Prep", 0, "content", [0.1, 0.2])
    fake_client = FakeAnthropicClient(
        turns=[
            (
                ["partial answer"],
                _final_message([_text_block("partial answer")], stop_reason="max_tokens"),
            )
        ]
    )

    events = await _collect(stream_note_answer(fake_client, "question", [chunk]))

    assert events[-1] == {
        "event": "error",
        "data": {"message": "The answer was cut off before it finished. Try again."},
    }
