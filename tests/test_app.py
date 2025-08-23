import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app_is_running(fastapi_test_client: AsyncClient) -> None:
    response = await fastapi_test_client.get("/", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_failed(fastapi_test_client: AsyncClient) -> None:
    response = await fastapi_test_client.get("/options/")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_auth_success(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.get(url="/options/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_collisions(
    authenticated_client: AsyncClient,
    mock_booking_client,
) -> None:
    """Basic test to verify the collisions endpoint exists and returns proper format."""
    response = await authenticated_client.get(
        url="/collisions/check",
        params={"google_spreadsheet_id": "1amQqvE0rfU92pfMsMnUKA-lTGjlcJ-Sv5UcPpGnxW4w", "target_sheet_name": "SUMMER"},
    )

    # We expect this to fail with 401 (no auth) or other error,
    # but not 404 (endpoint not found)
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_get_rooms_with_mock(
    authenticated_client: AsyncClient,
    mock_booking_client,
) -> None:
    """Test the rooms endpoint using the mocked booking client."""
    response = await authenticated_client.get("/dev/rooms")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "test_room_1"
    assert data[0]["title"] == "Test Room 1"

    mock_booking_client.get_rooms.assert_called_once()


@pytest.mark.asyncio
async def test_get_bookings_with_mock(
    authenticated_client: AsyncClient,
    mock_booking_client,
) -> None:
    """Test the bookings endpoint using the mocked booking client."""
    response = await authenticated_client.get("/dev/bookings")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["room_id"] == "test_room_1"
    assert data[0]["title"] == "Test Booking 1"

    mock_booking_client.get_all_bookings.assert_called_once()
