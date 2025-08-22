import datetime

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.domain.dtos.booking import BookingDTO
from src.domain.dtos.room import RoomDTO
from src.infrastructure.external_api.innohassle.booking import BookingService
from src.infrastructure.external_api.innohassle.room import RoomService

router = APIRouter(tags=["Bookings"], route_class=DishkaRoute)


@router.get("/dev/bookings/{room_id}")
async def get_bookings(
    room_id: str,
    booking_service: FromDishka[BookingService],
) -> list[BookingDTO]:
    return await booking_service.get_room_bookings(
        room_id,
        datetime.datetime.now(),
        datetime.datetime.now() + datetime.timedelta(days=1),
    )


@router.get("/dev/rooms")
async def get_rooms(room_service: FromDishka[RoomService]) -> list[RoomDTO]:
    return await room_service.get_rooms()
