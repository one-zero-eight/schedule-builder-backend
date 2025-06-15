import aiohttp

from src.application.external_api.innohassle.interfaces.room import (
    IRoomService,
)
from src.config import settings
from src.domain.dtos.room import RoomDTO
from src.domain.exceptions.base import AppException


class RoomService(IRoomService):
    def __init__(self) -> None:
        self.token = settings.accounts.api_jwt_token.get_secret_value()

    async def get_rooms(self) -> list[RoomDTO]:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.get(
                "https://api.innohassle.ru/room-booking/staging-v0/rooms/"
            ) as response:
                if response.status != 200:
                    raise AppException(
                        status_code=response.status, detail=response.reason
                    )
                return [
                    RoomDTO.model_validate(entry, from_attributes=True)
                    for entry in await response.json()
                ]
