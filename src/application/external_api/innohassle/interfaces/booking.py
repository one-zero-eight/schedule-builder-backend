from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.dtos.booking import BookingDTO


class IBookingService(ABC):
    @abstractmethod
    def get_bookings(
        self, room_id: int, start: datetime, end: datetime
    ) -> list[BookingDTO]:
        pass
