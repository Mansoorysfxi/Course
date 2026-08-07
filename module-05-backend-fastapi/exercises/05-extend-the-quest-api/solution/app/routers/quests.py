from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_quest_or_404, require_quests_in_line
from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate
from app import store

router = APIRouter(prefix="/api/quests", tags=["quests"])


@router.get("", response_model=list[Quest])
def list_quests():
    return store.list_quests()


# Registered BEFORE GET /{quest_id} -- see INSTRUCTIONS.md's ordering note.
# "stats" is, shape-wise, indistinguishable from a real quest_id value at
# this position in the path; the first-registered matching route wins.
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


@router.patch("/complete-line/{quest_line}", response_model=list[Quest])
def complete_line(
    # The dependency's own return value isn't actually needed here -- its
    # only job is to raise 404 if the line doesn't exist, per Lesson 04's
    # own pattern of putting a check in exactly one reusable place.
    _quests_in_line: Annotated[list[Quest], Depends(require_quests_in_line)],
    quest_line: str,
):
    return store.complete_line(quest_line)
