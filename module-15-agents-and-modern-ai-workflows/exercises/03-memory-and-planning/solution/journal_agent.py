"""Exercise 03 -- Memory and Planning -- reference solution."""

from types import SimpleNamespace

JOURNAL: list[str] = []

TOOLS = [
    {
        "name": "plan",
        "description": (
            "Write out a short plan of steps before acting. Has no real "
            "effect -- it just makes your intended next steps visible. "
            "Use this before a multi-step journal update."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"steps": {"type": "array", "items": {"type": "string"}}},
            "required": ["steps"],
        },
    },
    {
        "name": "add_journal_entry",
        "description": "Append one entry to the adventure journal.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]


def run_tool(name: str, tool_input: dict) -> str:
    if name == "plan":
        steps = tool_input["steps"]
        return "Plan:\n" + "\n".join(f"  {i + 1}. {step}" for i, step in enumerate(steps))
    if name == "add_journal_entry":
        JOURNAL.append(tool_input["text"])
        return f"Added entry #{len(JOURNAL)}: {tool_input['text']}"
    return f"Error: unknown tool '{name}'"


MAX_ITERATIONS = 5


def run_agent(client, messages: list[dict]) -> tuple[str, list[dict]]:
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model="claude-haiku-4-5", max_tokens=512, tools=TOOLS, messages=messages
        )
        print(f"-- iteration {iteration}: stop_reason={response.stop_reason}")

        if response.stop_reason != "tool_use":
            answer = next(b.text for b in response.content if b.type == "text")
            messages.append({"role": "assistant", "content": answer})
            return answer, messages

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"   tool call: {block.name}({block.input})")
                result = run_tool(block.name, block.input)
                print(f"   tool result: {result}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
        messages.append({"role": "user", "content": tool_results})

    return "Gave up after too many steps.", messages


class Conversation:
    """The entire "memory" this exercise has: a plain, growing list, kept
    alive by this object across separate send() calls -- the same
    short-term-memory shape Lesson 04 named, and the same "the API is
    stateless; the caller resends history" fact this course has taught
    since Module 13, now living inside a small class instead of a bare
    function."""

    def __init__(self, client):
        self.client = client
        self.messages: list[dict] = []

    def send(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        answer, self.messages = run_agent(self.client, self.messages)
        return answer


# ---- A scripted fake client ----
def text_block(text):
    return SimpleNamespace(type="text", text=text)


def tool_use_block(id_, name, input_):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=input_)


def final(content, stop_reason):
    return SimpleNamespace(content=content, stop_reason=stop_reason)


class FakeMessages:
    def __init__(self, turns):
        self._turns = iter(turns)

    def create(self, **kwargs):
        return next(self._turns)


class FakeClient:
    def __init__(self, turns):
        self.messages = FakeMessages(turns)


if __name__ == "__main__":
    fake = FakeClient(
        turns=[
            # send() #1: "Add a journal entry that I found a magic sword."
            final(
                [tool_use_block("t1", "add_journal_entry", {"text": "Found a magic sword."})],
                stop_reason="tool_use",
            ),
            final([text_block("Added it to your journal.")], stop_reason="end_turn"),
            # send() #2: "What did I just add?" -- scripted to reference
            # the first entry, proving the conversation remembers it.
            final(
                [text_block("You just added: 'Found a magic sword.'")],
                stop_reason="end_turn",
            ),
        ]
    )

    conversation = Conversation(fake)
    print("Before first send():", conversation.messages)

    print("\n--- send() #1 ---")
    answer1 = conversation.send("Add a journal entry that I found a magic sword.")
    print("Answer:", answer1)

    print("\n--- send() #2 ---")
    answer2 = conversation.send("What did I just add?")
    print("Answer:", answer2)

    print("\nFull conversation history length:", len(conversation.messages))
