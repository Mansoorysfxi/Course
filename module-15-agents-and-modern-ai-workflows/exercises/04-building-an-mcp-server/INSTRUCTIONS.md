# Exercise 04 — Building an MCP Server

**Difficulty:** Guided → independent. Needs the real `mcp[cli]` package
installed (Lesson 00's own Step 2) — this exercise runs against the real
SDK, not a fake client, because MCP itself has no equivalent of "a
scripted fake Claude response" to fall back on; the whole point is a real
server any real client could talk to.

## What you'll build

A real, standalone MCP server, `todo_server.py`, exposing a tiny todo
list as three tools any MCP-compliant client could call — modeled
directly on Lesson 05's own `quest_notes_server.py`, but with your own
tools this time.

## Concepts this exercise requires (all taught in Lesson 05)

- `MCPServer`, `@mcp.tool()`, and how the SDK builds a tool's schema
  automatically from your function's own type hints and docstring.
- Calling a server's own tools directly with `list_tools()`/`call_tool()`,
  without needing a full separate client process.
- What `mcp.run()` actually does, and why it blocks.

## Instructions

1. Make sure you've completed Lesson 00's Step 2 (a scratch virtual
   environment with `mcp[cli]` installed) — activate it before starting.
2. Open `starter/todo_server.py`. It has the server object created and
   an in-memory `TODOS` list, with three `# TODO` tool stubs.
3. Implement three tools:
   - `add_todo(text: str) -> str` — appends `text` to `TODOS`, returns a
     confirmation including the todo's own new index.
   - `list_todos() -> list[str]` — returns every todo, each prefixed with
     `"[done] "` or `"[ ] "` depending on its own completion state. (You
     will need to change `TODOS`'s own shape from a plain list of strings
     to something that can also track "done" — decide how, and explain
     your choice in a comment.)
   - `complete_todo(index: int) -> str` — marks the todo at that index
     done, or returns a clear message if the index doesn't exist.
4. Write a `client_probe.py` (a **separate** file, alongside
   `todo_server.py`, importing `mcp` from it) that calls all three tools
   directly, in order — add two todos, complete one, then list both — and
   prints the results, the exact same "call a server's own tools directly
   without a separate client process" pattern Lesson 05's own example
   used.
5. Run `client_probe.py` and confirm the final `list_todos()` output
   shows one `[done]` entry and one `[ ]` entry, matching what you did.
6. **Try it with the real inspector too:** run
   `mcp dev todo_server.py` and confirm you can call all three tools by
   hand through its UI and see the same results.

## Acceptance criteria

- All three tools work correctly when called via `client_probe.py`.
- `complete_todo` with an out-of-range index returns a clear error
  message, not a raised, unhandled exception.
- `list_todos`'s own output correctly distinguishes done from not-done
  todos.
- You can explain, in a comment, exactly what changed about `TODOS`'s own
  data structure to support tracking "done," and why you chose that
  structure.

## Hints

- **Level 1:** Re-read Lesson 05's own `quest_notes_server.py` in full —
  this exercise's `todo_server.py` follows the exact same shape (a module
  with an `MCPServer` instance, some module-level data, and
  `@mcp.tool()`-decorated functions).
- **Level 2:** A list of small dicts (`{"text": ..., "done": False}`)
  is a reasonable, simple choice for `TODOS`'s own new shape — you don't
  need a database or a dataclass for this exercise's scope.
- **Level 3:** For `client_probe.py`, import your server module
  (`from todo_server import mcp`) and use `asyncio.run(...)` around an
  `async def main()` that calls `await mcp.call_tool(...)` for each tool
  in turn, printing `.structured_content` or `.content[0].text` after
  each call — exactly the pattern Lesson 05's own `client_probe.py`
  already showed you.

## Running it

```bash
cd module-15-agents-and-modern-ai-workflows/exercises/04-building-an-mcp-server/starter
python client_probe.py
```

**Expected output shape:** confirmation messages for each `add_todo`/
`complete_todo` call, followed by a `list_todos()` result showing the
correct done/not-done state for both entries.
