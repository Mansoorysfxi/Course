"""Exercise 02 -- Embeddings for Search. Reference solution. See INSTRUCTIONS.md.

Do not read this until you've attempted the exercise yourself.
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
    return _model.encode(corpus)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search(
    query: str, corpus: list[str], corpus_embeddings: np.ndarray, top_k: int = 2
) -> list[tuple[str, float]]:
    query_embedding = _model.encode(query)
    scored = [
        (sentence, cosine_similarity(query_embedding, row))
        for sentence, row in zip(corpus, corpus_embeddings, strict=True)
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    corpus_embeddings = embed_corpus(CORPUS)

    for query in SAMPLE_QUERIES:
        print(f"\nQuery: {query!r}")
        for sentence, score in search(query, CORPUS, corpus_embeddings, top_k=2):
            print(f"  {score:.3f}  {sentence}")
