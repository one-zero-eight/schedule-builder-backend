from datetime import datetime

from dishka import Provider, Scope, provide

from src.domain.dtos.booking import BookingDTO


class MockBookingService:
    async def get_room_bookings(
        self, room_id: str, start: datetime, end: datetime
    ) -> list[BookingDTO]:
        return []

    async def get_all_bookings(
        self, start: datetime, end: datetime
    ) -> list[BookingDTO]:
        return []


class MockBookingServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_booking_service(self) -> MockBookingService:
        return MockBookingService()
