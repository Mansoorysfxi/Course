"""QuestLog's autonomous agent -- NEW in Module 15, the course's final
capstone feature. See lessons/10-building-questlogs-agent-backend.md for
the full, line-by-line walkthrough; this docstring is the short version,
and the honest accounting of what this feature does and does NOT do.

**This is a hand-built agent loop, on purpose -- no framework.** Per the
master plan's own explicit instruction (see lessons/02-building-a-minimal-agent-from-scratch.md
for the from-scratch version this file's loop is a real, applied instance
of), this is a plain `for` loop calling `client.messages.stream(...)`
directly, the exact same shape `app/ai_assistant.py`'s `stream_quest_breakdown`
already established in Module 13 -- decide (has Claude produced a final
answer, or does it want a tool?) -> act (run the tool) -> observe (feed
the result back) -> repeat. The only genuine difference from Module 13's
loop is that THIS agent has six tools instead of one, and its own
conversation can run for more than two turns.

**The six tools, every one of them a thin wrapper around code this course
already wrote and already tested -- see `AGENT_TOOLS` and `_execute_tool`
below:**

1. `list_quests` -- `app/repository.py`'s `list_quests`, unchanged.
2. `create_quest` -- `app/repository.py`'s `create_quest`, validated through
   the exact same `app/models.py` `QuestCreate` Pydantic model
   `POST /api/quests` already validates every request body against.
3. `update_quest` -- `app/repository.py`'s `update_quest`, through
   `QuestUpdate`.
4. `complete_quest` -- also `app/repository.py`'s `update_quest`, but as
   its own named tool rather than a generic "set done=true" case buried
   inside `update_quest`'s schema. See lessons/03-tool-design-and-multi-step-reasoning.md's
   "when a narrower tool beats a flag on a general one" section for why
   this course's own tool-design lesson treats this as a real design
   decision, not decoration.
5. `search_quest_notes` -- Module 14's own retrieval primitives
   (`app/embeddings.py`'s `embed_text`, `app/repository.py`'s
   `find_similar_chunks`), reused directly. This tool does NOT call
   `app/rag.py`'s `stream_note_answer` -- it returns the retrieved
   excerpts as the tool result and lets *this* agent's own model turn
   write the cited answer, using this file's own `SYSTEM_PROMPT`'s
   citation instruction. See this file's own "why this tool doesn't call
   Claude a second time" note below `search_quest_notes`'s implementation.
6. `suggest_quest_breakdown` -- reuses Module 13's own `BREAKDOWN_SCHEMA`
   and `QuestBreakdownResult` (imported directly from `app.ai_assistant`,
   never redefined here) for the JSON Schema and Pydantic validation, but
   makes its own single, direct, non-streaming, non-tool-use call to
   Claude rather than reusing `stream_quest_breakdown`'s whole
   round-trip machinery. See that function's own docstring below for
   exactly why: a tool this agent's own loop calls mid-conversation
   doesn't need its own *nested* tool-use loop -- one direct, structured
   call is enough, and it keeps one call to this endpoint from silently
   spending two independent iteration budgets at once.

**There is deliberately NO `delete_quest` tool.** This is a real,
considered guardrail, not an oversight -- see this file's own
"Guardrails, stated plainly" section below, and
lessons/08-agent-safety-guardrails-and-evals.md's "which actions get a
tool at all" section for the full reasoning.

**Guardrails, stated plainly (see lessons/08 for the full discussion of
each):**

1. **A hard iteration cap, `MAX_AGENT_ITERATIONS` below** -- the exact
   same pattern `app/ai_assistant.py`'s `MAX_TOOL_ITERATIONS` already
   established in Module 13, just larger (this agent can legitimately
   need to chain more tool calls in one turn -- "find the quest, check
   its notes, then create three quests from what it says" is four tool
   calls before a final answer). Every iteration is a real, billed API
   call; a bug or an unusually persistent model can never turn one HTTP
   request into an unbounded loop.
2. **No destructive tool at all.** The agent can create, read, update,
   and mark quests complete -- it can never delete one. A player who
   wants to delete a quest still uses QuestLog's existing UI, which
   already has that button. This course's own honest reasoning: QuestLog
   has no "trash"/undo for a deleted quest (`app/repository.py`'s
   `delete_quest` is a real, permanent `DELETE`), so there is no cheap,
   already-built safety net a mistaken or manipulated tool call could
   fall back on the way there is for, say, a wrongly-created quest (the
   player can just delete it). Removing the capability entirely is a
   simpler, more honest guardrail here than building a whole
   confirm-before-destructive-action flow for one tool this course's own
   scope doesn't need to prove.
3. **Ownership scoping on every single tool, with no exceptions.** Every
   tool that touches a specific quest resolves it through
   `_get_owned_quest` below, which calls `app/repository.py`'s own
   `get_quest(session, quest_id, owner_id=...)` -- the exact same
   "combine the id check and the ownership check in one query" function
   every other route in this app already depends on (see
   `app/dependencies.py`'s `get_quest_or_404`). A quest that exists but
   belongs to someone else produces the same "no quest with that id"
   tool result as a quest that doesn't exist at all -- the same 404,
   never 403, information-leak reasoning Module 07 already taught,
   applied here to a tool result instead of an HTTP response.
4. **Tool-call transparency, surfaced to the player, not hidden in a
   server log.** Every tool call this agent makes is yielded to the
   frontend as its own `tool_call` event (see `run_agent_turn` below) --
   the player watching QuestLog's own chat panel sees, in real time,
   every action the agent is taking on their account, not just its final
   words. A `usage` event, sent right before the final answer, reports
   how many turns and tool calls this one request actually took, so cost
   is never a hidden number.
5. **Structured, Pydantic-validated tool inputs, not raw dicts trusted
   blindly.** `create_quest` and `update_quest` validate the model's own
   tool-call arguments through the exact same `QuestCreate`/`QuestUpdate`
   models `POST`/`PATCH /api/quests` already validate real HTTP request
   bodies against -- the same "defense in depth" reasoning
   `app/ai_assistant.py`'s own module docstring already stated for its
   structured-output result, applied here to a tool's *input* instead.

**Memory scope, stated plainly (see lessons/04-memory-and-planning.md and
lessons/10 for the full discussion):** this feature has short-term memory
only, and it is held entirely on the frontend, not this backend. Every
call to `POST /api/agent/chat` carries the *entire* visible conversation
so far (`app/models.py`'s `AgentChatRequest.messages`) -- this backend
stores nothing about a conversation between requests, the same
"the API is stateless; the caller resends history" principle Module 13's
own `ConversationManager` example already taught. What this feature does
**NOT** implement, stated as plainly as Module 09/11's own "what this
deploy deliberately doesn't do yet" sections: no persistence of a
conversation across a page reload or a new browser session; no long-term,
cross-session memory of a player's preferences (the kind of thing
Anthropic's own memory tool, mentioned in lessons/04, is built for); and
no memory of a turn's own internal tool-calling scratch work once that
turn's final answer has been produced -- only the finished, visible
answer text becomes part of the history the next turn resends (see
`AgentChatMessage`'s own docstring in `app/models.py` for that last
point's own honest trade-off).
"""

