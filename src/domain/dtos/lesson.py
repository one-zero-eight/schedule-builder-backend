from datetime import time

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class BaseLessonDTO(BaseModel):
    lesson_name: str = Field(
        ..., description="Name of the lesson", max_length=200
    )
    weekday: str = Field(..., description="Weekday of a lesson", max_length=20)
    start: time = Field(..., description="Start time of lesson")
    end: time = Field(..., description="End time of lesson")
    room: str = Field(..., max_length=100, description="Room for lesson")

    @model_validator(mode="after")
    def validate_date(self) -> Self:
        if not self.start < self.end:
            raise ValueError("Start time has to be less than end time")
        return self


class LessonWithTeacherAndGroup(BaseLessonDTO):
    teacher: str = Field(..., max_length=100, description="Teacher on lesson")
    group_name: str | None = Field(
        ...,
        max_length=100,
        description="Name of the group",
    )
    students_number: int = Field(
        ..., description="Number of students in the group"
    )


class LessonWithExcelCells(LessonWithTeacherAndGroup):
    left: str = Field(
        ..., max_length=10, description="Topleft corner of the cell"
    )
    right: str = Field(
        ..., max_length=10, description="Bottom right corner of the cell"
    )


class LessonWithCollisionsDTO(LessonWithExcelCells):
    collisions: list[LessonWithExcelCells] = Field(
        ...,
        default_factory=lambda: list(),
        description="Lessons which current lesson intersects with",
    )


class LessonWithOutlookCollisionsDTO(LessonWithTeacherAndGroup):
    collisions: list[LessonWithTeacherAndGroup] = Field(
        ...,
        default_factory=lambda: list(),
        description="Outlook events which current lesson intersects with",
    )
