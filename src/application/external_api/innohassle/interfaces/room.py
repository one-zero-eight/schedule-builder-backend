from abc import ABC, abstractmethod

from src.domain.dtos.room import RoomDTO


class IRoomService(ABC):
    @abstractmethod
    def get_rooms(self) -> list[RoomDTO]:
        pass
