from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from src.custom_pydantic import CustomModel
from src.modules.bookings.client import BookingDTO
from src.modules.parsers.schemas import LessonWithExcelCellsDTO


class CollisionTypeEnum(StrEnum):
    ROOM = "room"
    TEACHER = "teacher"
    CAPACITY = "capacity"
    OUTLOOK = "outlook"


class LessonWithCollisionTypeDTO(LessonWithExcelCellsDTO):
    collision_type: CollisionTypeEnum
    "Type of collision"
    outlook_info: BookingDTO | None = None
    "Outlook info"
    room_capacity: int | None = None
    "Capacity of the room"


class CapacityIssue(CustomModel):
    """
    Issue when there is not enough places in the room for the lesson.
    """

    collision_type: Literal[CollisionTypeEnum.CAPACITY]

    room: str | tuple[str, ...]
    "Room name"
    room_capacity: int | None
    "Assumed capacity of the room"
    needed_capacity: int
    "Needed capacity for the lesson (sum of all groups)"

    lesson: LessonWithExcelCellsDTO


class RoomIssue(CustomModel):
    """
    Issue when there are multiple lessons in the room at the same time.
    """

    collision_type: Literal[CollisionTypeEnum.ROOM]

    room: str | tuple[str, ...]
    "Room name"

    lessons: list[LessonWithExcelCellsDTO]
    "Lessons in the room at the same time"


class OutlookIssue(CustomModel):
    """
    Issue when there is a Outlook booking in the room at the same time as the lesson.
    """

    collision_type: Literal[CollisionTypeEnum.OUTLOOK]

    outlook_info: list[BookingDTO]
    "Outlook info about the booking in the room same time"

    lesson: LessonWithExcelCellsDTO


class TeacherIssue(CustomModel):
    """
    Issue when there is a teacher with multiple lessons at the same time, or when teacher study in the same time as the lesson.
    """

    collision_type: Literal[CollisionTypeEnum.TEACHER]

    teacher: str
    "Teacher name"

    teaching_lessons: list[LessonWithExcelCellsDTO]
    "Lessons of the teacher at the same time"
    studying_lessons: list[LessonWithExcelCellsDTO]
    "Lessons of the teacher as a student at the same time"


type Issue = Annotated[CapacityIssue | RoomIssue | OutlookIssue | TeacherIssue, Field(discriminator="collision_type")]


class CheckResults(CustomModel):
    issues: list[Issue]
