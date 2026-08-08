"""
Exercise 01 -- Hand Tokenization Playground

Fill in the four TODO functions below using `tiktoken`, exactly as taught in
lessons/03-tokens-and-tokenization.md. Do not change any function's name or
parameter list -- the acceptance criteria in INSTRUCTIONS.md assume they
stay exactly as given.

This exercise needs NO API key and NO internet access once tiktoken is
installed (Lesson 00's setup). Everything here runs fully offline.
"""
import tiktoken

# The encoding used throughout Lesson 03 -- OpenAI's o200k_base scheme.
# (Lesson 03 explains why this isn't Claude's own tokenizer, and why that's
# still fine for practicing the general BPE mechanism.)
ENCODING_NAME = "o200k_base"

# Claude Haiku 4.5 pricing, verified in lessons/00-setup.md (August 2026).
HAIKU_INPUT_PRICE_PER_MILLION = 1.00
HAIKU_OUTPUT_PRICE_PER_MILLION = 5.00


def count_tokens(text: str, encoding_name: str = ENCODING_NAME) -> int:
    """Return the number of tokens `text` encodes into.

    TODO:
    1. Get the encoding via tiktoken.get_encoding(encoding_name).
    2. Encode `text` into a list of token IDs.
    3. Return the length of that list.
    """
    raise NotImplementedError


def show_token_pieces(text: str, encoding_name: str = ENCODING_NAME) -> list[str]:
    """Return a list of the actual decoded text piece for each token in `text`,
    in order (e.g. for "QuestLog" this should return ['Quest', 'Log']).

    TODO:
    1. Get the encoding via tiktoken.get_encoding(encoding_name).
    2. Encode `text` into a list of token IDs.
    3. For each token ID, decode it BACK into text using enc.decode([token_id])
       (note the list wrapper -- decode expects a list of IDs, not a single ID).
    4. Return the list of decoded pieces, in the same order as the token IDs.
    """
    raise NotImplementedError


def compare_word_vs_token_count(text: str) -> tuple[int, int]:
    """Return a (word_count, token_count) tuple for `text`.

    `word_count` should be a naive split on whitespace (text.split()).
    `token_count` should come from calling count_tokens(text) above.

    TODO: implement using the two approaches described above.
    """
    raise NotImplementedError


def estimate_input_cost(text: str, price_per_million: float = HAIKU_INPUT_PRICE_PER_MILLION) -> float:
    """Estimate the dollar cost of sending `text` as INPUT to a model priced
    at `price_per_million` dollars per million tokens.

    TODO:
    1. Get the token count for `text` using count_tokens.
    2. Return (tokens / 1_000_000) * price_per_million.
    """
    raise NotImplementedError


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
