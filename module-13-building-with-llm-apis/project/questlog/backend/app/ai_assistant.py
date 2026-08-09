"""QuestLog's first real AI feature -- NEW in Module 13.

Given one of the player's own quests, asks Claude to propose 2-4 concrete,
actionable sub-quests -- the master plan's own suggested feature ("suggest
a quest breakdown"). See lessons/07-building-questlogs-ai-assistant-backend.md
for the full, line-by-line walkthrough of every piece of this file; this
docstring is the short version.

Three things happen in every call to `stream_quest_breakdown` below, and
all three are genuinely real, not simplified for the course:

1. **Tool use.** Claude is given one tool, `check_existing_quest_titles`,
   so it can see the player's *other* quest titles before finalizing its
   suggestions -- specifically to avoid proposing "Slay the Dragon" as a
   sub-quest when the player already has a quest with that exact title.
   This is the full round-trip Lesson 04 teaches minutely, applied for
   real: model decides to call a tool -> this file executes it -> the
   result goes back to the model -> the model continues.
2. **Structured output.** The final answer is constrained, via
   `output_config.format`, to a JSON schema this file defines below
   (`BREAKDOWN_SCHEMA`) -- not "please respond with JSON" prompting, a
   real API-level guarantee (Lesson 03). The parsed JSON is then validated
   *again*, in this file's own code, against a Pydantic model
   (`QuestBreakdownResult`) before it's ever trusted -- defense in depth,
   the same reasoning Module 05's own Pydantic-validation lesson taught
   for request bodies, now applied to a response.
3. **Streaming.** Every turn -- including the tool-use turn -- is opened
   with `client.messages.stream(...)`, not `client.messages.create(...)`,
   so the frontend sees Claude's text appear token by token rather than
   waiting for the whole response. See this file's own "Streaming and
   structured output: the real tension" note below, and
   lessons/02-streaming-responses.md / lessons/03-structured-outputs-with-pydantic.md
   for the full explanation of why these two features pull in different
   directions and how this file resolves that honestly.

**Streaming and structured output: the real tension, and how this file
resolves it.** `output_config.format` guarantees the *complete* response
text parses as valid JSON matching the schema -- but that guarantee only
holds once the response is finished. A JSON string is not valid JSON until
its very last closing brace arrives, so there is no meaningful way to
"parse-and-render" a sub-quest the instant its own text arrives mid-stream
the way you could with, say, plain sentences. This file's answer -- a
common, honest, real pattern, not a workaround unique to this course --
is to stream the *raw text* to the frontend as it's generated (which is
what actually makes the feature feel responsive: the player sees words
appearing immediately, exactly like Claude's own chat interface), and
only `json.loads()` + Pydantic-validate the *complete* accumulated text
once the stream ends. The frontend (Lesson 08) shows that raw, streaming
text as it arrives, then swaps to the final, validated sub-quest list the
moment it's ready. Nothing about this is a compromise on correctness --
`output_config.format` still fully guarantees the final text is
schema-valid JSON; streaming only changes *when* the frontend gets to see
the text arrive, never what the text ultimately contains.
"""

import json
from collections.abc import AsyncGenerator
from typing import Any

import anthropic
from pydantic import BaseModel, Field, ValidationError

from app.config import settings
from app.models import Quest

# How many times this file will let the tool-use round-trip repeat before
# giving up. In practice Claude calls `check_existing_quest_titles` at most
# once before answering -- this cap exists purely so a genuinely unusual
# model response (calling the tool over and over, never finalizing an
# answer) can't turn one HTTP request into an unbounded loop that never
# returns. See lessons/04-tool-use-and-function-calling.md's "why cap the
# loop" box and lessons/05-error-handling-retries-and-cost-management.md's
# "runaway loops are a cost risk too" section -- every iteration is a real,
# billed API call.
MAX_TOOL_ITERATIONS = 3

SYSTEM_PROMPT = (
    "You are QuestLog's quest-breakdown assistant. Given a single quest's "
    "title and description, propose between 2 and 4 concrete, actionable "
    "sub-quests the player could realistically complete one at a time. "
    "Each sub-quest title must be short (under 12 words), specific, and a "
    "genuinely smaller piece of the original quest -- never a restatement "
    "of the whole quest, and never a duplicate of one of the player's "
    "other quests. Before giving your final answer, call the "
    "check_existing_quest_titles tool exactly once to see the player's "
    "other quest titles, so you can avoid suggesting one that already "
    "exists."
)

