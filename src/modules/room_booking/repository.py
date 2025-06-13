import datetime
from typing import Final

import httpx

from src.modules.room_booking.schemas import Booking, Room


class BookingRepository:
    def get_bookings(self, room_id: str, start: datetime.datetime, end: datetime.datetime, bearer_token: str) -> list[Booking]:
        with httpx.Client(headers={"Authorization": bearer_token}) as client:
            response = client.get(
                f"https://api.innohassle.ru/room-booking/staging-v0/room/{room_id}/bookings",
                params={
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            )

        response.raise_for_status()
        return [Booking(**entry) for entry in response.json()]


class RoomRepository:
    def get_rooms(self, bearer_token: str) -> list[Room]:
        with httpx.Client(headers={"Authorization": bearer_token}) as client:
            response = client.get("https://api.innohassle.ru/room-booking/staging-v0/rooms/")

        response.raise_for_status()
        return [Room(**entry) for entry in response.json()]


booking_repository: Final[BookingRepository] = BookingRepository()
room_repository: Final[RoomRepository] = RoomRepository()
