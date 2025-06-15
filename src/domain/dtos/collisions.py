from pydantic import BaseModel, Field

from src.domain.dtos.lesson import LessonWithCollisionsDTO


class CollisionsDTO(BaseModel):
    rooms: list[LessonWithCollisionsDTO] = Field(
        ..., description="List of pairs of collisions by room"
    )
    teachers: list[LessonWithCollisionsDTO] = Field(
        ..., description="List of pairs of collisions by teacher"
    )
