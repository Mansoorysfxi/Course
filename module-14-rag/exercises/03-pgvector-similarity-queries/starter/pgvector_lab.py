"""Exercise 03 -- Real pgvector Similarity Queries. See INSTRUCTIONS.md.

Needs a running, pgvector-enabled Postgres (Lesson 00) and
`pip install psycopg[binary] pgvector`.
"""

import psycopg
from pgvector.psycopg import register_vector

# Matches Lesson 00's default local setup. Edit if yours differs.
DATABASE_URL = "postgresql://questlog:questlog_dev_password@localhost:5432/questlog"

# Three tiny, 3-dimensional vectors, deliberately small so you can reason
# about the distances by hand. "close" and "query_vector" (below) point in
# almost the same direction; "far" points in a very different direction.
SAMPLE_ROWS = [
    ("close", [0.9, 0.1, 0.0]),
    ("medium", [0.5, 0.5, 0.0]),
    ("far", [0.0, 1.0, 0.0]),
]

QUERY_VECTOR = [1.0, 0.0, 0.0]


def setup_table(conn: psycopg.Connection) -> None:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.execute("DROP TABLE IF EXISTS pgvector_exercise")
    conn.execute("CREATE TABLE pgvector_exercise (label text, embedding vector(3))")
    conn.commit()


def insert_sample_vectors(conn: psycopg.Connection) -> None:
    """TODO: insert every (label, embedding) pair from SAMPLE_ROWS into
    the pgvector_exercise table."""
    raise NotImplementedError


def find_nearest(
    conn: psycopg.Connection, query_vector: list[float], top_k: int
) -> list[tuple[str, float]]:
    """TODO: run a real SQL query using the <=> cosine-distance operator,
    ordering by distance ascending, and return up to `top_k`
    (label, distance) pairs."""
    raise NotImplementedError


def cleanup_table(conn: psycopg.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS pgvector_exercise")
    conn.commit()


if __name__ == "__main__":
    with psycopg.connect(DATABASE_URL, autocommit=False) as conn:
        register_vector(conn)
        setup_table(conn)
        insert_sample_vectors(conn)

        print(f"Query vector: {QUERY_VECTOR}")
        for label, distance in find_nearest(conn, QUERY_VECTOR, top_k=3):
            print(f"  distance={distance:.4f}  label={label!r}")

        cleanup_table(conn)