import json
from collections.abc import AsyncGenerator
from typing import Any

import anthropic
from pydantic import ValidationError

from app import repository
from app.ai_assistant import BREAKDOWN_SCHEMA, QuestBreakdownResult
from app.config import settings
from app.embeddings import embed_text
from app.models import QuestCreate, QuestUpdate

# See this module's own docstring, guardrail 1. Deliberately larger than
# app/ai_assistant.py's MAX_TOOL_ITERATIONS=3 -- this agent has six tools
# and a genuinely open-ended job ("help the player with their quests"),
# not one narrow feature with one possible tool call. Still a small,
# fixed, real number, not "unlimited" -- see lessons/08's own "why a cap
# this size, and not larger or smaller" box for the honest reasoning.
MAX_AGENT_ITERATIONS = 8

# How many note chunks app/agent.py's own search_quest_notes tool retrieves
# per call -- the same value, and the same reasoning, as app/rag.py's
# TOP_K_CHUNKS (Module 14). Kept as this file's own constant rather than
# importing that one, because the two features' choice of k is allowed to
# diverge later without one accidentally changing the other's behavior --
# they happen to agree today because they're solving the same-shaped
# problem, not because they're required to.
SEARCH_NOTES_TOP_K = 3

SYSTEM_PROMPT = (
    "You are QuestLog's own in-app assistant. The player is chatting with "
    "you to manage their quests. You have tools to list, create, and "
    "update quests, mark a quest complete, search a quest's own notes to "
    "answer a question about it, and suggest a breakdown of one quest "
    "into smaller sub-quests.\n\n"
    "Ground rules:\n"
    "- You have no tool to delete a quest. If the player asks you to "
    "delete one, tell them plainly you can't, and that they can delete it "
    "themselves from the quest's own page.\n"
    "- A quest_id is an internal identifier, not something the player "
    "will type. When the player refers to a quest by title, call "
    "list_quests first to find its id before calling any tool that needs "
    "one. If more than one quest could match what they said, ask which "
    "one they mean instead of guessing.\n"
    "- When you use search_quest_notes, its result is excerpts from the "
    "player's own notes, labeled by note title. Cite the note by title in "
    "your answer (for example: According to your note 'Boss Fight Prep': "
    "...). If the excerpts don't answer the question, say so plainly "
    "instead of guessing or falling back on general knowledge.\n"
    "- Before creating a quest (including one from a suggested breakdown), "
    "briefly say what you're about to create. After any action, confirm "
    "in plain language what you did.\n"
    "- Keep answers short and specific. This is a chat panel, not an essay."
)

