from datetime import time

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from src.domain.enums import CollisionTypeEnum


class BaseLessonDTO(BaseModel):
    lesson_name: str = Field(
        ..., description="Name of the lesson", max_length=200
    )
    weekday: str = Field(..., description="Weekday of a lesson", max_length=20)
    start_time: time = Field(..., description="Start time of lesson")
    end_time: time = Field(..., description="End time of lesson")
    room: str = Field(..., max_length=100, description="Room for lesson")

    @model_validator(mode="after")
    def validate_date(self) -> Self:
        if not self.start_time < self.end_time:
            raise ValueError("Start time has to be less than end time")
        return self


class LessonWithTeacherAndGroupDTO(BaseLessonDTO):
    teacher: str = Field(..., max_length=100, description="Teacher on lesson")
    group_name: str | None = Field(
        ...,
        max_length=100,
        description="Name of the group",
    )
    students_number: int = Field(
        ..., description="Number of students in the group"
    )


class LessonWithExcelCellsDTO(LessonWithTeacherAndGroupDTO):
    excel_range: str = Field(
        ..., max_length=15, description="Topleft corner of the cell"
    )


class LessonWithCollisionTypeDTO(LessonWithExcelCellsDTO):
    collision_type: CollisionTypeEnum = Field(
        ..., description="Type of collision"
    )


class LessonWithCollisionsDTO(LessonWithExcelCellsDTO):
    collisions: list[LessonWithCollisionTypeDTO] = Field(
        ..., description="List of colliding lessons", default_factory=lambda: list()
    )
