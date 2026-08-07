"""See lessons/06-sqlalchemy-with-fastapi.md for why get_quest_or_404 below
is now `async def` and takes a `session` -- both new compared to Module
05's version of this exact function, and both explained there in full.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository
from app.database import get_db
from app.models import Quest

# A short alias so every route file that needs a database session can
# write `Annotated[AsyncSession, Depends(get_db)]` once, here, instead of
# spelling out `Depends(get_db)` fresh in every single route's signature.
# Purely a readability convenience -- see lessons/06's "DbSession alias"
# box for why this is a common, idiomatic FastAPI pattern.
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_quest_or_404(quest_id: str, session: DbSession) -> Quest:
    quest = await repository.get_quest(session, quest_id)
    if quest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quest with id '{quest_id}'",
        )
    return quest
