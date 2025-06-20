import datetime

from pydantic import BaseModel


class BookingDTO(BaseModel):
    """Booking description"""

    room_id: str
    "ID of the room"
    event_id: str | None = None
    "ID of the event"
    title: str
    "Title of the booking"
    start_time: datetime.datetime
    "Start time of booking"
    end_time: datetime.datetime
    "End time of booking"