AGENT_TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_quests",
        "description": (
            "List the player's own quests. Optionally filter by whether "
            "they're done, by priority, or by quest line. Call this to "
            "find a quest's id from its title, or to answer a question "
            "about what quests exist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "done": {
                    "type": "boolean",
                    "description": "Filter to only done, or only not-done, quests.",
                },
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "quest_line": {
                    "type": "string",
                    "description": "Filter to one quest line by its exact name.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "create_quest",
        "description": (
            "Create one new quest for the player. Use this after the "
            "player has confirmed what they want, or when adding one "
            "sub-quest from a breakdown you suggested."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short, specific quest title."},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "quest_line": {
                    "type": "string",
                    "description": "Which quest line this belongs to.",
                },
            },
            "required": ["title", "description", "priority", "quest_line"],
        },
    },
    {
        "name": "update_quest",
        "description": (
            "Change the title, description, priority, and/or quest line "
            "of an existing quest the player owns. Only include the "
            "fields you're actually changing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "quest_id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "quest_line": {"type": "string"},
            },
            "required": ["quest_id"],
        },
    },
    {
        "name": "complete_quest",
        "description": "Mark one of the player's quests as done.",
        "input_schema": {
            "type": "object",
            "properties": {"quest_id": {"type": "string"}},
            "required": ["quest_id"],
        },
    },
    {
        "name": "search_quest_notes",
        "description": (
            "Search one specific quest's own notes for content relevant "
            "to a question. Returns the most relevant excerpts, each "
            "labeled with the note they came from. Use this before "
            "answering any question about what a quest's notes say."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "quest_id": {"type": "string"},
                "question": {"type": "string"},
            },
            "required": ["quest_id", "question"],
        },
    },
    {
        "name": "suggest_quest_breakdown",
        "description": (
            "Ask for 2-4 suggested smaller sub-quests for one existing "
            "quest. Returns suggested titles only -- it does not create "
            "any quest itself. Tell the player the suggestions and ask "
            "before creating any of them."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"quest_id": {"type": "string"}},
            "required": ["quest_id"],
        },
    },
]


async def _get_owned_quest(session, quest_id: str, owner_id: str):
    """See this module's own docstring, guardrail 3. A thin, local wrapper
    around `app/repository.py`'s own `get_quest` -- not a new authorization
    check, the *same* one every other route in this app already depends
    on, just called directly here instead of through
    `app/dependencies.py`'s `get_quest_or_404` (which raises an
    `HTTPException`, the wrong shape for a tool result -- a tool that
    can't find its quest returns an `is_error` tool result so the model
    can tell the player, not a raised exception that would crash this
    entire streamed turn over one bad tool call)."""
    return await repository.get_quest(session, quest_id, owner_id=owner_id)


async def _tool_list_quests(session, owner_id: str, tool_input: dict[str, Any]) -> str:
    quests = await repository.list_quests(
        session,
        owner_id=owner_id,
        done=tool_input.get("done"),
        priority=tool_input.get("priority"),
        quest_line=tool_input.get("quest_line"),
    )
    return json.dumps(
        [
            {
                "id": q.id,
                "title": q.title,
                "priority": q.priority,
                "questLine": q.quest_line,
                "done": q.done,
            }
            for q in quests
        ]
    )


