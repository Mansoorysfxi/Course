"""Exercise 04 -- reference solution's own client probe."""

import asyncio

from todo_server import mcp


async def main():
    result = await mcp.call_tool("add_todo", {"text": "Buy a sword"})
    print(result.content[0].text)

    result = await mcp.call_tool("add_todo", {"text": "Find the ancient map"})
    print(result.content[0].text)

    result = await mcp.call_tool("complete_todo", {"index": 0})
    print(result.content[0].text)

    result = await mcp.call_tool("list_todos", {})
    print("\nFinal todo list:")
    for line in result.structured_content["result"]:
        print(" ", line)


if __name__ == "__main__":
    asyncio.run(main())
