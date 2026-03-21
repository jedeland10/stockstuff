import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import create_pool, close_pool


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    """Async test client that hits the FastAPI app directly (no server needed)."""
    await create_pool()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await close_pool()
