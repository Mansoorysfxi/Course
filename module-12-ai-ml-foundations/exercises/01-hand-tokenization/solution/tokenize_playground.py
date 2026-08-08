"""
Exercise 01 -- Hand Tokenization Playground (reference solution)

Do not peek at this until you've attempted the starter version yourself and
asked for a review, per this course's workflow (root README.md).
"""
import tiktoken

ENCODING_NAME = "o200k_base"

HAIKU_INPUT_PRICE_PER_MILLION = 1.00
HAIKU_OUTPUT_PRICE_PER_MILLION = 5.00


def count_tokens(text: str, encoding_name: str = ENCODING_NAME) -> int:
    enc = tiktoken.get_encoding(encoding_name)
    token_ids = enc.encode(text)
    return len(token_ids)


def show_token_pieces(text: str, encoding_name: str = ENCODING_NAME) -> list[str]:
    enc = tiktoken.get_encoding(encoding_name)
    token_ids = enc.encode(text)
    return [enc.decode([token_id]) for token_id in token_ids]


def compare_word_vs_token_count(text: str) -> tuple[int, int]:
    word_count = len(text.split())
    token_count = count_tokens(text)
    return word_count, token_count


def estimate_input_cost(text: str, price_per_million: float = HAIKU_INPUT_PRICE_PER_MILLION) -> float:
    tokens = count_tokens(text)
    return (tokens / 1_000_000) * price_per_million


if __name__ == "__main__":
    quest_description = (
        "QuestLog helps you track quests, side-quests, and daily grinding. "
        "Complete a quest line to earn bonus experience points."
    )

    print(f"Text: {quest_description!r}\n")

    pieces = show_token_pieces(quest_description)
    print(f"Token count: {len(pieces)}")
    print(f"Token pieces: {pieces}\n")

    words, tokens = compare_word_vs_token_count(quest_description)
    print(f"Naive word count: {words}")
    print(f"Real token count: {tokens}\n")

    cost = estimate_input_cost(quest_description)
    print(f"Estimated input cost at ${HAIKU_INPUT_PRICE_PER_MILLION}/million tokens: ${cost:.8f}")
