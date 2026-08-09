"""The QuestLog API's Pydantic models -- the request/response *contract*.

Unchanged from Module 05, on purpose: not one field, alias, or validation
rule below was touched while adding real Postgres persistence. That is
this module's whole point, stated in code -- see
lessons/06-sqlalchemy-with-fastapi.md's "the contract doesn't change"
section. Field-for-field, this still matches Module 04's frontend `Quest`
type (project/questlog/frontend/src/types/quest.ts) exactly --
`Field(alias=...)` is what lets this backend use idiomatic Python
snake_case internally while the actual JSON travelling to/from the
frontend uses the exact camelCase names that frontend already expects. See
lessons/03-request-bodies-and-pydantic-validation.md's "aside" on aliasing
(Module 05), and lessons/08-building-the-questlog-api.md (Module 05) for
this file in its original context.

Do not confuse these classes with app/db_models.py's SQLAlchemy classes,
below -- these Pydantic classes describe what travels over HTTP; those
describe what's actually stored in Postgres. They happen to look similar
for `Quest` because the API contract and the storage shape are similar,
but they are two separate things for two separate jobs, and
app/repository.py is the only code that translates between them.

The auth-related models at the bottom of this file (`UserCreate`,
`UserPublic`, `Token`) are new in Module 07 -- see
lessons/06-building-signup-login.md for `UserCreate`/`UserPublic` (used by
`POST /api/auth/signup`) and lessons/03-sessions-vs-jwts.md /
lessons/04-jwt-structure-in-depth.md for `Token` (returned by
`POST /api/auth/login`). `UserPublic` is the deliberate, minimal answer to
"what is safe to ever send back to a browser about a user" -- notice it
has no `hashed_password` field at all; there is no version of this
contract, ever, in which a password hash leaves this backend.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Priority = Literal["low", "medium", "high"]


class QuestBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str
    priority: Priority
    quest_line: str = Field(alias="questLine", min_length=1)


class QuestCreate(QuestBase):
    """Exactly the fields a client supplies to create a quest -- matches
    the frontend's NewQuestInput (Omit<Quest, "id" | "done" | "createdAt">).
    """


class QuestUpdate(BaseModel):
    """Every field optional -- matches the frontend's QuestUpdate
    (Partial<Omit<Quest, "id" | "createdAt">>). A client sends only the
    fields it's actually changing; see store.update_quest's use of
    `exclude_unset=True`, which is what makes that distinction matter."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    quest_line: str | None = Field(default=None, alias="questLine", min_length=1)
    done: bool | None = None


class Quest(QuestBase):
    """The full stored/returned shape -- matches the frontend's Quest type
    exactly, field for field."""

    id: str
    done: bool
    created_at: str = Field(alias="createdAt")


class QuestLineStats(BaseModel):
    """Used by GET /api/quests/stats -- per-quest-line totals, the backend
    equivalent of Module 04's Exercise 05 "Quest Lines Overview" page,
    computed here instead of in the frontend."""

    model_config = ConfigDict(populate_by_name=True)

    quest_line: str = Field(alias="questLine")
    total: int
    done: int


class UserCreate(BaseModel):
    """The body `POST /api/auth/signup` expects. `EmailStr` (Pydantic's
    built-in email-shaped-string type -- installed via the `email-validator`
    package, see requirements.txt) rejects a request outright, with a 422
    and a clear message, if `email` isn't even shaped like an email address
    -- the exact same "reject bad input before your own code ever runs"
    job Module 05, Lesson 03 taught for `Literal` and `Field(min_length=...)`,
    applied to a new, more specific validated type.

    `password` is a plain `str` with a `min_length` -- deliberately *not*
    validated any more strictly than that (no "must contain a symbol"
    regex). lessons/02-password-hashing.md's "why this course doesn't
    police password complexity" box explains why current guidance (NIST
    SP 800-63B) favors length and breach-checking over composition rules
    that mostly just annoy users into predictable substitutions
    ("Password1!" instead of "password"). This app has no breach-checking
    service, so it settles for a sane minimum length instead."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserPublic(BaseModel):
    """Everything about a user that is ever safe to put in an HTTP
    response -- returned by `POST /api/auth/signup` and
    `GET /api/auth/me`. See this file's own module docstring for why
    `hashed_password` deliberately has no place in this class at all."""

    # `populate_by_name=True` -- exactly like QuestBase above -- because
    # app/repository.py builds this model explicitly with keyword
    # arguments (`created_at=...`, the Python field name), not from a raw
    # `{"createdAt": ...}` dict, the same "translate ORM row to Pydantic
    # model, by hand, in one function" pattern `_to_pydantic` in
    # repository.py already uses for `Quest`.
    model_config = ConfigDict(populate_by_name=True)

    id: str
    email: str
    created_at: str = Field(alias="createdAt")


class QuestNoteCreate(BaseModel):
    """NEW in Module 14 -- the body `POST /api/quests/{quest_id}/notes`
    expects. See lessons/08-building-questlogs-notes-feature-backend.md.
    Plain text/markdown only -- no file upload, no PDF parsing -- kept
    deliberately small in scope, per this module's own "the full RAG
    pipeline by hand first" framing: the interesting new material is
    chunking/embedding/retrieval, not document parsing."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class QuestNote(BaseModel):
    """The shape returned by both `POST` and `GET .../notes` -- notice
    there is no `content` field here at all. The list view
    (`GET .../notes`) has no need to ship every note's full text back down
    just to render a title and a chunk count, and the create response
    doesn't need to echo back exactly what the caller just sent it either
    -- see lessons/08's "what a note's own API response should, and
    shouldn't, contain" box."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    created_at: str = Field(alias="createdAt")
    chunk_count: int = Field(alias="chunkCount")


class AskQuestionRequest(BaseModel):
    """The body `POST /api/quests/{quest_id}/notes/ask` expects."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=2000)


class AgentChatMessage(BaseModel):
    """NEW in Module 15 -- one turn of the visible chat transcript the
    frontend keeps and re-sends on every call to `POST /api/agent/chat`.
    See app/agent.py's own module docstring for exactly why this is the
    *entire* memory this feature has -- there is deliberately no
    server-side conversation storage at all, and this model is honestly
    that boundary made concrete: it holds a `role` and plain `content`
    text, nothing else. A turn where the agent called tools mid-answer
    still collapses to one of these -- its own tool-calling scratch work
    is never part of what gets sent back next time (see app/agent.py's
    module docstring for the full, stated trade-off)."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AgentChatRequest(BaseModel):
    """The body `POST /api/agent/chat` expects: the *entire* visible
    transcript so far, including the newest user message as its last
    entry. `max_length=40` is a real, small guardrail of its own -- not
    the loop cap `app/agent.py`'s `MAX_AGENT_ITERATIONS` already enforces
    per turn, but a cap on how much history one single request can ever
    carry, so a runaway frontend bug (or a deliberately abusive caller)
    can't hand this endpoint an unbounded, ever-growing message list to
    re-process every turn."""

    messages: list[AgentChatMessage] = Field(min_length=1, max_length=40)


class Token(BaseModel):
    """The body `POST /api/auth/login` returns on success. Field names
    (`access_token`, `token_type`) match the OAuth2 spec's own vocabulary
    exactly (lessons/05-oauth2-conceptual.md explains why this app's local
    login endpoint deliberately borrows OAuth2's shape even though it
    doesn't implement third-party OAuth2 at all) and, not coincidentally,
    exactly what FastAPI's own interactive `/docs` "Authorize" button
    expects to receive back from a login endpoint it's configured against."""

    access_token: str
    token_type: str = "bearer"
