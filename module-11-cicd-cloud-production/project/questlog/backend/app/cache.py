"""Redis client setup and cache-key helpers -- NEW in Module 10.

QuestLog's busiest read is `GET /api/quests` (the Quest Board's very
first network call, every time the frontend loads) -- and, for any one
signed-in user, its answer usually hasn't changed between one page load
and the next: most users read their quest list far more often than they
create/update/delete a quest. That gap -- "read constantly, write rarely"
-- is exactly the shape of problem a **cache** exists to solve. See
lessons/06-docker-compose-multi-service-apps.md for the full "what is a
cache, and why Redis specifically instead of a plain Python dict"
explanation; this file is that lesson's concrete, running code.

**Scope, deliberately kept small:** this file caches exactly one thing --
a signed-in user's own *unfiltered* quest list (`GET /api/quests` with no
`done`/`priority`/`quest_line` query parameters, the call the frontend's
Quest Board page actually makes). Filtered queries (`?done=true`, etc.)
still go straight to Postgres, uncached, every time. A real production
system might cache those too, with a cache key that encodes every filter
combination -- but that's real added complexity (more keys to invalidate,
more ways for a stale value to hide in some corner) for a case this
course's QuestLog doesn't need to demonstrate the concept. This module is
about Docker and Compose, not about building a general-purpose caching
layer -- see app/routers/quests.py for exactly where this narrow scope is
enforced.
"""

from redis.asyncio import ConnectionPool, Redis

from app.config import settings

# A connection **pool**, created once, when this module is first imported
# -- not a single open connection. This deliberately mirrors
# app/database.py's `engine = create_async_engine(...)`: both are "the one
# object, per process, that actually knows how to open real network
# connections to a specific external service," created once and reused,
# never recreated per-request. `ConnectionPool.from_url` parses
# `settings.redis_url` (e.g. `redis://localhost:6379/0`) into the host,
# port, and database number Redis's own wire protocol needs.
_redis_pool = ConnectionPool.from_url(settings.redis_url, decode_responses=True)
# `decode_responses=True` -- without it, every value this client reads
# back from Redis would be raw `bytes` (`b"..."`) instead of a normal
# Python `str`, because Redis itself has no concept of "this value is
# text" -- it stores and returns everything as raw bytes. Setting this
# once, here, means every call site in this file and in
# app/routers/quests.py can work with plain strings and never think about
# encoding/decoding again.


def get_redis_client() -> Redis:
    """A FastAPI dependency -- same shape and same job as
    app/database.py's `get_db`, just for Redis instead of Postgres. Every
    route that wants a Redis client declares
    `redis: Annotated[Redis, Depends(get_redis_client)]` (aliased to
    `RedisClient` in app/dependencies.py), and FastAPI calls this function
    to produce it, exactly the same dependency-injection mechanism Module
    05 taught for `get_db`.

    Unlike `get_db`, this isn't an `async def` generator with a `yield` --
    there's no per-request "session" to open and guarantee closed
    afterward the way there is for a SQL transaction. `Redis(...)`
    constructed from an existing pool is a cheap, effectively free object
    to create per call; the actual, expensive-to-create thing (the pool of
    real TCP connections) was already built once, above, at import time.
    """
    return Redis(connection_pool=_redis_pool)


# How long a cached quest list is trusted before it's treated as stale and
# re-fetched from Postgres, even if nothing ever explicitly invalidated
# it. 30 seconds is deliberately short for a learning project: long enough
# to demonstrably matter (Lesson 06's own "Try it yourself" has you watch
# a cache hit happen), short enough that if this course's own
# invalidation-on-write logic ever missed a case, the damage -- someone
# seeing a slightly stale quest list -- self-heals within half a minute
# without any human intervening. See lessons/06's "what TTL actually
# buys you, and why this app doesn't try to invalidate perfectly" section.
QUEST_LIST_CACHE_TTL_SECONDS = 30


def quest_list_cache_key(owner_id: str) -> str:
    """One cache key per user, for their unfiltered quest list. The
    `questlog:` prefix is a convention, not a requirement -- Redis has no
    concept of folders or namespaces, every key lives in one flat space
    per database number, so a shared prefix is how real projects avoid two
    unrelated features accidentally colliding on the same key name (e.g.
    if a future module added a second cache for something else entirely).
    """
    return f"questlog:quests:{owner_id}"
