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

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
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


class QuestNote(Base):
    """NEW in Module 14 -- one raw, human-written note attached to one
    quest. See lessons/08-building-questlogs-notes-feature-backend.md for
    the full walkthrough; short version here: a player pastes or types
    free text about a quest (boss strategies, NPC dialogue they want to
    remember, their own planning notes -- anything), this table stores
    that text verbatim, and app/chunking.py + app/embeddings.py turn it
    into the `NoteChunk` rows below, which is what retrieval actually
    searches.

    `owner_id` is kept directly on this table too, even though it's
    already reachable via `quest.owner_id` through a join -- a small,
    deliberate denormalization, for the exact same reason
    `Quest.owner_id` itself exists directly on `quests` instead of forcing
    every ownership check through `quest_lines` (see
    lessons/09-normalization-and-schema-design.md and
    lessons/10-designing-questlogs-schema.md, Module 06): a direct column
    means `WHERE owner_id = :owner_id` on *this* table, with no join
    required, for every query that needs to prove "this note belongs to
    this user" -- simpler code, one fewer join, and a query plan that
    doesn't depend on the `quests` table being touched at all. See
    lessons/06-similarity-search-in-practice.md's "denormalizing on
    purpose, again" box for the full discussion, and `NoteChunk.quest_id`
    below for a second, related instance of the same idea.
    """

    __tablename__ = "quest_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    quest_id: Mapped[str] = mapped_column(String(36), ForeignKey("quests.id"), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    chunks: Mapped[list["NoteChunk"]] = relationship(
        back_populates="note", cascade="all, delete-orphan"
    )


class NoteChunk(Base):
    """NEW in Module 14 -- one chunk of one `QuestNote`, plus that chunk's
    embedding vector. This is the table `app/repository.py`'s
    `find_similar_chunks` actually queries -- see
    lessons/05-similarity-search-in-practice.md for the full walkthrough
    of that query, and app/chunking.py / app/embeddings.py for how a row
    here gets created in the first place.

    `note_id`'s `ondelete="CASCADE"` is the **first** foreign key in this
    entire codebase to use it. Every earlier foreign key in this app
    (`Quest.quest_line_id`, `Quest.owner_id`) relied on the ORM/repository
    layer to delete or reassign child rows itself before removing a
    parent -- see, e.g., how nothing in this app ever deletes a
    `QuestLine` at all. `ondelete="CASCADE"` instead pushes that rule down
    into Postgres itself: it tells the database "if the `quest_notes` row
    this chunk points at is ever deleted, delete this row too, as part of
    the very same transaction, with no second query required." This
    matters here specifically because `app/repository.py`'s `delete_note`
    only issues one `DELETE FROM quest_notes WHERE id = ...` -- it never
    touches `note_chunks` itself at all; the chunks disappear purely
    because Postgres's own foreign key enforcement removes them
    automatically. The trade-off, stated honestly: this rule now lives in
    the database schema (this migration) rather than in Python you can
    read and step through -- see lessons/04-vector-databases-and-pgvector.md's
    "ON DELETE CASCADE: convenience with a cost" box for the full
    discussion of why this module picks it anyway for this specific
    parent/child relationship (a note's chunks have no meaning at all
    without their note) where earlier ones didn't.

    `quest_id` is copied from the parent `QuestNote` -- a second,
    deliberate denormalization (see `QuestNote`'s own docstring above),
    for a different, more important reason this time: **read performance
    on the hot retrieval path**. `repository.find_similar_chunks` needs to
    answer "which chunks belong to this one quest" on every single
    question a player asks -- if `quest_id` weren't copied here, that
    query would need to join `note_chunks` to `quest_notes` just to filter
    by quest, on every request. Copying `quest_id` onto this table means
    `WHERE quest_id = :quest_id` filters directly, with zero joins, right
    where the actual `<=>` (cosine distance) operator does its
    (comparatively expensive) work. This is a textbook answer to "when is
    denormalizing for read performance a reasonable, honest trade-off"
    (Module 06's own normalization lesson asked this question in the
    abstract; this is a concrete, real answer): the copied value can never
    drift out of sync with its source (a chunk's `quest_id` is written
    once, at creation, from its parent note, and a chunk is never moved to
    a different note afterward), and the join it avoids sits on a query
    that runs on every single request this feature makes, not an
    occasional report.

    `embedding`'s type, `Vector(384).with_variant(JSON(), "sqlite")`, is
    explained in full in this file's own module docstring reference (see
    lessons/04-vector-databases-and-pgvector.md's "with_variant, in full"
    section) -- short version: on Postgres, this column is a real
    `vector(384)` with real pgvector operators (`.cosine_distance()`,
    used by `find_similar_chunks`) available on it; on SQLite (used only
    by this backend's own test suite), it compiles to a plain `JSON`
    column that can store and round-trip the same Python `list[float]` for
    structural tests, but has no distance operator at all -- which is
    exactly why the real similarity *math* also exists as a plain,
    DB-independent Python function, `app/rag.py`'s
    `rank_by_cosine_similarity`, that the test suite uses instead.
    """

    __tablename__ = "note_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    note_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quest_notes.id", ondelete="CASCADE"), nullable=False
    )
    quest_id: Mapped[str] = mapped_column(String(36), ForeignKey("quests.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384).with_variant(JSON(), "sqlite"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    note: Mapped["QuestNote"] = relationship(back_populates="chunks")