async def _tool_create_quest(
    session, owner_id: str, tool_input: dict[str, Any]
) -> tuple[str, bool]:
    """Returns `(content, is_error)` -- see `_execute_tool` below for why
    every `_tool_*` function shares this return shape. Validating
    `tool_input` through the real `QuestCreate` model (see this module's
    own docstring, guardrail 5) means a model that omits a required field,
    or supplies a `priority` outside `low`/`medium`/`high`, produces a
    clear validation-error tool result instead of an unhandled exception
    reaching all the way up through this streamed response."""
    try:
        data = QuestCreate.model_validate(tool_input)
    except ValidationError as exc:
        return f"Invalid quest data: {exc.errors()[0]['msg']}", True
    quest = await repository.create_quest(session, data, owner_id=owner_id)
    return json.dumps({"id": quest.id, "title": quest.title}), False


async def _tool_update_quest(
    session, owner_id: str, tool_input: dict[str, Any]
) -> tuple[str, bool]:
    quest_id = tool_input.get("quest_id")
    if not quest_id:
        return "quest_id is required.", True
    changes = {k: v for k, v in tool_input.items() if k != "quest_id"}
    try:
        data = QuestUpdate.model_validate(changes)
    except ValidationError as exc:
        return f"Invalid update: {exc.errors()[0]['msg']}", True
    updated = await repository.update_quest(session, quest_id, data, owner_id=owner_id)
    if updated is None:
        return f"No quest with id '{quest_id}' belongs to this player.", True
    return json.dumps({"id": updated.id, "title": updated.title, "done": updated.done}), False


async def _tool_complete_quest(
    session, owner_id: str, tool_input: dict[str, Any]
) -> tuple[str, bool]:
    quest_id = tool_input.get("quest_id")
    if not quest_id:
        return "quest_id is required.", True
    updated = await repository.update_quest(
        session, quest_id, QuestUpdate(done=True), owner_id=owner_id
    )
    if updated is None:
        return f"No quest with id '{quest_id}' belongs to this player.", True
    return json.dumps({"id": updated.id, "title": updated.title, "done": True}), False


async def _tool_search_quest_notes(
    session, owner_id: str, tool_input: dict[str, Any]
) -> tuple[str, bool, dict[str, Any] | None]:
    """Returns `(content, is_error, extra_event)` -- the one tool that
    also produces a `sources` event (see `run_agent_turn` below), so the
    frontend can show exactly which notes were consulted the same way
    Module 14's own `QuestNotesPanel` already does for `POST .../notes/ask`.

    **Why this tool does NOT call Claude a second time.** Module 14's own
    `app/rag.py`'s `stream_note_answer` both retrieves chunks AND asks
    Claude to write a cited answer from them. Nesting a whole second
    Claude call inside one tool call of THIS agent's own loop would mean
    one player turn could trigger two independent, unrelated
    conversations with the model, each with its own cost and its own
    chance of a `refusal`/`max_tokens` -- real complexity for no real
    benefit, since this agent's own outer loop is already going to make
    another Claude call right after this tool result comes back, and
    that outer call can write the cited answer itself once it has the
    excerpts in hand (see `SYSTEM_PROMPT`'s own citation instruction
    above). Returning the raw excerpts and letting the *agent's own next
    turn* do the writing keeps this tool to exactly one job: retrieval.
    """
    quest_id = tool_input.get("quest_id")
    question = tool_input.get("question")
    if not quest_id or not question:
        return "quest_id and question are both required.", True, None

    quest = await _get_owned_quest(session, quest_id, owner_id)
    if quest is None:
        return f"No quest with id '{quest_id}' belongs to this player.", True, None

    query_embedding = embed_text(question)
    chunks = await repository.find_similar_chunks(
        session, quest_id=quest_id, query_embedding=query_embedding, top_k=SEARCH_NOTES_TOP_K
    )
    if not chunks:
        return "This quest has no notes yet.", False, None

    sources_event = {
        "event": "sources",
        "data": {
            "sources": [
                {"note_id": c.note_id, "note_title": c.note_title, "excerpt": c.content[:150]}
                for c in chunks
            ]
        },
    }
    excerpts = json.dumps([{"note_title": c.note_title, "excerpt": c.content} for c in chunks])
    return excerpts, False, sources_event


