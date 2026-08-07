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
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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
