"""Exercise 02 -- Embeddings for Search. See INSTRUCTIONS.md.

Needs `pip install sentence-transformers numpy` -- no API key required.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

CORPUS = [
    "The dragon sleeps in the northern cave, guarded by two goblins.",
    "Bring fire-resistant armor and a silver sword to fight the dragon.",
    "The village healer needs five bundles of silverleaf herbs.",
    "A courier's letter must reach the capital before the harvest festival.",
    "The old mine has new tunnels dug by something unknown.",
    "The stone bridge to the market town has a collapsed section.",
]

SAMPLE_QUERIES = [
    "What should I bring to fight the dragon?",
    "Where can I find healing herbs?",
    "Is there a way into the capital city?",
]

_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_corpus(corpus: list[str]) -> np.ndarray:
    """TODO: embed every sentence in `corpus` in one call and return the
    resulting NumPy array (one row per sentence)."""
    raise NotImplementedError


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """TODO: the same formula Module 12, Lesson 04 introduced."""
    raise NotImplementedError


def search(query: str, corpus: list[str], corpus_embeddings: np.ndarray, top_k: int = 2) -> list[tuple[str, float]]:
    """TODO: embed `query`, score it against every row of
    `corpus_embeddings` using cosine_similarity, and return up to `top_k`
    (sentence, score) pairs, highest score first."""
    raise NotImplementedError


if __name__ == "__main__":
    corpus_embeddings = embed_corpus(CORPUS)

    for query in SAMPLE_QUERIES:
        print(f"\nQuery: {query!r}")
        for sentence, score in search(query, CORPUS, corpus_embeddings, top_k=2):
            print(f"  {score:.3f}  {sentence}")
