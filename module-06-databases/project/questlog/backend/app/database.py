"""The async SQLAlchemy engine, session factory, and declarative base.

See lessons/05-orms-and-sqlalchemy-basics.md for what an "engine" and a
"session" actually are, and lessons/06-sqlalchemy-with-fastapi.md for why
`get_db` below is written as a FastAPI dependency (Module 05, Lesson 04)
rather than a plain function every route calls itself.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL

# The engine is the object that actually knows how to talk to Postgres --
# it owns a pool of real network connections underneath. `echo=False` keeps
# the terminal quiet; flip it to True locally (lessons/05, "Try it
# yourself") to watch the exact SQL SQLAlchemy sends for every operation
# this app performs.
engine = create_async_engine(DATABASE_URL, echo=False)

# A "factory" that produces a new AsyncSession bound to `engine` each time
# it's called. `expire_on_commit=False` means an object you already loaded
# stays readable after a commit instead of SQLAlchemy forcing a fresh
# database round-trip the next time you touch one of its attributes --
# convenient for this app's pattern of committing, then immediately
# returning the just-written object in the HTTP response.
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Every ORM model in db_models.py inherits from this. SQLAlchemy uses
    the collection of every class that inherits from one shared Base to
    know the *complete* set of tables a project defines -- this is exactly
    what Alembic's autogenerate (lessons/07) reads from, via
    `Base.metadata`, to compare "what the models say" against "what the
    actual database currently has"."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """A FastAPI dependency (Module 05, Lesson 04) that hands a route a
    real, open database session for exactly the lifetime of one request,
    and guarantees it's closed afterward -- even if the route raises an
    exception. `async with` is doing the same guaranteed-cleanup job here
    that Module 01, Lesson 10's context managers do generally; AsyncSession
    supports `async with` specifically because opening/closing a database
    session is itself an operation worth awaiting."""
    async with AsyncSessionLocal() as session:
        yield session
