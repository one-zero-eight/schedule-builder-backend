import datetime
from urllib.parse import quote, urljoin, urlparse

import aiohttp

from src.domain.dtos.booking import BookingDTO
from src.domain.exceptions.base import AppException
from src.domain.exceptions.room import RoomNotFoundException
from src.domain.exceptions.tokens import InvalidTokenException

DOMAINS_ALLOWLIST = ["api.innohassle.ru"]


class BookingService:
    def __init__(self, token: str) -> None:
        self.token = token

    async def get_room_bookings(
        self, room_id: str, start: datetime.datetime, end: datetime.datetime
    ) -> list[
        BookingDTO
    ]:  # TODO: Rewrite functions to use same endpoint once updated booking is in production
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            base_url = (
                "https://api.innohassle.ru/room-booking/staging-v0/room/"
            )
            safe_room_id = quote(room_id, safe="")
            full_url = urljoin(base_url, f"{safe_room_id}/bookings")

            if urlparse(full_url).hostname not in DOMAINS_ALLOWLIST:
                raise AppException(f"URL {full_url} is not whitelisted.")

            async with client.get(
                full_url,
                params={
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            ) as response:
                if response.status == 401:
                    raise InvalidTokenException()
                if response.status == 404:
                    raise RoomNotFoundException()
                if response.status != 200:
                    raise AppException()
                data = await response.json()
                for entry in data:
                    entry["start_time"] = entry["start"]
                    del entry["start"]
                    entry["end_time"] = entry["end"]
                    del entry["end"]
                return [
                    BookingDTO.model_validate(entry, from_attributes=True)
                    for entry in data
                ]

    async def get_all_bookings(
        self, start: datetime, end: datetime
    ) -> list[BookingDTO]:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.get(
                "https://api.innohassle.ru/room-booking/staging-v0/bookings/",
                params={
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            ) as response:
                if response.status == 401:
                    raise InvalidTokenException()
                if response.status == 404:
                    raise RoomNotFoundException()
                if response.status != 200:
                    raise AppException()
                data = await response.json()
                for entry in data:
                    entry["start_time"] = entry["start"]
                    del entry["start"]
                    entry["end_time"] = entry["end"]
                    del entry["end"]
                return [
                    BookingDTO.model_validate(entry, from_attributes=True)
                    for entry in data
                ]
