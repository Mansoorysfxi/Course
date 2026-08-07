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


class QuestLineStats(BaseModel):
    quest_line: str
    total: int
    done: int
