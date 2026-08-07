"""Already complete -- do not modify. See INSTRUCTIONS.md.

A deliberately simpler model set than the real QuestLog capstone's (no
camelCase aliasing -- this is a standalone practice API, not required to
match any particular frontend). See lessons/03-request-bodies-and-pydantic-validation.md
and lessons/08-building-the-questlog-api.md for the patterns this follows.
"""

from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["low", "medium", "high"]


class QuestBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str
    priority: Priority
    quest_line: str = Field(min_length=1)


class QuestCreate(QuestBase):
    pass


class QuestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    quest_line: str | None = Field(default=None, min_length=1)
    done: bool | None = None


class Quest(QuestBase):
    id: str
    done: bool
    created_at: str
