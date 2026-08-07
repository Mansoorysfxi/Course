from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import _announcements, app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """See lessons/05-testing-fastapi-endpoints.md for exactly what
    ASGITransport does. `_announcements.clear()` before yielding gives
    every test a genuinely empty board, the same "fresh state, every
    test, guaranteed" property lessons/02 and 06 both build fixtures
    around -- there's no real database here to recreate (this app has
    none, deliberately), so clearing the one in-memory dict this app
    actually stores everything in is the direct equivalent."""
    _announcements.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
