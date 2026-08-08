"""
Exercise 02 -- Embedding Visualization

Fill in the four TODO functions below using `sentence-transformers` and
`numpy`, exactly as taught in lessons/04-embeddings-meaning-as-coordinates.md.
Do not change any function's name or parameter list.

This exercise needs NO API key -- it uses a small, free, local embedding
model (`all-MiniLM-L6-v2`) that runs entirely on your own machine, per
Lesson 00's setup. The first run downloads the model (~90 MB, one time);
every run after that is fast and fully offline.

matplotlib is OPTIONAL for this exercise -- if it isn't installed, the
plotting step is skipped automatically and the rest of the exercise (the
numeric similarity comparisons, which are the actual required deliverable)
still runs and still satisfies every acceptance criterion. Install it with
`pip install matplotlib` if you want the visual plot too.
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
    """Return the cosine similarity between two 1D numpy vectors.

    TODO:
    1. Compute the dot product of a and b (np.dot(a, b)).
    2. Compute the product of their lengths (np.linalg.norm(a) * np.linalg.norm(b)).
    3. Return the dot product divided by that length product, as a plain float.
    """
    raise NotImplementedError


def most_similar_pair(embeddings: np.ndarray, sentences: list[str]) -> tuple[tuple[int, int], float]:
    """Find the pair of DIFFERENT sentences (by index) with the highest
    cosine similarity. Return ((i, j), score) where i < j.

    TODO:
    1. Loop over every unique pair of indices (i, j) with i < j.
    2. Compute cosine_similarity(embeddings[i], embeddings[j]) for each pair.
    3. Track and return the pair with the highest score, and that score.
    """
    raise NotImplementedError


def project_to_2d(embeddings: np.ndarray) -> np.ndarray:
    """Project the (n, 384) embeddings array down to (n, 2) for plotting,
    using SVD (Singular Value Decomposition) -- a real, standard dimensionality
    reduction technique.

    TODO:
    1. Center the embeddings by subtracting the mean of each column
       (embeddings.mean(axis=0)) from every row.
    2. Run np.linalg.svd(centered, full_matrices=False) to get u, s, vt.
    3. Return centered @ vt[:2].T -- this projects onto the top 2 directions
       of variance in the data.
    """
    raise NotImplementedError


def plot_embeddings(coords_2d: np.ndarray, sentences: list[str], output_path: str = "embedding_plot.png") -> None:
    """Save a 2D scatter plot of the projected embeddings, labeled by index.
    If matplotlib isn't installed, print a message and return without error
    -- this step is optional, per this file's module docstring.

    TODO:
    1. Try to `import matplotlib.pyplot as plt` inside a try/except ImportError.
    2. On success: create a figure, scatter-plot coords_2d[:, 0] vs coords_2d[:, 1],
       annotate each point with its index, and save to output_path.
    3. On ImportError: print a short message explaining the plot was skipped,
       and return (do not raise).
    """
    raise NotImplementedError


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
