"""Every /api/quests route. See lessons/08-building-the-questlog-api.md for
the full, line-by-line explanation of every piece of this file."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_quest_or_404
from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate
from app import store

router = APIRouter(prefix="/api/quests", tags=["quests"])


@router.get("", response_model=list[Quest])
def list_quests(
    done: bool | None = None,
    priority: str | None = None,
    quest_line: str | None = None,
):
    """The frontend's own QuestListPage still filters/sorts client-side
    (unchanged from Module 04) -- these query parameters exist so this
    route's use of Lesson 02's query-parameter mechanism is real and
    testable via curl/Swagger UI, not merely decorative."""
    quests = store.list_quests()
    if done is not None:
        quests = [q for q in quests if q.done == done]
    if priority is not None:
        quests = [q for q in quests if q.priority == priority]
    if quest_line is not None:
        quests = [q for q in quests if q.quest_line == quest_line]
    return quests


# Registered BEFORE GET /{quest_id} -- "stats" would otherwise be
# indistinguishable, shape-wise, from a real quest_id at this position in
# the path. See lessons/02-path-and-query-parameters.md and Exercise 05.
@router.get("/stats", response_model=list[QuestLineStats])
def quest_stats():
    return store.quest_line_stats()


@router.get("/{quest_id}", response_model=Quest)
def get_quest(quest: Annotated[Quest, Depends(get_quest_or_404)]):
    return quest


@router.post("", response_model=Quest, status_code=status.HTTP_201_CREATED)
def create_quest(data: QuestCreate):
    return store.create_quest(data)


@router.patch("/{quest_id}", response_model=Quest)
def update_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    changes: QuestUpdate,
):
    return store.update_quest(quest.id, changes)


@router.delete("/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quest(quest: Annotated[Quest, Depends(get_quest_or_404)]):
    store.delete_quest(quest.id)
    return None
