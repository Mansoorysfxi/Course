"""Exercise 04 -- A Complete RAG Pipeline, by Hand. Reference solution.
See INSTRUCTIONS.md. Do not read this until you've attempted the
exercise yourself.
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

SYSTEM_PROMPT = (
    "You will be given one or more excerpts from the player's own documents, each "
    "labeled with its source title, followed by a question. Answer using ONLY the "
    "information in the provided excerpts -- never from your own general knowledge. "
    "When you use an excerpt, say which document it came from by title. If the "
    "excerpts do not contain enough information to answer, say so plainly."
)

_model = SentenceTransformer("all-MiniLM-L6-v2")

StoreEntry = tuple[str, int, str, np.ndarray]


def chunk_and_embed(documents: dict[str, str]) -> list[StoreEntry]:
    store: list[StoreEntry] = []
    for title, text in documents.items():
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        embeddings = _model.encode(chunks)
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
            store.append((title, index, chunk, embedding))
    return store


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def retrieve(question: str, store: list[StoreEntry], top_k: int = 2) -> list[StoreEntry]:
    query_embedding = _model.encode(question)
    scored = [(entry, _cosine_similarity(query_embedding, entry[3])) for entry in store]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [entry for entry, _score in scored[:top_k]]


def build_prompt(question: str, retrieved: list[StoreEntry]) -> str:
    excerpts = "\n\n".join(
        f'Excerpt from "{title}":\n{text}' for title, _index, text, _embedding in retrieved
    )
    return f"{excerpts}\n\nQuestion: {question}"


def generate_answer(prompt: str) -> None:
    client = anthropic.Anthropic()
    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


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
