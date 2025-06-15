from datetime import time

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class BaseLessonDTO(BaseModel):
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


class LessonWithCollisionsDTO(LessonWithTeacherAndGroup):
    collisions: list[LessonWithTeacherAndGroup] = Field(
        ...,
        default_factory=lambda: list(),
        description="Lessons which current lesson intersects with",
    )
