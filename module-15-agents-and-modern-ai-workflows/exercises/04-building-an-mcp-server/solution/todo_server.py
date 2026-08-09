"""Exercise 04 -- Building an MCP Server -- reference solution."""

from mcp.server import MCPServer

mcp = MCPServer("todo-list")

# Each todo is a small dict, {"text": ..., "done": bool} -- the simplest
# structure that can represent both pieces of state this exercise needs.
# A dataclass or a real database row would both be reasonable
# alternatives for a bigger project; a plain dict is proportionate to
# this exercise's own scope (an in-memory, single-process example with no
# persistence at all).
TODOS: list[dict] = []


@mcp.tool()
def add_todo(text: str) -> str:
    """Add a new, not-done todo."""
    TODOS.append({"text": text, "done": False})
    return f"Added todo #{len(TODOS) - 1}: {text}"


@mcp.tool()
def list_todos() -> list[str]:
    """List every todo, each prefixed with its own done/not-done state."""
    return [f"{'[done]' if t['done'] else '[ ]'} {t['text']}" for t in TODOS]


@mcp.tool()
def complete_todo(index: int) -> str:
    """Mark the todo at `index` as done."""
    if index < 0 or index >= len(TODOS):
        return f"No todo at index {index}."
    TODOS[index]["done"] = True
    return f"Marked todo #{index} done: {TODOS[index]['text']}"


if __name__ == "__main__":
    mcp.run()
