"""The ONE thing this backend's default test suite genuinely cannot verify
without real infrastructure: whether `app/repository.py`'s
`find_similar_chunks` real `.cosine_distance()` SQL actually executes
correctly against real Postgres+pgvector.

**Why this file exists, and why it's separate from tests/test_rag.py and
tests/test_notes.py.** Module 08 chose in-memory SQLite for this whole
backend's test suite because the schema used no Postgres-specific types.
`pgvector`'s `Vector` column type IS genuinely Postgres-specific --
`NoteChunk.embedding` (app/db_models.py) compiles to a plain `JSON` column
on SQLite via `.with_variant(JSON(), "sqlite")`, which has no
`.cosine_distance()` operator at all. `app/rag.py`'s
`rank_by_cosine_similarity` is what lets every *other* test in this suite
verify similarity-ranking *logic* without a real Postgres+pgvector
instance -- but it cannot prove the real SQL statement
`find_similar_chunks` sends to Postgres is itself syntactically and
semantically correct. Only running that exact statement against a real
`pgvector`-enabled Postgres can prove that.

**The decision, stated honestly** (see lessons/00-setup.md's own testing
note and lessons/05-similarity-search-in-practice.md's "testing this
without a fake" box for the full reasoning): this module does NOT require
a real Postgres+pgvector instance for `pytest`'s normal/default run --
that would break the "tests never need real external infra" principle
every earlier module in this course has held to (Module 08's SQLite
choice, Module 10's `FakeRedis`, Module 13's `FakeAnthropicClient`).
Instead, this ONE file is skipped entirely, at collection time, unless a
`TEST_PGVECTOR_DATABASE_URL` environment variable is set, pointing at a
real, running Postgres database with the `vector` extension already
enabled and this project's migrations already applied
(`alembic upgrade head`). This mirrors how many real-world teams handle
"this one code path needs real infra": skip by default, opt in via an
environment variable, never let it silently fail (or silently pass for
the wrong reason) for everyone else's normal test run.

**Honesty note, per this course's own standing practice (Modules 09-13):**
no Docker and no real Postgres instance were available while this module
was generated, so the tests in this file were never actually executed
against a real Postgres+pgvector database during generation -- they were
hand-verified for correctness by careful reading against `pgvector-python`'s
documented API and app/repository.py's own real query, not run. If you
have Docker available (see lessons/00-setup.md), you can verify this file
for real yourself: bring up `docker compose up -d postgres`, run
`alembic upgrade head`, set `TEST_PGVECTOR_DATABASE_URL` to that database's
URL, and run `pytest tests/test_notes_pgvector_integration.py -v`.

**Also deliberately out of scope:** wiring a real Postgres+pgvector
service into `.github/workflows/ci-cd.yml` so this file runs automatically
in CI. That's a real, legitimate improvement a team maintaining this app
for real might make next -- but it's a genuinely separate piece of work
(a new CI service container, a migration step in the pipeline, secrets
management for a second database) this module deliberately doesn't take
on, to keep this module's own footprint contained. See lessons/00-setup.md
for this scope boundary stated in the same place as the rest of this
module's setup instructions.
"""

import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import repository
from app.db_models import NoteChunk, Quest, QuestLine, QuestNote, User

TEST_PGVECTOR_DATABASE_URL = os.environ.get("TEST_PGVECTOR_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_PGVECTOR_DATABASE_URL,
    reason=(
        "TEST_PGVECTOR_DATABASE_URL is not set -- these tests need a real "
        "Postgres database with the pgvector extension enabled and this "
        "project's migrations applied. See this file's own module "
        "docstring and lessons/00-setup.md."
    ),
)


@pytest_asyncio.fixture
async def pgvector_session():
    """Deliberately does NOT create tables itself (unlike conftest.py's
    SQLite `db_session` fixture) -- this fixture assumes
    `alembic upgrade head` has already been run against
    `TEST_PGVECTOR_DATABASE_URL` (see this file's own module docstring),
    exactly the way a real deployment's database is prepared, never by the
    test suite creating tables ad hoc."""
    engine = create_async_engine(TEST_PGVECTOR_DATABASE_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        # Clean up only what this test run itself created, so repeated
        # runs against a real, persistent Postgres instance don't
        # accumulate stray rows.
        await session.rollback()
    await engine.dispose()


async def test_find_similar_chunks_orders_by_cosine_distance(pgvector_session: AsyncSession):
    """Inserts three chunks with hand-picked, easy-to-reason-about
    embeddings, then asserts the real pgvector query returns them ordered
    from most to least similar to a query vector -- the real-infrastructure
    counterpart to tests/test_rag.py's
    `test_rank_by_cosine_similarity_orders_most_similar_first`, which
    checks the exact same scenario against the plain-Python function
    instead."""
    session = pgvector_session
    user = User(email=f"pgvector-test-{uuid.uuid4()}@example.com", hashed_password="x")
    quest_line = QuestLine(name=f"Test Line {uuid.uuid4()}")
    session.add_all([user, quest_line])
    await session.flush()

    quest = Quest(
        title="Test Quest",
        description="d",
        priority="low",
        quest_line_id=quest_line.id,
        owner_id=user.id,
    )
    session.add(quest)
    await session.flush()

    note = QuestNote(quest_id=quest.id, owner_id=user.id, title="Test Note", content="content")
    session.add(note)
    await session.flush()

    close = NoteChunk(
        note_id=note.id,
        quest_id=quest.id,
        chunk_index=0,
        content="close",
        embedding=[0.9, 0.1] + [0.0] * 382,
    )
    far = NoteChunk(
        note_id=note.id,
        quest_id=quest.id,
        chunk_index=1,
        content="far",
        embedding=[0.0, 1.0] + [0.0] * 382,
    )
    session.add_all([close, far])
    await session.flush()

    query_embedding = [1.0, 0.0] + [0.0] * 382
    results = await repository.find_similar_chunks(session, quest.id, query_embedding, top_k=2)

    assert [chunk.content for chunk in results] == ["close", "far"]


async def test_find_similar_chunks_only_returns_this_quests_chunks(pgvector_session: AsyncSession):
    """The denormalized `NoteChunk.quest_id` filter (app/db_models.py's own
    docstring explains why it's there) must actually scope results --
    otherwise one player's notes could leak into another quest's answer."""
    session = pgvector_session
    user = User(email=f"pgvector-test-{uuid.uuid4()}@example.com", hashed_password="x")
    quest_line = QuestLine(name=f"Test Line {uuid.uuid4()}")
    session.add_all([user, quest_line])
    await session.flush()

    quest_a = Quest(
        title="Quest A",
        description="d",
        priority="low",
        quest_line_id=quest_line.id,
        owner_id=user.id,
    )
    quest_b = Quest(
        title="Quest B",
        description="d",
        priority="low",
        quest_line_id=quest_line.id,
        owner_id=user.id,
    )
    session.add_all([quest_a, quest_b])
    await session.flush()

    note_a = QuestNote(quest_id=quest_a.id, owner_id=user.id, title="Note A", content="c")
    session.add(note_a)
    await session.flush()

    chunk_a = NoteChunk(
        note_id=note_a.id,
        quest_id=quest_a.id,
        chunk_index=0,
        content="belongs to quest A",
        embedding=[1.0, 0.0] + [0.0] * 382,
    )
    session.add(chunk_a)
    await session.flush()

    query_embedding = [1.0, 0.0] + [0.0] * 382
    results = await repository.find_similar_chunks(session, quest_b.id, query_embedding, top_k=5)

    assert results == []
