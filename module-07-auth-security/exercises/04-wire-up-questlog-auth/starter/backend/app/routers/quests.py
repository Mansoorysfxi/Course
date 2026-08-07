"""Every /api/quests route. Compare this file, line for line, against
Module 05's version -- see lessons/06-sqlalchemy-with-fastapi.md's
"the swap, concretely" section for exactly what changed (every route
gained `async` and a `session` parameter; nothing about a route's path,
method, status code, or response_model changed at all) and why.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import DbSession, get_quest_or_404
from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate
from app import repository

router = APIRouter(prefix="/api/quests", tags=["quests"])


@router.get("", response_model=list[Quest])
async def list_quests(
    session: DbSession,
    done: bool | None = None,
    priority: str | None = None,
    quest_line: str | None = None,
):
    """The frontend's own QuestListPage still filters/sorts client-side
    (unchanged from Module 04) -- these query parameters exist so this
    route's use of Module 05's query-parameter mechanism stays real and
    testable via curl/Swagger UI, not merely decorative."""
    return await repository.list_quests(session, done, priority, quest_line)


# Registered BEFORE GET /{quest_id} -- "stats" would otherwise be
# indistinguishable, shape-wise, from a real quest_id at this position in
# the path. See Module 05, lessons/02-path-and-query-parameters.md.
@router.get("/stats", response_model=list[QuestLineStats])
async def quest_stats(session: DbSession):
    return await repository.quest_line_stats(session)


@router.get("/{quest_id}", response_model=Quest)
async def get_quest(quest: Annotated[Quest, Depends(get_quest_or_404)]):
    return quest


@router.post("", response_model=Quest, status_code=status.HTTP_201_CREATED)
async def create_quest(data: QuestCreate, session: DbSession):
    return await repository.create_quest(session, data)


@router.patch("/{quest_id}", response_model=Quest)
async def update_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    changes: QuestUpdate,
    session: DbSession,
):
    return await repository.update_quest(session, quest.id, changes)


@router.delete("/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
):
    await repository.delete_quest(session, quest.id)
    return None
