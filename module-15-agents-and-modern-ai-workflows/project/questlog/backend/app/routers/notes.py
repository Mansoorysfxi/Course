"""Every /api/quests/{quest_id}/notes route -- NEW in Module 14. See
lessons/08-building-questlogs-notes-feature-backend.md for the full
walkthrough.

Every route below takes `quest: Annotated[Quest, Depends(get_quest_or_404)]`
-- the exact same dependency `app/routers/quests.py`'s own single-quest
routes already use. There is no new authorization logic anywhere in this
file: a request for a quest that doesn't exist, or belongs to someone
else, never reaches any route body here at all, exactly the same guarantee
`suggest_quest_breakdown` (Module 13) already relies on for the same
reason.
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app import repository
from app.chunking import chunk_text
from app.dependencies import AiClient, CurrentUser, DbSession, get_quest_or_404
from app.embeddings import embed_text, embed_texts
from app.models import AskQuestionRequest, Quest, QuestNote, QuestNoteCreate
from app.rag import TOP_K_CHUNKS, stream_note_answer

router = APIRouter(prefix="/api/quests/{quest_id}/notes", tags=["notes"])


@router.post("", response_model=QuestNote, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: QuestNoteCreate,
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
    current_user: CurrentUser,
):
    """Chunks `data.content` (app/chunking.py), embeds every chunk in one
    batched call (app/embeddings.py), and stores the note plus its chunks
    (app/repository.py) -- the full "ingest" half of this module's RAG
    pipeline, all three steps visible in this one route, in order, exactly
    the sequence lessons/06-building-a-rag-pipeline-by-hand.md walks
    through by hand before this route ever existed.

    A note whose `content` chunks to zero pieces (only possible if
    `content` were empty or pure whitespace, which `QuestNoteCreate`'s own
    `Field(min_length=1)` already rejects with a 422 before this function
    body ever runs) is not a case this route needs to handle -- see
    app/chunking.py's own `chunk_text` docstring for that guarantee.
    """
    chunks = chunk_text(data.content)
    embeddings = embed_texts(chunks)
    return await repository.create_note_with_chunks(
        session,
        quest_id=quest.id,
        owner_id=current_user.id,
        title=data.title,
        content=data.content,
        chunk_texts=chunks,
        chunk_embeddings=embeddings,
    )


@router.get("", response_model=list[QuestNote])
async def list_notes(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
):
    return await repository.list_notes(session, quest_id=quest.id)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
):
    deleted = await repository.delete_note(session, quest_id=quest.id, note_id=note_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No note with id '{note_id}' on this quest",
        )
    return None


@router.post("/ask")
async def ask_question(
    data: AskQuestionRequest,
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
    ai_client: AiClient,
):
    """Streams a Server-Sent Events response -- the exact same
    `StreamingResponse(..., media_type="text/event-stream")` shape
    `suggest_quest_breakdown` (Module 13) already established, and the
    exact same `503` when `ai_client` is `None` (no `ANTHROPIC_API_KEY`
    configured), for the exact same reason.

    The retrieval half of this module's pipeline happens here, in this
    route, BEFORE `stream_note_answer` is ever called: the question is
    embedded (app/embeddings.py), then the real `pgvector` similarity
    query (app/repository.py's `find_similar_chunks`) finds the
    `TOP_K_CHUNKS` most relevant chunks *for this specific quest* -- one
    more place `quest.id` (already auth-scoped by `get_quest_or_404`)
    keeps one player's notes from ever being searchable by another.
    """
    if ai_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The notes assistant isn't configured. Set ANTHROPIC_API_KEY and restart "
                "the server."
            ),
        )

    query_embedding = embed_text(data.question)
    retrieved_chunks = await repository.find_similar_chunks(
        session, quest_id=quest.id, query_embedding=query_embedding, top_k=TOP_K_CHUNKS
    )

    async def event_stream():
        # The SSE wire format itself lives here, and only here, exactly
        # the same "app/rag.py yields plain dicts; this router formats the
        # wire bytes" split app/routers/quests.py already established for
        # app/ai_assistant.py.
        async for event in stream_note_answer(ai_client, data.question, retrieved_chunks):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
