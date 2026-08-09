# Lesson 05 — Model Context Protocol (MCP)

**Verified live on August 9, 2026, by installing the current SDK into a
throwaway virtual environment and running every code sample below for
real** (not just reading documentation about it): current MCP
specification version `2026-07-28`; current official Python SDK package
`mcp`, version `2.0.0` (released the same day as the spec); its server
class is `mcp.server.MCPServer` (the in-SDK successor to the standalone
`fastmcp` package's `FastMCP` — same job, renamed as part of the `2.0.0`
rework); tools are declared with an `@mcp.tool()` decorator; `mcp.run()`
defaults to `transport="stdio"`. Source: `blog.modelcontextprotocol.io`'s
own `2026-07-28` release post, and `pypi.org/pypi/mcp/json`, both fetched
live, cross-checked against the actual installed package's own API.

## What you'll learn

- What MCP is, and the exact problem it solves — one that should feel
  very familiar from game development.
- The three roles in every MCP interaction: **host**, **client**, and
  **server** — and which one *you* are building in this lesson.
- How to build a real, working MCP server, using the current official
  Python SDK, that exposes tools any MCP-compliant client (including
  Claude Desktop, Claude Code, and other AI products) could call.
- What a *transport* is in MCP's own vocabulary, and which one this
  lesson's own server uses, and why.

## Why this matters

Every tool this module has built so far has been wired directly into one
specific Python script or one specific FastAPI backend — useful, but not
*reusable*. If you wanted the exact same "search my quest notes" tool
available to Claude Desktop, to a completely different agent framework,
and to QuestLog's own backend, without MCP you'd write three separate,
bespoke integrations — three different ways of exposing the same
underlying capability, each with its own quirks. MCP exists specifically
to make that unnecessary.

## Prerequisites

- **Lessons 01–03, in full** — the concept of a "tool" (a name, a
  description, a schema, a function) is assumed throughout this lesson;
  MCP is a *standard way to expose* the same kind of tool you've already
  been defining, not a new kind of tool.
- **Lesson 00's own setup, Step 2** — the `mcp[cli]` package installed
  into its own scratch virtual environment, separate from QuestLog's own
  backend.

## The concept, explained simply

Imagine every game engine needed its own bespoke, hand-written
integration code for every single third-party tool or mod it wanted to
support — one integration for a level editor, a completely different one
for an asset importer, a third for a version-control plugin, each
speaking its own private protocol. That's real, extra work multiplied by
every engine-times-tool combination, and it's exactly the problem a
standardized **plugin interface** solves: agree on one common protocol
once, and any compliant tool can talk to any compliant engine, with zero
bespoke glue code per pairing.

