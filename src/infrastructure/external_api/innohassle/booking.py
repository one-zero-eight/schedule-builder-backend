import datetime

import aiohttp

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.domain.dtos.booking import BookingDTO
from src.domain.exceptions.base import AppException
from src.domain.exceptions.room import RoomNotFoundException
from src.domain.exceptions.tokens import InvalidTokenException


class BookingService(IBookingService):
    def __init__(self, token: str) -> None:
        self.token = token

    async def get_bookings(
        self, room_id: str, start: datetime.datetime, end: datetime.datetime
    ) -> list[BookingDTO]:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.get(
                f"https://api.innohassle.ru/room-booking/staging-v0/room/{room_id}/bookings",
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
                return [
                    BookingDTO.model_validate(entry, from_attributes=True)
                    for entry in await response.json()
                ]
