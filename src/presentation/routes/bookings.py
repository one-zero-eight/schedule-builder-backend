import datetime

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Request

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.application.external_api.innohassle.interfaces.room import (
    IRoomService,
)
from src.domain.dtos.booking import BookingDTO
from src.domain.dtos.room import RoomDTO


router = APIRouter(tags=["Bookings"], route_class=DishkaRoute)


@router.get("/dev/bookings/{room_id}")
async def get_bookings(
    room_id: str,
    booking_service: FromDishka[IBookingService],
) -> list[BookingDTO]:
    return await booking_service.get_bookings(
        room_id,
        datetime.datetime.now(),
        datetime.datetime.now() + datetime.timedelta(days=1),
    )


@router.get("/dev/rooms")
async def get_rooms(room_service: FromDishka[IRoomService]) -> list[RoomDTO]:
    return await room_service.get_rooms()
