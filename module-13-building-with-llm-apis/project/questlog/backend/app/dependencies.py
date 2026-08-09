"""FastAPI dependencies -- see lessons/06-sqlalchemy-with-fastapi.md
(Module 06) for `DbSession`, unchanged here,
lessons/07-protecting-routes-with-dependencies.md (Module 07) for
`oauth2_scheme`, `get_current_user`, `CurrentUser`, and the
authenticated `get_quest_or_404`,
lessons/06-docker-compose-multi-service-apps.md (Module 10) for
`RedisClient`, and
lessons/07-building-questlogs-ai-assistant-backend.md (Module 13, this
module) for `get_ai_client`/`AiClient`, new below.
"""

from typing import Annotated

import anthropic
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository
from app.cache import get_redis_client
from app.config import settings
from app.database import get_db
from app.db_models import User
from app.models import Quest
from app.security import decode_access_token

# A short alias so every route file that needs a database session can
# write `Annotated[AsyncSession, Depends(get_db)]` once, here, instead of
# spelling out `Depends(get_db)` fresh in every single route's signature.
# Purely a readability convenience -- see lessons/06's "DbSession alias"
# box (Module 06) for why this is a common, idiomatic FastAPI pattern.
DbSession = Annotated[AsyncSession, Depends(get_db)]

# NEW in Module 10 -- the exact same alias pattern as DbSession above, for
# app/cache.py's `get_redis_client`. A route that wants the Redis client
# writes `redis: RedisClient` in its signature, exactly like
# `session: DbSession`; FastAPI resolves both the same way. See
# app/routers/quests.py for where this is actually used.
RedisClient = Annotated[Redis, Depends(get_redis_client)]


# `OAuth2PasswordBearer` is a FastAPI **security scheme** -- see
# lessons/07-protecting-routes-with-dependencies.md for exactly what that
# means and what this one specific class actually does (two things, and
# two things only: reads the `Authorization: Bearer <token>` header off
# the incoming request, and raises a 401 itself if that header is
# missing entirely -- it does **not** check whether the token inside it
# is genuine; that is entirely `get_current_user`'s job, below).
# `tokenUrl` doesn't change this dependency's runtime behavior at all --
# it exists purely so FastAPI's auto-generated OpenAPI docs (Module 05,
# Lesson 07) know which endpoint's "Authorize" button should ask for a
# username/password and hand back a token, letting you log in and try
# protected routes directly from `/docs`.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: DbSession,
) -> User:
    """The dependency every protected route in this app ultimately depends
    on (directly, or via `get_quest_or_404` below). Three things can go
    wrong, and all three produce the exact same response on purpose --
    a `401 Unauthorized` with a `WWW-Authenticate: Bearer` header (part of
    the HTTP spec's own convention for 401s, not something this app
    invented) -- so a caller can never distinguish "your token is expired"
    from "your token is forged" from "that user no longer exists," which
    is exactly the point: telling an attacker *which* of those is true
    would hand them a diagnostic tool for free. See
    lessons/07-protecting-routes-with-dependencies.md's "one error
    message, three failure reasons" box.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        # Covers a forged signature, a malformed token, AND an expired one
        # (PyJWT's ExpiredSignatureError is itself a subclass of
        # InvalidTokenError) -- one `except` clause, three real causes,
        # exactly the "don't tell attackers which" reasoning above.
        # `from exc` (Module 08's ruff, rule B904, flagged the version of
        # this line with no `from` at all) keeps Python's own exception
        # chain intact for anyone reading a server-side traceback/log --
        # it changes nothing about what the client ever sees over HTTP.
        raise credentials_exception from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await repository.get_user_by_id(session, user_id)
    if user is None:
        # The token is genuinely valid and unexpired, but the account it
        # names no longer exists (e.g. deleted after the token was
        # issued). Still a 401, for the same reason as above.
        raise credentials_exception

    return user


# The alias every route in app/routers/quests.py and app/routers/auth.py
# actually writes -- `current_user: CurrentUser` -- instead of spelling
# out `Annotated[User, Depends(get_current_user)]` in every single
# signature. Adding this one parameter to a route is the entire mechanism
# that makes that route "protected" -- see
# lessons/07-protecting-routes-with-dependencies.md for why a route with
# no such parameter at all is reachable by anyone, token or not.
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_ai_client() -> anthropic.AsyncAnthropic | None:
    """NEW in Module 13 -- the exact same "resolve a real external client
    from settings, once per request, via FastAPI's own dependency
    mechanism" shape as `get_redis_client` (app/cache.py) and `get_db`
    (app/database.py). Deliberately returns `None` -- not a client that
    would immediately fail its first real call -- when no
    `ANTHROPIC_API_KEY` is configured, rather than letting
    `anthropic.AsyncAnthropic()` construct a client against a missing key
    and fail later, deeper in the call stack, with a less obvious error.
    See lessons/00-setup.md for exactly why this field is optional (the
    same "this app must run correctly with no key at all" principle
    app/config.py's `sentry_dsn` already established in Module 11) and
    lessons/07-building-questlogs-ai-assistant-backend.md for why the
    route that depends on this (app/routers/quests.py's
    `suggest_quest_breakdown`) turns a `None` here into a clean, specific
    `503 Service Unavailable` rather than a confusing 500.

    Uses the **async** client (`anthropic.AsyncAnthropic`, not the plain
    `anthropic.Anthropic` this course's earlier, synchronous scripts and
    exercises use) because this function runs inside an `async def` FastAPI
    route -- calling the synchronous client's blocking network I/O directly
    from an async route would freeze the entire event loop (every other
    request this server is handling) for as long as the Anthropic API call
    takes. See lessons/01-calling-the-anthropic-api.md's "sync vs. async
    client" box, and Module 01's own event-loop lesson, for the full "why."

    Constructing an `AsyncAnthropic` instance itself does no network I/O
    (it doesn't check the key is valid, doesn't make a request) -- it's a
    cheap object to create fresh on every request, exactly like
    `get_redis_client` already does for `Redis(connection_pool=...)`.
    """
    if not settings.anthropic_api_key:
        return None
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


# The alias app/routers/quests.py's `suggest_quest_breakdown` route
# actually writes -- `ai_client: AiClient` -- exactly the same pattern as
# `DbSession` and `RedisClient` above. Typed as `AsyncAnthropic | None`
# (not just `AsyncAnthropic`) so the route's own type checker keeps it
# honest that it MUST handle the "not configured" case before ever calling
# `ai_client.messages.stream(...)`.
AiClient = Annotated[anthropic.AsyncAnthropic | None, Depends(get_ai_client)]


async def get_quest_or_404(quest_id: str, session: DbSession, current_user: CurrentUser) -> Quest:
    """Now takes `current_user` too (new in Module 07) and passes
    `current_user.id` through to `repository.get_quest` as the required
    `owner_id` -- see that function's own docstring for exactly why a
    quest that exists, but belongs to someone else, produces this same
    404 rather than a 403."""
    quest = await repository.get_quest(session, quest_id, owner_id=current_user.id)
    if quest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quest with id '{quest_id}'",
        )
    return quest
