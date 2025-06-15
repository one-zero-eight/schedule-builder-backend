from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class BaseLessonDTO(BaseModel):
    start: datetime = Field(..., description="Start time of room reservation")
    end: datetime = Field(..., description="End time of room reservation")
    room: str = Field(..., max_length=10, description="Room for reservation")

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
