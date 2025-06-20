from dishka import Provider, Scope, provide

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.application.use_cases.collisions import CollisionsChecker
from src.domain.dtos.room import RoomDTO
from src.domain.dtos.teacher import TeacherDTO
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


class CollisionsCheckerProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_collisions_checker(
        self,
        parser: ICoursesParser,
        teachers: list[TeacherDTO],
        rooms: list[RoomDTO],
        booking_service: IBookingService,
    ) -> ICollisionsChecker:
        return CollisionsChecker(parser, teachers, rooms, booking_service)
