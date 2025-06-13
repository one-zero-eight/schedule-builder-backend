import datetime

from fastapi import APIRouter, Request

from src.api.auth import VerifiedDep
from src.modules.room_booking.repository import booking_repository, room_repository

router = APIRouter(tags=["bookings"])


@router.get("/dev/bookings/{room_id}")
def get_bookings(room_id: str, request: Request, _: VerifiedDep):
    return booking_repository.get_bookings(
        room_id, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=1), request.headers.get("Authorization")
    )


@router.get("/dev/rooms")
def get_rooms(request: Request, _: VerifiedDep):
    return room_repository.get_rooms(
        request.headers.get("Authorization")
    )
