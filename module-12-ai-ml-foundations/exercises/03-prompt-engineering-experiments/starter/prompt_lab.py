"""
Exercise 03 -- Prompt Engineering Experiments

Fill in the two TODO functions below using the Anthropic SDK, exactly as
taught in lessons/07-prompt-engineering-as-a-skill.md. Do not change any
function's name or parameter list.

*** This exercise is optional-but-recommended and works two ways: ***

1. WITH a real ANTHROPIC_API_KEY (Lesson 00, Step 5) -- this script makes
   real, tiny API calls (Claude Haiku 4.5, a fraction of a cent total for
   every experiment below) and prints the ACTUAL naive-vs-improved
   responses side by side, with real token counts and real estimated cost.
2. WITHOUT a key -- this script automatically runs in DRY RUN mode: it
   still prints every prompt clearly, does not attempt any network call,
   and costs nothing. Reading lessons/07's own worked examples alongside
   this dry run is a fully legitimate way to complete this exercise.

Either way, do not skip filling in the TODOs -- they're required whether or
not you actually run this against a real key, since the acceptance
criteria check the CODE, not just its live output.
"""
import os

MODEL = "claude-haiku-4-5"
INPUT_PRICE_PER_MILLION = 1.00   # verified in lessons/00-setup.md
OUTPUT_PRICE_PER_MILLION = 5.00  # verified in lessons/00-setup.md


def get_client():
    """Return an anthropic.Anthropic() client if ANTHROPIC_API_KEY is set
    in the environment, otherwise return None (triggering dry-run mode).

    TODO:
    1. Check os.environ for "ANTHROPIC_API_KEY". If it's missing or empty,
       return None immediately.
    2. Otherwise, import anthropic (do this INSIDE the function, so the
       import never happens at all in dry-run mode -- someone without the
       `anthropic` package installed should still be able to run this
       script in dry-run mode without an ImportError).
    3. Return anthropic.Anthropic() (it reads the key from the environment
       automatically).
    """
    raise NotImplementedError


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Return the estimated dollar cost of a real API call, given its real
    input and output token counts, using the pricing constants above.

    TODO:
    1. Compute input cost: (input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION.
    2. Compute output cost: (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION.
    3. Return their sum.
    """
    raise NotImplementedError


def call_model(client, system: str | None, user_message: str, max_tokens: int = 300) -> tuple[str, int, int]:
    """Make a real API call and return (response_text, input_tokens, output_tokens).

    Already implemented for you -- this is the exact call shape from
    Lesson 07. Study it; you don't need to change it.
    """
    kwargs = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user_message}],
    }
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    text = response.content[0].text
    return text, response.usage.input_tokens, response.usage.output_tokens


def run_experiment(name: str, client, naive: dict, improved: dict) -> None:
    """Print a naive-vs-improved comparison for one experiment. Already
    implemented for you -- study how it branches on `client is None` to
    support both the live and dry-run paths."""
    print(f"\n{'=' * 70}")
    print(f"EXPERIMENT: {name}")
    print(f"{'=' * 70}")

    for label, variant in [("NAIVE", naive), ("IMPROVED", improved)]:
        print(f"\n--- {label} ---")
        print(f"System: {variant.get('system')!r}")
        print(f"User message: {variant['user']!r}")

        if client is None:
            print("(DRY RUN -- no ANTHROPIC_API_KEY set. Read lessons/07's")
            print(" corresponding worked example for a realistic illustration")
            print(" of what this prompt should produce, and why.)")
            continue

        text, in_tok, out_tok = call_model(client, variant.get("system"), variant["user"])
        cost = estimate_cost(in_tok, out_tok)
        print(f"Response: {text}")
        print(f"Tokens: {in_tok} in / {out_tok} out  |  Estimated cost: ${cost:.6f}")


EXPERIMENTS = [
    {
        "name": "System prompt",
        "naive": {
            "system": None,
            "user": "Break down this quest into steps: Defeat the dragon guarding the old mine.",
        },
        "improved": {
            "system": (
                "You are QuestLog's quest-breakdown assistant. Break every quest "
                "into 3-5 short, actionable steps a player could actually check "
                "off. Use a slightly playful, RPG-flavored tone. Never break a "
                "quest into more than 5 steps."
            ),
            "user": "Break down this quest into steps: Defeat the dragon guarding the old mine.",
        },
    },
    {
        "name": "Few-shot prompting",
        "naive": {
            "system": None,
            "user": "Classify this quest's difficulty as Easy, Medium, or Hard: Deliver a letter to the next village over.",
        },
        "improved": {
            "system": None,
            "user": (
                "Classify each quest's difficulty as Easy, Medium, or Hard.\n\n"
                'Quest: "Fetch 5 herbs from the meadow." -> Easy\n'
                'Quest: "Defeat the bandit captain and his lieutenant." -> Medium\n'
                'Quest: "Slay the ancient dragon terrorizing the kingdom." -> Hard\n\n'
                'Quest: "Deliver a letter to the next village over." ->'
            ),
        },
    },
    {
        "name": "Chain-of-thought",
        "naive": {
            "system": None,
            "user": (
                "A player has completed 7 out of 12 quests in the 'Dragon's "
                "Bane' questline, each worth 150 XP, and has 340 XP already "
                "banked from other questlines. How much total XP does the "
                "player have?"
            ),
        },
        "improved": {
            "system": None,
            "user": (
                "A player has completed 7 out of 12 quests in the 'Dragon's "
                "Bane' questline, each worth 150 XP, and has 340 XP already "
                "banked from other questlines. How much total XP does the "
                "player have? Think through this step by step before giving "
                "your final answer."
            ),
        },
    },
    {
        "name": "Structured output",
        "naive": {
            "system": None,
            "user": "Break down this quest into steps: Defeat the dragon guarding the old mine.",
        },
        "improved": {
            "system": None,
            "user": (
                "Break down this quest into steps and respond with ONLY valid "
                "JSON, no other text, in exactly this shape:\n"
                '{"quest": "<quest name>", "steps": ["<step 1>", "<step 2>", '
                '...], "estimated_difficulty": "Easy" | "Medium" | "Hard"}\n\n'
                "Quest: Defeat the dragon guarding the old mine."
            ),
        },
    },
    # TODO (independent step): add a FIFTH experiment of your own here,
    # applying any technique from Lesson 07 (or combining two, e.g. a
    # system prompt AND chain-of-thought together) to a QuestLog-flavored
    # prompt you write yourself. Follow the exact same
    # {"name": ..., "naive": {...}, "improved": {...}} shape as the four above.
]


def main() -> None:
    client = get_client()
    if client is None:
        print("No ANTHROPIC_API_KEY found -- running in DRY RUN mode.")
        print("This is a fully legitimate way to complete this exercise.")
        print("See lessons/07-prompt-engineering-as-a-skill.md for realistic,")
        print("carefully-reasoned illustrations of what each prompt below")
        print("should produce, and read this script's own prompts to predict")
        print("the differences yourself before checking the lesson.\n")
    else:
        print(f"Running real experiments against {MODEL}...\n")

    for experiment in EXPERIMENTS:
        run_experiment(experiment["name"], client, experiment["naive"], experiment["improved"])


if __name__ == "__main__":
    main()
