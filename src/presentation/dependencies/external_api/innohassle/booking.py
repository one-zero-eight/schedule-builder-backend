import aiohttp
from dishka import Provider, Scope, provide

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.infrastructure.external_api.innohassle.booking import BookingService
from src.domain.dtos.users import UserTokenDataDTO


class BookingServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_booking_service(self, token_data: UserTokenDataDTO) -> IBookingService:
        return BookingService(token_data.token)
