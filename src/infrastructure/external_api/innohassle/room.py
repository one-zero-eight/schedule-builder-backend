import aiohttp

from src.application.external_api.innohassle.interfaces.room import (
    IRoomService,
)
from src.domain.dtos.room import RoomDTO


class RoomService(IRoomService):
    def __init__(self, token: str) -> None:
        self.token = token

    async def get_rooms(self) -> list[RoomDTO]:
        async with aiohttp.ClientSession(
            headers={"Authorization": self.token}
        ) as client:
            async with client.get(
                "https://api.innohassle.ru/room-booking/staging-v0/rooms/"
            ) as response:
                return [RoomDTO(**entry) for entry in response.json()]
