from datetime import date, time
from typing import Self

from pydantic import model_validator

from src.custom_pydantic import CustomModel


class BaseLessonDTO(CustomModel):
    lesson_name: str
    "Name of the lesson"
    weekday: str | None = None
    "Weekday of a lesson"
    start_time: time
    "Start time of lesson"
    end_time: time
    "End time of lesson"
    room: str | tuple[str, ...] | None = None
    "Room for lesson, None - TBA, if list - multiple rooms simultaneously"
    date_on: date | None = None
    "Specific dates with lessons"
    date_except: list[date] | None = None
    "Specific dates when there is no lessons"

    @model_validator(mode="after")
    def validate_date(self) -> Self:
        if not self.start_time < self.end_time:
            raise ValueError("Start time has to be less than end time")
        return self


class LessonWithTeacherAndGroupDTO(BaseLessonDTO):
    teacher: str
    "Teacher on lesson"
    teacher_email: str | None = None
    "Email of teacher"
    group_name: str | tuple[str, ...] | None = None
    "Name of the group or list of groups"
    students_number: int
    "Number of students in the group"


class LessonWithExcelCellsDTO(LessonWithTeacherAndGroupDTO):
    excel_sheet_name: str | None = None
    "Sheet name to which the lesson belongs"
    excel_range: str | None = None
    "Range of the lesson: may be multiple cells, for example 'A1:A10'"
