import datetime
from typing import Literal
from urllib.parse import quote, urljoin, urlparse

import httpx
from pydantic import Field

from src.config import settings
from src.custom_pydantic import CustomModel

DOMAINS_ALLOWLIST = ["api.innohassle.ru"]


class BookingDTO(CustomModel):
    """Booking description"""

    room_id: str
    "ID of the room"
    event_id: str | None = None
    "ID of the event"
    title: str
    "Title of the booking"
    start_time: datetime.datetime = Field(validation_alias="start")
    "Start time of booking"
    end_time: datetime.datetime = Field(validation_alias="end")
    "End time of booking"


class RoomDTO(CustomModel):
    """Room description."""

    id: str
    "Room slug"
    title: str | None = None
    "Room title"
    short_name: str | None = None
    "Shorter version of room title"
    my_uni_id: int | None = None
    "ID of room on My University portal"
    capacity: int | None = None
    "Room capacity, amount of people"
    access_level: Literal["yellow", "red", "special"] | None = None
    "Access level to the room. Yellow = for students. Red = for employees. Special = special rules apply."
    restrict_daytime: bool = False
    "Prohibit to book during working hours. True = this room is available only at night 19:00-8:00, or full day on weekends."


class BookingClient:
    def __init__(self, url: str) -> None:
        self.url = url

    async def get_room_bookings(
        self,
        token: str,
        room_id: str,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> list[BookingDTO]:  # TODO: Rewrite functions to use same endpoint once updated booking is in production
        async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as client:
            safe_room_id = quote(room_id, safe="")
            full_url = urljoin(self.url, f"{safe_room_id}/bookings")

            if urlparse(full_url).hostname not in DOMAINS_ALLOWLIST:
                raise ValueError(f"URL {full_url} is not whitelisted.")

            response = await client.get(
                full_url,
                params={"start": start.isoformat(), "end": end.isoformat()},
            )
            response.raise_for_status()
            data = response.json()
            return [BookingDTO.model_validate(entry) for entry in data]

    async def get_all_bookings(
        self,
        token: str,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> list[BookingDTO]:
        async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as client:
            response = await client.get(
                urljoin(self.url, "bookings/"),
                params={"start": start.isoformat(), "end": end.isoformat()},
            )
            response.raise_for_status()
            data = response.json()
            return [BookingDTO.model_validate(entry) for entry in data]

    async def get_rooms(self, token: str) -> list[RoomDTO]:
        async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as client:
            response = await client.get(urljoin(self.url, "rooms/"), params={"include_red": True})
            response.raise_for_status()
            return [RoomDTO.model_validate(entry) for entry in response.json()]


booking_client: BookingClient = BookingClient(url=settings.booking.api_url)
