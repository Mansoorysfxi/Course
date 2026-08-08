"""
Exercise 02 -- Embedding Visualization (reference solution)

Do not peek at this until you've attempted the starter version yourself and
asked for a review, per this course's workflow (root README.md).
"""
import numpy as np
from sentence_transformers import SentenceTransformer

SENTENCES = [
    "The dragon guards the ancient castle.",
    "A fierce lizard watches over the old fortress.",
    "I need to buy milk and eggs from the store.",
    "Remember to pick up groceries after work.",
    "QuestLog helps you track your daily quests.",
    "The wizard cast a powerful fireball spell.",
]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def most_similar_pair(embeddings: np.ndarray, sentences: list[str]) -> tuple[tuple[int, int], float]:
    best_score = -1.0
    best_pair = (0, 1)
    n = len(sentences)
    for i in range(n):
        for j in range(i + 1, n):
            score = cosine_similarity(embeddings[i], embeddings[j])
            if score > best_score:
                best_score = score
                best_pair = (i, j)
    return best_pair, best_score


def project_to_2d(embeddings: np.ndarray) -> np.ndarray:
    centered = embeddings - embeddings.mean(axis=0)
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    return centered @ vt[:2].T


def plot_embeddings(coords_2d: np.ndarray, sentences: list[str], output_path: str = "embedding_plot.png") -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not installed -- skipping the plot (this is fine;")
        print("`pip install matplotlib` if you want it). The numeric")
        print("similarities above are the actual required deliverable.")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(coords_2d[:, 0], coords_2d[:, 1])
    for idx, (x, y) in enumerate(coords_2d):
        ax.annotate(f"[{idx}]", (x, y), textcoords="offset points", xytext=(5, 5))
    ax.set_title("Sentence embeddings projected to 2D (via SVD)")
    fig.savefig(output_path)
    print(f"\nSaved plot to {output_path}")


def main() -> None:
    print(f"Computing embeddings for {len(SENTENCES)} sentences...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(SENTENCES)
    print(f"Embedding shape: {embeddings.shape}")

    print("\nPairwise cosine similarities:")
    n = len(SENTENCES)
    for i in range(n):
        for j in range(i + 1, n):
            score = cosine_similarity(embeddings[i], embeddings[j])
            print(f"  [{i}] vs [{j}]: {score:.4f}")

    (i, j), score = most_similar_pair(embeddings, SENTENCES)
    print(f"\nMost similar pair (score={score:.4f}):")
    print(f"  [{i}] {SENTENCES[i]!r}")
    print(f"  [{j}] {SENTENCES[j]!r}")

    coords_2d = project_to_2d(embeddings)
    print("\n2D projected coordinates:")
    for idx, (x, y) in enumerate(coords_2d):
        print(f"  [{idx}] ({x:.3f}, {y:.3f})  {SENTENCES[idx][:40]!r}")

    plot_embeddings(coords_2d, SENTENCES)


if __name__ == "__main__":
    main()
