import aiohttp

from src.domain.dtos.room import RoomDTO
from src.domain.exceptions.base import AppException
from src.domain.exceptions.tokens import InvalidTokenException


class RoomService:
    def __init__(self, token: str) -> None:
        self.token = token

    async def get_rooms(self) -> list[RoomDTO]:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.get(
                "https://api.innohassle.ru/room-booking/staging-v0/rooms/"
            ) as response:
                if response.status == 401:
                    raise InvalidTokenException()
                if response.status != 200:
                    raise AppException()
                return [
                    RoomDTO.model_validate(entry, from_attributes=True)
                    for entry in await response.json()
                ]
