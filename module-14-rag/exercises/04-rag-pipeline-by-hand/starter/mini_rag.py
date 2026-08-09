"""Exercise 04 -- A Complete RAG Pipeline, by Hand. See INSTRUCTIONS.md.

Steps 1-4 (chunk, embed, retrieve, build the prompt) need no API key.
Step 5 (generate_answer) needs a real ANTHROPIC_API_KEY.
"""

import os

import anthropic
import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = {
    "Boss Fight Prep": (
        "The dragon sleeps in the northern cave, guarded by two goblins.\n\n"
        "Bring fire-resistant armor and a silver sword -- regular steel won't cut its scales."
    ),
    "Village Errands": (
        "The village healer needs five bundles of silverleaf herbs from the eastern woods.\n\n"
        "A courier's letter must reach the capital before the harvest festival."
    ),
}

QUESTION = "What should I bring to fight the dragon?"

_model = SentenceTransformer("all-MiniLM-L6-v2")

# A store entry: (document_title, chunk_index, chunk_text, embedding)
StoreEntry = tuple[str, int, str, np.ndarray]


def chunk_and_embed(documents: dict[str, str]) -> list[StoreEntry]:
    """TODO: for every (title, text) pair in `documents`, split `text` on
    blank lines into chunks, embed every chunk, and return a flat list of
    (title, chunk_index, chunk_text, embedding) tuples."""
    raise NotImplementedError


def retrieve(question: str, store: list[StoreEntry], top_k: int = 2) -> list[StoreEntry]:
    """TODO: embed `question`, rank every entry in `store` by cosine
    similarity to the question, and return the top_k most similar
    entries, most similar first."""
    raise NotImplementedError


def build_prompt(question: str, retrieved: list[StoreEntry]) -> str:
    """TODO: assemble the retrieved chunks and the question into one
    prompt string, labeling each excerpt with its source document title."""
    raise NotImplementedError


def generate_answer(prompt: str) -> None:
    """TODO: call the real Anthropic API (claude-haiku-4-5) with a system
    prompt instructing it to answer using only the provided excerpts and
    cite which document each fact came from. Stream the response and
    print it as it arrives."""
    raise NotImplementedError


if __name__ == "__main__":
    store = chunk_and_embed(DOCUMENTS)
    print(f"Built a store of {len(store)} chunks from {len(DOCUMENTS)} documents.\n")

    retrieved = retrieve(QUESTION, store, top_k=2)
    print("Retrieved chunks:")
    for title, index, text, _ in retrieved:
        print(f"  [{title} #{index}] {text}")

    prompt = build_prompt(QUESTION, retrieved)
    print(f"\nAssembled prompt:\n{prompt}\n")

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("Answer:")
        generate_answer(prompt)
    else:
        print("(Set ANTHROPIC_API_KEY to run Step 5 and see a real generated answer.)")
