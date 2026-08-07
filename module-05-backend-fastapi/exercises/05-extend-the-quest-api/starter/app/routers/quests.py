"""The existing CRUD routes are already complete -- do not modify them.
Add your two new routes (GET /stats and PATCH /complete-line/{quest_line})
per INSTRUCTIONS.md -- pay close attention to WHERE you register them
relative to the existing {quest_id} routes (see INSTRUCTIONS.md's ordering
note, and lessons/02-path-and-query-parameters.md).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_quest_or_404
from app.models import Quest, QuestCreate, QuestUpdate
from app import store

router = APIRouter(prefix="/api/quests", tags=["quests"])


@router.get("", response_model=list[Quest])
def list_quests():
    return store.list_quests()


# TODO (exercise 05): GET /stats -- register this BEFORE the
# GET /{quest_id} route below, per INSTRUCTIONS.md's ordering note.


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


# TODO (exercise 05): PATCH /complete-line/{quest_line} -- marks every
# quest in that quest line done, returns the updated list. 404 via a new
# dependency if no quest currently has that quest line.
