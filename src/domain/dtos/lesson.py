from datetime import time

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class BaseLessonDTO(BaseModel):
    weekday: str = Field(..., description="Weekday of a lesson")
    start: time = Field(..., description="Start time of lesson")
    end: time = Field(..., description="End time of lesson")
    room: str = Field(..., max_length=10, description="Room for lesson")

    @model_validator(mode="after")
    def validate_date(self) -> Self:
        if not self.start < self.end:
            raise ValueError("Start time has to be less than end time")
        return self


class LessonWithTeacherAndGroup(BaseLessonDTO):
    teacher: str = Field(..., max_length=50, description="Teacher on lesson")
    group_name: str = Field(
        ..., max_length=10, description="Name of the group"
    )
