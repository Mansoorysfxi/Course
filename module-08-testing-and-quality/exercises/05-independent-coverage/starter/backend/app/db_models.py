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
from datetime import UTC, datetime

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
    return datetime.now(UTC)


class User(Base):
    """Module 06 left this table deliberately minimal -- no password, no
    login -- for a single concrete reason explained in that module's
    lessons/10: adding an owner_id foreign key to quests *after* real
    users existed would have meant an awkward migration that invents an
    owner for every already-existing quest. That's why this table, and
    `Quest.owner_id`, already existed a full module before this one.

    This module (07) is what finally makes a `User` a real account: the
    new `hashed_password` column below (see the accompanying Alembic
    migration, `alembic/versions/..._add_hashed_password_to_users.py`,
    for exactly how a column gets added to an already-existing table) is
    the one and only piece of a user's password this backend ever stores
    -- see app/security.py's `hash_password`/`verify_password` and
    lessons/02-password-hashing.md for what actually goes into it and why
    a real plain-text password never reaches this file, this table, or any
    log line this app writes."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # A bcrypt hash string (see app/security.py's hash_password), never a
    # plain-text password. String(255) is comfortably larger than a bcrypt
    # hash actually needs (bcrypt hashes are a fixed 60 characters) --
    # matching the generous sizing convention db_models.py already used
    # for `email` above.
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
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
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    # `relationship(...)` is an ORM-only convenience -- it is not a real
    # database column and Alembic will never generate a migration for it.
    # It lets Python code write `quest.quest_line.name` and have SQLAlchemy
    # run the join for you, instead of you writing that join by hand every
    # time. See lessons/05's "relationship() vs a foreign key column" box.
    quest_line: Mapped["QuestLine"] = relationship(back_populates="quests")
    owner: Mapped["User"] = relationship(back_populates="quests")
