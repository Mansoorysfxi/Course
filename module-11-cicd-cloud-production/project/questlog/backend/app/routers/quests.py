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

**NEW in Module 10:** `list_quests` now reads from, and every mutating
route (`create_quest`/`update_quest`/`delete_quest`) now invalidates, a
Redis cache of each user's own unfiltered quest list -- see app/cache.py
for the cache-key/TTL policy and
lessons/06-docker-compose-multi-service-apps.md for the full explanation
of what a cache is, why Redis, and why this is deliberately scoped to
only the unfiltered list call. Every route's underlying `repository` call
is completely unchanged from Module 07 -- caching is added entirely
*around* the existing database logic, in this router file only, never
inside app/repository.py itself. That separation is deliberate: this
file decides *when* to trust a cached answer instead of asking Postgres;
app/repository.py stays exactly what it always was, "the only code that
knows how to talk to the database," with zero awareness that a cache
exists at all.
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app import repository
from app.cache import QUEST_LIST_CACHE_TTL_SECONDS, quest_list_cache_key
from app.dependencies import CurrentUser, DbSession, RedisClient, get_quest_or_404
from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate

router = APIRouter(prefix="/api/quests", tags=["quests"])


@router.get("", response_model=list[Quest])
async def list_quests(
    response: Response,
    session: DbSession,
    current_user: CurrentUser,
    redis: RedisClient,
    done: bool | None = None,
    priority: str | None = None,
    quest_line: str | None = None,
):
    """The frontend's own QuestListPage still filters/sorts client-side
    (unchanged from Module 04) -- these query parameters exist so this
    route's use of Module 05's query-parameter mechanism stays real and
    testable via curl/Swagger UI, not merely decorative.

    **Caching, added in Module 10:** only the *unfiltered* call (no
    `done`/`priority`/`quest_line` at all -- exactly what the frontend's
    Quest Board requests on every page load) is cached. A filtered
    request (e.g. `?done=true`) deliberately bypasses the cache entirely
    and always asks Postgres directly -- see app/cache.py's module
    docstring for why this module keeps the cached surface area small on
    purpose. The `X-Cache` response header (`HIT`, `MISS`, or `BYPASS`)
    is not part of QuestLog's real API contract -- it exists purely so
    this course's lesson and exercises can *observe*, from a plain
    `curl -i`, which of the three happened on any given request, without
    needing server logs open. See
    lessons/06-docker-compose-multi-service-apps.md, "Try it yourself."
    """
    if done is not None or priority is not None or quest_line is not None:
        response.headers["X-Cache"] = "BYPASS"
        return await repository.list_quests(
            session, owner_id=current_user.id, done=done, priority=priority, quest_line=quest_line
        )

    cache_key = quest_list_cache_key(current_user.id)
    cached_json = await redis.get(cache_key)
    if cached_json is not None:
        response.headers["X-Cache"] = "HIT"
        return [Quest(**item) for item in json.loads(cached_json)]

    quests = await repository.list_quests(session, owner_id=current_user.id)
    response.headers["X-Cache"] = "MISS"
    await redis.set(
        cache_key,
        json.dumps([quest.model_dump(by_alias=True) for quest in quests]),
        ex=QUEST_LIST_CACHE_TTL_SECONDS,
    )
    return quests


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
async def create_quest(
    data: QuestCreate, session: DbSession, current_user: CurrentUser, redis: RedisClient
):
    quest = await repository.create_quest(session, data, owner_id=current_user.id)
    # Cache invalidation, added in Module 10: a newly created quest means
    # this user's previously cached "all my quests" answer (if one still
    # exists -- it may already have expired on its own, this call is safe
    # either way) is now wrong -- it's missing the quest that was just
    # created. Deleting the key outright, rather than trying to patch it
    # in place, is the simplest correct option: the *next* GET
    # /api/quests naturally re-fetches from Postgres and re-populates the
    # cache with a fresh, correct answer. See
    # lessons/06-docker-compose-multi-service-apps.md's "cache
    # invalidation" section for why this course deliberately doesn't try
    # to be cleverer than this.
    await redis.delete(quest_list_cache_key(current_user.id))
    return quest


@router.patch("/{quest_id}", response_model=Quest)
async def update_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    changes: QuestUpdate,
    session: DbSession,
    current_user: CurrentUser,
    redis: RedisClient,
):
    updated = await repository.update_quest(session, quest.id, changes, owner_id=current_user.id)
    await redis.delete(quest_list_cache_key(current_user.id))
    return updated


@router.delete("/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    session: DbSession,
    current_user: CurrentUser,
    redis: RedisClient,
):
    await repository.delete_quest(session, quest.id, owner_id=current_user.id)
    await redis.delete(quest_list_cache_key(current_user.id))
    return None
