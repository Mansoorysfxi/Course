"""Exercise 04 -- calls todo_server.py's own tools directly, the exact
same "call a server's own tools without a separate client process"
pattern Lesson 05's own client_probe.py used.

TODO: call add_todo twice, complete_todo once, then list_todos, and print
each result, per INSTRUCTIONS.md's own Step 4.
"""

import asyncio

from todo_server import mcp


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
