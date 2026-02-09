from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api.app import app
from src.api.dependencies import verify_token_dep
from src.modules.bookings.client import BookingDTO, RoomDTO
from src.modules.inh_accounts_sdk import UserTokenData


@pytest.fixture(scope="function")
def fastapi_app() -> FastAPI:
    return app


@pytest_asyncio.fixture(scope="function")
async def fastapi_test_client(
    fastapi_app: FastAPI,
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(fastapi_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    async def fake_verify_token_dep() -> tuple[UserTokenData, str] | None:
        return UserTokenData(innohassle_id="123", email="test@test.com"), "test_token"

    fastapi_app.dependency_overrides[verify_token_dep] = fake_verify_token_dep

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        yield client

    fastapi_app.dependency_overrides.pop(verify_token_dep)


@pytest.fixture(scope="function")
def mock_booking_client():
    """Mock booking_client with default return values."""
    mock_client = AsyncMock()

    bookings = [
        {
            "room_id": "test_room_1",
            "event_id": "event_1",
            "title": "Test Booking 1",
            "start": "2025-01-01T09:00:00Z",
            "end": "2025-01-01T10:00:00Z",
        },
        {
            "room_id": "test_room_2",
            "event_id": "event_2",
            "title": "Test Booking 2",
            "start": "2025-01-01T11:00:00Z",
            "end": "2025-01-01T12:00:00Z",
        },
    ]

    mock_client.get_all_bookings.return_value = [BookingDTO.model_validate(booking) for booking in bookings]
    mock_client.get_room_bookings.return_value = [BookingDTO.model_validate(booking) for booking in bookings[:1]]

    mock_client.get_rooms.return_value = [
        RoomDTO(
            id="test_room_1",
            title="Test Room 1",
            short_name="TR1",
            my_uni_id=101,
            capacity=25,
            access_level="yellow",
            restrict_daytime=False,
        ),
        RoomDTO(
            id="test_room_2",
            title="Test Room 2",
            short_name="TR2",
            my_uni_id=102,
            capacity=50,
            access_level="red",
            restrict_daytime=True,
        ),
    ]

    with (
        patch("src.modules.bookings.client.booking_client", mock_client),
        patch("src.modules.bookings.routes.booking_client", mock_client),
        patch("src.modules.collisions.collision_checker.booking_client", mock_client),
        patch("src.modules.collisions.routes.booking_client", mock_client),
    ):
        yield mock_client
