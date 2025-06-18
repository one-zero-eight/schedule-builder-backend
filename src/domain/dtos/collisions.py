from pydantic import BaseModel, Field

from src.domain.dtos.lesson import LessonWithCollisionsDTO, LessonWithTeacherAndGroup


class CollisionsDTO(BaseModel):
    rooms: list[LessonWithCollisionsDTO] = Field(
        ..., description="List of pairs of collisions by room"
    )
    teachers: list[LessonWithCollisionsDTO] = Field(
        ..., description="List of pairs of collisions by teacher"
    )
    capacity: list[LessonWithTeacherAndGroup] = Field(
        ...,
        description="Lessons where number of students is more than capacity of the room",
    )
