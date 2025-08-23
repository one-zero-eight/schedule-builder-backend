from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api.app import app


@pytest.fixture(scope="function")
def fastapi_app() -> FastAPI:
    return app


@pytest_asyncio.fixture(scope="function")
async def fastapi_test_client(
    fastapi_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        yield client
