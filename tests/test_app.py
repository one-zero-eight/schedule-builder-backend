import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app_is_running(fastapi_test_client: AsyncClient) -> None:
    response = await fastapi_test_client.get("/", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_failed(fastapi_test_client: AsyncClient) -> None:
    response = await fastapi_test_client.get(
        "/collisions/check",
        params={
            "google_spreadsheet_id": "dummy_id",
            "target_sheet_name": "dummy_sheet",
        },
        follow_redirects=True,
    )
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.skip(reason="Integration test requires real Google Sheets and credentials")
@pytest.mark.asyncio
async def test_check_excel_collisions_endpoint_exists(
    fastapi_test_client: AsyncClient,
) -> None:
    """Basic test to verify the collisions endpoint exists and returns proper format."""
    response = await fastapi_test_client.get(
        url="/collisions/check",
        params={
            "google_spreadsheet_id": "dummy_id",
            "target_sheet_name": "dummy_sheet",
        },
    )

    # We expect this to fail with 401 (no auth) or other error,
    # but not 404 (endpoint not found)
    assert response.status_code != 404