**MCP (Model Context Protocol) is that same idea, applied to AI tools.**
Before MCP, if you built a genuinely useful tool (say, "search my
company's internal wiki"), making it available to Claude Desktop, to a
custom agent script, *and* to some other AI product each meant writing
that tool's logic three separate times, in three separate integration
shapes. MCP defines one standard protocol — a fixed way to describe what
tools a server offers, and a fixed way for a client to discover and call
them — so you write the tool's logic **once**, as an MCP server, and any
MCP-compliant client can use it immediately, with no bespoke code on
either side.

### The three roles: host, client, server

MCP's own vocabulary names three distinct participants, and it's worth
knowing all three even though this lesson only builds one of them:

- **Host** — the actual application a person is using (Claude Desktop,
  Claude Code, a custom chat UI you build). The host is where a person
  types a message.
- **Client** — the piece of code, living *inside* the host, that speaks
  MCP to a specific server. A host can run several clients at once, one
  per connected server.
- **Server** — the thing you're about to build: a standalone program that
  exposes tools (and, optionally, other kinds of context — MCP also
  standardizes "resources" and "prompts," which this lesson doesn't cover
  in depth) over the protocol, for any client to discover and call.

This lesson builds a **server**. Claude Desktop and Claude Code are
examples of real **hosts** you could point your finished server at,
without writing a single line of client code yourself — that's the entire
point of the standard.

### Transports: how a client and server actually talk

MCP separates *what gets said* (the protocol: tool discovery, tool calls,
results) from *how it physically gets sent* (the transport). The current
spec (`2026-07-28`, verified live above) and SDK support:

- **`stdio`** — the client starts your server as a subprocess and talks
  to it over its standard input/output streams. This is the default and
  the right choice for a *local* server (one running on the same machine
  as the host) — no network, no ports, no auth to configure. This
  lesson's own server uses `stdio`.
- **Streamable HTTP** — the right choice for a *remote* server (one
  running somewhere else entirely, reachable over the network). Involves
  real HTTP concerns (auth, hosting) this lesson's own local example
  doesn't need.
- **SSE** (Server-Sent Events) — an older transport, now deprecated as of
  the `2026-07-28` spec (with a stated year-long transition window before
  it's removed entirely). New servers should use `stdio` or Streamable
  HTTP, not SSE.

## The details

### Step 1 — A minimal MCP server, in full

Two tools over a tiny, hard-coded, in-memory set of notes — deliberately
no database, no Anthropic API key, so this example runs in under a
minute with nothing beyond Lesson 00's own `mcp[cli]` install:

```python
"""quest_notes_server.py -- a small, standalone MCP server."""
from mcp.server import MCPServer

mcp = MCPServer("quest-notes")

NOTES = {
    "boss-fight-prep": "Bring fire resistant armor. Approach from the east ridge.",
    "village-errands": "The healer needs five bundles of silverleaf from the eastern woods.",
}


@mcp.tool()
def list_notes() -> list[str]:
    """List the titles of every available note."""
    return list(NOTES.keys())


@mcp.tool()
def read_note(title: str) -> str:
    """Read the full content of one note by its exact title."""
    if title not in NOTES:
        return f"No note titled '{title}'."
    return NOTES[title]


if __name__ == "__main__":
    mcp.run()
```

Every piece here should already feel familiar:

- `MCPServer("quest-notes")` — creates the server, named `"quest-notes"`
  (this name is what a host shows a user when listing connected servers).
- `@mcp.tool()` — the SDK builds a tool's JSON Schema **automatically**
  from your function's own type hints and docstring — you never
  hand-write an `input_schema` dict the way every earlier lesson in this
  module has. `list_notes`'s return type (`list[str]`) and `read_note`'s
  parameter (`title: str`) are both read directly from the function
  signature.
- `mcp.run()` — starts the server, defaulting to the `stdio` transport
  (verified above) — this call blocks, waiting for a client to connect
  over standard input/output, exactly the way a game server's own main
  loop blocks waiting for connections.

### Step 2 — Call it directly, without a full client, to see it work

Before connecting a real host, you can call a server's own tools directly
in Python — useful for exactly the same reason Lesson 02's fake client
was useful: seeing the mechanism work before adding a second moving part.

```python
"""client_probe.py -- calls quest_notes_server.py's tools directly, in
the same process, with no separate client/host needed."""
import asyncio
from quest_notes_server import mcp

async def main():
    tools = await mcp.list_tools()
    print("Available tools:")
    for t in tools:
        print(f"  - {t.name}: {t.description}")

    result = await mcp.call_tool("list_notes", {})
    print("\nlist_notes() ->", result.structured_content["result"])

    result = await mcp.call_tool("read_note", {"title": "boss-fight-prep"})
    print("read_note('boss-fight-prep') ->", result.content[0].text)

    result = await mcp.call_tool("read_note", {"title": "does-not-exist"})
    print("read_note('does-not-exist') ->", result.content[0].text)

asyncio.run(main())
```

Run it:

```bash
python client_probe.py
```

**Expected output, live-verified exactly as shown, August 9, 2026:**

```
Available tools:
  - list_notes: List the titles of every available note.
  - read_note: Read the full content of one note by its exact title.

list_notes() -> ['boss-fight-prep', 'village-errands']
read_note('boss-fight-prep') -> Bring fire resistant armor. Approach from the east ridge.
read_note('does-not-exist') -> No note titled 'does-not-exist'.
```

Notice `read_note`'s own "not found" handling — a plain returned string,
not a raised exception. `call_tool` also has a real error path: calling a
tool name that doesn't exist at all (as opposed to one that exists but
was given bad input, like `read_note`'s own `title` check above) raises a
`ToolError` — live-verified, same session:

```python
try:
    await mcp.call_tool("delete_everything", {})
except Exception as exc:
    print(type(exc).__name__, exc)
# ToolError Unknown tool: delete_everything
```

### Step 3 — Run it as a real server, over stdio

`client_probe.py` above calls the server's own Python object directly, in
the same process — genuinely useful for understanding, but it never
actually exercises the protocol or the `stdio` transport at all. To run
it as a real, separate MCP server a real client could connect to:

```bash
python quest_notes_server.py
```

**Expected:** the process starts and appears to hang — this is correct.
It's now waiting on stdin for a client speaking MCP to connect, exactly
like a dedicated game server process blocking on its own accept loop
until a player connects. Press Ctrl+C to stop it.

**Try it yourself:** The `mcp[cli]` extra installs an interactive
inspector. Run `mcp dev quest_notes_server.py` and follow the URL it
prints — it opens a browser-based tool that connects to your server as a
real MCP client, lets you see both tools listed exactly as
`client_probe.py` did, and call them by hand through a UI instead of
code. Confirm you can call `read_note` with a note title and get the same
text back.

### Connecting a real host (conceptual — no hands-on step required)

Claude Desktop and Claude Code can both be configured to launch a local
`stdio` server like this one and use its tools directly in a
conversation, with zero client code of your own — you'd add an entry
naming the command to run (`python`, with `quest_notes_server.py` as an
argument) to that host's own MCP configuration. This lesson doesn't walk
through that configuration step by step (it's host-specific and outside
this course's own scope), but it's worth knowing this is the entire
remaining step between what you just built and using it inside a real AI
product you didn't have to write any client code for.

## Common mistakes & gotchas

- **`ImportError: cannot import name 'FastMCP' from 'mcp.server.fastmcp'`.**
  See Lesson 00's own note on this — `FastMCP` was the standalone
  package's (and an earlier SDK generation's) class name. The current
  official SDK (`mcp` `2.0.0`, verified live above) uses
  `mcp.server.MCPServer` instead. If a tutorial or search result shows
  `FastMCP`, the concepts transfer directly; only the import changed.
- **Forgetting `mcp.run()` blocks.** It's meant to — a server waiting for
  connections is supposed to sit there. If you want to inspect a server's
  tools programmatically without starting the blocking server loop
  (Step 2 above), call `mcp.list_tools()` / `mcp.call_tool()` directly
  instead of `mcp.run()`.
- **Expecting `call_tool`'s `.content[0].text` to hold a whole list
  result.** For `list_notes`, which returns a Python `list[str]`, the SDK
  produces one `TextContent` block *per item* in `.content`, plus a
  separate `.structured_content` field holding the real, structured
  Python value (`{"result": [...]}`) — use `.structured_content` when you
  want the actual data back, not just its individually-rendered text
  form.
- **Treating MCP as a replacement for the tool-use round trip you already
  know.** It isn't — MCP standardizes how a tool gets *discovered and
  invoked across systems*; the round trip itself (model decides → calls
  tool → observes result) is identical either way, whether the tool is
  wired in by hand (Lessons 02–03) or exposed over MCP.

## How this connects

Lessons 02–03 taught you tool design and the loop that calls tools;
this lesson gave you a standardized way to expose those same kinds of
tools to *any* compliant client, not just your own hand-written loop.
Lesson 06 covers what happens when more than one agent — potentially each
with its own tool set, potentially reached over MCP — needs to
coordinate. Lesson 11 revisits MCP one more time, with a concrete,
honest decision about whether and how QuestLog's own capstone exposes any
of its real agent tools this same way.

## Quick self-check

1. Name MCP's three roles (host, client, server) and state, in one
   sentence each, what distinguishes them.
2. What specific, repeated integration problem does MCP solve — described
   in your own words, not copied from this lesson?
3. Which transport did this lesson's own server use, and why is it the
   right choice for a *local* server specifically?
4. What does `@mcp.tool()` do for you automatically that every earlier
   tool definition in this module required you to write by hand?
5. What is the actual difference between `.content` and
   `.structured_content` on a tool call's result, and when would you
   reach for one over the other?
