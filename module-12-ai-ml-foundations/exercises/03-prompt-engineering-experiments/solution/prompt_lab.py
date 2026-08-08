"""
Exercise 03 -- Prompt Engineering Experiments (reference solution)

Do not peek at this until you've attempted the starter version yourself and
asked for a review, per this course's workflow (root README.md).
"""
import os

MODEL = "claude-haiku-4-5"
INPUT_PRICE_PER_MILLION = 1.00
OUTPUT_PRICE_PER_MILLION = 5.00


def get_client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    import anthropic
    return anthropic.Anthropic()


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    input_cost = (input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION
    return input_cost + output_cost


def call_model(client, system: str | None, user_message: str, max_tokens: int = 300) -> tuple[str, int, int]:
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
    {
        # A fifth experiment combining TWO techniques from Lesson 07 at once:
        # a system prompt AND chain-of-thought, applied to a "recommend the
        # next quest" scenario -- exactly the kind of feature QuestLog's own
        # AI assistant gains in Module 13.
        "name": "System prompt + chain-of-thought combined",
        "naive": {
            "system": None,
            "user": (
                "A player is level 8, has completed all Easy quests, 2 of 5 "
                "Medium quests, and no Hard quests. Which difficulty quest "
                "should they try next?"
            ),
        },
        "improved": {
            "system": (
                "You are QuestLog's quest-recommendation assistant. You help "
                "players pick their next quest based on their current "
                "progress. Always reason about the player's demonstrated "
                "skill level before recommending, and always end with a "
                "single clear recommendation on its own line starting with "
                "'Recommendation:'."
            ),
            "user": (
                "A player is level 8, has completed all Easy quests, 2 of 5 "
                "Medium quests, and no Hard quests. Which difficulty quest "
                "should they try next? Think through their progress step by "
                "step before recommending."
            ),
        },
    },
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
