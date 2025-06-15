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
from src.domain.dtos.users import UserTokenDataDTO


router = APIRouter(tags=["bookings"], route_class=DishkaRoute)


@router.get("/dev/bookings/{room_id}")
async def get_bookings(
    room_id: str,
    _: FromDishka[UserTokenDataDTO],
    booking_service: FromDishka[IBookingService],
):
    return await booking_service.get_bookings(
        room_id,
        datetime.datetime.now(),
        datetime.datetime.now() + datetime.timedelta(days=1),
    )


@router.get("/dev/rooms")
async def get_rooms(
    _: FromDishka[UserTokenDataDTO], room_service: FromDishka[IRoomService]
):
    return await room_service.get_rooms()
