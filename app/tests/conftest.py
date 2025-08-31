from app.main import app
import pytest, pytest_asyncio
from httpx import ASGITransport, AsyncClient

@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    print("...Setting up...")
    yield
    print("...Tearing down...")