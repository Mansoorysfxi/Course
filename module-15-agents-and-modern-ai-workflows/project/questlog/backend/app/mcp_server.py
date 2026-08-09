"""A small, standalone, **read-only** MCP server exposing two of
QuestLog's own real capabilities -- NEW in Module 15. See
lessons/11-building-questlogs-agent-frontend-and-going-live.md's own "the
MCP tie-back, and why it stays this small" section for the full,
honest reasoning behind every scope decision in this file.

**This file is deliberately NOT part of the production FastAPI app.** It
is never imported by `app/main.py`, it is not started by `uvicorn`, and
it is not required for the backend's own test suite (`pytest -q`) to
pass -- it is an additional, clearly-scoped teaching artifact you run by
hand, per Lesson 05's own MCP lesson, to see QuestLog's own real
repository functions exposed over the Model Context Protocol to any
MCP-compliant client (Claude Desktop, Claude Code, `mcp dev`'s own
inspector), not just this app's own FastAPI routes.

**Why read-only, and why one hard-coded user, stated honestly:**

1. **Read-only.** Both tools below only ever call `repository.list_quests`
   and `repository.find_similar_chunks` -- never `create_quest`,
   `update_quest`, or anything that writes. A real MCP server exposing
   write access to someone's account needs a real authentication and
   authorization story for *which* MCP client is allowed to act on
   *whose* behalf -- a genuinely different, harder problem than this
   file's own scope, and one this course's own capstone (`app/agent.py`,
   which HTTP-authenticates every caller via a real JWT, exactly like
   every other route in this app) already solves correctly for the
   feature that actually needs write access. Duplicating that
   authorization logic here, for a teaching example, would be real,
   unnecessary complexity for no real benefit -- see Lesson 11's own
   "why this file doesn't duplicate app/agent.py's own tools" box.
2. **One hard-coded user.** An MCP `stdio` server, run locally the way
   Lesson 05 taught, has no HTTP request, no `Authorization` header, and
   therefore no natural place a real per-caller identity would come
   from -- unlike `app/routers/agent.py`'s own route, which resolves
   `current_user` from a verified JWT on every single call. This file
   resolves QuestLog's own seeded demo account instead
   (`app/repository.py`'s own `DEMO_USER_EMAIL`) -- the same account
   `project/BRIEF.md` already tells you how to log into --  precisely so
   this example has *something* real to query without inventing a whole
   second authentication scheme for a teaching artifact. A production MCP
   server exposing a real, multi-user application's data would need a
   genuine per-connection identity; this file says so, out loud, rather
   than quietly pretending the problem doesn't exist.

Run it (from `module-15-agents-and-modern-ai-workflows/project/questlog/backend`,
with this backend's own regular `venv` activated, plus the one extra,
optional dependency in `requirements-mcp.txt`):

```bash
pip install -r requirements-mcp.txt
python -m app.mcp_server
```

Or explore it interactively with the MCP inspector (Lesson 05):

```bash
mcp dev app/mcp_server.py
```
"""

import asyncio

from mcp.server import MCPServer

from app import repository
from app.database import AsyncSessionLocal
from app.embeddings import embed_text
from app.rag import TOP_K_CHUNKS

mcp = MCPServer(
    "questlog-notes",
    description=(
        "Read-only access to one demo QuestLog account's quests and quest "
        "notes. See this file's own module docstring for why it's "
        "read-only and scoped to a single, fixed demo account."
    ),
)


async def _demo_owner_id() -> str:
    async with AsyncSessionLocal() as session:
        user = await repository.get_user_by_email(session, repository.DEMO_USER_EMAIL)
        if user is None:
            raise RuntimeError(
                "The demo account doesn't exist yet -- start the FastAPI app at least once "
                "(its own startup seeds it) before running this MCP server."
            )
        return user.id


@mcp.tool()
async def list_quests() -> list[dict[str, str]]:
    """List the demo QuestLog account's own quests -- title, priority,
    and whether each one is done. Read-only; creates or changes nothing."""
    owner_id = await _demo_owner_id()
    async with AsyncSessionLocal() as session:
        quests = await repository.list_quests(session, owner_id=owner_id)
    return [{"title": q.title, "priority": q.priority, "done": str(q.done)} for q in quests]


@mcp.tool()
async def search_quest_notes(quest_title: str, question: str) -> str:
    """Search one of the demo account's quests -- matched by its exact
    title -- for notes relevant to a question. Returns the most relevant
    excerpts, or a plain message if the quest or its notes can't be
    found. Read-only; the same retrieval building blocks
    (app/embeddings.py, app/repository.py's find_similar_chunks) this
    course's own capstone agent uses for the exact same job."""
    owner_id = await _demo_owner_id()
    async with AsyncSessionLocal() as session:
        quests = await repository.list_quests(session, owner_id=owner_id)
        matched = next((q for q in quests if q.title.lower() == quest_title.lower()), None)
        if matched is None:
            return f"No quest titled '{quest_title}' on the demo account."

        query_embedding = embed_text(question)
        chunks = await repository.find_similar_chunks(
            session, quest_id=matched.id, query_embedding=query_embedding, top_k=TOP_K_CHUNKS
        )
    if not chunks:
        return f"'{quest_title}' has no notes yet."
    return "\n\n".join(f'From note "{c.note_title}": {c.content}' for c in chunks)


if __name__ == "__main__":
    asyncio.run(_demo_owner_id())  # fails fast, before mcp.run(), if the demo account is missing
    mcp.run()
