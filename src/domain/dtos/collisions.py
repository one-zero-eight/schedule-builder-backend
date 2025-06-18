from pydantic import BaseModel, Field

from src.domain.dtos.lesson import (
    LessonWithCollisionsDTO,
    LessonWithExcelCells,
)


class CollisionsDTO(BaseModel):
    rooms: list[LessonWithCollisionsDTO] = Field(
        ..., description="List of pairs of collisions by room"
    )
    teachers: list[LessonWithCollisionsDTO] = Field(
        ..., description="List of pairs of collisions by teacher"
    )
    capacity: list[LessonWithExcelCells] = Field(
        ...,
        description="Lessons where number of students is more than capacity of the room",
    )
