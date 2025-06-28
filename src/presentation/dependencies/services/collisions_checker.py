from dishka import Provider, Scope, provide

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.domain.dtos.room import RoomDTO
from src.domain.dtos.teacher import TeacherDTO
from src.domain.interfaces.graph import IGraph
from src.domain.interfaces.services.collisions_checker import (
    ICollisionsChecker,
)
from src.infrastructure.services.collisions_checker import CollisionsChecker


class CollisionsCheckerProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_collisions_checker(
        self,
        teachers: list[TeacherDTO],
        rooms: list[RoomDTO],
        booking_service: IBookingService,
        graph: IGraph,
    ) -> ICollisionsChecker:
        return CollisionsChecker(teachers, rooms, booking_service, graph)
