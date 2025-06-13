from pydantic import BaseModel, Field
from src.domain.dtos.booking import BookingWithTeacherAndGroup


class CollisionsDTO(BaseModel):
    rooms: list[
        tuple[BookingWithTeacherAndGroup, BookingWithTeacherAndGroup]
    ] = Field(..., description="List of pairs of collisions by room")
    teachers: list[
        tuple[BookingWithTeacherAndGroup, BookingWithTeacherAndGroup]
    ] = Field(..., description="List of pairs of collisions by room")
