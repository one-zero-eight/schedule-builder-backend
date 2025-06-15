from pydantic import BaseModel, Field

from src.domain.dtos.lesson import LessonWithTeacherAndGroup


class CollisionsDTO(BaseModel):
    rooms: list[
        tuple[LessonWithTeacherAndGroup, LessonWithTeacherAndGroup]
    ] = Field(..., description="List of pairs of collisions by room")
    teachers: list[
        tuple[LessonWithTeacherAndGroup, LessonWithTeacherAndGroup]
    ] = Field(..., description="List of pairs of collisions by room")
