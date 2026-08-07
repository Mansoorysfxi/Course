"""Every /api/quests route. Every route below now takes a `current_user:
CurrentUser` parameter -- new in Module 07 -- which is what makes the
route **protected**: a request with no `Authorization: Bearer <token>`
header, or an invalid/expired one, never reaches this file's own code at
all -- `CurrentUser`'s underlying dependency chain (`get_current_user`,
`oauth2_scheme` -- see app/dependencies.py) rejects it first, with a 401.
Every call into `repository` below also now passes `owner_id=current_user.id`
(directly, or implicitly via `get_quest_or_404`, which itself now requires
`current_user`) -- see lessons/07-protecting-routes-with-dependencies.md
for the full explanation of both changes, and compare this file line for
line against `module-06-databases/.../routers/quests.py` for the exact,
minimal diff Module 07 added: one new parameter per route, one new keyword
argument per repository call.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app import repository
from app.dependencies import CurrentUser, DbSession, get_quest_or_404
from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate

router = APIRouter(prefix="/api/quests", tags=["quests"])


@router.get("", response_model=list[Quest])
async def list_quests(
    session: DbSession,
    current_user: CurrentUser,
    done: bool | None = None,
    priority: str | None = None,
    quest_line: str | None = None,
):
    """The frontend's own QuestListPage still filters/sorts client-side
    (unchanged from Module 04) -- these query parameters exist so this
    route's use of Module 05's query-parameter mechanism stays real and
    testable via curl/Swagger UI, not merely decorative."""
    return await repository.list_quests(
        session, owner_id=current_user.id, done=done, priority=priority, quest_line=quest_line
    )


# Registered BEFORE GET /{quest_id} -- "stats" would otherwise be
# indistinguishable, shape-wise, from a real quest_id at this position in
# the path. See Module 05, lessons/02-path-and-query-parameters.md.
@router.get("/stats", response_model=list[QuestLineStats])
async def quest_stats(session: DbSession, current_user: CurrentUser):
    return await repository.quest_line_stats(session, owner_id=current_user.id)


@router.get("/{quest_id}", response_model=Quest)
async def get_quest(quest: Annotated[Quest, Depends(get_quest_or_404)]):
    # No explicit `current_user` parameter here -- `get_quest_or_404`
    # (app/dependencies.py) already requires and uses one internally.
    # FastAPI still runs that whole dependency chain before this function
    # body executes even once; this route simply never needed the user
    # object *directly* for anything beyond what get_quest_or_404 already
    # did with it.
    return quest


@router.post("", response_model=Quest, status_code=status.HTTP_201_CREATED)
async def create_quest(data: QuestCreate, session: DbSession, current_user: CurrentUser):
    return await repository.create_quest(session, data, owner_id=current_user.id)


@router.patch("/{quest_id}", response_model=Quest)
async def update_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    changes: QuestUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    return await repository.update_quest(session, quest.id, changes, owner_id=current_user.id)


@router.delete("/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
    current_user: CurrentUser,
):
    await repository.delete_quest(session, quest.id, owner_id=current_user.id)
    return None
