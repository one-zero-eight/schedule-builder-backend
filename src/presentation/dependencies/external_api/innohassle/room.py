from dishka import Provider, Scope, provide

from src.domain.dtos.users import UserTokenDataDTO
from src.infrastructure.external_api.innohassle.room import RoomService


class RoomServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_room_service(
        self, token_data: UserTokenDataDTO
    ) -> RoomService:
        return RoomService(token_data.token)
