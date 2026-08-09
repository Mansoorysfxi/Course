"""Exercise 03 -- Real pgvector Similarity Queries. Reference solution.
See INSTRUCTIONS.md. Do not read this until you've attempted the
exercise yourself.
"""

import psycopg
from pgvector.psycopg import register_vector

DATABASE_URL = "postgresql://questlog:questlog_dev_password@localhost:5432/questlog"

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
    for label, embedding in SAMPLE_ROWS:
        conn.execute(
            "INSERT INTO pgvector_exercise (label, embedding) VALUES (%s, %s)",
            (label, embedding),
        )
    conn.commit()


def find_nearest(
    conn: psycopg.Connection, query_vector: list[float], top_k: int
) -> list[tuple[str, float]]:
    result = conn.execute(
        "SELECT label, embedding <=> %s AS distance "
        "FROM pgvector_exercise ORDER BY distance LIMIT %s",
        (query_vector, top_k),
    )
    return result.fetchall()


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
