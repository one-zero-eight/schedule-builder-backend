import datetime

from fastapi import APIRouter
from fastapi.security import HTTPBearer

from src.api.dependencies import VerifyTokenDep
from src.modules.bookings.client import BookingDTO, RoomDTO, booking_client
from src.utcnow import utcnow

security = HTTPBearer()

router = APIRouter(tags=["Bookings"])


@router.get("/dev/bookings/{room_id}")
async def get_bookings(
    room_id: str,
    user_and_token: VerifyTokenDep,
) -> list[BookingDTO]:
    _now = utcnow()
    user, token = user_and_token
    return await booking_client.get_room_bookings(
        token,
        room_id,
        _now,
        _now + datetime.timedelta(days=1),
    )


@router.get("/dev/rooms")
async def get_rooms(user_and_token: VerifyTokenDep) -> list[RoomDTO]:
    user, token = user_and_token
    return await booking_client.get_rooms(token)
