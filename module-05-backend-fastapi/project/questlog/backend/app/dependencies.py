"""See lessons/04-dependency-injection-and-depends.md -- exactly the
get_quest_or_404 pattern taught there, used for real by every route in
routers/quests.py that needs an existing quest by id."""

from fastapi import HTTPException, status

from app import store
from app.models import Quest


def get_quest_or_404(quest_id: str) -> Quest:
    quest = store.get_quest(quest_id)
    if quest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quest with id '{quest_id}'",
        )
    return quest
