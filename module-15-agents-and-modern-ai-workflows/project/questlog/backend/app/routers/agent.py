"""`POST /api/agent/chat` -- NEW in Module 15, QuestLog's final capstone
feature. See app/agent.py's own module docstring for what the agent can
and can't do, and lessons/10-building-questlogs-agent-backend.md for the
full walkthrough of this one route.

Deliberately the **only** route in this file, and deliberately not scoped
under `/api/quests/{quest_id}/...` the way `app/routers/notes.py` is --
this agent is a general assistant across all of the player's quests (it
decides, itself, via the `list_quests` tool, which quest a player means),
not a per-quest feature. `current_user: CurrentUser` is the only
authorization this route needs; every tool call the agent makes is scoped
to `current_user.id` from there down (see `app/agent.py`'s own module
docstring, guardrail 3). `session: DbSession` is passed straight through
to `run_agent_turn` and reused for every tool call this one turn makes --
see `app/agent.py`'s own `_execute_tool` docstring for why this route
hands over its one request-scoped session rather than letting
`app/agent.py` open its own.
"""

import json

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.agent import run_agent_turn
from app.dependencies import AiClient, CurrentUser, DbSession
from app.models import AgentChatRequest

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat")
async def agent_chat(
    data: AgentChatRequest, current_user: CurrentUser, ai_client: AiClient, session: DbSession
):
    """Streams a Server-Sent Events response -- the exact same
    `StreamingResponse(..., media_type="text/event-stream")` shape
    `app/routers/quests.py`'s `suggest_quest_breakdown` and
    `app/routers/notes.py`'s `ask_question` already established, and the
    exact same `503` when `ai_client` is `None` (no `ANTHROPIC_API_KEY`
    configured), for the exact same reason.
    """
    if ai_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The agent isn't configured. Set ANTHROPIC_API_KEY and restart the server.",
        )

    history = [{"role": message.role, "content": message.content} for message in data.messages]

    async def event_stream():
        # The SSE wire format itself lives here, and only here -- the same
        # "app/agent.py yields plain dicts; this router formats the wire
        # bytes" split every earlier streaming route in this app already
        # establishes.
        async for event in run_agent_turn(ai_client, session, current_user.id, history):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
