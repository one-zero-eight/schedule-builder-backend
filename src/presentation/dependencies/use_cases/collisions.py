from dishka import Provider, Scope, provide

from src.application.use_cases.collisions import CollisionsChecker
from src.domain.dtos.teacher import TeacherDTO
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker
from src.domain.dtos.room import RoomDTO


class CollisionsCheckerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_collisions_checker(
        self, parser: ICoursesParser, teachers: list[TeacherDTO], rooms: list[RoomDTO]
    ) -> ICollisionsChecker:
        return CollisionsChecker(parser, teachers, rooms)
