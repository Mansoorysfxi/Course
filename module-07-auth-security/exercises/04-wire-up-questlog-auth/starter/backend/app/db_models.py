"""The real, persistent schema: three SQLAlchemy ORM classes, each mapping
to one real Postgres table. See lessons/09-normalization-and-schema-design.md
and lessons/10-designing-questlogs-schema.md for exactly why the schema is
shaped this way (three tables, not one), and lessons/05-orms-and-sqlalchemy-basics.md
for what every piece of syntax below (`Mapped`, `mapped_column`,
`relationship`) actually does.

Distinct from app/models.py (the Pydantic *API* shapes) on purpose -- see
that file's own module docstring for the reasoning. Nothing in this file is
ever sent directly over HTTP; app/repository.py is the only code that reads
from these classes and turns the result into the Pydantic shapes
app/models.py describes.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _new_id() -> str:
    """A plain Python function, not a database feature -- called once per
    new row, before it's ever sent to Postgres. Deliberately the exact same
    `str(uuid.uuid4())` app/store.py used in Module 05, so switching from
    the in-memory dict to a real table changes *where* an id comes from
    (Python, either way) not *how*."""
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """A stub, deliberately minimal -- real authentication (password
    hashes, login, sessions/JWTs) is Module 07's entire job, not this
    module's. This table exists now, one module early, for a single
    concrete reason explained in lessons/10: adding an owner_id foreign key
    to quests *after* real users exist would mean an awkward migration that
    invents an owner for every already-existing quest. Adding the column
    now, backed by exactly one seeded row (see repository.py's
    `seed_if_empty`), costs almost nothing today and saves Module 07 from
    that exact pain."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    quests: Mapped[list["Quest"]] = relationship(back_populates="owner")


class QuestLine(Base):
    """Module 05's `Quest.quest_line` was a free-typed string -- anyone
    creating a quest could type "Side Quests", "side quests", or "Side
    Quest" and the in-memory store would happily treat those as three
    unrelated groups. This table is exactly lessons/09's normalization
    argument made real: one authoritative row per quest line, referenced
    by id from every quest that belongs to it, so a typo can no longer
    silently fork a group in two. The external API contract does not
    change -- app/repository.py joins this table in and still hands the
    frontend a plain `questLine` *name* string, per lessons/10's "why the
    contract doesn't need to change" section."""

    __tablename__ = "quest_lines"
    __table_args__ = (UniqueConstraint("name", name="uq_quest_lines_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    quests: Mapped[list["Quest"]] = relationship(back_populates="quest_line")


class Quest(Base):
    """The one table with a direct Module 05 ancestor -- compare this
    class's columns field-for-field against app/models.py's `Quest`
    Pydantic model and Module 05's own `app/store.py`. The two new columns
    (`quest_line_id`, `owner_id`) are foreign keys -- see
    lessons/01-why-a-database-and-the-relational-model.md for exactly what
    that term means and why a *reference* replaces a *copy* of the related
    row's data."""

    __tablename__ = "quests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    quest_line_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quest_lines.id"), nullable=False
    )
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # `relationship(...)` is an ORM-only convenience -- it is not a real
    # database column and Alembic will never generate a migration for it.
    # It lets Python code write `quest.quest_line.name` and have SQLAlchemy
    # run the join for you, instead of you writing that join by hand every
    # time. See lessons/05's "relationship() vs a foreign key column" box.
    quest_line: Mapped["QuestLine"] = relationship(back_populates="quests")
    owner: Mapped["User"] = relationship(back_populates="quests")
