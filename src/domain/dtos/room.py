from typing import Literal

from pydantic import BaseModel


class RoomDTO(BaseModel):
    """Room description."""

    id: str
    "Room slug"
    title: str | None = None
    "Room title"
    short_name: str | None = None
    "Shorter version of room title"
    my_uni_id: int | None = None
    "ID of room on My University portal"
    capacity: int | None = None
    "Room capacity, amount of people"
    access_level: Literal["yellow", "red", "special"] | None = None
    "Access level to the room. Yellow = for students. Red = for employees. Special = special rules apply."
    restrict_daytime: bool = False
    "Prohibit to book during working hours. True = this room is available only at night 19:00-8:00, or full day on weekends."
