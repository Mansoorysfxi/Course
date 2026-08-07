"""Real PostgreSQL queries. Extended in Module 07 with two things:
`get_user_by_email` / `get_user_by_id` / `create_user` (new, for real
signup/login -- see app/routers/auth.py), and, more importantly, every
*quest* function below now takes an `owner_id` parameter and uses it to
scope which rows a caller can even see or touch.

That second change is this module's entire payoff on this file. Compare
`list_quests`/`get_quest`/`update_quest`/`delete_quest` against Module 06's
versions (still visible in `module-06-databases/.../repository.py` if you
want the exact diff): every one of them now filters `WHERE owner_id = :owner_id`
-- not as an afterthought bolted onto the SQL, but as a parameter every
route (app/routers/quests.py) is now *required* to supply, sourced from
`app.dependencies.CurrentUser`, itself derived from a verified JWT (see
app/security.py). There is no code path left in this file that can return
or modify a quest without knowing, and checking, whose it is. See
lessons/06-building-signup-login.md and
lessons/07-protecting-routes-with-dependencies.md for the full story of
*why* this is the right place to enforce ownership (in the query itself,
not as a check bolted on after the fact in the route function).
"""

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db_models import Quest as QuestRow
from app.db_models import QuestLine, User
from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate

# Kept only as the identity of the demo account seed_if_empty creates below
# -- unlike Module 06, this is no longer "the one user every quest is
# silently assigned to." See lessons/00-setup.md / project/BRIEF.md for
# this account's seeded password, which lets you log in and see the five
# starter quests immediately, without first running through signup by hand.
DEMO_USER_EMAIL = "player@questlog.local"
DEMO_USER_PASSWORD = "dragon-slayer-1"


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
    (Module 06) calls out by name. Looking a quest line up by `name` and
    only creating a new row if none matches is exactly what keeps "Side
    Quests" as one single row no matter how many quests reference it --
    unchanged from Module 06; quest lines are still shared across all
    users, on purpose (a design note in lessons/06-building-signup-login.md
    explains why that's fine even in a multi-user app)."""
    existing = await session.scalar(select(QuestLine).where(QuestLine.name == name))
    if existing is not None:
        return existing
    quest_line = QuestLine(name=name)
    session.add(quest_line)
    await session.flush()  # assigns quest_line.id without a full commit yet
    return quest_line


# --- Users ------------------------------------------------------------


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Used by both signup (to reject a duplicate email with a clean 400
    instead of letting Postgres's own UNIQUE constraint raise a raw
    database error) and login (to find the account a login attempt claims
    to be)."""
    return await session.scalar(select(User).where(User.email == email))


async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
    """Used by app/dependencies.py's `get_current_user` to turn a JWT's
    `sub` claim (a user id -- see app/security.py's `create_access_token`)
    back into a real `User` row for the current request."""
    return await session.scalar(select(User).where(User.id == user_id))


async def create_user(session: AsyncSession, email: str, hashed_password: str) -> User:
    """Inserts a new `users` row. Takes an already-hashed password, never
    a plain one -- app/routers/auth.py's `signup` route is responsible for
    calling `app.security.hash_password` *before* this function ever sees
    the value, exactly the same "this layer never sees a plain-text
    password" boundary app/security.py's own docstring describes."""
    user = User(email=email, hashed_password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# --- Quests (every function below is scoped to one owner) -------------


async def list_quests(
    session: AsyncSession,
    owner_id: str,
    done: bool | None = None,
    priority: str | None = None,
    quest_line: str | None = None,
) -> list[Quest]:
    stmt = (
        select(QuestRow)
        .options(selectinload(QuestRow.quest_line))
        .where(QuestRow.owner_id == owner_id)
    )
    if done is not None:
        stmt = stmt.where(QuestRow.done == done)
    if priority is not None:
        stmt = stmt.where(QuestRow.priority == priority)
    if quest_line is not None:
        stmt = stmt.join(QuestLine).where(QuestLine.name == quest_line)
    stmt = stmt.order_by(QuestRow.created_at)
    rows = (await session.scalars(stmt)).all()
    return [_to_pydantic(row) for row in rows]


async def get_quest(session: AsyncSession, quest_id: str, owner_id: str) -> Quest | None:
    """`WHERE id = :quest_id AND owner_id = :owner_id` -- both conditions,
    combined, not two separate checks. This is deliberate and important:
    if quest `abc123` exists but belongs to a *different* user, this
    returns `None`, exactly the same as if it didn't exist at all. The
    caller (app/dependencies.py's `get_quest_or_404`) turns that into a
    404 -- never a 403 ("Forbidden"). See
    lessons/07-protecting-routes-with-dependencies.md's "404, not 403"
    box: a 403 would confirm to an attacker that a quest with that id
    exists and belongs to *someone*, just not them -- a small information
    leak (an "IDOR," Insecure Direct Object Reference, one of the attacks
    lessons/08-sql-injection-and-orm-safety.md's sibling lesson on broken
    access control names directly) this one query shape closes off
    entirely, for free, just by combining both conditions in the same
    `WHERE` clause instead of fetching the quest first and checking
    ownership as a second, separate step."""
    stmt = (
        select(QuestRow)
        .options(selectinload(QuestRow.quest_line))
        .where(QuestRow.id == quest_id, QuestRow.owner_id == owner_id)
    )
    row = await session.scalar(stmt)
    return _to_pydantic(row) if row is not None else None


async def create_quest(session: AsyncSession, data: QuestCreate, owner_id: str) -> Quest:
    quest_line = await _get_or_create_quest_line(session, data.quest_line)
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
    session: AsyncSession, quest_id: str, changes: QuestUpdate, owner_id: str
) -> Quest | None:
    stmt = (
        select(QuestRow)
        .options(selectinload(QuestRow.quest_line))
        .where(QuestRow.id == quest_id, QuestRow.owner_id == owner_id)
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


async def delete_quest(session: AsyncSession, quest_id: str, owner_id: str) -> bool:
    row = await session.scalar(
        select(QuestRow).where(QuestRow.id == quest_id, QuestRow.owner_id == owner_id)
    )
    if row is None:
        return False
    await session.delete(row)
    await session.commit()
    return True


async def quest_line_stats(session: AsyncSession, owner_id: str) -> list[QuestLineStats]:
    """The GROUP BY lesson's worked example (Module 06), now also scoped
    to one owner -- your stats page shows *your* quest lines' totals, not
    every QuestLog user's combined."""
    done_count = func.sum(case((QuestRow.done.is_(True), 1), else_=0)).label("done")
    stmt = (
        select(
            QuestLine.name.label("quest_line"),
            func.count(QuestRow.id).label("total"),
            done_count,
        )
        .join(QuestRow, QuestRow.quest_line_id == QuestLine.id)
        .where(QuestRow.owner_id == owner_id)
        .group_by(QuestLine.name)
        .order_by(QuestLine.name)
    )
    result = await session.execute(stmt)
    return [
        QuestLineStats(quest_line=row.quest_line, total=row.total, done=row.done)
        for row in result
    ]


async def seed_if_empty(session: AsyncSession) -> None:
    """Runs once at startup (app/main.py's lifespan). Creates one demo
    *account* -- with a real, hashed password this time, unlike Module
    06's password-less stub -- and the same five starter quests, all owned
    by that account, so a fresh checkout of this project has something to
    log into and look at immediately. See project/BRIEF.md for this
    account's seeded credentials.

    Every real quest going forward is created by `POST /api/quests`
    through a signed-in user's own token (app/routers/quests.py) -- this
    function exists purely to give a brand-new database some starting
    content, exactly the job it did in Module 06, just now against an
    account with a real, checkable password instead of no password at
    all."""
    existing_count = await session.scalar(select(func.count(QuestRow.id)))
    if existing_count and existing_count > 0:
        return

    from app.security import hash_password  # local import avoids a cycle:
    # app.security imports app.config, not app.repository -- but keeping
    # this import here, right where it's used once, keeps this module's
    # top-level imports focused on what every other function in this file
    # actually needs.

    user = await get_user_by_email(session, DEMO_USER_EMAIL)
    if user is None:
        user = User(email=DEMO_USER_EMAIL, hashed_password=hash_password(DEMO_USER_PASSWORD))
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
        created.append(await create_quest(session, quest_create, owner_id=user.id))

    # Matches Module 06's seed: the 2nd and 5th seeded quests start already
    # done.
    await update_quest(session, created[1].id, QuestUpdate(done=True), owner_id=user.id)
    await update_quest(session, created[4].id, QuestUpdate(done=True), owner_id=user.id)
