from dishka import Provider, Scope, provide

from src.application.external_api.innohassle.interfaces.room import (
    IRoomService,
)
from src.infrastructure.external_api.innohassle.room import RoomService
from src.domain.dtos.users import UserTokenDataDTO


class RoomServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_room_service(self, token_data: UserTokenDataDTO) -> IRoomService:
        return RoomService(token_data.token)
