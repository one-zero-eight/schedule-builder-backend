from dishka import Provider, provide, Scope
from src.domain.dtos.room import RoomDTO
from yaml import safe_load


class RoomsWithCapacityProvider(Provider):
    scope = Scope.APP

    @provide
    def get_rooms_with_capacity(self) -> list[RoomDTO]:
        rooms = list()
        with open("rooms.yaml", "r", encoding="utf-8") as file:
            data = safe_load(file)
            for room in data["rooms"]:
                rooms.append(
                    RoomDTO(
                        id=str(room["name"]), capacity=int(room["capacity"])
                    )
                )
        return rooms
