from src.domain.exceptions.base import AppException


class RoomNotFoundException(AppException):
    status_code = 404
    detail = "room not found"
