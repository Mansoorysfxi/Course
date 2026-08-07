"""Real PostgreSQL queries, replacing Module 05's app/store.py dict.

Every function below takes an AsyncSession (Module 05's routes never saw
one of these -- lessons/06-sqlalchemy-with-fastapi.md explains exactly why
a real database forces this parameter to exist where an in-memory dict
never needed it) and does exactly the job app/store.py's matching function
did, with the exact same name and return type wherever possible -- see
lessons/06's "the swap, concretely" section for a line-by-line diff against
Module 05's store.py. app/routers/quests.py still never writes raw SQL and
never imports app/db_models.py directly -- it only ever calls functions in
this file, exactly the separation Module 05, Lesson 08 set up on purpose.
"""

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db_models import Quest as QuestRow
from app.db_models import QuestLine, User
from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate

DEFAULT_USER_EMAIL = "player@questlog.local"


def _to_pydantic(row: QuestRow) -> Quest:
    """Translates one ORM row (with its `quest_line` relationship already
    loaded -- see the `selectinload` calls below) into the Pydantic `Quest`
    the API contract promises. This one small function is the *entire*
    seam between "how it's stored" (app/db_models.py) and "what the
    frontend sees" (app/models.py) -- see this file's own module docstring.
    """
    return Quest(
        id=row.id,
        title=row.title,
        description=row.description,
        priority=row.priority,
        done=row.done,
        quest_line=row.quest_line.name,
        created_at=row.created_at.isoformat(),
    )


async def _get_or_create_quest_line(session: AsyncSession, name: str) -> QuestLine:
    """The "get it if it exists, otherwise make it" pattern lessons/10
    calls out by name. Looking a quest line up by `name` and only creating
    a new row if none matches is exactly what keeps "Side Quests" as one
    single row no matter how many quests reference it -- the normalization
    payoff from db_models.py's own QuestLine docstring, made concrete."""
    existing = await session.scalar(select(QuestLine).where(QuestLine.name == name))
    if existing is not None:
        return existing
    quest_line = QuestLine(name=name)
    session.add(quest_line)
    await session.flush()  # assigns quest_line.id without a full commit yet
    return quest_line


async def _get_default_owner_id(session: AsyncSession) -> str:
    """Every quest needs an owner_id (db_models.py's Quest.owner_id is
    `nullable=False`). Module 07 will add real signup/login; until then,
    every quest this API creates is silently assigned to one seeded
    "default" user -- see seed_if_empty below and lessons/10's reasoning
    for why this column exists a full module before real auth does."""
    user_id = await session.scalar(
        select(User.id).where(User.email == DEFAULT_USER_EMAIL)
    )
    if user_id is None:  # pragma: no cover -- seed_if_empty should prevent this
        raise RuntimeError(
            "No default user found -- did startup's seed_if_empty() run?"
        )
    return user_id


async def list_quests(
    session: AsyncSession,
    done: bool | None = None,
    priority: str | None = None,
    quest_line: str | None = None,
) -> list[Quest]:
    stmt = select(QuestRow).options(selectinload(QuestRow.quest_line))
    if done is not None:
        stmt = stmt.where(QuestRow.done == done)
    if priority is not None:
        stmt = stmt.where(QuestRow.priority == priority)
    if quest_line is not None:
        stmt = stmt.join(QuestLine).where(QuestLine.name == quest_line)
    stmt = stmt.order_by(QuestRow.created_at)
    rows = (await session.scalars(stmt)).all()
    return [_to_pydantic(row) for row in rows]


async def get_quest(session: AsyncSession, quest_id: str) -> Quest | None:
    stmt = (
        select(QuestRow)
        .options(selectinload(QuestRow.quest_line))
        .where(QuestRow.id == quest_id)
    )
    row = await session.scalar(stmt)
    return _to_pydantic(row) if row is not None else None


async def create_quest(session: AsyncSession, data: QuestCreate) -> Quest:
    quest_line = await _get_or_create_quest_line(session, data.quest_line)
    owner_id = await _get_default_owner_id(session)
    row = QuestRow(
        title=data.title,
        description=data.description,
        priority=data.priority,
        quest_line_id=quest_line.id,
        owner_id=owner_id,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row, attribute_names=["quest_line"])
    return _to_pydantic(row)