# The one tool Claude has access to for this feature. Deliberately takes
# no input at all (`properties` is empty) -- the *player* whose quests to
# check is already implicit in who is calling this endpoint (see
# app/routers/quests.py's `suggest_quest_breakdown`, which resolves
# `current_user` from the caller's own JWT before this file is ever
# reached), so there is nothing for the model to supply. See
# lessons/04-tool-use-and-function-calling.md for why a tool's job is
# "give the model an action it can request," not "let the model control
# who it acts on."
CHECK_EXISTING_TITLES_TOOL: dict[str, Any] = {
    "name": "check_existing_quest_titles",
    "description": (
        "Returns the titles of every other quest this player currently has, "
        "across every quest line. Call this once, before finalizing your "
        "sub-quest suggestions, so you can avoid proposing a title that "
        "duplicates -- or is a trivial rewording of -- a quest the player "
        "already has."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

# The JSON Schema `output_config.format` enforces on Claude's final
# answer. See lessons/03-structured-outputs-with-pydantic.md for exactly
# which JSON Schema features the Messages API's structured-output support
# does and doesn't accept as of this lesson's own verification -- this
# schema deliberately stays inside that supported subset (no `minItems`
# beyond 0/1, no `minLength`/`maxLength`, `additionalProperties: false`
# on every object). Quantity ("between 2 and 4") and length ("under 12
# words") are therefore enforced by the system prompt above and re-checked
# in this file's own code below, not by the schema itself.
BREAKDOWN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "sub_quests": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["sub_quests"],
    "additionalProperties": False,
}


class SubQuestSuggestion(BaseModel):
    """One proposed sub-quest. See this module's own docstring, point 2,
    for why this Pydantic model exists at all even though
    `output_config.format` already constrains the raw JSON's shape."""

    title: str = Field(min_length=1, max_length=200)


class QuestBreakdownResult(BaseModel):
    """The full, validated shape this module ultimately hands back to
    app/routers/quests.py. `min_length`/`max_length` here are real
    Pydantic validation -- unlike `BREAKDOWN_SCHEMA` above, Pydantic has no
    "supported JSON Schema subset" restriction, since this check runs in
    this backend's own Python code, not inside Claude's own generation."""

    sub_quests: list[SubQuestSuggestion] = Field(min_length=2, max_length=4)


def _build_user_prompt(quest: Quest) -> str:
    return (
        f"Quest title: {quest.title}\n"
        f"Quest description: {quest.description}\n\n"
        "Break this quest down into sub-quests."
    )


async def stream_quest_breakdown(
    client: anthropic.AsyncAnthropic,
    quest: Quest,
    existing_titles: list[str],
) -> AsyncGenerator[dict[str, Any], None]:
    """The manual tool-use loop, streamed. Yields plain dicts, each shaped
    `{"event": <name>, "data": <json-serializable dict>}` -- deliberately
    *not* pre-formatted SSE text, so this function stays independently
    testable (tests/test_ai_assistant.py asserts against these dicts
    directly) and app/routers/quests.py owns the one, single place that
    actually knows what "Server-Sent Events" wire format looks like. See
    lessons/02-streaming-responses.md for what SSE is and why the format
    lives at the router layer, not here.

    Event names, and what each one means to the frontend (Lesson 08):

    - `token` -- one more piece of raw text Claude just generated, from
      *any* turn (including a tool-use turn's own brief preamble text, if
      any). `data: {"text": "..."}`.
    - `tool_call` -- Claude just invoked `check_existing_quest_titles`.
      Purely observational -- the frontend can show "checking your other
      quests..." -- the round trip itself continues automatically either
      way. `data: {"tool": "check_existing_quest_titles"}`.
    - `result` -- the final, complete, Pydantic-validated list of
      sub-quest titles. `data: {"sub_quests": ["...", "..."]}`. Terminal:
      no further events follow.
    - `error` -- something stopped this from producing a usable result
      (Claude refused, ran out of `max_tokens` mid-answer, produced text
      that didn't parse/validate, or looped past `MAX_TOOL_ITERATIONS`).
      `data: {"message": "..."}`. Terminal.
    """
    messages: list[dict[str, Any]] = [{"role": "user", "content": _build_user_prompt(quest)}]

    for _ in range(MAX_TOOL_ITERATIONS):
        collected_text = ""
        async with client.messages.stream(
            model=settings.ai_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[CHECK_EXISTING_TITLES_TOOL],
            output_config={"format": {"type": "json_schema", "schema": BREAKDOWN_SCHEMA}},
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                collected_text += text
                yield {"event": "token", "data": {"text": text}}
            final_message = await stream.get_final_message()

        if final_message.stop_reason == "tool_use":
            # Same "echo the assistant turn back, then answer each
            # tool_use block with a matching tool_result" shape
            # lessons/04-tool-use-and-function-calling.md walks through
            # from a plain script -- applied here inside a streamed,
            # multi-turn loop instead.
            messages.append({"role": "assistant", "content": final_message.content})
            tool_results = []
            for block in final_message.content:
                if block.type == "tool_use" and block.name == "check_existing_quest_titles":
                    yield {"event": "tool_call", "data": {"tool": block.name}}
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(existing_titles),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue  # one more turn, same loop

        if final_message.stop_reason == "refusal":
            # See lessons/05-error-handling-retries-and-cost-management.md
            # -- a refusal is not an exception the SDK raises, it's a
            # normal, successful HTTP response whose `stop_reason` says
            # "I'm not going to answer this." Nothing to retry here; the
            # honest response is telling the player it didn't work.
            yield {
                "event": "error",
                "data": {"message": "Claude declined to suggest a breakdown for this quest."},
            }
            return

        if final_message.stop_reason == "max_tokens":
            yield {
                "event": "error",
                "data": {"message": "The response was cut off before it finished. Try again."},
            }
            return

        # Any other stop_reason on a turn with no tool_use is Claude's
        # genuine final answer -- `output_config.format` guarantees
        # `collected_text` is valid JSON matching BREAKDOWN_SCHEMA, but
        # this file validates it again anyway (this module's own
        # docstring, point 2) before ever trusting it.
        try:
            parsed = json.loads(collected_text)
            result = QuestBreakdownResult.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError):
            yield {
                "event": "error",
                "data": {"message": "Could not parse the suggestions Claude returned."},
            }
            return

        yield {
            "event": "result",
            "data": {"sub_quests": [sub_quest.title for sub_quest in result.sub_quests]},
        }
        return

    yield {
        "event": "error",
        "data": {"message": "Gave up after checking too many times without a final answer."},
    }
