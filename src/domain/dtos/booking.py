from pydantic import BaseModel, EmailStr, Field, model_validator
from typing_extensions import Self
from datetime import datetime


class BookingDTO(BaseModel):
    email: EmailStr = Field(
        ..., description="The email of the person making the reservation"
    )
    title: str = Field("", max_length=40, description="Booking title")
    room: str = Field(
        ..., max_length=10, description="Room number for reservation"
    )
    start: datetime = Field(..., description="Start time of room reservation")
    end: datetime = Field(..., description="End time of room reservation")

    @model_validator(mode="after")
    def validate_date(self) -> Self:
        if not self.start < self.end:
            raise ValueError("Start time has to be less than end time")
        return self
