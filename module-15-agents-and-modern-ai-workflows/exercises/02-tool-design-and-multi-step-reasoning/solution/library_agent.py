"""Exercise 02 -- Tool Design and Multi-Step Reasoning -- reference solution."""

from types import SimpleNamespace

BOOKS = {
    "b1": {"title": "Dune", "available": True},
    "b2": {"title": "Foundation", "available": False},
}

TOOLS = [
    {
        "name": "find_book",
        "description": (
            "Look up a book by its title. Returns its book_id and whether "
            "it's currently available. Use this before checking out a "
            "book whenever you only know its title, not its id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"title": {"type": "string"}},
            "required": ["title"],
        },
    },
    {
        "name": "checkout_book",
        "description": (
            "Check out one book by its book_id (never its title). Fails "
            "with an error if the id doesn't exist or the book is "
            "already checked out."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"book_id": {"type": "string"}},
            "required": ["book_id"],
        },
    },
]


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    if name == "find_book":
        title = tool_input["title"]
        for book_id, book in BOOKS.items():
            if book["title"].lower() == title.lower():
                return f"book_id={book_id}, available={book['available']}", False
        return f"No book titled '{title}' found.", True

    if name == "checkout_book":
        book_id = tool_input["book_id"]
        book = BOOKS.get(book_id)
        if book is None:
            return f"No book with id '{book_id}'.", True
        if not book["available"]:
            return f"'{book['title']}' is already checked out.", True
        book["available"] = False
        return f"Checked out '{book['title']}'.", False

    return f"Error: unknown tool '{name}'", True


MAX_ITERATIONS = 5


def run_agent(client, user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model="claude-haiku-4-5", max_tokens=512, tools=TOOLS, messages=messages
        )
        print(f"-- iteration {iteration}: stop_reason={response.stop_reason}")

        if response.stop_reason != "tool_use":
            return next(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"   tool call: {block.name}({block.input})")
                content, is_error = run_tool(block.name, block.input)
                print(f"   tool result: {content} (is_error={is_error})")
                result = {"type": "tool_result", "tool_use_id": block.id, "content": content}
                if is_error:
                    result["is_error"] = True
                tool_results.append(result)
        messages.append({"role": "user", "content": tool_results})

    return "Gave up after too many steps."


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
    # Predicted sequence: iteration 1 -> find_book("Dune"); iteration 2
    # -> checkout_book("b1") (the id find_book's own implementation
    # returns for "Dune"); iteration 3 -> final text answer.
    fake = FakeClient(
        turns=[
            final([tool_use_block("t1", "find_book", {"title": "Dune"})], stop_reason="tool_use"),
            final(
                [tool_use_block("t2", "checkout_book", {"book_id": "b1"})], stop_reason="tool_use"
            ),
            final([text_block("Checked out Dune for you.")], stop_reason="end_turn"),
        ]
    )
    print("\nFinal answer:", run_agent(fake, "Check out Dune for me."))

# Written answer (Step 5): the agent can't call checkout_book directly
# with a title because checkout_book's own schema only accepts a
# book_id -- it has no title parameter at all. For direct-by-title
# checkout to be possible, checkout_book's schema would have to accept
# EITHER a title or an id, which re-introduces the exact overloaded,
# ambiguous-argument problem this exercise's own redesign was meant to
# remove: the tool's implementation would need its own internal
# title-to-id lookup logic, duplicating what find_book already does, and
# it would silently succeed or fail differently depending on which kind
# of argument happened to be supplied -- a worse, less predictable design
# than keeping the two steps separate and explicit.
