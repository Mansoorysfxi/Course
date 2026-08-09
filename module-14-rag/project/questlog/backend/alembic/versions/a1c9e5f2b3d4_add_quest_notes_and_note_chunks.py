"""add quest_notes and note_chunks (pgvector)

Revision ID: a1c9e5f2b3d4
Revises: 62f2ef5e3f58
Create Date: 2026-08-09 10:00:00.000000

See lessons/04-vector-databases-and-pgvector.md's "the migration,
concretely" section for the full, line-by-line walkthrough of this file.
Short version: this migration adds the two tables Module 14's "chat with
your quest notes" feature needs (see app/db_models.py's `QuestNote` and
`NoteChunk` for the ORM side of the exact same schema), plus two things no
earlier migration in this project has ever needed:

1. `CREATE EXTENSION IF NOT EXISTS vector` -- pgvector is a real Postgres
   *extension*, not something built into Postgres itself. It has to be
   enabled once, per database, before any table in that database can use
   the `vector` column type at all. `IF NOT EXISTS` makes this safe to run
   again (e.g. if a learner already enabled it by hand while following
   lessons/00-setup.md's "Verify your setup" section) without erroring.
2. A real vector index, created with a raw `op.execute(...)` call rather
   than any `op.create_index(...)` helper -- Alembic (and SQLAlchemy Core
   generally) has no built-in knowledge of pgvector's own index syntax
   (`USING hnsw (... vector_cosine_ops)`), so this migration drops down to
   plain SQL for this one statement, exactly the same "op.execute for
   anything Alembic's own helpers don't model" pattern
   lessons/07-alembic-migrations.md (Module 06) already introduced in the
   abstract, now used here for a genuinely new reason. **HNSW, not
   IVFFlat** (pgvector's other common index type) specifically because
   HNSW can be built on a table with zero rows in it -- this migration
   runs before any note has ever been created, and IVFFlat's own
   recommended usage needs a representative sample of real data already
   present to pick good cluster centers, which doesn't exist yet on a
   brand-new database.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1c9e5f2b3d4"
down_revision: str | Sequence[str] | None = "62f2ef5e3f58"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: enable the extension. Must run before `op.create_table` below
    # -- a table column can't use a type (`vector(384)`) that doesn't exist
    # yet.
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

    op.create_table(
        "quest_notes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("quest_id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["quest_id"], ["quests.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "note_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("note_id", sa.String(length=36), nullable=False),
        sa.Column("quest_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        # `Vector(384)` -- 384 dimensions to exactly match
        # `all-MiniLM-L6-v2`'s own output shape (app/embeddings.py's
        # `EMBEDDING_DIMENSIONS`). A mismatched dimension count here would
        # not be a subtle bug -- pgvector raises a real, immediate error
        # the instant a differently-sized vector is inserted, see
        # lessons/04's own "what a dimension mismatch actually looks like"
        # troubleshooting box.
        sa.Column("embedding", Vector(384), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["note_id"], ["quest_notes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quest_id"], ["quests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Step 3: the vector index. `vector_cosine_ops` tells pgvector to build
    # this index specifically for cosine-distance queries (the same
    # `<=>` operator app/repository.py's `find_similar_chunks` uses via
    # `.cosine_distance()`) -- pgvector supports other operator classes
    # (`vector_l2_ops`, `vector_ip_ops`) for L2 distance and inner product,
    # but this app only ever queries by cosine distance, so this is the
    # only index it needs.
    op.execute(
        sa.text(
            "CREATE INDEX ix_note_chunks_embedding_hnsw ON note_chunks "
            "USING hnsw (embedding vector_cosine_ops)"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    # No explicit `DROP INDEX` needed -- `op.drop_table("note_chunks")`
    # drops the index along with it, since the index belongs to that table.
    op.drop_table("note_chunks")
    op.drop_table("quest_notes")
    # Deliberately does NOT `DROP EXTENSION vector` -- another table this
    # database doesn't know about yet might depend on it, and dropping a
    # Postgres extension is a database-wide action this one feature's own
    # downgrade has no business taking. See lessons/04's "why this
    # migration never drops the extension it created" box.