async def _tool_suggest_quest_breakdown(
    ai_client: anthropic.AsyncAnthropic, session, owner_id: str, tool_input: dict[str, Any]
) -> tuple[str, bool]:
    """See this module's own docstring, tool 6, for why this makes its
    own single, direct call rather than reusing
    `app/ai_assistant.py.stream_quest_breakdown`. Non-streaming
    (`client.messages.create`, not `.stream(...)`) is a deliberate,
    different choice from every other Claude call in this app: this
    call's own text never reaches the player directly (only the parsed
    `sub_quests` titles do, folded into the agent's own next turn), so
    there is nothing here for token-by-token streaming to make more
    responsive -- see lessons/10's own "when NOT to stream" box."""
    quest_id = tool_input.get("quest_id")
    if not quest_id:
        return "quest_id is required.", True
    quest = await _get_owned_quest(session, quest_id, owner_id)
    if quest is None:
        return f"No quest with id '{quest_id}' belongs to this player.", True

    existing = await repository.list_quests(session, owner_id=owner_id)
    existing_titles = [q.title for q in existing if q.id != quest_id]

    system_prompt = (
        "You are QuestLog's quest-breakdown assistant. Propose 2-4 "
        "concrete, actionable sub-quests for the given quest. Each title "
        "must be short, specific, and never a duplicate of one of these "
        f"existing quest titles: {existing_titles}"
    )
    try:
        response = await ai_client.messages.create(
            model=settings.ai_model,
            max_tokens=512,
            system=system_prompt,
            output_config={"format": {"type": "json_schema", "schema": BREAKDOWN_SCHEMA}},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Quest title: {quest.title}\nQuest description: {quest.description}\n\n"
                        "Break this quest down into sub-quests."
                    ),
                }
            ],
        )
    except anthropic.APIError:
        return "Could not reach Claude to suggest a breakdown right now.", True

    if response.stop_reason == "refusal":
        return "Claude declined to suggest a breakdown for this quest.", True

    text_block = next((b for b in response.content if b.type == "text"), None)
    if text_block is None:
        return "Claude did not return a usable breakdown.", True
    try:
        parsed = json.loads(text_block.text)
        result = QuestBreakdownResult.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError):
        return "Could not parse the suggested breakdown.", True

    return json.dumps({"sub_quests": [s.title for s in result.sub_quests]}), False


async def _execute_tool(
    ai_client: anthropic.AsyncAnthropic,
    session,
    owner_id: str,
    name: str,
    tool_input: dict[str, Any],
) -> tuple[str, bool, dict[str, Any] | None]:
    """The single dispatch point every tool call in `run_agent_turn`
    passes through -- `(content, is_error, extra_event)`, where
    `extra_event` is `None` for every tool except `search_quest_notes`.

    Takes `session` from its caller rather than opening its own -- the
    same request-scoped `AsyncSession` FastAPI's own `Depends(get_db)`
    (`app/dependencies.py`'s `DbSession`) already hands
    `app/routers/agent.py`'s route, reused across every tool call this one
    conversational turn makes. This matters for a reason beyond
    consistency: it's what lets this backend's own test suite substitute
    its in-memory SQLite session via `app.dependency_overrides` (the exact
    same mechanism `tests/conftest.py`'s `client` fixture already
    establishes for every other route in this app) and have every tool
    call in `tests/test_agent.py` transparently run against that test
    database instead of a real Postgres connection this test process was
    never given. An earlier version of this file opened a fresh session
    per tool call directly against `app/database.py`'s own
    `AsyncSessionLocal` -- which looked like better resource hygiene on
    paper, but silently bypassed the test override entirely and tried to
    open a real network connection to Postgres during every test run. See
    lessons/10's own "why this file takes a session as a parameter,
    rather than opening its own" box for the full story of that mistake
    and why the fix is the right call, not just the convenient one.
    """
    if name == "list_quests":
        return await _tool_list_quests(session, owner_id, tool_input), False, None
    if name == "create_quest":
        content, is_error = await _tool_create_quest(session, owner_id, tool_input)
        return content, is_error, None
    if name == "update_quest":
        content, is_error = await _tool_update_quest(session, owner_id, tool_input)
        return content, is_error, None
    if name == "complete_quest":
        content, is_error = await _tool_complete_quest(session, owner_id, tool_input)
        return content, is_error, None
    if name == "search_quest_notes":
        return await _tool_search_quest_notes(session, owner_id, tool_input)
    if name == "suggest_quest_breakdown":
        content, is_error = await _tool_suggest_quest_breakdown(
            ai_client, session, owner_id, tool_input
        )
        return content, is_error, None
    return f"Unknown tool '{name}'.", True, None


