"""Exercise 04 -- Building an MCP Server.

Requires the real `mcp[cli]` package (Lesson 00's own Step 2) -- this is
a real MCP server, not a fake/scripted one.
"""

from mcp.server import MCPServer

mcp = MCPServer("todo-list")

# TODO: decide TODOS's own shape so it can track both the text AND
# whether each todo is done. A plain list[str] (as started here) can't
# represent "done" at all -- change this before implementing the tools
# below, and explain your choice in a comment.
TODOS: list[str] = []


@mcp.tool()
def add_todo(text: str) -> str:
    """TODO: append `text` as a new, not-done todo. Return a confirmation
    message including this todo's own new index."""
    raise NotImplementedError


@mcp.tool()
def list_todos() -> list[str]:
    """TODO: return every todo as a string, each prefixed with '[done] '
    or '[ ] ' depending on its own completion state."""
    raise NotImplementedError


@mcp.tool()
def complete_todo(index: int) -> str:
    """TODO: mark the todo at `index` as done. Return a clear message
    (not a raised exception) if `index` doesn't exist."""
    raise NotImplementedError


if __name__ == "__main__":
    mcp.run()
