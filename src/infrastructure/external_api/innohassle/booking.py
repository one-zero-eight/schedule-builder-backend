import datetime

import aiohttp

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.domain.dtos.booking import BookingDTO


class BookingService(IBookingService):
    def __init__(self, token: str) -> None:
        self.token = token

    async def get_bookings(
        self, room_id: str, start: datetime.datetime, end: datetime.datetime
    ) -> list[BookingDTO]:
        async with aiohttp.ClientSession(
            headers={"Authorization": self.token}
        ) as client:
            async with client.get(
                f"https://api.innohassle.ru/room-booking/staging-v0/room/{room_id}/bookings",
                params={
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            ) as response:
                return [BookingDTO(**entry) for entry in response.json()]