async def run_agent_turn(
    ai_client: anthropic.AsyncAnthropic,
    session,
    owner_id: str,
    history: list[dict[str, str]],
) -> AsyncGenerator[dict[str, Any], None]:
    """The agent loop itself -- decide, act, observe, repeat, capped at
    `MAX_AGENT_ITERATIONS`. `history` is the caller's own
    `AgentChatRequest.messages`, already converted to the plain
    `{"role": ..., "content": ...}` shape the Anthropic API expects (see
    `app/routers/agent.py`).

    Yields the same `{"event": ..., "data": ...}` dict shape
    `app/ai_assistant.py`'s `stream_quest_breakdown` and `app/rag.py`'s
    `stream_note_answer` both already established, for the same reason:
    this function stays independently testable
    (`tests/test_agent.py` asserts against these dicts directly), and
    `app/routers/agent.py` owns the one place that knows what SSE's wire
    format looks like.

    Event names:

    - `token` -- a piece of raw text from any turn, exactly as it streams.
    - `tool_call` -- `{"tool": name, "input": {...}}`, sent the moment
      this loop sees a `tool_use` block, before that tool has even run --
      this is what lets the frontend show "Creating quest: ..." live,
      not after the fact.
    - `sources` -- sent only when `search_quest_notes` was called; see
      that tool's own docstring above.
    - `usage` -- `{"iterations": int, "tool_calls": int}`, sent once,
      immediately before this turn's terminal event (`result` or
      `error`). See this module's own docstring, guardrail 4.
    - `result` -- `{"answer": str}`. Terminal.
    - `error` -- `{"message": str}`. Terminal.
    """
    messages: list[dict[str, Any]] = list(history)
    tool_calls_made = 0

    for iteration in range(1, MAX_AGENT_ITERATIONS + 1):
        collected_text = ""
        async with ai_client.messages.stream(
            model=settings.ai_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=AGENT_TOOLS,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                collected_text += text
                yield {"event": "token", "data": {"text": text}}
            final_message = await stream.get_final_message()

        if final_message.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": final_message.content})
            tool_results = []
            for block in final_message.content:
                if block.type != "tool_use":
                    continue
                tool_calls_made += 1
                yield {"event": "tool_call", "data": {"tool": block.name, "input": block.input}}
                content, is_error, extra_event = await _execute_tool(
                    ai_client, session, owner_id, block.name, block.input
                )
                if extra_event is not None:
                    yield extra_event
                tool_result: dict[str, Any] = {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                }
                if is_error:
                    tool_result["is_error"] = True
                tool_results.append(tool_result)
            messages.append({"role": "user", "content": tool_results})
            continue  # one more turn, same loop

        usage_data = {"iterations": iteration, "tool_calls": tool_calls_made}

        if final_message.stop_reason == "refusal":
            yield {"event": "usage", "data": usage_data}
            yield {"event": "error", "data": {"message": "Claude declined to answer that."}}
            return

        if final_message.stop_reason == "max_tokens":
            yield {"event": "usage", "data": usage_data}
            yield {
                "event": "error",
                "data": {"message": "The response was cut off before it finished. Try again."},
            }
            return

        # Any other stop_reason with no tool_use is Claude's genuine final
        # answer for this turn.
        yield {"event": "usage", "data": usage_data}
        yield {"event": "result", "data": {"answer": collected_text}}
        return

    # The loop cap (guardrail 1) was reached without a final answer.
    yield {
        "event": "usage",
        "data": {"iterations": MAX_AGENT_ITERATIONS, "tool_calls": tool_calls_made},
    }
    yield {
        "event": "error",
        "data": {
            "message": (
                f"Stopped after {MAX_AGENT_ITERATIONS} steps without a final answer. "
                "Try asking again, more specifically."
            )
        },
    }
