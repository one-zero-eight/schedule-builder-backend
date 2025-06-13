import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Booking(BaseModel):
    """Booking description"""

    room_id: str
    "ID of the room"
    event_id: str | None = None
    "ID of the event"
    title: str
    "Title of the booking"
    start: datetime.datetime
    "Start time of booking"
    end: datetime.datetime
    "End time of booking"


class Room(BaseModel):
    """Room description."""

    id: str
    "Room slug"
    title: str
    "Room title"
    short_name: str
    "Shorter version of room title"
    my_uni_id: int
    "ID of room on My University portal"
    capacity: int | None = None
    "Room capacity, amount of people"
    access_level: Literal["yellow", "red", "special"] | None = None
    "Access level to the room. Yellow = for students. Red = for employees. Special = special rules apply."
    restrict_daytime: bool = False
    "Prohibit to book during working hours. True = this room is available only at night 19:00-8:00, or full day on weekends."