async def update_quest(
    session: AsyncSession, quest_id: str, changes: QuestUpdate
) -> Quest | None:
    stmt = (
        select(QuestRow)
        .options(selectinload(QuestRow.quest_line))
        .where(QuestRow.id == quest_id)
    )
    row = await session.scalar(stmt)
    if row is None:
        return None

    updates = changes.model_dump(exclude_unset=True)
    if "quest_line" in updates:
        quest_line_name = updates.pop("quest_line")
        quest_line = await _get_or_create_quest_line(session, quest_line_name)
        row.quest_line_id = quest_line.id
    for field, value in updates.items():
        setattr(row, field, value)

    await session.commit()
    await session.refresh(row, attribute_names=["quest_line"])
    return _to_pydantic(row)


async def delete_quest(session: AsyncSession, quest_id: str) -> bool:
    row = await session.scalar(select(QuestRow).where(QuestRow.id == quest_id))
    if row is None:
        return False
    await session.delete(row)
    await session.commit()
    return True


async def quest_line_stats(session: AsyncSession) -> list[QuestLineStats]:
    """The GROUP BY lesson's worked example, for real: one row per quest
    line, with a total count and a done count, computed by Postgres itself
    rather than by looping over every quest in Python the way Module 05's
    store.py did. See lessons/03-sql-select-insert-update-delete.md and
    lessons/04-joins-and-group-by.md for the plain-SQL version of exactly
    this query before this file translates it into SQLAlchemy."""
    done_count = func.sum(case((QuestRow.done.is_(True), 1), else_=0)).label("done")
    stmt = (
        select(
            QuestLine.name.label("quest_line"),
            func.count(QuestRow.id).label("total"),
            done_count,
        )
        .join(QuestRow, QuestRow.quest_line_id == QuestLine.id)
        .group_by(QuestLine.name)
        .order_by(QuestLine.name)
    )
    result = await session.execute(stmt)
    return [
        QuestLineStats(quest_line=row.quest_line, total=row.total, done=row.done)
        for row in result
    ]


async def seed_if_empty(session: AsyncSession) -> None:
    """Runs once at startup (app/main.py's lifespan). Seeds a default user
    and the same starting quests Module 05's store.seed() used, but only if
    the quests table is genuinely empty -- so restarting this app (or
    `--reload` triggering) never duplicates seed data the way re-running
    Module 05's in-memory seed() on every startup never risked (there was
    nothing left to duplicate against). Migrations (Alembic, lessons/07)
    create the *tables*; this function is purely about starting *data*, a
    distinction lessons/07 draws explicitly."""
    existing_count = await session.scalar(select(func.count(QuestRow.id)))
    if existing_count and existing_count > 0:
        return

    user = await session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    if user is None:
        user = User(email=DEFAULT_USER_EMAIL)
        session.add(user)
        await session.flush()

    starter = [
        QuestCreate(
            title="Slay the Dragon",
            description="The dragon has been terrorizing the northern villages. Someone has to go.",
            priority="high",
            quest_line="Main Story",
        ),
        QuestCreate(
            title="Gather Healing Herbs",
            description="The village healer needs five bundles of silverleaf from the eastern woods.",
            priority="low",
            quest_line="Village Errands",
        ),
        QuestCreate(
            title="Deliver the Sealed Letter",
            description="A courier's letter must reach the capital before the harvest festival begins.",
            priority="medium",
            quest_line="Village Errands",
        ),
        QuestCreate(
            title="Clear the Old Mine",
            description="Something has been digging new tunnels in the abandoned mine. Investigate.",
            priority="high",
            quest_line="Side Quests",
        ),
        QuestCreate(
            title="Repair the Bridge",
            description="The stone bridge to the market town has a collapsed section.",
            priority="medium",
            quest_line="Side Quests",
        ),
    ]
    created: list[Quest] = []
    for quest_create in starter:
        created.append(await create_quest(session, quest_create))

    # Matches Module 05's store.seed(): the 2nd and 5th seeded quests start
    # already done.
    await update_quest(session, created[1].id, QuestUpdate(done=True))
    await update_quest(session, created[4].id, QuestUpdate(done=True))
