from pydantic import BaseModel, Field

from src.domain.dtos.lesson import (
    LessonWithCollisionsDTO,
    LessonWithExcelCells,
    LessonWithOutlookCollisionsDTO,
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
    outlook: list[LessonWithOutlookCollisionsDTO] = Field(
        ..., description="List of pairs of collisions with outlook events"
    )
