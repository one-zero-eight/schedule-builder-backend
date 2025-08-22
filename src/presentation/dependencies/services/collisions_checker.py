from dishka import Provider, Scope, provide

from src.domain.dtos.room import RoomDTO
from src.domain.dtos.teacher import TeacherDTO
from src.domain.services.graph import UndirectedGraph
from src.infrastructure.external_api.innohassle.booking import BookingService
from src.infrastructure.services.collisions_checker import CollisionsChecker


class CollisionsCheckerProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_collisions_checker(
        self,
        teachers: list[TeacherDTO],
        rooms: list[RoomDTO],
        booking_service: BookingService,
        graph: UndirectedGraph,
    ) -> CollisionsChecker:
        return CollisionsChecker(teachers, rooms, booking_service, graph)
