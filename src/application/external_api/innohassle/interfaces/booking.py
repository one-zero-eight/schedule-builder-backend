from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.dtos.booking import BookingDTO


class IBookingService(ABC):
    @abstractmethod
    async def get_room_bookings(
        self, room_id: str, start: datetime, end: datetime
    ) -> list[BookingDTO]:
        pass

    @abstractmethod
    async def get_all_bookings(
        self, start: datetime, end: datetime
    ) -> list[BookingDTO]:
        pass
