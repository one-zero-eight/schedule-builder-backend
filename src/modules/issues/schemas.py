import datetime
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from src.custom_pydantic import CustomModel
from src.modules.bookings.client import BookingDTO
from src.modules.schedule_config.schemas import WeeklyPatternSlotEdit
from src.weekday import Weekday


class OccurrencePlacement(CustomModel):
    kind: Literal["occurrence"] = "occurrence"
    date: datetime.date


class WeeklyPatternPlacement(CustomModel):
    kind: Literal["weekly_pattern"] = "weekly_pattern"
    weekday: Weekday
    edits: list[WeeklyPatternSlotEdit] = Field(default_factory=list)


MeetingPlacement = Annotated[
    OccurrencePlacement | WeeklyPatternPlacement,
    Field(discriminator="kind"),
]


class ScheduledMeeting(CustomModel):
    course_name: str
    component_tag: str
    source_kind: Literal["core_course", "elective"]
    placement: MeetingPlacement
    start_time: datetime.time
    end_time: datetime.time
    room: str | None = None
    instructor: str | list[str] | None = None
    groups: tuple[str, ...] = ()
    students_number: int | None = None

    @model_validator(mode="after")
    def validate_time(self) -> Self:
        if not self.start_time < self.end_time:
            raise ValueError("Start time has to be less than end time")
        return self


class IssueTypeEnum(StrEnum):
    ROOM = "room"
    TEACHER = "teacher"
    CAPACITY = "capacity"
    OUTLOOK = "outlook"
    UNPLACED = "unplaced"
    INSTRUCTOR_ID = "instructor_id"
    UNBOOKED = "unbooked"
    GROUP = "group"
    STUDENT = "student"
    PER_WEEK = "per_week"


class CapacityIssue(CustomModel):
    """Занятие не помещается в аудиторию: число студентов превышает вместимость комнаты."""

    issue_type: Literal[IssueTypeEnum.CAPACITY]

    text: str = ""
    room: str
    room_capacity: int | None
    needed_capacity: int

    meeting: ScheduledMeeting


class RoomIssue(CustomModel):
    """В одной аудитории одновременно запланированы несколько разных занятий."""

    issue_type: Literal[IssueTypeEnum.ROOM]

    text: str = ""
    room: str
    meetings: list[ScheduledMeeting]


class OutlookIssue(CustomModel):
    """Занятие пересекается по времени с бронированием в Outlook/room-booking."""

    issue_type: Literal[IssueTypeEnum.OUTLOOK]

    text: str = ""
    outlook_event_title: str
    outlook_info: list[BookingDTO]
    meetings: list[ScheduledMeeting]


class TeacherIssue(CustomModel):
    """Преподаватель одновременно ведёт занятие и учится на другом (или ведёт несколько занятий)."""

    issue_type: Literal[IssueTypeEnum.TEACHER]

    text: str = ""
    instructor: str
    teaching_meetings: list[ScheduledMeeting]
    studying_meetings: list[ScheduledMeeting]


class UnplacedIssue(CustomModel):
    """Компонент курса объявлен в конфигурации, но для него не задано расписание."""

    issue_type: Literal[IssueTypeEnum.UNPLACED]

    text: str = ""
    course_name: str
    component_tag: str
    source_kind: Literal["core_course", "elective"]
    student_groups: tuple[str, ...] = ()


class InstructorIdIssue(CustomModel):
    """Идентификатор преподавателя не является корпоративным email Innopolis."""

    issue_type: Literal[IssueTypeEnum.INSTRUCTOR_ID]

    text: str = ""
    instructor_id: str


class UnbookedIssue(CustomModel):
    """Занятие из конфигурации не имеет соответствующего бронирования в Outlook."""

    issue_type: Literal[IssueTypeEnum.UNBOOKED]

    text: str = ""
    meeting: ScheduledMeeting


class GroupIssue(CustomModel):
    """Одна группа одновременно должна быть на нескольких занятиях."""

    issue_type: Literal[IssueTypeEnum.GROUP]

    text: str = ""
    group: str
    meetings: list[ScheduledMeeting]


class StudentIssue(CustomModel):
    """Студент из нескольких групп одновременно должен быть на нескольких занятиях."""

    issue_type: Literal[IssueTypeEnum.STUDENT]

    text: str = ""
    student: str
    meetings: list[ScheduledMeeting]


class PerWeekIssue(CustomModel):
    """Число занятий в неделю не совпадает с per_week в конфигурации компонента."""

    issue_type: Literal[IssueTypeEnum.PER_WEEK]

    text: str = ""
    course_name: str
    component_tag: str
    source_kind: Literal["core_course", "elective"]
    student_groups: tuple[str, ...] = ()
    expected_per_week: int
    actual_per_week: int


type Issue = Annotated[
    CapacityIssue
    | RoomIssue
    | OutlookIssue
    | TeacherIssue
    | UnplacedIssue
    | InstructorIdIssue
    | UnbookedIssue
    | GroupIssue
    | StudentIssue
    | PerWeekIssue,
    Field(discriminator="issue_type"),
]


class CheckParameters(CustomModel):
    check_room: bool = True
    check_teacher: bool = True
    check_capacity: bool = True
    check_group: bool = True
    check_student: bool = True
    check_outlook: bool = False
    check_unbooked: bool = True
    check_unplaced: bool = True
    check_per_week: bool = True
    check_instructor_id: bool = True


class CheckResults(CustomModel):
    issues: list[Issue]


class DateRange(CustomModel):
    start_date: datetime.date
    end_date: datetime.date

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError("start_date must be on or before end_date")
        return self
