import datetime
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from src.custom_pydantic import CustomModel
from src.modules.bookings.client import BookingDTO


class CollisionTypeEnum(StrEnum):
    ROOM = "room"
    TEACHER = "teacher"
    CAPACITY = "capacity"
    OUTLOOK = "outlook"


class Lesson(CustomModel):
    # > Main lesson info
    lesson_name: str
    "Name of the lesson"
    weekday: str | None = None
    "Weekday of a lesson"
    start_time: datetime.time
    "Start time of lesson"
    end_time: datetime.time
    "End time of lesson"
    room: str | tuple[str, ...] | None = None
    "Room for lesson, None - TBA, if list - multiple rooms simultaneously"
    teacher: str | None = None
    "Teacher on lesson"
    source_type: Literal["core_course", "elective"] | None = None
    "Whether the lesson comes from core courses or electives"
    # <

    # > Course and group info
    course_name: str | None = None
    "Name of the course"
    group_name: str | tuple[str, ...] | None = None
    "Name of the group or list of groups"
    students_number: int | None = None
    "Number of students in the group"
    # <

    # > Location Parser extras
    date_on: list[datetime.date] | None = None
    "Specific dates with lessons"
    date_except: list[datetime.date] | None = None
    "Specific dates when there is no lessons"
    date_from: datetime.date | None = None
    "Date from which the lesson starts"
    # <

    # > Google Spreadsheet info
    spreadsheet_id: str
    "Spreadsheet ID"
    google_sheet_gid: str
    "Google Spreadsheet ID of the sheet"
    google_sheet_name: str
    "Sheet name to which the lesson belongs in Google Spreadsheet"
    a1_range: str | None = None
    "Range of the lesson: may be multiple cells, for example 'A1:A10'"
    # <

    @model_validator(mode="after")
    def validate_date(self) -> Self:
        if not self.start_time < self.end_time:
            raise ValueError("Start time has to be less than end time")
        return self


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

    lesson: Lesson


class RoomIssue(CustomModel):
    """
    Issue when there are multiple lessons in the room at the same time.
    """

    collision_type: Literal[CollisionTypeEnum.ROOM]

    room: str | tuple[str, ...]
    "Room name"

    lessons: list[Lesson]
    "Lessons in the room at the same time"


class OutlookIssue(CustomModel):
    """
    Issue when there is a Outlook booking in the room at the same time as the lesson. Grouped by Outlook event title.
    """

    collision_type: Literal[CollisionTypeEnum.OUTLOOK]

    outlook_event_title: str
    "Title of the Outlook event"

    outlook_info: list[BookingDTO]
    "Outlook info about the bookings in the same time"

    lessons: list[Lesson]
    "Lessons that are in conflict with the Outlook event"


class TeacherIssue(CustomModel):
    """
    Issue when there is a teacher with multiple lessons at the same time, or when teacher study in the same time as the lesson.
    """

    collision_type: Literal[CollisionTypeEnum.TEACHER]

    teacher: str
    "Teacher name"

    teaching_lessons: list[Lesson]
    "Lessons of the teacher at the same time"
    studying_lessons: list[Lesson]
    "Lessons of the teacher as a student at the same time"


type Issue = Annotated[CapacityIssue | RoomIssue | OutlookIssue | TeacherIssue, Field(discriminator="collision_type")]


class CheckResults(CustomModel):
    issues: list[Issue]
